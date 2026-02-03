"""
Сервисы бизнес-логики Mluv.Me.

Все сервисы следуют принципу единственной ответственности
и могут быть использованы через Dependency Injection.
"""

from .openai_client import OpenAIClient
from .honzik_personality import HonzikPersonality
from .correction_engine import CorrectionEngine
from .gamification import GamificationService
from .achievement_service import AchievementService
from .challenge_service import ChallengeService

__all__ = [
    "OpenAIClient",
    "HonzikPersonality",
    "CorrectionEngine",
    "GamificationService",
    "AchievementService",
    "ChallengeService",
]


