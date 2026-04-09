"""
Subscription and Payment models.
Управление подписками и платежами пользователей.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.db.database import Base

if TYPE_CHECKING:
    from backend.models.user import User


class Subscription(Base):
    """
    Подписка пользователя.

    plan: 'free' | 'pro'
    status: 'active' | 'expired' | 'cancelled'
    source: 'telegram_stars' | 'stripe' | 'admin'
    """

    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID",
    )

    plan: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="free",
        server_default="free",
        comment="Subscription plan: free, pro",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        server_default="active",
        comment="Status: active, expired, cancelled",
    )

    source: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="telegram_stars",
        comment="Payment source: telegram_stars, tribute, stripe, admin",
    )

    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Subscription start date",
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Subscription expiry date",
    )

    # Stripe-specific (for future use)
    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Stripe subscription ID (for future Stripe integration)",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")

    def __repr__(self) -> str:
        return (
            f"<Subscription(user_id={self.user_id}, plan={self.plan}, "
            f"status={self.status}, expires={self.expires_at})>"
        )


class Payment(Base):
    """
    История платежей (Telegram Stars и Stripe).

    provider: 'telegram_stars' | 'stripe'
    """

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID",
    )

    provider: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Payment provider: telegram_stars, tribute, stripe",
    )

    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Amount in smallest unit (Stars count or cents)",
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="XTR",
        comment="Currency: XTR (Telegram Stars), CZK, USD",
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Human-readable payment description",
    )

    # What was purchased
    product: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Product: pro_7d, pro_30d, extra_voice, extra_text",
    )

    # External reference
    telegram_payment_charge_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Telegram payment charge ID",
    )

    stripe_payment_intent_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Stripe payment intent ID (future)",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="payments")

    def __repr__(self) -> str:
        return (
            f"<Payment(user_id={self.user_id}, provider={self.provider}, "
            f"amount={self.amount} {self.currency}, product={self.product})>"
        )
