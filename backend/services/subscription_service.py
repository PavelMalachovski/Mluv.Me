"""
Subscription & quota management service.

Plans:
  - free:  10 text + 5 voice messages per day
  - pro:   unlimited (159 CZK/month ≈ 350 Telegram Stars / 30 days)

Products (Telegram Stars):
  - pro_7d:  100 Stars → 7 days Pro
  - pro_30d: 350 Stars → 30 days Pro
"""

from datetime import datetime, timedelta, timezone
from typing import Literal

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from backend.cache.redis_client import redis_client
from backend.models.subscription import Subscription, Payment

logger = structlog.get_logger(__name__)

# ──────────────────── Plan limits ────────────────────
PLAN_LIMITS: dict[str, dict[str, int]] = {
    "free": {
        "text_per_day": 10,
        "voice_per_day": 5,
    },
    "pro": {
        "text_per_day": 999_999,  # effectively unlimited
        "voice_per_day": 999_999,
    },
}

# ──────────────────── Products ──────
STAR_PRODUCTS = {
    "pro_7d": {
        "label": "Pro na 7 dní",
        "description": "7 dní neomezeného přístupu ke všem funkcím Mluv.Me",
        "stars": 100,
        "czk": 49,
        "days": 7,
        "plan": "pro",
    },
    "pro_30d": {
        "label": "Pro na 30 dní",
        "description": "30 dní neomezeného přístupu ke všem funkcím Mluv.Me",
        "stars": 350,
        "czk": 159,
        "days": 30,
        "plan": "pro",
    },
}

# Redis key patterns
_QUOTA_TEXT_KEY = "quota:text:{user_id}:{date}"
_QUOTA_VOICE_KEY = "quota:voice:{user_id}:{date}"
_QUOTA_TTL = 60 * 60 * 26  # 26 hours (covers timezone edge)


