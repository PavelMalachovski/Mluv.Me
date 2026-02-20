"""
Pydantic schemas для User и UserSettings.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    """Schema для создания пользователя."""

    model_config = ConfigDict(
        # Performance optimizations
        validate_assignment=False,
        str_strip_whitespace=True,
        use_enum_values=True,
    )

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
    native_language: str = Field(
        default="ru",
        description="Родной язык — ISO 639-1 код (ru, uk, vi, ...)"
    )
    level: Literal["beginner", "intermediate", "advanced", "native"] = Field(
        default="beginner",
        description="Уровень чешского языка"
    )


class UserUpdate(BaseModel):
    """Schema для обновления пользователя."""

    model_config = ConfigDict(
        # Performance optimizations
        validate_assignment=False,
        str_strip_whitespace=True,
        use_enum_values=True,
    )

    username: str | None = None
    first_name: str | None = None
    native_language: str | None = None
    level: Literal["beginner", "intermediate", "advanced", "native"] | None = None


class UserResponse(BaseModel):
    """Schema для ответа с пользователем."""

    model_config = ConfigDict(
        from_attributes=True,
        # Performance optimizations
        validate_assignment=False,
        str_strip_whitespace=True,
        use_enum_values=True,
    )

    id: int
    telegram_id: int
    username: str | None
    first_name: str
    native_language: str
    level: Literal["beginner", "intermediate", "advanced", "native"]
    created_at: datetime
    updated_at: datetime


class UserSettingsUpdate(BaseModel):
    """Schema для обновления настроек пользователя."""

    model_config = ConfigDict(
        # Performance optimizations
        validate_assignment=False,
        use_enum_values=True,
    )

    conversation_style: Literal["friendly", "tutor", "casual"] | None = None
    voice_speed: Literal["very_slow", "slow", "normal", "native"] | None = None
    corrections_level: Literal["minimal", "balanced", "detailed"] | None = None
    timezone: str | None = None
    notifications_enabled: bool | None = None


class UserSettingsResponse(BaseModel):
    """Schema для ответа с настройками пользователя."""

    model_config = ConfigDict(
        from_attributes=True,
        # Performance optimizations
        validate_assignment=False,
        use_enum_values=True,
    )

    id: int
    user_id: int
    conversation_style: Literal["friendly", "tutor", "casual"]
    voice_speed: Literal["very_slow", "slow", "normal", "native"]
    corrections_level: Literal["minimal", "balanced", "detailed"]
    timezone: str
    notifications_enabled: bool



