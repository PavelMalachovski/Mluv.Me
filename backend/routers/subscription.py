"""
Subscription & payments API router.

Endpoints:
  GET  /api/v1/subscription          — current plan + quotas
  POST /api/v1/subscription/checkout  — create Stripe Checkout session
  POST /api/v1/subscription/webhook   — Stripe webhook
  POST /api/v1/subscription/activate-stars — activate after Telegram Stars payment
  GET  /api/v1/subscription/quota/{telegram_id} — quota check for bot
"""

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from backend.config import Settings, get_settings
from backend.db.database import get_session
from backend.db.repositories import UserRepository
from backend.routers.web_auth import get_authenticated_user
from backend.services.subscription_service import (
    SubscriptionService,
    STAR_PRODUCTS,
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
    """Stripe checkout request."""
    product_id: str  # "pro_7d" or "pro_30d"
    telegram_id: int


class CheckoutResponse(BaseModel):
    """Stripe checkout response."""
    url: str
    session_id: str


def _stripe_available(settings: Settings) -> bool:
    return bool(settings.stripe_secret_key)


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


# ──────────────────── POST /subscription/checkout ────────────


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    request: CheckoutRequest,
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_session),
):
    """
    Create a Stripe Checkout Session.
    Called by the bot when user taps 'Pay with card'.
    Returns a URL the user opens in their browser.
    """
    if not _stripe_available(settings):
        raise HTTPException(status_code=503, detail="Stripe is not configured")

    product = STAR_PRODUCTS.get(request.product_id)
    if not product:
        raise HTTPException(status_code=400, detail=f"Unknown product: {request.product_id}")

    stripe.api_key = settings.stripe_secret_key

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "czk",
                        "product_data": {
                            "name": product["label"],
                            "description": product["description"],
                        },
                        "unit_amount": product["czk"] * 100,  # haléře
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            metadata={
                "telegram_id": str(request.telegram_id),
                "product_id": request.product_id,
            },
            success_url="https://t.me/MluvMeBot?start=payment_success",
            cancel_url="https://t.me/MluvMeBot?start=payment_cancel",
        )
    except stripe.StripeError as e:
        logger.error("stripe_checkout_error", error=str(e))
        raise HTTPException(status_code=502, detail="Stripe error")

    logger.info(
        "stripe_checkout_created",
        telegram_id=request.telegram_id,
        product=request.product_id,
        session_id=session.id,
    )

    return CheckoutResponse(url=session.url, session_id=session.id)


# ──────────────────── POST /subscription/webhook ─────────────


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_session),
):
    """
    Stripe webhook endpoint.
    Handles checkout.session.completed to activate subscriptions.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook secret not configured")

    stripe.api_key = settings.stripe_secret_key

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        logger.warning("stripe_webhook_invalid_payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.SignatureVerificationError:
        logger.warning("stripe_webhook_invalid_signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        telegram_id = int(metadata.get("telegram_id", 0))
        product_id = metadata.get("product_id", "")
        stripe_session_id = session.get("id", "")

        if not telegram_id or not product_id:
            logger.error("stripe_webhook_missing_metadata", metadata=metadata)
            return {"status": "error", "detail": "missing metadata"}

        user_repo = UserRepository(db)
        user = await user_repo.get_by_telegram_id(telegram_id)
        if not user:
            logger.error("stripe_webhook_user_not_found", telegram_id=telegram_id)
            return {"status": "error", "detail": "user not found"}

        svc = SubscriptionService(db)
        try:
            sub = await svc.process_stars_purchase(
                user_id=user.id,
                product_id=product_id,
                telegram_payment_charge_id=stripe_session_id,
                provider="stripe",
            )
            logger.info(
                "stripe_payment_activated",
                telegram_id=telegram_id,
                product=product_id,
                expires_at=sub.expires_at.isoformat(),
            )
        except ValueError as e:
            logger.error("stripe_activation_failed", error=str(e))
            return {"status": "error", "detail": str(e)}

    return {"status": "ok"}


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
        return {"allowed": True, "plan": "free", "used": 0, "limit": 6, "remaining": 6}

    svc = SubscriptionService(db)
    return await svc.check_quota(user.id, msg_type)
