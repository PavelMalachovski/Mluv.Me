"""Web authentication endpoints for Telegram Login Widget"""

from fastapi import APIRouter, HTTPException, Response, Depends
from pydantic import BaseModel
from typing import Optional
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.db.database import get_db
from backend.db.repositories import UserRepository
from backend.models.user import User

router = APIRouter(prefix="/api/v1/web/auth", tags=["web_auth"])


class TelegramAuthData(BaseModel):
    """Telegram Login Widget auth data"""
    id: int
    first_name: str
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str


class SessionData(BaseModel):
    """Session data"""
    user_id: int
    session_token: str
    created_at: datetime
    expires_at: datetime


# Simple in-memory session storage (for MVP, replace with Redis in production)
sessions: dict[str, SessionData] = {}


def verify_telegram_auth(auth_data: TelegramAuthData) -> bool:
    """
    Verify Telegram auth data hash

    Args:
        auth_data: Telegram authentication data

    Returns:
        True if hash is valid, False otherwise
    """
    # Create check string
    check_dict = auth_data.dict(exclude={"hash"})
    check_dict = {k: v for k, v in check_dict.items() if v is not None}

    check_string = "\n".join([
        f"{k}={v}"
        for k, v in sorted(check_dict.items())
    ])

    # Create secret key from bot token
    secret_key = hashlib.sha256(
        settings.TELEGRAM_BOT_TOKEN.encode()
    ).digest()

    # Calculate expected hash
    expected_hash = hmac.new(
        secret_key,
        check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    return expected_hash == auth_data.hash


def generate_session_token() -> str:
    """Generate secure session token"""
    return secrets.token_urlsafe(32)


@router.post("/telegram")
async def telegram_web_auth(
    auth_data: TelegramAuthData,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify Telegram Login Widget data and create session

    Args:
        auth_data: Telegram authentication data
        response: FastAPI response object
        db: Database session

    Returns:
        User data and access token
    """
    # Verify hash
    if not verify_telegram_auth(auth_data):
        raise HTTPException(status_code=403, detail="Invalid auth data")

    # Check auth date (max 1 hour old)
    current_timestamp = int(datetime.now().timestamp())
    if current_timestamp - auth_data.auth_date > 3600:
        raise HTTPException(status_code=403, detail="Auth data expired")

    # Get or create user
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(auth_data.id)

    if not user:
        # Create new user
        user = await user_repo.create(
            telegram_id=auth_data.id,
            first_name=auth_data.first_name,
            username=auth_data.username,
            ui_language="ru",  # Default language
            czech_level="beginner"  # Default level
        )

    # Create session
    session_token = generate_session_token()
    expires_at = datetime.now() + timedelta(days=30)

    session_data = SessionData(
        user_id=user.id,
        session_token=session_token,
        created_at=datetime.now(),
        expires_at=expires_at
    )

    sessions[session_token] = session_data

    # Set httpOnly cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=30 * 24 * 60 * 60  # 30 days
    )

    return {
        "user": {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "first_name": user.first_name,
            "username": user.username,
            "ui_language": user.ui_language,
            "czech_level": user.czech_level,
            "created_at": user.created_at.isoformat()
        },
        "access_token": session_token
    }


@router.post("/logout")
async def logout(response: Response, session_token: Optional[str] = None):
    """
    Logout user and invalidate session

    Args:
        response: FastAPI response object
        session_token: Session token to invalidate
    """
    if session_token and session_token in sessions:
        del sessions[session_token]

    response.delete_cookie("session_token")

    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user(
    session_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user

    Args:
        session_token: Session token from cookie
        db: Database session

    Returns:
        Current user data
    """
    if not session_token or session_token not in sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session_data = sessions[session_token]

    # Check if session expired
    if datetime.now() > session_data.expires_at:
        del sessions[session_token]
        raise HTTPException(status_code=401, detail="Session expired")

    # Get user from database
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(session_data.user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "first_name": user.first_name,
        "username": user.username,
        "ui_language": user.ui_language,
        "czech_level": user.czech_level,
        "created_at": user.created_at.isoformat()
    }
