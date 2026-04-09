"""
Subscription & payments API router.

Endpoints:
  GET  /api/v1/subscription          — current plan + quotas
  POST /api/v1/subscription/checkout  — initiate Stripe checkout (TODO)
  POST /api/v1/subscription/webhook   — Stripe webhook (TODO)
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from backend.db.database import get_session
from backend.db.repositories import UserRepository
from backend.routers.web_auth import get_authenticated_user
from backend.services.subscription_service import (
    SubscriptionService,
)

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/v1/subscription", tags=["subscription"])


class SubscriptionInfoResponse(BaseModel):
    plan: str
    expires_at: str | None
    text_quota: dict
    voice_quota: dict
    products: dict


class CheckoutRequest(BaseModel):
    """Stripe checkout request (placeholder)."""

    plan: str = "pro"
    period: str = "monthly"  # monthly | yearly


class CheckoutResponse(BaseModel):
    """Stripe checkout response (placeholder)."""

    url: str
    session_id: str


# ──────────────────── GET /subscription ────────────────────


@router.get("", response_model=SubscriptionInfoResponse)
async def get_subscription_info(
    auth_user=Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_session),
):
    """Get current subscription plan, quotas, and available products."""
    svc = SubscriptionService(db)
    info = await svc.get_subscription_info(auth_user.id)
    return info


# ──────────────────── POST /subscription/checkout (STUB) ────


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    request: CheckoutRequest,
    auth_user=Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Create a Stripe Checkout Session for web subscription.

    TODO: Implement when Stripe account is ready.
    Requires STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET env vars.
    """
    raise HTTPException(
        status_code=501,
        detail="Stripe checkout is not yet implemented. "
        "Use Telegram Stars to subscribe via the bot.",
    )


# ──────────────────── POST /subscription/webhook (STUB) ─────


@router.post("/webhook")
async def stripe_webhook():
    """
    Stripe webhook endpoint.

    TODO: Implement when Stripe account is ready.
    Will handle:
      - checkout.session.completed → activate subscription
      - invoice.payment_succeeded → renew subscription
      - customer.subscription.deleted → expire subscription
    """
    raise HTTPException(status_code=501, detail="Stripe webhooks not yet implemented")


# ──────────────────── POST /subscription/activate-stars ───────
# Called by the Telegram bot after successful Stars payment.


class ActivateStarsRequest(BaseModel):
    telegram_id: int
    product_id: str
    telegram_payment_charge_id: str
    provider: str = "telegram_stars"


@router.post("/activate-stars")
async def activate_stars(
    request: ActivateStarsRequest,
    db: AsyncSession = Depends(get_session),
):
    """
    Record a Telegram payment (Stars or Tribute) and activate/extend Pro subscription.
    Called by the bot's successful_payment handler.
    """
    # Resolve user by telegram_id
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(request.telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    svc = SubscriptionService(db)
    try:
        sub = await svc.process_stars_purchase(
            user_id=user.id,
            product_id=request.product_id,
            telegram_payment_charge_id=request.telegram_payment_charge_id,
            provider=request.provider,
            telegram_payment_charge_id=request.telegram_payment_charge_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "success": True,
        "plan": sub.plan,
        "expires_at": sub.expires_at.isoformat(),
    }


# ──────────────────── GET /subscription/quota/{telegram_id} ──
# Called by the bot to check if user can send a message.


@router.get("/quota/{telegram_id}")
async def check_quota_by_telegram_id(
    telegram_id: int,
    msg_type: str = "text",
    db: AsyncSession = Depends(get_session),
):
    """
    Check daily quota for a user (identified by telegram_id).
    Used by the Telegram bot before processing messages.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(telegram_id)
    if not user:
        # Unknown user → allow (they'll create account on first message)
        return {"allowed": True, "plan": "free", "used": 0, "limit": 5, "remaining": 5}

    svc = SubscriptionService(db)
    return await svc.check_quota(user.id, msg_type)
