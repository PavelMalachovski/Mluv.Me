"""Web-specific lesson endpoints for text-based learning"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_session
from backend.db.repositories import (
    MessageRepository,
    UserSettingsRepository,
)
from backend.services.honzik_personality import HonzikPersonality
from backend.services.openai_client import OpenAIClient
from backend.services.lesson_processing import (
    save_lesson_messages,
    update_lesson_gamification,
)
from backend.config import get_settings
from backend.routers.web_auth import get_authenticated_user
from backend.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/api/v1/web/lessons", tags=["web_lessons"])


class TextMessageRequest(BaseModel):
    """Request for text message processing"""

    text: str
    user_id: int


class TextMessageResponse(BaseModel):
    """Response for text message processing"""

    honzik_text: str
    honzik_transcript: str  # Transcript of Honzík's audio response
    user_mistakes: List[str]
    suggestions: List[str]
    stars_earned: int
    correctness_score: float


class MessageHistoryItem(BaseModel):
    """Single message in history"""

    id: int
    role: str
    text: str
    correctness_score: Optional[float]
    created_at: str
    user_mistakes: Optional[List[str]]


class MessageHistoryResponse(BaseModel):
    """Paginated message history response"""

    messages: List[MessageHistoryItem]
    pagination: dict


@router.post("/text", response_model=TextMessageResponse)
async def process_text_message(
    request: TextMessageRequest,
    auth_user=Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Process text input (no audio) for web users.
    Requires authentication (Bearer token or httpOnly cookie).
    """
    # Use authenticated user, ignore request.user_id to prevent IDOR
    user = auth_user
    user_id = user.id

    # Quota check (text)
    sub_svc = SubscriptionService(db)
    quota = await sub_svc.check_quota(user_id, "text")
    if not quota["allowed"]:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "daily_limit_reached",
                "message": "Denní limit textových zpráv vyčerpán",
                "plan": quota["plan"],
                "used": quota["used"],
                "limit": quota["limit"],
            },
        )

    # Get user settings
    settings_repo = UserSettingsRepository(db)
    message_repo = MessageRepository(db)

    settings = await settings_repo.get_by_user_id(user_id)

    # Get conversation history (last 5 messages)
    recent_messages = await message_repo.get_recent_by_user(user_id=user_id, limit=5)

    conversation_history = [
        {"role": msg.role, "content": msg.text} for msg in reversed(recent_messages)
    ]

    # Process with character (Honzík or paní Nováková)
    settings_obj = get_settings()
    openai_client = OpenAIClient(settings_obj)
    honzik = HonzikPersonality(openai_client)

    character = settings.character if settings else "honzik"

    response = await honzik.generate_response(
        user_text=request.text,
        style=settings.conversation_style if settings else "friendly",
        level=user.level,
        corrections_level=settings.corrections_level if settings else "balanced",
        native_language=user.native_language,
        conversation_history=conversation_history,
        character=character,
    )

    # Save messages using shared service
    correctness = response.get("correctness_score", 0)
    await save_lesson_messages(
        db=db,
        user_id=user_id,
        user_text=request.text,
        assistant_text=response["honzik_response"],
        correctness_score=correctness,
    )

    # Update gamification using shared service
    user_timezone = settings.timezone if settings else None
    stars_result = await update_lesson_gamification(
        db=db,
        user_id=user_id,
        correctness_score=correctness,
        words_count=len(request.text.split()),
        timezone_str=user_timezone,
    )

    await db.commit()

    # Increment daily text quota
    await sub_svc.increment_usage(user_id, "text")

    return TextMessageResponse(
        honzik_text=response["honzik_response"],
        honzik_transcript=response["honzik_response"],  # Same as text response for now
        user_mistakes=response.get("mistakes", []),
        suggestions=[response.get("suggestion", "")],
        stars_earned=stars_result["stars_earned"],
        correctness_score=response.get("correctness_score", 0),
    )


@router.get("/history", response_model=MessageHistoryResponse)
async def get_lesson_history(
    page: int = 1,
    limit: int = 20,
    auth_user=Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get paginated lesson history.
    Requires authentication (Bearer token or httpOnly cookie).
    """
    user_id = auth_user.id
    message_repo = MessageRepository(db)

    offset = (page - 1) * limit

    messages = await message_repo.get_by_user_paginated(
        user_id=user_id, offset=offset, limit=limit
    )

    total = await message_repo.count_by_user(user_id)

    message_items = [
        MessageHistoryItem(
            id=msg.id,
            role=msg.role,
            text=msg.text,
            correctness_score=msg.correctness_score,
            created_at=msg.created_at.isoformat(),
            user_mistakes=[]
            if not msg.role == "user"
            else [],  # TODO: Add mistakes parsing
        )
        for msg in messages
    ]

    return MessageHistoryResponse(
        messages=message_items,
        pagination={
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit,
        },
    )
