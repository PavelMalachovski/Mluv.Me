"""
Pydantic schemas for gamification API endpoints.
"""

from typing import Any
from pydantic import BaseModel, Field


# ============ Challenge Schemas ============

class ChallengeBase(BaseModel):
    """Base challenge schema."""
    id: int
    code: str
    type: str
    title: str = Field(..., alias="title_cs")
    description: str = Field(..., alias="description_cs")
    goal_type: str
    goal_topic: str | None = None
    goal_value: int
    reward_stars: int

    class Config:
        from_attributes = True
        populate_by_name = True


class ChallengeResponse(ChallengeBase):
    """Challenge response with progress."""
    progress: int
    completed: bool
    reward_claimed: bool
    expires_at: str | None = None
    week_start: str | None = None


class AllChallengesResponse(BaseModel):
    """Response for all challenges endpoint."""
    daily_challenge: dict[str, Any]
    weekly_challenges: list[dict[str, Any]]
    stats: dict[str, Any]
    current_date: str


class ClaimRewardRequest(BaseModel):
    """Request to claim a challenge reward."""
    challenge_id: int
    challenge_date: str = Field(..., description="Date in YYYY-MM-DD format")


class ClaimRewardResponse(BaseModel):
    """Response for claiming a reward."""
    success: bool
    stars_earned: int | None = None
    total_stars: int | None = None
    challenge_title: str | None = None
    error: str | None = None


# ============ Achievement Schemas ============

class AchievementBase(BaseModel):
    """Base achievement schema."""
    id: int
    code: str
    name: str
    description: str
    icon: str
    category: str
    threshold: int
    stars_reward: int

    class Config:
        from_attributes = True


class AchievementResponse(AchievementBase):
    """Achievement response with unlock status."""
    is_unlocked: bool
    unlocked_at: str | None = None
    progress: int


class AchievementProgressResponse(BaseModel):
    """Achievement progress summary."""
    total_achievements: int
    unlocked_achievements: int
    completion_percent: int
    category_progress: dict[str, int]
    topic_progress: dict[str, int]


class NewlyUnlockedAchievement(BaseModel):
    """Newly unlocked achievement notification."""
    id: int
    code: str
    name: str
    description: str
    icon: str
    category: str
    stars_reward: int


# ============ Leaderboard Schemas ============

class LeaderboardEntry(BaseModel):
    """A single leaderboard entry."""
    rank: int
    telegram_id: int
    first_name: str
    username: str | None = None
    level: str
    score: int | float
    total_messages: int
    total_stars: int
    max_streak: int
    avg_correctness: float | None = None


class LeaderboardResponse(BaseModel):
    """Leaderboard response."""
    metric: str
    period: str
    leaderboard: list[LeaderboardEntry]
    user_rank: int | None = None
    user_score: int | float | None = None


class MyRankResponse(BaseModel):
    """User's rank response."""
    metric: str
    rank: int | None
    score: int | float | None
    total_users: int
    error: str | None = None
