"""
Pydantic schemas для User и UserSettings.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    """Schema для создания пользователя."""

    telegram_id: int = Field(
        description="Telegram user ID"
    )
    username: str | None = Field(
        default=None,
        description="Telegram username"
    )
    first_name: str = Field(
        description="Имя пользователя"
    )
    ui_language: Literal["ru", "uk"] = Field(
        default="ru",
        description="Язык интерфейса"
    )
    level: Literal["beginner", "intermediate", "advanced", "native"] = Field(
        default="beginner",
        description="Уровень чешского языка"
    )


class UserUpdate(BaseModel):
    """Schema для обновления пользователя."""

    username: str | None = None
    first_name: str | None = None
    ui_language: Literal["ru", "uk"] | None = None
    level: Literal["beginner", "intermediate", "advanced", "native"] | None = None


class UserResponse(BaseModel):
    """Schema для ответа с пользователем."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int
    username: str | None
    first_name: str
    ui_language: Literal["ru", "uk"]
    level: Literal["beginner", "intermediate", "advanced", "native"]
    created_at: datetime
    updated_at: datetime


class UserSettingsUpdate(BaseModel):
    """Schema для обновления настроек пользователя."""

    conversation_style: Literal["friendly", "tutor", "casual"] | None = None
    voice_speed: Literal["very_slow", "slow", "normal", "native"] | None = None
    corrections_level: Literal["minimal", "balanced", "detailed"] | None = None
    timezone: str | None = None
    notifications_enabled: bool | None = None


class UserSettingsResponse(BaseModel):
    """Schema для ответа с настройками пользователя."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    conversation_style: Literal["friendly", "tutor", "casual"]
    voice_speed: Literal["very_slow", "slow", "normal", "native"]
    corrections_level: Literal["minimal", "balanced", "detailed"]
    timezone: str
    notifications_enabled: bool