class SubscriptionService:
    """Service to check plans, enforce quotas, process payments."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ─────────── Active subscription ───────────

    async def get_active_subscription(self, user_id: int) -> Subscription | None:
        """Return the currently active Pro subscription, or None (= free)."""
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(Subscription)
            .where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.plan == "pro",
                    Subscription.status == "active",
                    Subscription.expires_at > now,
                )
            )
            .order_by(Subscription.expires_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_user_plan(self, user_id: int) -> Literal["free", "pro"]:
        """Return 'pro' if user has active subscription, else 'free'."""
        sub = await self.get_active_subscription(user_id)
        return "pro" if sub else "free"

    # ─────────── Quota checking ───────────

    async def get_usage_today(
        self, user_id: int, msg_type: Literal["text", "voice"]
    ) -> int:
        """Get how many messages of given type the user sent today."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        key_tpl = _QUOTA_TEXT_KEY if msg_type == "text" else _QUOTA_VOICE_KEY
        key = key_tpl.format(user_id=user_id, date=today)
        val = await redis_client.get(key)
        return int(val) if val else 0

    async def increment_usage(
        self, user_id: int, msg_type: Literal["text", "voice"]
    ) -> int:
        """Increment daily counter and return new value."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        key_tpl = _QUOTA_TEXT_KEY if msg_type == "text" else _QUOTA_VOICE_KEY
        key = key_tpl.format(user_id=user_id, date=today)

        # Use raw redis for INCR
        r = redis_client.redis
        if r is None:
            # Redis disabled — allow everything
            return 0
        new_val = await r.incr(key)
        if new_val == 1:
            await r.expire(key, _QUOTA_TTL)
        return int(new_val)

    async def check_quota(
        self, user_id: int, msg_type: Literal["text", "voice"]
    ) -> dict:
        """
        Check if user can send a message of given type.

        Returns dict:
          allowed: bool
          plan: str
          used: int
          limit: int
          remaining: int
        """
        plan = await self.get_user_plan(user_id)
        limits = PLAN_LIMITS[plan]
        limit_key = f"{msg_type}_per_day"
        limit_val = limits[limit_key]
        used = await self.get_usage_today(user_id, msg_type)

        remaining = max(0, limit_val - used)
        allowed = remaining > 0

        return {
            "allowed": allowed,
            "plan": plan,
            "used": used,
            "limit": limit_val,
            "remaining": remaining,
        }

    # ─────────── Subscription creation ───────────

    async def activate_pro(
        self,
        user_id: int,
        days: int,
        source: str = "telegram_stars",
    ) -> Subscription:
        """Create (or extend) a Pro subscription."""
        now = datetime.now(timezone.utc)

        # Check if there's an existing active sub to extend
        existing = await self.get_active_subscription(user_id)
        if existing and existing.expires_at > now:
            # Extend from the current expiry
            new_expires = existing.expires_at + timedelta(days=days)
            existing.expires_at = new_expires
            await self.db.flush()
            logger.info(
                "subscription_extended",
                user_id=user_id,
                new_expires=new_expires.isoformat(),
            )
            return existing

        # Create new subscription
        sub = Subscription(
            user_id=user_id,
            plan="pro",
            status="active",
            source=source,
            starts_at=now,
            expires_at=now + timedelta(days=days),
        )
        self.db.add(sub)
        await self.db.flush()
        logger.info(
            "subscription_created",
            user_id=user_id,
            plan="pro",
            days=days,
            source=source,
        )
        return sub

    # ─────────── Payment recording ───────────

    async def record_payment(
        self,
        user_id: int,
        provider: str,
        amount: int,
        currency: str,
        description: str,
        product: str,
        telegram_payment_charge_id: str | None = None,
        stripe_payment_intent_id: str | None = None,
    ) -> Payment:
        """Record a payment in the database."""
        payment = Payment(
            user_id=user_id,
            provider=provider,
            amount=amount,
            currency=currency,
            description=description,
            product=product,
            telegram_payment_charge_id=telegram_payment_charge_id,
            stripe_payment_intent_id=stripe_payment_intent_id,
        )
        self.db.add(payment)
        await self.db.flush()
        logger.info(
            "payment_recorded",
            user_id=user_id,
            provider=provider,
            amount=amount,
            currency=currency,
            product=product,
        )
        return payment

    # ─────────── Process Stars purchase ───────────

    async def process_stars_purchase(
        self,
        user_id: int,
        product_id: str,
        telegram_payment_charge_id: str,
        provider: str = "telegram_stars",
    ) -> Subscription:
        """
        Full flow after successful Telegram payment (Stars or Tribute):
        1. Record payment
        2. Activate/extend Pro subscription
        """
        product = STAR_PRODUCTS.get(product_id)
        if not product:
            raise ValueError(f"Unknown product: {product_id}")

        # Determine amount and currency based on provider
        if provider == "tribute":
            amount = product["czk"] * 100  # haéře
            currency = "CZK"
        else:
            amount = product["stars"]
            currency = "XTR"

        # Record payment
        await self.record_payment(
            user_id=user_id,
            provider=provider,
            amount=amount,
            currency=currency,
            description=product["description"],
            product=product_id,
            telegram_payment_charge_id=telegram_payment_charge_id,
        )

        # Activate Pro
        sub = await self.activate_pro(
            user_id=user_id,
            days=product["days"],
            source=provider,
        )

        await self.db.commit()
        return sub

    # ─────────── Subscription info for API ───────────

    async def get_subscription_info(self, user_id: int) -> dict:
        """Return subscription info for the API/frontend."""
        plan = await self.get_user_plan(user_id)
        sub = await self.get_active_subscription(user_id) if plan == "pro" else None

        text_quota = await self.check_quota(user_id, "text")
        voice_quota = await self.check_quota(user_id, "voice")

        return {
            "plan": plan,
            "expires_at": sub.expires_at.isoformat() if sub else None,
            "text_quota": text_quota,
            "voice_quota": voice_quota,
            "products": STAR_PRODUCTS,
        }
