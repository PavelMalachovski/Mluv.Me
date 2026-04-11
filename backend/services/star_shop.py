"""
Star Shop Service — spending earned stars on in-app items.

Three features:
1. Streak Shield  — protect streak for 1 missed day (100 ⭐)
2. Scenario Unlock — unlock premium scenarios with stars
3. Trial Premium   — buy 1 day of Pro access (500 ⭐)
"""

from datetime import datetime, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from backend.cache.redis_client import redis_client
from backend.db.repositories import StatsRepository
from backend.services.subscription_service import SubscriptionService

logger = structlog.get_logger(__name__)

# ── Prices ──────────────────────────────────────────
STREAK_SHIELD_COST = 100
TRIAL_PREMIUM_COST = 500
TRIAL_PREMIUM_DAYS = 1
DISCOUNT_COST = 500       # 500 earned stars → 50 CZK discount on subscription
DISCOUNT_CZK = 50
_DISCOUNT_KEY = "star_discount:{user_id}"
_DISCOUNT_TTL = 60 * 15   # 15 minutes to use the discount

# Scenarios that require star-unlock (intermediate+ scenarios)
# key = scenario_id, value = unlock cost in stars
SCENARIO_UNLOCK_PRICES: dict[str, int] = {
    "na_cizinecke_policii": 200,
    "pracovni_pohovor": 300,
    "telefonni_hovor": 250,
}

# Free scenarios (no unlock needed)
FREE_SCENARIOS = {
    "v_hospode",
    "u_lekare",
    "pronajem_bytu",
    "v_tramvaji",
    "v_obchode",
}

# Redis keys
_STREAK_SHIELD_KEY = "streak_shield:{user_id}"
_SCENARIO_UNLOCK_KEY = "scenario_unlocked:{user_id}:{scenario_id}"
_STREAK_SHIELD_TTL = 60 * 60 * 48  # 48 hours (covers 1 missed day + buffer)


