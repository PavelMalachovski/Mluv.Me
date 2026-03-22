"""
Star Shop API — endpoints for spending earned stars.

Items:
  - Streak Shield (100 ⭐) — protect streak for 1 missed day
  - Scenario Unlock (200-300 ⭐) — unlock premium scenarios
  - Trial Premium (500 ⭐) — 1 day Pro access
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_session
from backend.db.repositories import UserRepository
from backend.services.star_shop import StarShopService

router = APIRouter(prefix="/api/v1/star-shop", tags=["star-shop"])


# ── Dependencies ────────────────────────────────────


async def get_verified_user(
    telegram_id: int = Query(..., description="Telegram user ID"),
    db: AsyncSession = Depends(get_session),
):
    """Resolve telegram_id → User, raise 404 if not found."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_star_shop(db: AsyncSession = Depends(get_session)) -> StarShopService:
    return StarShopService(db)


# ── Schemas ─────────────────────────────────────────


class PurchaseResponse(BaseModel):
    success: bool
    cost: int | None = None
    remaining_stars: int | None = None
    total_stars: int | None = None
    error: str | None = None
    message: str | None = None


class ScenarioUnlockRequest(BaseModel):
    scenario_id: str


# ── Endpoints ───────────────────────────────────────


@router.get("/catalog")
async def get_shop_catalog(
    telegram_id: int = Query(...),
    db: AsyncSession = Depends(get_session),
):
    """Get the full star shop catalog with user-specific state."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shop = StarShopService(db)
    return await shop.get_shop_items(user.id)


@router.post("/streak-shield", response_model=PurchaseResponse)
async def buy_streak_shield(
    telegram_id: int = Query(...),
    db: AsyncSession = Depends(get_session),
):
    """Buy a streak shield (100 ⭐). Protects streak for 1 missed day."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shop = StarShopService(db)
    return await shop.buy_streak_shield(user.id)


@router.post("/unlock-scenario", response_model=PurchaseResponse)
async def unlock_scenario(
    request: ScenarioUnlockRequest,
    telegram_id: int = Query(...),
    db: AsyncSession = Depends(get_session),
):
    """Unlock a premium scenario with stars (200-300 ⭐)."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shop = StarShopService(db)
    result = await shop.unlock_scenario(user.id, request.scenario_id)
    if not result["success"] and result.get("error") == "unknown_scenario":
        raise HTTPException(status_code=404, detail="Scenario not found")
    return result


@router.get("/scenario-status/{scenario_id}")
async def get_scenario_status(
    scenario_id: str,
    telegram_id: int = Query(...),
    db: AsyncSession = Depends(get_session),
):
    """Check if a scenario is unlocked for the user."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shop = StarShopService(db)
    return await shop.get_scenario_unlock_status(user.id, scenario_id)


@router.post("/trial-premium", response_model=PurchaseResponse)
async def buy_trial_premium(
    telegram_id: int = Query(...),
    db: AsyncSession = Depends(get_session),
):
    """Buy 1 day of Pro access with stars (500 ⭐)."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shop = StarShopService(db)
    return await shop.buy_trial_premium(user.id)
