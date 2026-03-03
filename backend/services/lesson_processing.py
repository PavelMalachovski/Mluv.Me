"""
Shared lesson processing logic.

Extracted from web_lessons.py and lesson.py to avoid code duplication.
Both endpoints (web text, mobile voice/text) share the same core:
 - Save user/assistant messages
 - Update daily stats
 - Award stars via gamification
"""

from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from backend.db.repositories import (
    MessageRepository,
    StatsRepository,
    UserRepository,
)
from backend.services.gamification import GamificationService

logger = structlog.get_logger(__name__)


async def save_lesson_messages(
    db: AsyncSession,
    user_id: int,
    user_text: str,
    assistant_text: str,
    correctness_score: float = 0,
    corrected_text: str | None = None,
    words_total: int | None = None,
    words_correct: int | None = None,
) -> None:
    """
    Save user and assistant messages to the database.

    Args:
        db: Database session
        user_id: User ID
        user_text: Original user text
        assistant_text: Honzik's response text
        correctness_score: Score 0-100
        corrected_text: Corrected version of user text (optional)
        words_total: Total words in message
        words_correct: Correct words count
    """
    message_repo = MessageRepository(db)

    w_total = words_total if words_total is not None else len(user_text.split())
    w_correct = words_correct if words_correct is not None else int(
        w_total * correctness_score / 100
    )

    # Save user message
    await message_repo.create(
        user_id=user_id,
        role="user",
        text=corrected_text or user_text,
        transcript_raw=user_text,
        transcript_normalized=corrected_text or user_text,
        correctness_score=correctness_score,
        words_total=w_total,
        words_correct=w_correct,
    )

    # Save assistant message
    await message_repo.create(
        user_id=user_id,
        role="assistant",
        text=assistant_text,
    )


async def update_lesson_gamification(
    db: AsyncSession,
    user_id: int,
    correctness_score: float,
    words_count: int,
    timezone_str: str | None = None,
) -> dict:
    """
    Update daily stats and award stars after a lesson message.

    Args:
        db: Database session
        user_id: User ID
        correctness_score: Score 0-100
        words_count: Number of words in message
        timezone_str: User timezone string

    Returns:
        dict with stars_earned, total_stars, available_stars
    """
    stats_repo = StatsRepository(db)
    user_repo = UserRepository(db)
    gamification = GamificationService(stats_repo, user_repo)

    user_date = gamification.get_user_date(timezone_str)

    # Get current streak for star calculation
    summary = await stats_repo.get_user_summary(user_id)
    current_streak = summary.get("current_streak", 0)

    stars = gamification.calculate_stars_for_message(
        correctness_score=int(correctness_score),
        current_streak=current_streak,
    )

    # Award stars atomically
    stars_result = await gamification.award_stars(db, user_id, stars)

    # Update daily stats
    daily_stats = await stats_repo.get_or_create_daily(user_id, user_date)
    await stats_repo.update_daily(
        user_id=user_id,
        date_value=user_date,
        messages_count=daily_stats.messages_count + 1,
        words_said=daily_stats.words_said + words_count,
        correct_percent=int(correctness_score),
    )

    return stars_result