class StarShopService:
    """Service for spending earned stars on in-app items."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.stats_repo = StatsRepository(db)

    # ── 1. Streak Shield ────────────────────────────

    async def buy_streak_shield(self, user_id: int) -> dict:
        """
        Buy a streak shield that protects the user's streak for 1 missed day.

        Cost: 100 stars.
        Duration: Until next streak check (resets daily at 00:05 UTC).

        Returns:
            dict with success status and details
        """
        # Check if already has active shield
        if await self.has_streak_shield(user_id):
            return {
                "success": False,
                "error": "already_active",
                "message": "Streak shield is already active",
            }

        # Try to spend stars
        result = await self.stats_repo.spend_user_stars(user_id, STREAK_SHIELD_COST)
        if result is None:
            stars = await self.stats_repo.get_user_stars(user_id)
            return {
                "success": False,
                "error": "insufficient_stars",
                "message": f"Need {STREAK_SHIELD_COST} stars, have {stars.available if stars else 0}",
                "cost": STREAK_SHIELD_COST,
                "available": stars.available if stars else 0,
            }

        # Activate shield in Redis
        await redis_client.set(
            _STREAK_SHIELD_KEY.format(user_id=user_id),
            {"activated_at": datetime.now(timezone.utc).isoformat()},
            ttl=_STREAK_SHIELD_TTL,
        )

        await self.db.commit()

        logger.info(
            "streak_shield_purchased",
            user_id=user_id,
            cost=STREAK_SHIELD_COST,
            remaining_stars=result["available"],
        )

        return {
            "success": True,
            "cost": STREAK_SHIELD_COST,
            "remaining_stars": result["available"],
            "total_stars": result["total"],
        }

    async def has_streak_shield(self, user_id: int) -> bool:
        """Check if user has an active streak shield."""
        shield = await redis_client.get(
            _STREAK_SHIELD_KEY.format(user_id=user_id)
        )
        return shield is not None

    async def consume_streak_shield(self, user_id: int) -> bool:
        """
        Consume the streak shield (called by streak reset task).
        Returns True if shield was consumed (streak saved).
        """
        key = _STREAK_SHIELD_KEY.format(user_id=user_id)
        shield = await redis_client.get(key)
        if shield:
            await redis_client.delete(key)
            logger.info("streak_shield_consumed", user_id=user_id)
            return True
        return False

    # ── 2. Scenario Unlock ──────────────────────────

    async def get_scenario_unlock_status(
        self, user_id: int, scenario_id: str
    ) -> dict:
        """Check if a scenario is unlocked for the user."""
        # Free scenarios are always unlocked
        if scenario_id in FREE_SCENARIOS:
            return {"unlocked": True, "free": True, "cost": 0}

        cost = SCENARIO_UNLOCK_PRICES.get(scenario_id)
        if cost is None:
            return {"unlocked": True, "free": True, "cost": 0}

        # Check if already unlocked
        is_unlocked = await self._is_scenario_unlocked(user_id, scenario_id)

        # Pro users get all scenarios for free
        sub_service = SubscriptionService(self.db)
        plan = await sub_service.get_user_plan(user_id)
        if plan == "pro":
            return {"unlocked": True, "free": False, "cost": 0, "reason": "pro"}

        return {
            "unlocked": is_unlocked,
            "free": False,
            "cost": cost,
        }

    async def unlock_scenario(self, user_id: int, scenario_id: str) -> dict:
        """
        Unlock a premium scenario with stars.

        Returns:
            dict with success status and details
        """
        # Already free?
        if scenario_id in FREE_SCENARIOS:
            return {"success": True, "already_free": True, "cost": 0}

        cost = SCENARIO_UNLOCK_PRICES.get(scenario_id)
        if cost is None:
            return {"success": False, "error": "unknown_scenario"}

        # Pro users don't need to unlock
        sub_service = SubscriptionService(self.db)
        plan = await sub_service.get_user_plan(user_id)
        if plan == "pro":
            return {"success": True, "reason": "pro", "cost": 0}

        # Already unlocked?
        if await self._is_scenario_unlocked(user_id, scenario_id):
            return {"success": True, "already_unlocked": True, "cost": 0}

        # Spend stars
        result = await self.stats_repo.spend_user_stars(user_id, cost)
        if result is None:
            stars = await self.stats_repo.get_user_stars(user_id)
            return {
                "success": False,
                "error": "insufficient_stars",
                "cost": cost,
                "available": stars.available if stars else 0,
            }

        # Mark as unlocked permanently
        await redis_client.set(
            _SCENARIO_UNLOCK_KEY.format(user_id=user_id, scenario_id=scenario_id),
            {"unlocked_at": datetime.now(timezone.utc).isoformat()},
            ttl=None,  # permanent
        )

        await self.db.commit()

        logger.info(
            "scenario_unlocked",
            user_id=user_id,
            scenario_id=scenario_id,
            cost=cost,
            remaining_stars=result["available"],
        )

        return {
            "success": True,
            "scenario_id": scenario_id,
            "cost": cost,
            "remaining_stars": result["available"],
            "total_stars": result["total"],
        }

    async def _is_scenario_unlocked(
        self, user_id: int, scenario_id: str
    ) -> bool:
        """Check Redis for permanent scenario unlock."""
        key = _SCENARIO_UNLOCK_KEY.format(
            user_id=user_id, scenario_id=scenario_id
        )
        return await redis_client.get(key) is not None

    # ── 3. Trial Premium ────────────────────────────

    async def buy_trial_premium(self, user_id: int) -> dict:
        """
        Buy 1 day of Pro access with stars.

        Cost: 500 stars.
        Duration: 1 day.

        Returns:
            dict with success status
        """
        # Check if already Pro
        sub_service = SubscriptionService(self.db)
        plan = await sub_service.get_user_plan(user_id)
        if plan == "pro":
            return {
                "success": False,
                "error": "already_pro",
                "message": "You already have Pro access",
            }

        # Spend stars
        result = await self.stats_repo.spend_user_stars(
            user_id, TRIAL_PREMIUM_COST
        )
        if result is None:
            stars = await self.stats_repo.get_user_stars(user_id)
            return {
                "success": False,
                "error": "insufficient_stars",
                "cost": TRIAL_PREMIUM_COST,
                "available": stars.available if stars else 0,
            }

        # Activate Pro subscription for 1 day
        sub = await sub_service.activate_pro(
            user_id=user_id,
            days=TRIAL_PREMIUM_DAYS,
            source="star_shop",
        )

        await self.db.commit()

        logger.info(
            "trial_premium_purchased",
            user_id=user_id,
            cost=TRIAL_PREMIUM_COST,
            expires_at=sub.expires_at.isoformat(),
            remaining_stars=result["available"],
        )

        return {
            "success": True,
            "cost": TRIAL_PREMIUM_COST,
            "days": TRIAL_PREMIUM_DAYS,
            "expires_at": sub.expires_at.isoformat(),
            "remaining_stars": result["available"],
            "total_stars": result["total"],
        }

    # ── Shop catalog ────────────────────────────────

    async def redeem_discount(self, user_id: int) -> dict:
        """
        Spend 500 earned stars to get a 50 CZK discount on the next subscription.

        Sets a Redis flag valid for 15 minutes.
        Returns dict with success status.
        """
        # Check if already has an active discount
        if await self.has_discount(user_id):
            return {
                "success": False,
                "error": "already_active",
                "message": "Discount already active — use it within 15 minutes",
            }

        # Spend stars
        result = await self.stats_repo.spend_user_stars(user_id, DISCOUNT_COST)
        if result is None:
            stars = await self.stats_repo.get_user_stars(user_id)
            return {
                "success": False,
                "error": "insufficient_stars",
                "cost": DISCOUNT_COST,
                "available": stars.available if stars else 0,
            }

        await redis_client.set(
            _DISCOUNT_KEY.format(user_id=user_id),
            {"activated_at": datetime.now(timezone.utc).isoformat(), "czk": DISCOUNT_CZK},
            ttl=_DISCOUNT_TTL,
        )

        await self.db.commit()

        logger.info(
            "star_discount_redeemed",
            user_id=user_id,
            cost=DISCOUNT_COST,
            discount_czk=DISCOUNT_CZK,
            remaining_stars=result["available"],
        )

        return {
            "success": True,
            "cost": DISCOUNT_COST,
            "discount_czk": DISCOUNT_CZK,
            "remaining_stars": result["available"],
            "total_stars": result["total"],
        }

    async def has_discount(self, user_id: int) -> bool:
        """Check if user has an active star discount."""
        return await redis_client.get(_DISCOUNT_KEY.format(user_id=user_id)) is not None

    async def consume_discount(self, user_id: int) -> int | None:
        """Consume discount and return CZK amount. None if no discount."""
        key = _DISCOUNT_KEY.format(user_id=user_id)
        data = await redis_client.get(key)
        if data:
            await redis_client.delete(key)
            return data.get("czk", DISCOUNT_CZK)
        return None

    async def get_shop_items(self, user_id: int) -> dict:
        """Return the full star shop catalog with user-specific state."""
        stars = await self.stats_repo.get_user_stars(user_id)
        available = stars.available if stars else 0

        has_shield = await self.has_streak_shield(user_id)

        sub_service = SubscriptionService(self.db)
        plan = await sub_service.get_user_plan(user_id)

        # Build scenario unlock list
        scenarios = []
        for sid, cost in SCENARIO_UNLOCK_PRICES.items():
            unlocked = await self._is_scenario_unlocked(user_id, sid)
            scenarios.append({
                "scenario_id": sid,
                "cost": cost,
                "unlocked": unlocked or plan == "pro",
                "can_afford": available >= cost,
            })

        return {
            "available_stars": available,
            "items": {
                "streak_shield": {
                    "cost": STREAK_SHIELD_COST,
                    "active": has_shield,
                    "can_afford": available >= STREAK_SHIELD_COST,
                    "description": "Protect your streak for 1 missed day",
                },
                "trial_premium": {
                    "cost": TRIAL_PREMIUM_COST,
                    "days": TRIAL_PREMIUM_DAYS,
                    "already_pro": plan == "pro",
                    "can_afford": available >= TRIAL_PREMIUM_COST,
                    "description": f"{TRIAL_PREMIUM_DAYS}-day Pro access",
                },
                "discount": {
                    "cost": DISCOUNT_COST,
                    "discount_czk": DISCOUNT_CZK,
                    "active": await self.has_discount(user_id),
                    "can_afford": available >= DISCOUNT_COST,
                    "description": f"Spend {DISCOUNT_COST} ⭐ for {DISCOUNT_CZK} Kč off subscription",
                },
                "scenario_unlocks": scenarios,
            },
        }
