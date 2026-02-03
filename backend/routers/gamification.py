"""
Gamification API endpoints.
Endpoints для челленджей, достижений и лидерборда.
"""

from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
import structlog

from backend.db.database import get_session
from backend.db.repositories import UserRepository, MaterializedViewRepository
from backend.services.achievement_service import AchievementService, AchievementCategory
from backend.services.challenge_service import ChallengeService

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/gamification", tags=["gamification"])


# ============ Pydantic Schemas ============

class ChallengeResponse(BaseModel):
    """Response schema for a challenge."""
    id: int
    code: str
    type: str
    title: str
    description: str
    goal_type: str
    goal_value: int
    reward_stars: int
    progress: int
    completed: bool
    reward_claimed: bool
    expires_at: str | None = None


class AllChallengesResponse(BaseModel):
    """Response schema for all challenges."""
    daily_challenge: dict[str, Any]
    weekly_challenges: list[dict[str, Any]]
    stats: dict[str, Any]
    current_date: str


class ClaimRewardRequest(BaseModel):
    """Request to claim a challenge reward."""
    challenge_id: int
    challenge_date: str = Field(description="Date in YYYY-MM-DD format")


class ClaimRewardResponse(BaseModel):
    """Response for claiming a reward."""
    success: bool
    stars_earned: int | None = None
    total_stars: int | None = None
    challenge_title: str | None = None
    error: str | None = None


class AchievementResponse(BaseModel):
    """Response schema for an achievement."""
    id: int
    code: str
    name: str
    description: str
    icon: str
    category: str
    threshold: int
    stars_reward: int
    is_unlocked: bool
    unlocked_at: str | None = None
    progress: int


class AchievementProgressResponse(BaseModel):
    """Response schema for achievement progress summary."""
    total_achievements: int
    unlocked_achievements: int
    completion_percent: int
    category_progress: dict[str, int]
    topic_progress: dict[str, int]


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
    """Response schema for leaderboard."""
    metric: str
    period: str
    leaderboard: list[LeaderboardEntry]
    user_rank: int | None = None
    user_score: int | float | None = None


# ============ Dependencies ============

async def get_achievement_service() -> AchievementService:
    """Get AchievementService instance."""
    return AchievementService()


async def get_challenge_service() -> ChallengeService:
    """Get ChallengeService instance."""
    return ChallengeService()


# ============ Challenge Endpoints ============

@router.get("/challenges", response_model=AllChallengesResponse)
async def get_all_challenges(
    telegram_id: int = Query(..., description="Telegram user ID"),
    db: AsyncSession = Depends(get_session),
    challenge_service: ChallengeService = Depends(get_challenge_service),
):
    """
    Získat všechny výzvy uživatele (denní a týdenní).

    Get all challenges for a user (daily and weekly) with progress.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    timezone_str = user.settings.timezone if user.settings else "Europe/Prague"

    result = await challenge_service.get_all_challenges(
        session=db,
        user_id=user.id,
        timezone_str=timezone_str,
    )

    return AllChallengesResponse(**result)


@router.get("/challenges/daily")
async def get_daily_challenge(
    telegram_id: int = Query(..., description="Telegram user ID"),
    db: AsyncSession = Depends(get_session),
    challenge_service: ChallengeService = Depends(get_challenge_service),
):
    """
    Získat denní výzvu pro uživatele.

    Get the daily challenge for a user.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    timezone_str = user.settings.timezone if user.settings else "Europe/Prague"

    try:
        tz = ZoneInfo(timezone_str)
    except Exception:
        tz = ZoneInfo("Europe/Prague")

    user_date = datetime.now(tz).date()

    result = await challenge_service.get_daily_challenge(
        session=db,
        user_id=user.id,
        user_date=user_date,
    )

    return result


