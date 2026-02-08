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
from .scenario_service import ScenarioService
from .pronunciation_analyzer import PronunciationAnalyzer
from .game_service import GameService
from .seasonal_service import SeasonalService
from .exam_prep_service import ExamPrepService
from .story_generator import StoryGenerator
from .podcast_service import PodcastService

__all__ = [
    "OpenAIClient",
    "HonzikPersonality",
    "CorrectionEngine",
    "GamificationService",
    "AchievementService",
    "ChallengeService",
    "ScenarioService",
    "PronunciationAnalyzer",
    "GameService",
    "SeasonalService",
    "ExamPrepService",
    "StoryGenerator",
    "PodcastService",
]

