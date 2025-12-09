"""
Spaced Repetition Service using SM-2 Algorithm.

SM-2 Algorithm (SuperMemo 2):
- Качество ответа: 0-5 (0=полный провал, 5=идеально)
- Мы упрощаем до 4 уровней: again(0), hard(1), good(2), easy(3)
"""

from datetime import date, timedelta
from typing import Dict, Any, Tuple
from enum import IntEnum

import structlog

logger = structlog.get_logger()


class ResponseQuality(IntEnum):
    """Quality of user response."""
    AGAIN = 0  # Complete blackout, need to relearn
    HARD = 1   # Incorrect but upon seeing the answer, remembered
    GOOD = 2   # Correct with difficulty
    EASY = 3   # Perfect response, very easy


# SM-2 quality mapping (our 0-3 -> SM-2 0-5)
SM2_QUALITY_MAP = {
    ResponseQuality.AGAIN: 0,
    ResponseQuality.HARD: 2,
    ResponseQuality.GOOD: 4,
    ResponseQuality.EASY: 5,
}


class SpacedRepetitionService:
    """
    Сервис для расчета интервалов повторения по алгоритму SM-2.

    SM-2 Algorithm:
    1. EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
    2. If EF < 1.3, set EF = 1.3
    3. If q < 3, reset interval to 1 day
    4. Otherwise: I(1) = 1, I(2) = 6, I(n) = I(n-1) * EF
    """

    MIN_EASE_FACTOR = 1.3
    MAX_EASE_FACTOR = 3.0
    DEFAULT_EASE_FACTOR = 2.5

    def calculate_next_review(
        self,
        quality: int,
        current_ease_factor: float,
        current_interval: int,
        review_count: int
    ) -> Tuple[float, int, date]:
        """
        Calculate next review parameters based on response quality.

        Args:
            quality: Response quality (0-3, mapped to SM-2 0-5)
            current_ease_factor: Current ease factor
            current_interval: Current interval in days
            review_count: Number of previous reviews

        Returns:
            Tuple of (new_ease_factor, new_interval, next_review_date)
        """
        # Map our quality to SM-2 quality
        q = SM2_QUALITY_MAP.get(quality, 0)

        # Calculate new ease factor
        new_ef = current_ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))

        # Clamp ease factor
        new_ef = max(self.MIN_EASE_FACTOR, min(self.MAX_EASE_FACTOR, new_ef))

        # Calculate new interval
        if quality == ResponseQuality.AGAIN:
            # Reset - need to relearn
            new_interval = 1
        elif review_count == 0:
            # First review
            new_interval = 1
        elif review_count == 1:
            # Second review
            new_interval = 6
        else:
            # Subsequent reviews
            new_interval = round(current_interval * new_ef)

        # Apply bonus/penalty based on quality
        if quality == ResponseQuality.EASY:
            new_interval = round(new_interval * 1.3)  # 30% bonus for easy
        elif quality == ResponseQuality.HARD:
            new_interval = max(1, round(new_interval * 0.6))  # 40% reduction for hard

        # Cap max interval at 365 days
        new_interval = min(new_interval, 365)

        # Calculate next review date
        next_date = date.today() + timedelta(days=new_interval)

        logger.info(
            "sr_calculation",
            quality=quality,
            old_ef=current_ease_factor,
            new_ef=new_ef,
            old_interval=current_interval,
            new_interval=new_interval,
            next_date=next_date.isoformat(),
        )

        return new_ef, new_interval, next_date

    def get_review_summary(
        self,
        words_reviewed: int,
        correct_count: int,
        again_count: int,
        hard_count: int,
        good_count: int,
        easy_count: int
    ) -> Dict[str, Any]:
        """
        Generate review session summary.

        Args:
            words_reviewed: Total words reviewed
            correct_count: Words answered correctly (good or easy)
            again_count: Words marked as 'again'
            hard_count: Words marked as 'hard'
            good_count: Words marked as 'good'
            easy_count: Words marked as 'easy'

        Returns:
            Summary dictionary with stats and encouragement
        """
        if words_reviewed == 0:
            return {
                "message": "No words reviewed yet!",
                "accuracy": 0,
                "stars_earned": 0,
            }

        accuracy = round((correct_count / words_reviewed) * 100)

        # Calculate stars based on performance
        stars = 0
        if accuracy >= 90:
            stars = 5
        elif accuracy >= 75:
            stars = 3
        elif accuracy >= 50:
            stars = 2
        elif correct_count > 0:
            stars = 1

        # Generate encouraging message
        if accuracy >= 90:
            message = "🌟 Výborně! Skvělá práce!"
        elif accuracy >= 75:
            message = "👍 Dobrá práce! Keep it up!"
        elif accuracy >= 50:
            message = "📚 Pokračuj v učení!"
        else:
            message = "💪 Nevzdávej se! Practice makes perfect!"

        return {
            "words_reviewed": words_reviewed,
            "correct_count": correct_count,
            "accuracy": accuracy,
            "breakdown": {
                "again": again_count,
                "hard": hard_count,
                "good": good_count,
                "easy": easy_count,
            },
            "stars_earned": stars,
            "message": message,
        }

    def estimate_review_time(self, word_count: int, avg_seconds_per_word: int = 8) -> int:
        """
        Estimate review session duration in minutes.

        Args:
            word_count: Number of words to review
            avg_seconds_per_word: Average seconds per word (default 8)

        Returns:
            Estimated minutes
        """
        total_seconds = word_count * avg_seconds_per_word
        return max(1, round(total_seconds / 60))