@router.get("/challenges/weekly")
async def get_weekly_challenges(
    telegram_id: int = Query(..., description="Telegram user ID"),
    db: AsyncSession = Depends(get_session),
    challenge_service: ChallengeService = Depends(get_challenge_service),
):
    """
    Získat týdenní výzvy pro uživatele.

    Get all weekly challenges for a user with progress.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    timezone_str = user.settings.timezone if user.settings else "Europe/Prague"

    try:
        tz = ZoneInfo(timezone_str)
    except Exception:
        tz = ZoneInfo("Europe/Prague")

    user_date = datetime.now(tz).date()

    result = await challenge_service.get_weekly_challenges(
        session=db,
        user_id=user.id,
        user_date=user_date,
    )

    return {"weekly_challenges": result}


@router.post("/challenges/claim", response_model=ClaimRewardResponse)
async def claim_challenge_reward(
    request: ClaimRewardRequest,
    telegram_id: int = Query(..., description="Telegram user ID"),
    db: AsyncSession = Depends(get_session),
    challenge_service: ChallengeService = Depends(get_challenge_service),
):
    """
    Získat odměnu za dokončenou výzvu.

    Claim the reward for a completed challenge.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Parse date
    try:
        challenge_date = date.fromisoformat(request.challenge_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    result = await challenge_service.claim_challenge_reward(
        session=db,
        user_id=user.id,
        challenge_id=request.challenge_id,
        challenge_date=challenge_date,
    )

    if "error" in result:
        return ClaimRewardResponse(success=False, error=result["error"])

    await db.commit()

    return ClaimRewardResponse(
        success=True,
        stars_earned=result.get("stars_earned"),
        total_stars=result.get("total_stars"),
        challenge_title=result.get("challenge_title"),
    )


# ============ Achievement Endpoints ============

@router.get("/achievements", response_model=list[AchievementResponse])
async def get_user_achievements(
    telegram_id: int = Query(..., description="Telegram user ID"),
    db: AsyncSession = Depends(get_session),
    achievement_service: AchievementService = Depends(get_achievement_service),
):
    """
    Získat všechny úspěchy uživatele.

    Get all achievements for a user with unlock status and progress.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    achievements = await achievement_service.get_user_achievements(
        session=db,
        user_id=user.id,
    )

    return achievements


@router.get("/achievements/progress", response_model=AchievementProgressResponse)
async def get_achievement_progress(
    telegram_id: int = Query(..., description="Telegram user ID"),
    db: AsyncSession = Depends(get_session),
    achievement_service: AchievementService = Depends(get_achievement_service),
):
    """
    Získat souhrn pokroku v úspěších.

    Get achievement progress summary by category.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    progress = await achievement_service.get_achievement_progress(
        session=db,
        user=user,
    )

    return AchievementProgressResponse(**progress)


@router.get("/achievements/category/{category}")
async def get_achievements_by_category(
    category: str,
    telegram_id: int = Query(..., description="Telegram user ID"),
    db: AsyncSession = Depends(get_session),
    achievement_service: AchievementService = Depends(get_achievement_service),
):
    """
    Získat úspěchy v konkrétní kategorii.

    Get achievements for a specific category.
    """
    # Validate category
    valid_categories = [c.value for c in AchievementCategory]
    if category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Valid categories: {', '.join(valid_categories)}"
        )

    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    all_achievements = await achievement_service.get_user_achievements(
        session=db,
        user_id=user.id,
    )

    # Filter by category
    category_achievements = [a for a in all_achievements if a["category"] == category]

    return {"category": category, "achievements": category_achievements}


# ============ Leaderboard Endpoints ============

