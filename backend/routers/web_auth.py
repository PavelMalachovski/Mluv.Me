"""Web authentication endpoints for Telegram Login Widget and Web App"""

from fastapi import APIRouter, HTTPException, Response, Depends
from pydantic import BaseModel
from typing import Optional
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from urllib.parse import parse_qsl
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import get_settings
from backend.db.database import get_session
from backend.db.repositories import UserRepository
from backend.models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def format_datetime(dt) -> str:
    """
    Safely format datetime to ISO string.
    Handles both datetime objects and strings.

    Args:
        dt: datetime object or ISO string

    Returns:
        ISO formatted string
    """
    if isinstance(dt, str):
        return dt
    if isinstance(dt, datetime):
        return dt.isoformat()
    return str(dt) if dt else None


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
    settings = get_settings()

    # Create check string
    check_dict = auth_data.dict(exclude={"hash"})
    check_dict = {k: v for k, v in check_dict.items() if v is not None}

    check_string = "\n".join([
        f"{k}={v}"
        for k, v in sorted(check_dict.items())
    ])

    # Create secret key from bot token
    secret_key = hashlib.sha256(
        settings.telegram_bot_token.encode()
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
    db: AsyncSession = Depends(get_session)
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
            level="beginner"  # Default level
        )
        await db.commit()

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
            "level": user.level,
            "created_at": format_datetime(user.created_at)
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
    db: AsyncSession = Depends(get_session)
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
        "level": user.level,
        "created_at": format_datetime(user.created_at)
    }


class WebAppAuthData(BaseModel):
    """Telegram Web App auth data"""
    initData: str


def validate_telegram_web_app_data(init_data: str, bot_token: str) -> dict:
    """
    Validate Telegram Web App initData signature

    Args:
        init_data: initData string from Telegram Web App
        bot_token: Bot token from BotFather

    Returns:
        Parsed and validated data

    Raises:
        ValueError: If signature is invalid
    """
    try:
        # Parse init_data
        parsed_data = dict(parse_qsl(init_data, keep_blank_values=True))

        # Extract hash
        hash_value = parsed_data.pop('hash', None)
        if not hash_value:
            raise ValueError("No hash in init_data")

        # Create data-check-string
        data_check_arr = [f"{k}={v}" for k, v in sorted(parsed_data.items())]
        data_check_string = '\n'.join(data_check_arr)

        # Create secret key
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=bot_token.encode(),
            digestmod=hashlib.sha256
        ).digest()

        # Calculate hash
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        # Verify hash
        if calculated_hash != hash_value:
            raise ValueError("Invalid hash")

        # Check auth_date (not older than 1 hour)
        if 'auth_date' in parsed_data:
            auth_date = int(parsed_data['auth_date'])
            current_time = int(datetime.utcnow().timestamp())
            if current_time - auth_date > 3600:  # 1 hour
                raise ValueError("Auth data expired")

        return parsed_data

    except Exception as e:
        raise ValueError(f"Invalid init_data: {str(e)}")


@router.post("/webapp")
async def authenticate_web_app(
    auth_data: WebAppAuthData,
    db: AsyncSession = Depends(get_session)
):
    """
    Authenticate user via Telegram Web App

    This endpoint validates the initData from Telegram Web App
    and creates a session for the user.
    """
    settings = get_settings()

    try:
        # Validate initData
        validated_data = validate_telegram_web_app_data(
            auth_data.initData,
            settings.telegram_bot_token
        )

        # Extract user data
        import json
        user_data = json.loads(validated_data.get('user', '{}'))

        if not user_data or 'id' not in user_data:
            raise HTTPException(status_code=400, detail="No user data in initData")

        telegram_id = user_data['id']
        first_name = user_data.get('first_name', 'User')
        username = user_data.get('username')

        # Get or create user
        user_repo = UserRepository(db)
        user = await user_repo.get_by_telegram_id(telegram_id)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found. Please start the bot first with /start"
            )

        # Create session
        session_token = secrets.token_urlsafe(32)
        session_data = SessionData(
            user_id=user.id,
            session_token=session_token,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )

        sessions[session_token] = session_data

        return {
            "success": True,
            "token": session_token,
            "user": {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "first_name": user.first_name,
                "username": user.username,
                "ui_language": user.ui_language,
                "level": user.level,
                "created_at": format_datetime(user.created_at)
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")
