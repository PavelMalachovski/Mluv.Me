"""Web-specific lesson endpoints for text-based learning"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from backend.db.database import get_session
from backend.db.repositories import (
    UserRepository,
    MessageRepository,
    UserSettingsRepository
)
from backend.services.honzik_personality import HonzikPersonality
from backend.services.gamification import GamificationService
from backend.services.openai_client import OpenAIClient

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
    db: AsyncSession = Depends(get_session)
):
    """
    Process text input (no audio) for web users

    Args:
        request: Text message request
        db: Database session

    Returns:
        Honzík's response with corrections
    """
    # Get user settings
    user_repo = UserRepository(db)
    settings_repo = UserSettingsRepository(db)
    message_repo = MessageRepository(db)

    user = await user_repo.get_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    settings = await settings_repo.get_by_user_id(request.user_id)

    # Get conversation history (last 5 messages)
    recent_messages = await message_repo.get_recent_by_user(
        user_id=request.user_id,
        limit=5
    )

    conversation_history = [
        {
            "role": msg.role,
            "content": msg.text
        }
        for msg in reversed(recent_messages)
    ]

    # Process with Honzík
    openai_client = OpenAIClient()
    honzik = HonzikPersonality(openai_client)

    response = await honzik.generate_response(
        user_text=request.text,
        style=settings.conversation_style if settings else "friendly",
        level=user.level,
        corrections_level=settings.corrections_level if settings else "balanced",
        ui_language=user.ui_language,
        conversation_history=conversation_history
    )

    # Save user message
    user_message = await message_repo.create(
        user_id=request.user_id,
        role="user",
        text=request.text,
        transcript_raw=request.text,
        transcript_normalized=request.text,
        correctness_score=response.get("correctness_score", 0),
        words_total=len(request.text.split()),
        words_correct=int(len(request.text.split()) * response.get("correctness_score", 0) / 100)
    )

    # Save Honzík's response
    await message_repo.create(
        user_id=request.user_id,
        role="assistant",
        text=response["honzik_response"]
    )

    # Calculate stars
    gamification = GamificationService(db)
    stars = await gamification.calculate_stars(
        correctness_score=response.get("correctness_score", 0)
    )

    # Update user stats
    await gamification.update_daily_stats(
        user_id=request.user_id,
        messages_count=1,
        words_said=len(request.text.split()),
        correct_percent=response.get("correctness_score", 0)
    )

    return TextMessageResponse(
        honzik_text=response["honzik_response"],
        honzik_transcript=response["honzik_response"],  # Same as text response for now
        user_mistakes=response.get("mistakes", []),
        suggestions=[response.get("suggestion", "")],
        stars_earned=stars,
        correctness_score=response.get("correctness_score", 0)
    )


@router.get("/history", response_model=MessageHistoryResponse)
async def get_lesson_history(
    user_id: int,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_session)
):
    """
    Get paginated lesson history with audio URLs

    Args:
        user_id: User ID
        page: Page number (1-indexed)
        limit: Items per page
        db: Database session

    Returns:
        Paginated message history
    """
    message_repo = MessageRepository(db)

    offset = (page - 1) * limit

    messages = await message_repo.get_by_user_paginated(
        user_id=user_id,
        offset=offset,
        limit=limit
    )

    total = await message_repo.count_by_user(user_id)

    message_items = [
        MessageHistoryItem(
            id=msg.id,
            role=msg.role,
            text=msg.text,
            correctness_score=msg.correctness_score,
            created_at=msg.created_at.isoformat(),
            user_mistakes=[] if not msg.role == "user" else []  # TODO: Add mistakes parsing
        )
        for msg in messages
    ]

    return MessageHistoryResponse(
        messages=message_items,
        pagination={
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    )