@router.get("/leaderboard/weekly", response_model=LeaderboardResponse)
async def get_weekly_leaderboard(
    metric: str = Query("stars", description="Metric: stars, streak, messages"),
    limit: int = Query(10, ge=1, le=100, description="Number of entries"),
    telegram_id: int | None = Query(None, description="Current user's Telegram ID for rank"),
    db: AsyncSession = Depends(get_session),
):
    """
    Získat týdenní žebříček.

    Get the weekly leaderboard. Users can opt out via privacy settings.
    """
    valid_metrics = ["stars", "streak", "messages", "accuracy"]
    if metric not in valid_metrics:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric. Valid metrics: {', '.join(valid_metrics)}"
        )

    # Map metric names to DB column names
    metric_map = {
        "stars": "total_stars",
        "streak": "max_streak",
        "messages": "total_messages",
        "accuracy": "avg_correctness",
    }

    mv_repo = MaterializedViewRepository(db)

    try:
        leaderboard_data = await mv_repo.get_leaderboard(
            metric=metric_map[metric],
            limit=limit,
        )
    except Exception as e:
        logger.warning("leaderboard_query_failed", error=str(e))
        # Fallback to empty leaderboard if materialized view doesn't exist
        leaderboard_data = []

    # Add ranks
    leaderboard = []
    for i, entry in enumerate(leaderboard_data, 1):
        # Check privacy setting - hide names for users who opted out
        # (This is handled in the query itself, but we double-check here)
        leaderboard.append(LeaderboardEntry(
            rank=i,
            telegram_id=entry.get("telegram_id", 0),
            first_name=entry.get("first_name", "User"),
            username=entry.get("username"),
            level=entry.get("level", "beginner"),
            score=entry.get("score", 0),
            total_messages=entry.get("total_messages", 0),
            total_stars=entry.get("total_stars", 0),
            max_streak=entry.get("max_streak", 0),
            avg_correctness=entry.get("avg_correctness"),
        ))

    # Get current user's rank if telegram_id provided
    user_rank = None
    user_score = None
    if telegram_id:
        for entry in leaderboard:
            if entry.telegram_id == telegram_id:
                user_rank = entry.rank
                user_score = entry.score
                break

        # If not in top N, try to find their rank
        if user_rank is None:
            try:
                user_data = await mv_repo.get_user_stats_summary(telegram_id=telegram_id)
                if user_data:
                    user_score = user_data[0].get(metric_map[metric], 0)
            except Exception:
                pass

    return LeaderboardResponse(
        metric=metric,
        period="weekly",
        leaderboard=leaderboard,
        user_rank=user_rank,
        user_score=user_score,
    )


@router.get("/leaderboard/friends")
async def get_friends_leaderboard(
    telegram_id: int = Query(..., description="Telegram user ID"),
    metric: str = Query("stars", description="Metric: stars, streak, messages"),
    db: AsyncSession = Depends(get_session),
):
    """
    Získat žebříček mezi přáteli (referraly).

    Get leaderboard among friends (referrals).
    Note: This is a placeholder - referral system not yet implemented.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Placeholder response - referral system to be implemented
    return {
        "metric": metric,
        "friends_count": 0,
        "leaderboard": [],
        "message": "Referral system coming soon!",
    }


@router.get("/leaderboard/my-rank")
async def get_my_rank(
    telegram_id: int = Query(..., description="Telegram user ID"),
    metric: str = Query("stars", description="Metric: stars, streak, messages"),
    db: AsyncSession = Depends(get_session),
):
    """
    Získat vlastní pozici v žebříčku.

    Get the current user's rank in the leaderboard.
    """
    valid_metrics = ["stars", "streak", "messages", "accuracy"]
    if metric not in valid_metrics:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric. Valid metrics: {', '.join(valid_metrics)}"
        )

    metric_map = {
        "stars": "total_stars",
        "streak": "max_streak",
        "messages": "total_messages",
        "accuracy": "avg_correctness",
    }

    mv_repo = MaterializedViewRepository(db)

    try:
        # Get all users sorted by metric
        all_data = await mv_repo.get_leaderboard(
            metric=metric_map[metric],
            limit=1000,  # Get enough to find user
        )

        # Find user's rank
        rank = None
        score = None
        for i, entry in enumerate(all_data, 1):
            if entry.get("telegram_id") == telegram_id:
                rank = i
                score = entry.get("score", 0)
                break

        return {
            "metric": metric,
            "rank": rank,
            "score": score,
            "total_users": len(all_data),
        }

    except Exception as e:
        logger.warning("my_rank_query_failed", error=str(e))
        return {
            "metric": metric,
            "rank": None,
            "score": None,
            "total_users": 0,
            "error": "Leaderboard temporarily unavailable",
        }
