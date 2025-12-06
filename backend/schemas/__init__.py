"""
Pydantic schemas для API endpoints.
"""

from backend.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserSettingsResponse,
    UserSettingsUpdate,
)
from backend.schemas.lesson import (
    MistakeSchema,
    CorrectionSchema,
    DailyChallengeSchema,
    LessonProcessRequest,
    LessonProcessResponse,
    VoiceSettingsSchema,
)

__all__ = [
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "UserSettingsResponse",
    "UserSettingsUpdate",
    "MistakeSchema",
    "CorrectionSchema",
    "DailyChallengeSchema",
    "LessonProcessRequest",
    "LessonProcessResponse",
    "VoiceSettingsSchema",
]


