"""
Achievement Service.
Сервис для проверки и выдачи достижений.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.achievement import Achievement, UserAchievement
from backend.models.user import User
from backend.models.word import SavedWord

logger = structlog.get_logger()


class AchievementCategory(str, Enum):
    """Achievement categories."""
    STREAK = "streak"
    MESSAGES = "messages"
    VOCABULARY = "vocabulary"
    ACCURACY = "accuracy"
    STARS = "stars"
    REVIEW = "review"


class AchievementService:
    """
    Сервис для работы с достижениями.

    Проверяет условия и выдает достижения пользователям.
    """

    async def check_achievements(
        self,
        session: AsyncSession,
        user: User,
        category: Optional[AchievementCategory] = None,
        current_value: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Check and unlock achievements for a user.

        Args:
            session: Database session
            user: User to check achievements for
            category: Optional category to check (checks all if not specified)
            current_value: Current value for the category (e.g., streak count)

        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked = []

        # Get all achievements for the category (or all if not specified)
        query = select(Achievement)
        if category:
            query = query.where(Achievement.category == category.value)

        result = await session.execute(query)
        achievements = result.scalars().all()

        # Get user's already unlocked achievements
        unlocked_query = select(UserAchievement.achievement_id).where(
            UserAchievement.user_id == user.id
        )
        unlocked_result = await session.execute(unlocked_query)
        unlocked_ids = set(unlocked_result.scalars().all())

        for achievement in achievements:
            if achievement.id in unlocked_ids:
                continue

            # Calculate current value based on category
            value = current_value
            if value is None:
                value = await self._get_category_value(session, user, achievement.category)

            # Check if threshold is met
            if value >= achievement.threshold:
                # Unlock achievement
                user_achievement = UserAchievement(
                    user_id=user.id,
                    achievement_id=achievement.id,
                    progress=value,
                )
                session.add(user_achievement)

                # Award stars
                if achievement.stars_reward > 0:
                    user.stars = (user.stars or 0) + achievement.stars_reward

                newly_unlocked.append({
                    "id": achievement.id,
                    "code": achievement.code,
                    "name": achievement.name,
                    "description": achievement.description,
                    "icon": achievement.icon,
                    "category": achievement.category,
                    "stars_reward": achievement.stars_reward,
                })

                logger.info(
                    "achievement_unlocked",
                    user_id=user.id,
                    achievement_code=achievement.code,
                    stars_reward=achievement.stars_reward,
                )

        if newly_unlocked:
            await session.commit()

        return newly_unlocked

    async def _get_category_value(
        self,
        session: AsyncSession,
        user: User,
        category: str,
    ) -> int:
        """Get current value for a category."""
        if category == "streak":
            return user.streak or 0
        elif category == "messages":
            return user.messages_count or 0
        elif category == "stars":
            return user.stars or 0
        elif category == "vocabulary":
            # Count saved words
            query = select(SavedWord).where(SavedWord.user_id == user.id)
            result = await session.execute(query)
            return len(result.scalars().all())
        elif category == "review":
            # Count mastered words (interval >= 90 days)
            query = select(SavedWord).where(
                SavedWord.user_id == user.id,
                SavedWord.interval_days >= 90
            )
            result = await session.execute(query)
            return len(result.scalars().all())
        return 0

    async def get_user_achievements(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Get all achievements for a user with unlock status.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            List of achievements with unlock status
        """
        # Get all achievements
        all_query = select(Achievement).order_by(Achievement.category, Achievement.threshold)
        all_result = await session.execute(all_query)
        all_achievements = all_result.scalars().all()

        # Get user's unlocked achievements
        unlocked_query = (
            select(UserAchievement)
            .where(UserAchievement.user_id == user_id)
        )
        unlocked_result = await session.execute(unlocked_query)
        unlocked_map = {ua.achievement_id: ua for ua in unlocked_result.scalars().all()}

        achievements = []
        for achievement in all_achievements:
            unlocked = unlocked_map.get(achievement.id)

            # Skip hidden achievements that aren't unlocked
            if achievement.is_hidden and not unlocked:
                continue

            achievements.append({
                "id": achievement.id,
                "code": achievement.code,
                "name": achievement.name,
                "description": achievement.description,
                "icon": achievement.icon,
                "category": achievement.category,
                "threshold": achievement.threshold,
                "stars_reward": achievement.stars_reward,
                "is_unlocked": unlocked is not None,
                "unlocked_at": unlocked.unlocked_at.isoformat() if unlocked else None,
                "progress": unlocked.progress if unlocked else 0,
            })

        return achievements

    async def get_achievement_progress(
        self,
        session: AsyncSession,
        user: User,
    ) -> Dict[str, Any]:
        """
        Get achievement progress summary for a user.

        Args:
            session: Database session
            user: User

        Returns:
            Progress summary by category
        """
        # Get counts
        total_query = select(Achievement).where(Achievement.is_hidden == False)
        total_result = await session.execute(total_query)
        total_count = len(total_result.scalars().all())

        unlocked_query = select(UserAchievement).where(UserAchievement.user_id == user.id)
        unlocked_result = await session.execute(unlocked_query)
        unlocked_count = len(unlocked_result.scalars().all())

        # Get category values
        categories = {
            "streak": user.streak or 0,
            "messages": user.messages_count or 0,
            "stars": user.stars or 0,
            "vocabulary": await self._get_category_value(session, user, "vocabulary"),
            "review": await self._get_category_value(session, user, "review"),
        }

        return {
            "total_achievements": total_count,
            "unlocked_achievements": unlocked_count,
            "completion_percent": round((unlocked_count / total_count) * 100) if total_count > 0 else 0,
            "category_progress": categories,
        }
