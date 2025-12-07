"""
SQLAlchemy models для Mluv.Me.
"""

from backend.models.user import User, UserSettings
from backend.models.message import Message
from backend.models.word import SavedWord
from backend.models.stats import DailyStats, Stars

__all__ = [
    "User",
    "UserSettings",
    "Message",
    "SavedWord",
    "DailyStats",
    "Stars",
]



