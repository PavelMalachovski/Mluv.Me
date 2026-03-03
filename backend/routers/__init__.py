"""
API routers для FastAPI endpoints.
"""

from . import (
    users,
    lesson,
    stats,
    words,
    web_auth,
    web_lessons,
    gamification,
    messages,
    subscription,
)

__all__ = [
    "users",
    "lesson",
    "stats",
    "words",
    "web_auth",
    "web_lessons",
    "gamification",
    "messages",
    "subscription",
]
