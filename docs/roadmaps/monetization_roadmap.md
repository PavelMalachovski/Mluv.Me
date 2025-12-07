# Monetization Roadmap

**Project:** Mluv.Me
**Last Updated:** December 7, 2025
**Status:** Ready for Implementation
**Expected Timeline:** 18-24 months
**Priority:** HIGH

---

## 📊 Executive Summary

This roadmap outlines a comprehensive monetization strategy for Mluv.Me, targeting $100,000+ MRR within 24 months through multiple revenue streams:

1. **Freemium Model** (Primary) - Individual subscriptions
2. **B2B/Enterprise** - Team and organizational licenses
3. **Marketplace** - Tutor platform with commissions
4. **Partnerships** - Affiliate and content revenue
5. **Grants** - Institutional funding

**Revenue Projections:**
- Month 6: $5,000 MRR
- Month 12: $25,000 MRR
- Month 18: $60,000 MRR
- Month 24: $120,000 MRR

---

## 🎯 Revenue Goals & Targets

### Year 1 Goals
| Quarter | MRR Target | ARR Target | Paying Users | Conversion Rate |
|---------|------------|------------|--------------|-----------------|
| Q1 | $2,000 | $24k | 200 | 2% |
| Q2 | $8,000 | $96k | 800 | 4% |
| Q3 | $18,000 | $216k | 1,800 | 5% |
| Q4 | $35,000 | $420k | 3,500 | 6% |

### Year 2 Goals
| Quarter | MRR Target | ARR Target | Paying Users | Conversion Rate |
|---------|------------|------------|--------------|-----------------|
| Q1 | $55,000 | $660k | 5,500 | 7% |
| Q2 | $80,000 | $960k | 8,000 | 8% |
| Q3 | $100,000 | $1.2M | 10,000 | 8.5% |
| Q4 | $130,000 | $1.56M | 13,000 | 9% |

---

## 💎 Phase 1: Freemium Model Implementation (8 weeks)

### Priority: CRITICAL
**Target:** $5,000 MRR by Month 6
**Effort:** 8 weeks
**Dependencies:** Web UI (for premium features)

### 1.1 Pricing Tier Design

#### Tier Structure

**Free Tier**
- 5 voice messages per day
- Basic corrections (A1-B1 level)
- Standard response speed (no queue priority)
- Telegram bot access only
- 7-day message history
- Basic statistics
- Ad-supported (non-intrusive)

**Pro Tier - $9.99/month or $99/year (17% discount)**
- ✅ Unlimited voice messages
- ✅ Advanced corrections (all levels A1-C2)
- ✅ Priority processing (2x faster)
- ✅ Web dashboard access
- ✅ Spaced repetition system
- ✅ Custom learning paths
- ✅ Unlimited history
- ✅ Export progress (PDF/CSV)
- ✅ Ad-free experience
- ✅ Advanced analytics

**Expert Tier - $19.99/month or $199/year**
- ✅ All Pro features
- ✅ 1-on-1 monthly video call with Czech tutor (30 min)
- ✅ Personalized curriculum
- ✅ Advanced speech analysis
- ✅ Certification prep materials
- ✅ Priority support (24h email response)
- ✅ Custom Honzík personality
- ✅ Exclusive content

### 1.2 Database Schema

#### Task 1.2.1: Subscription Models
**Duration:** 2 days

```python
# backend/models/subscription.py

from enum import Enum
from datetime import datetime, timedelta

class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    EXPERT = "expert"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAUSED = "paused"
    TRIAL = "trial"

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)

    # Subscription details
    tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)

    # Billing
    stripe_customer_id = Column(String(255), unique=True, index=True)
    stripe_subscription_id = Column(String(255), unique=True, index=True)

    # Dates
    started_at = Column(DateTime, default=datetime.utcnow)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancelled_at = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)

    # Billing cycle
    billing_cycle = Column(String(20))  # 'monthly', 'yearly'
    amount = Column(Float)
    currency = Column(String(3), default="USD")

    # Relationships
    user = relationship("User", back_populates="subscription")
    invoices = relationship("Invoice", back_populates="subscription")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey('subscriptions.id'))

    stripe_invoice_id = Column(String(255), unique=True)
    amount = Column(Float)
    currency = Column(String(3))
    status = Column(String(20))  # 'paid', 'pending', 'failed'

    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)

    subscription = relationship("Subscription", back_populates="invoices")

class UsageLimit(Base):
    __tablename__ = "usage_limits"

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    date = Column(Date, primary_key=True)

    messages_count = Column(Integer, default=0)
    messages_limit = Column(Integer)  # Based on tier

    # For future features
    api_calls_count = Column(Integer, default=0)
    api_calls_limit = Column(Integer)
```

**Acceptance Criteria:**
- [ ] Schema created via Alembic
- [ ] Relationships working
- [ ] Indexes optimized
- [ ] Default values set

### 1.3 Stripe Integration

#### Task 1.3.1: Stripe Setup
**Duration:** 3 days

```python
# backend/services/payment_service.py

import stripe
from backend.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:
    """Handle Stripe payments and subscriptions"""

    # Price IDs (from Stripe Dashboard)
    PRICES = {
        "pro_monthly": settings.STRIPE_PRICE_PRO_MONTHLY,
        "pro_yearly": settings.STRIPE_PRICE_PRO_YEARLY,
        "expert_monthly": settings.STRIPE_PRICE_EXPERT_MONTHLY,
        "expert_yearly": settings.STRIPE_PRICE_EXPERT_YEARLY,
    }

    async def create_customer(
        self,
        user: User,
        email: Optional[str] = None
    ) -> str:
        """Create Stripe customer"""
        customer = stripe.Customer.create(
            email=email,
            metadata={
                "user_id": user.id,
                "telegram_id": user.telegram_id
            },
            name=user.first_name
        )

        # Save customer ID
        await subscription_repo.update(
            user.id,
            stripe_customer_id=customer.id
        )

        return customer.id

    async def create_subscription(
        self,
        user_id: int,
        tier: str,
        billing_cycle: str,
        payment_method_id: str
    ) -> dict:
        """Create new subscription"""

        user = await user_repo.get_by_id(user_id)
        subscription_record = await subscription_repo.get_by_user_id(user_id)

        # Create customer if needed
        if not subscription_record.stripe_customer_id:
            customer_id = await self.create_customer(user)
        else:
            customer_id = subscription_record.stripe_customer_id

        # Attach payment method
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer_id
        )

        # Set as default
        stripe.Customer.modify(
            customer_id,
            invoice_settings={
                'default_payment_method': payment_method_id
            }
        )

        # Get price ID
        price_key = f"{tier}_{billing_cycle}"
        price_id = self.PRICES[price_key]

        # Create subscription
        stripe_subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            metadata={
                "user_id": user_id,
                "tier": tier
            },
            trial_period_days=7,  # 7-day trial
            expand=['latest_invoice.payment_intent']
        )

        # Update database
        await subscription_repo.update(
            user_id,
            tier=tier,
            status="trial" if stripe_subscription.trial_end else "active",
            stripe_subscription_id=stripe_subscription.id,
            current_period_start=datetime.fromtimestamp(
                stripe_subscription.current_period_start
            ),
            current_period_end=datetime.fromtimestamp(
                stripe_subscription.current_period_end
            ),
            trial_end=datetime.fromtimestamp(stripe_subscription.trial_end)
                if stripe_subscription.trial_end else None,
            billing_cycle=billing_cycle,
            amount=stripe_subscription.items.data[0].price.unit_amount / 100
        )

        return {
            "subscription_id": stripe_subscription.id,
            "client_secret": stripe_subscription.latest_invoice.payment_intent.client_secret,
            "status": stripe_subscription.status
        }

    async def cancel_subscription(
        self,
        user_id: int,
        immediate: bool = False
    ):
        """Cancel subscription"""
        subscription_record = await subscription_repo.get_by_user_id(user_id)

        if immediate:
            # Cancel immediately
            stripe.Subscription.delete(
                subscription_record.stripe_subscription_id
            )
            status = "cancelled"
        else:
            # Cancel at period end
            stripe.Subscription.modify(
                subscription_record.stripe_subscription_id,
                cancel_at_period_end=True
            )
            status = "active"  # Still active until period ends

        await subscription_repo.update(
            user_id,
            status=status,
            cancelled_at=datetime.utcnow()
        )

    async def handle_webhook(self, event: dict):
        """Handle Stripe webhooks"""
        event_type = event['type']

        if event_type == 'customer.subscription.updated':
            await self._handle_subscription_updated(event['data']['object'])

        elif event_type == 'customer.subscription.deleted':
            await self._handle_subscription_deleted(event['data']['object'])

        elif event_type == 'invoice.paid':
            await self._handle_invoice_paid(event['data']['object'])

        elif event_type == 'invoice.payment_failed':
            await self._handle_payment_failed(event['data']['object'])

    async def _handle_subscription_updated(self, subscription: dict):
        """Handle subscription update webhook"""
        user_id = int(subscription['metadata']['user_id'])

        await subscription_repo.update(
            user_id,
            status=subscription['status'],
            current_period_start=datetime.fromtimestamp(
                subscription['current_period_start']
            ),
            current_period_end=datetime.fromtimestamp(
                subscription['current_period_end']
            )
        )

    async def _handle_invoice_paid(self, invoice: dict):
        """Handle successful payment"""
        subscription_id = invoice['subscription']

        # Create invoice record
        await invoice_repo.create(
            stripe_invoice_id=invoice['id'],
            amount=invoice['amount_paid'] / 100,
            currency=invoice['currency'],
            status='paid',
            paid_at=datetime.fromtimestamp(invoice['status_transitions']['paid_at'])
        )
```

**Acceptance Criteria:**
- [ ] Stripe account configured
- [ ] Products and prices created
- [ ] Payment flows working
- [ ] Webhooks handling events
- [ ] Error handling robust

#### Task 1.3.2: Subscription Endpoints
**Duration:** 2 days

```python
# backend/routers/subscriptions.py

from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/subscriptions", tags=["subscriptions"])

class SubscriptionCreateRequest(BaseModel):
    tier: str  # 'pro' or 'expert'
    billing_cycle: str  # 'monthly' or 'yearly'
    payment_method_id: str

@router.post("/create")
async def create_subscription(
    request: SubscriptionCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create new subscription"""

    # Check if already subscribed
    existing = await subscription_repo.get_by_user_id(current_user.id)
    if existing and existing.status == "active":
        raise HTTPException(
            status_code=400,
            detail="User already has active subscription"
        )

    # Create subscription
    result = await payment_service.create_subscription(
        user_id=current_user.id,
        tier=request.tier,
        billing_cycle=request.billing_cycle,
        payment_method_id=request.payment_method_id
    )

    return result

@router.post("/cancel")
async def cancel_subscription(
    immediate: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Cancel subscription"""

    subscription = await subscription_repo.get_by_user_id(current_user.id)
    if not subscription or subscription.status != "active":
        raise HTTPException(
            status_code=400,
            detail="No active subscription found"
        )

    await payment_service.cancel_subscription(
        user_id=current_user.id,
        immediate=immediate
    )

    return {"message": "Subscription cancelled successfully"}

@router.get("/status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user)
):
    """Get current subscription status"""

    subscription = await subscription_repo.get_by_user_id(current_user.id)

    return {
        "tier": subscription.tier,
        "status": subscription.status,
        "current_period_end": subscription.current_period_end,
        "cancel_at_period_end": subscription.cancelled_at is not None,
        "trial_end": subscription.trial_end
    }

@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None)
):
    """Handle Stripe webhooks"""

    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle event
    await payment_service.handle_webhook(event)

    return {"status": "success"}

@router.get("/invoices")
async def get_invoices(
    current_user: User = Depends(get_current_user)
):
    """Get user's invoice history"""

    subscription = await subscription_repo.get_by_user_id(current_user.id)
    invoices = await invoice_repo.get_by_subscription_id(subscription.id)

    return [invoice.to_dict() for invoice in invoices]
```

**Acceptance Criteria:**
- [ ] All endpoints working
- [ ] Webhook verification
- [ ] Error handling
- [ ] API documentation

### 1.4 Usage Limits & Middleware

#### Task 1.4.1: Usage Tracking Middleware
**Duration:** 2 days

```python
# backend/middleware/usage_limits.py

from fastapi import HTTPException
from datetime import datetime, date

class UsageLimitMiddleware:
    """Track and enforce usage limits based on subscription tier"""

    LIMITS = {
        "free": {
            "daily_messages": 5,
            "features": ["basic_corrections"]
        },
        "pro": {
            "daily_messages": -1,  # Unlimited
            "features": ["basic_corrections", "advanced_corrections", "web_access"]
        },
        "expert": {
            "daily_messages": -1,
            "features": ["all"]
        }
    }

    async def check_message_limit(self, user_id: int) -> bool:
        """Check if user can send another message"""

        # Get subscription
        subscription = await subscription_repo.get_by_user_id(user_id)
        tier = subscription.tier if subscription else "free"

        # Check limits
        limit = self.LIMITS[tier]["daily_messages"]

        if limit == -1:  # Unlimited
            return True

        # Get today's usage
        usage = await usage_repo.get_or_create(
            user_id=user_id,
            date=date.today()
        )

        if usage.messages_count >= limit:
            return False

        # Increment usage
        await usage_repo.increment_messages(user_id, date.today())

        return True

    async def check_feature_access(
        self,
        user_id: int,
        feature: str
    ) -> bool:
        """Check if user has access to feature"""

        subscription = await subscription_repo.get_by_user_id(user_id)
        tier = subscription.tier if subscription else "free"

        allowed_features = self.LIMITS[tier]["features"]

        if "all" in allowed_features:
            return True

        return feature in allowed_features

usage_limit_middleware = UsageLimitMiddleware()

# Dependency for routes
async def require_message_quota(
    current_user: User = Depends(get_current_user)
):
    """Require user to have message quota"""

    can_send = await usage_limit_middleware.check_message_limit(
        current_user.id
    )

    if not can_send:
        raise HTTPException(
            status_code=402,  # Payment Required
            detail={
                "error": "daily_limit_reached",
                "message": "You've reached your daily message limit. Upgrade to Pro for unlimited messages!",
                "upgrade_url": "/subscriptions/upgrade"
            }
        )

# Usage in routes
@router.post("/api/v1/lessons/process")
async def process_lesson(
    ...,
    _: None = Depends(require_message_quota)
):
    """Process lesson with usage check"""
    pass
```

**Acceptance Criteria:**
- [ ] Usage tracking working
- [ ] Limits enforced correctly
- [ ] Graceful error messages
- [ ] Reset at midnight

### 1.5 Frontend Integration

#### Task 1.5.1: Subscription UI
**Duration:** 4 days

```tsx
// frontend/app/dashboard/subscription/page.tsx

'use client';

import { useState } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';
import { Button } from '@/components/ui/button';
import { PricingCard } from '@/components/features/PricingCard';

const stripePromise = loadStripe(
  process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!
);

function SubscriptionForm({ tier, billingCycle }: {
  tier: string;
  billingCycle: string;
}) {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setLoading(true);
    setError(null);

    // Create payment method
    const cardElement = elements.getElement(CardElement);
    const { error: pmError, paymentMethod } = await stripe.createPaymentMethod({
      type: 'card',
      card: cardElement!,
    });

    if (pmError) {
      setError(pmError.message || 'Payment failed');
      setLoading(false);
      return;
    }

    // Create subscription
    try {
      const response = await fetch('/api/v1/subscriptions/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          tier,
          billing_cycle: billingCycle,
          payment_method_id: paymentMethod!.id
        })
      });

      if (!response.ok) {
        throw new Error('Subscription creation failed');
      }

      const { client_secret } = await response.json();

      // Confirm payment if needed
      if (client_secret) {
        const { error: confirmError } = await stripe.confirmCardPayment(
          client_secret
        );

        if (confirmError) {
          throw new Error(confirmError.message);
        }
      }

      // Success!
      window.location.href = '/dashboard?subscribed=true';
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <CardElement
        options={{
          style: {
            base: {
              fontSize: '16px',
              color: '#424770',
              '::placeholder': {
                color: '#aab7c4',
              },
            },
          },
        }}
      />

      {error && (
        <div className="rounded-md bg-red-50 p-4 text-red-800">
          {error}
        </div>
      )}

      <Button
        type="submit"
        disabled={!stripe || loading}
        className="w-full"
      >
        {loading ? 'Processing...' : 'Subscribe'}
      </Button>
    </form>
  );
}

export default function SubscriptionPage() {
  const [selectedTier, setSelectedTier] = useState<string | null>(null);
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');

  return (
    <div className="container mx-auto p-6">
      <h1 className="mb-8 text-center text-4xl font-bold">
        Choose Your Plan
      </h1>

      {/* Billing Toggle */}
      <div className="mb-8 flex justify-center">
        <div className="rounded-lg border p-1">
          <button
            onClick={() => setBillingCycle('monthly')}
            className={`px-4 py-2 rounded ${
              billingCycle === 'monthly' ? 'bg-blue-500 text-white' : ''
            }`}
          >
            Monthly
          </button>
          <button
            onClick={() => setBillingCycle('yearly')}
            className={`px-4 py-2 rounded ${
              billingCycle === 'yearly' ? 'bg-blue-500 text-white' : ''
            }`}
          >
            Yearly (Save 17%)
          </button>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="grid gap-8 md:grid-cols-3">
        <PricingCard
          tier="free"
          title="Free"
          price={0}
          billingCycle={billingCycle}
          features={[
            '5 messages per day',
            'Basic corrections',
            'Telegram bot',
            '7-day history'
          ]}
          current={true}
        />

        <PricingCard
          tier="pro"
          title="Pro"
          price={billingCycle === 'monthly' ? 9.99 : 99}
          billingCycle={billingCycle}
          features={[
            'Unlimited messages',
            'Advanced corrections',
            'Web dashboard',
            'Spaced repetition',
            'Ad-free'
          ]}
          onSelect={() => setSelectedTier('pro')}
          highlighted={true}
        />

        <PricingCard
          tier="expert"
          title="Expert"
          price={billingCycle === 'monthly' ? 19.99 : 199}
          billingCycle={billingCycle}
          features={[
            'All Pro features',
            'Monthly tutor call',
            'Custom curriculum',
            'Speech analysis',
            'Priority support'
          ]}
          onSelect={() => setSelectedTier('expert')}
        />
      </div>

      {/* Payment Form */}
      {selectedTier && (
        <div className="mx-auto mt-12 max-w-md rounded-lg border p-6">
          <h2 className="mb-4 text-2xl font-semibold">
            Complete Your Subscription
          </h2>
          <Elements stripe={stripePromise}>
            <SubscriptionForm
              tier={selectedTier}
              billingCycle={billingCycle}
            />
          </Elements>
        </div>
      )}
    </div>
  );
}
```

**Acceptance Criteria:**
- [ ] Pricing cards display correctly
- [ ] Stripe Elements integration working
- [ ] Payment flow smooth
- [ ] Error handling
- [ ] Success redirect

### 1.6 Conversion Optimization

#### Task 1.6.1: Upgrade Prompts
**Duration:** 2 days

```python
# bot/handlers/upgrade.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def show_upgrade_prompt(
    message: Message,
    reason: str = "daily_limit"
):
    """Show contextual upgrade prompt"""

    prompts = {
        "daily_limit": {
            "text": """
🔒 Daily Limit Reached!

You've used all 5 free messages today. Upgrade to Pro for:
✅ Unlimited messages
✅ Advanced corrections
✅ Web dashboard
✅ Priority processing

Start with 7-day free trial!
            """,
            "cta": "Try Pro Free for 7 Days"
        },
        "advanced_feature": {
            "text": """
💎 Pro Feature

This feature is available in Pro and Expert plans.
Unlock advanced analytics, personalized exercises, and more!
            """,
            "cta": "Upgrade to Pro"
        },
        "web_access": {
            "text": """
🌐 Web Dashboard

Access your progress, detailed analytics, and practice
on desktop with Mluv.Me Pro!
            """,
            "cta": "Get Web Access"
        }
    }

    prompt = prompts.get(reason, prompts["daily_limit"])

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=prompt["cta"],
                url="https://app.mluv.me/subscription"
            )
        ],
        [
            InlineKeyboardButton(
                text="📊 Compare Plans",
                url="https://app.mluv.me/pricing"
            )
        ]
    ])

    await message.answer(prompt["text"], reply_markup=keyboard)
```

**Acceptance Criteria:**
- [ ] Prompts shown at right time
- [ ] Non-intrusive messaging
- [ ] Clear value proposition
- [ ] Easy upgrade path

---

## 🏢 Phase 2: B2B/Enterprise Model (8 weeks)

### Priority: HIGH
**Target:** $20,000 MRR from B2B by Month 18
**Effort:** 8 weeks
**Dependencies:** Phase 1

### 2.1 Organization Management

#### Task 2.1.1: Multi-Tenant Architecture
**Duration:** 5 days

```python
# backend/models/organization.py

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, index=True)

    # Subscription
    subscription_tier = Column(String(20))  # 'team', 'enterprise'
    max_users = Column(Integer, default=10)
    billing_email = Column(String(255))

    # Settings
    custom_branding = Column(JSON)  # Logo, colors
    sso_enabled = Column(Boolean, default=False)
    sso_config = Column(JSON, nullable=True)

    # Dates
    created_at = Column(DateTime, default=datetime.utcnow)
    subscription_start = Column(DateTime)
    subscription_end = Column(DateTime)

    # Relationships
    users = relationship("User", back_populates="organization")
    admins = relationship("OrganizationAdmin", back_populates="organization")
    invitations = relationship("OrganizationInvitation")

class OrganizationAdmin(Base):
    __tablename__ = "organization_admins"

    organization_id = Column(Integer, ForeignKey('organizations.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    role = Column(String(20))  # 'owner', 'admin', 'billing'
    added_at = Column(DateTime, default=datetime.utcnow)

class OrganizationInvitation(Base):
    __tablename__ = "organization_invitations"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    email = Column(String(255))
    token = Column(String(255), unique=True, index=True)
    invited_by = Column(Integer, ForeignKey('users.id'))
    expires_at = Column(DateTime)
    accepted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Update User model
class User(Base):
    # ... existing fields ...
    organization_id = Column(
        Integer,
        ForeignKey('organizations.id'),
        nullable=True
    )
    organization = relationship("Organization", back_populates="users")
```

**Acceptance Criteria:**
- [ ] Organization schema created
- [ ] User-organization linking
- [ ] Admin roles working
- [ ] Invitation system

### 2.2 Team Analytics Dashboard

#### Task 2.2.1: Organization Analytics API
**Duration:** 5 days

```python
# backend/routers/organizations.py

@router.get("/api/v1/orgs/{org_id}/analytics")
@require_org_admin
async def get_org_analytics(
    org_id: int,
    period: str = "30d",
    current_user: User = Depends(get_current_user)
):
    """Team-wide learning analytics"""

    # Get organization members
    org = await org_repo.get_by_id(org_id)
    user_ids = [user.id for user in org.users]

    # Aggregate statistics
    stats = await analytics_service.aggregate_org_stats(
        user_ids=user_ids,
        period=period
    )

    return {
        "organization": {
            "name": org.name,
            "total_users": len(user_ids),
            "active_users": stats["active_users"]
        },
        "metrics": {
            "total_messages": stats["total_messages"],
            "avg_correctness_score": stats["avg_score"],
            "total_practice_time": stats["total_time"],
            "completion_rate": stats["completion_rate"]
        },
        "top_performers": stats["top_performers"],
        "struggling_users": stats["struggling_users"],
        "progress_chart": stats["progress_over_time"]
    }

@router.get("/api/v1/orgs/{org_id}/users")
@require_org_admin
async def get_org_users(
    org_id: int,
    current_user: User = Depends(get_current_user)
):
    """List organization members with their progress"""

    org = await org_repo.get_by_id(org_id)
    users_data = []

    for user in org.users:
        stats = await stats_service.get_user_summary(user.id)
        users_data.append({
            "user_id": user.id,
            "name": user.first_name,
            "email": user.email,
            "czech_level": user.settings.czech_level,
            "current_streak": stats.streak,
            "total_messages": stats.total_messages,
            "avg_score": stats.avg_correctness,
            "last_activity": stats.last_activity
        })

    return {"users": users_data}

@router.post("/api/v1/orgs/{org_id}/users/invite")
@require_org_admin
async def invite_user(
    org_id: int,
    email: str,
    current_user: User = Depends(get_current_user)
):
    """Invite user to organization"""

    # Create invitation token
    token = generate_secure_token()
    expires_at = datetime.now() + timedelta(days=7)

    invitation = await invitation_repo.create(
        organization_id=org_id,
        email=email,
        token=token,
        invited_by=current_user.id,
        expires_at=expires_at
    )

    # Send invitation email
    await email_service.send_org_invitation(
        to_email=email,
        org_name=org.name,
        invitation_url=f"https://app.mluv.me/join/{token}"
    )

    return {"message": "Invitation sent", "expires_at": expires_at}
```

**Acceptance Criteria:**
- [ ] Analytics aggregation working
- [ ] Dashboard displays data correctly
- [ ] Real-time updates
- [ ] Export functionality

### 2.3 Enterprise Features

#### Task 2.3.1: SSO Integration (SAML/OAuth)
**Duration:** 7 days

```python
# backend/services/sso_service.py

from onelogin.saml2.auth import OneLogin_Saml2_Auth

class SSOService:
    """Handle SSO authentication for enterprise customers"""

    async def initiate_saml_login(
        self,
        org_id: int,
        relay_state: str = None
    ) -> str:
        """Initiate SAML login flow"""

        org = await org_repo.get_by_id(org_id)

        if not org.sso_enabled:
            raise HTTPException(400, "SSO not enabled")

        saml_auth = OneLogin_Saml2_Auth(
            self._get_saml_settings(org),
            {}
        )

        return saml_auth.login(relay_state)

    async def handle_saml_callback(
        self,
        org_id: int,
        saml_response: str
    ) -> User:
        """Process SAML response"""

        org = await org_repo.get_by_id(org_id)

        saml_auth = OneLogin_Saml2_Auth(
            self._get_saml_settings(org),
            {"SAMLResponse": saml_response}
        )

        saml_auth.process_response()

        if not saml_auth.is_authenticated():
            raise HTTPException(403, "SAML authentication failed")

        # Get user attributes
        attrs = saml_auth.get_attributes()
        email = attrs['email'][0]
        name = attrs['name'][0]

        # Get or create user
        user = await user_repo.get_by_email(email)

        if not user:
            user = await user_repo.create(
                email=email,
                first_name=name,
                organization_id=org_id
            )

        return user
```

**Acceptance Criteria:**
- [ ] SAML 2.0 support
- [ ] OAuth 2.0 support
- [ ] Azure AD integration tested
- [ ] Google Workspace integration tested

### 2.4 Enterprise Pricing

**Team Plan - $49/month + $9/user/month**
- Up to 50 users
- Centralized billing
- Team analytics dashboard
- Shared vocabulary lists
- Group challenges
- Email support

**Enterprise Plan - Custom Pricing**
- Unlimited users
- SSO (SAML/OAuth)
- Custom branding
- API access
- Dedicated account manager
- SLA guarantee (99.9% uptime)
- Custom integrations
- On-premise deployment option
- Priority feature requests

### 2.5 Sales & Onboarding

#### Task 2.5.1: Enterprise Sales Page
**Duration:** 3 days

- Landing page for enterprise
- Lead capture form
- Demo scheduling
- ROI calculator
- Case studies

**Acceptance Criteria:**
- [ ] Landing page live
- [ ] Form submissions working
- [ ] Auto-response email
- [ ] CRM integration (HubSpot/Salesforce)

---

## 👨‍🏫 Phase 3: Tutor Marketplace (10 weeks)

### Priority: MEDIUM
**Target:** $10,000 MRR by Month 24
**Effort:** 10 weeks
**Dependencies:** Phases 1 & 2

### 3.1 Tutor Platform

#### Task 3.1.1: Tutor Profiles & Verification
**Duration:** 5 days

```python
# backend/models/marketplace.py

class Tutor(Base):
    __tablename__ = "tutors"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)

    # Profile
    bio = Column(Text)
    languages = Column(JSON)  # Languages tutor speaks
    specializations = Column(JSON)  # ['business', 'exam_prep', 'conversation']
    hourly_rate = Column(Float)
    currency = Column(String(3), default="USD")

    # Verification
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    verification_documents = Column(JSON)

    # Stats
    rating = Column(Float, default=5.0)
    total_lessons = Column(Integer, default=0)
    total_earnings = Column(Float, default=0)

    # Settings
    availability = Column(JSON)  # Weekly schedule
    is_premium_listed = Column(Boolean, default=False)
    is_accepting_students = Column(Boolean, default=True)

    # Relationships
    user = relationship("User")
    lessons = relationship("TutorLesson", back_populates="tutor")
    reviews = relationship("TutorReview", back_populates="tutor")

class TutorLesson(Base):
    __tablename__ = "tutor_lessons"

    id = Column(Integer, primary_key=True)
    tutor_id = Column(Integer, ForeignKey('tutors.id'))
    student_id = Column(Integer, ForeignKey('users.id'))

    # Scheduling
    scheduled_at = Column(DateTime)
    duration_minutes = Column(Integer, default=60)
    timezone = Column(String(50))

    # Status
    status = Column(String(20))  # 'scheduled', 'completed', 'cancelled', 'no_show'

    # Payment
    price = Column(Float)
    platform_fee = Column(Float)  # 15-20% commission
    tutor_payout = Column(Float)
    payment_status = Column(String(20))  # 'pending', 'paid', 'refunded'

    # Meeting
    meeting_url = Column(String(255))  # Zoom/Google Meet link
    meeting_notes = Column(Text, nullable=True)

    # Feedback
    rating = Column(Integer, nullable=True)  # 1-5
    review = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    cancelled_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

class TutorReview(Base):
    __tablename__ = "tutor_reviews"

    id = Column(Integer, primary_key=True)
    tutor_id = Column(Integer, ForeignKey('tutors.id'))
    student_id = Column(Integer, ForeignKey('users.id'))
    lesson_id = Column(Integer, ForeignKey('tutor_lessons.id'))

    rating = Column(Integer)  # 1-5
    review_text = Column(Text)
    response = Column(Text, nullable=True)  # Tutor's response

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
```

**Acceptance Criteria:**
- [ ] Schema implemented
- [ ] Tutor application flow
- [ ] Verification process
- [ ] Profile customization

### 3.2 Booking & Scheduling

#### Task 3.2.1: Booking System
**Duration:** 7 days

```python
# backend/services/booking_service.py

class BookingService:
    """Handle lesson bookings and scheduling"""

    async def get_tutor_availability(
        self,
        tutor_id: int,
        start_date: date,
        end_date: date
    ) -> List[dict]:
        """Get available time slots for tutor"""

        tutor = await tutor_repo.get_by_id(tutor_id)

        # Get weekly availability template
        availability = tutor.availability

        # Get existing bookings
        bookings = await lesson_repo.get_by_tutor_and_date_range(
            tutor_id,
            start_date,
            end_date
        )

        # Generate available slots
        slots = []
        current_date = start_date

        while current_date <= end_date:
            day_name = current_date.strftime('%A').lower()

            if day_name in availability:
                day_slots = availability[day_name]

                for slot in day_slots:
                    slot_time = datetime.combine(
                        current_date,
                        time.fromisoformat(slot['start'])
                    )

                    # Check if slot is not booked
                    is_available = not any(
                        booking.scheduled_at == slot_time
                        for booking in bookings
                    )

                    if is_available and slot_time > datetime.now():
                        slots.append({
                            "datetime": slot_time,
                            "duration": slot['duration']
                        })

            current_date += timedelta(days=1)

        return slots

    async def book_lesson(
        self,
        student_id: int,
        tutor_id: int,
        scheduled_at: datetime,
        duration: int = 60
    ) -> TutorLesson:
        """Book a lesson with tutor"""

        tutor = await tutor_repo.get_by_id(tutor_id)

        # Check availability
        is_available = await self._check_slot_available(
            tutor_id,
            scheduled_at
        )

        if not is_available:
            raise HTTPException(400, "Time slot not available")

        # Calculate pricing
        price = tutor.hourly_rate * (duration / 60)
        platform_fee = price * 0.20  # 20% commission
        tutor_payout = price - platform_fee

        # Create booking
        lesson = await lesson_repo.create(
            tutor_id=tutor_id,
            student_id=student_id,
            scheduled_at=scheduled_at,
            duration_minutes=duration,
            price=price,
            platform_fee=platform_fee,
            tutor_payout=tutor_payout,
            status='scheduled'
        )

        # Create meeting link (integrate with Zoom/Google Meet)
        meeting_url = await meeting_service.create_meeting(
            title=f"Czech Lesson with {tutor.user.first_name}",
            start_time=scheduled_at,
            duration=duration
        )

        await lesson_repo.update(lesson.id, meeting_url=meeting_url)

        # Process payment
        await payment_service.charge_for_lesson(
            student_id=student_id,
            amount=price,
            lesson_id=lesson.id
        )

        # Send notifications
        await notification_service.send_booking_confirmation(
            lesson_id=lesson.id
        )

        return lesson
```

**Acceptance Criteria:**
- [ ] Booking flow smooth
- [ ] Calendar integration
- [ ] Conflict detection
- [ ] Payment processing
- [ ] Meeting link generation

### 3.3 Revenue Sharing

**Commission Structure:**
- Standard tutors: 20% platform commission
- Premium listed tutors: 15% commission + $29/month listing fee
- Volume discount: 10% commission for 50+ lessons/month

**Payout Schedule:**
- Weekly payouts via Stripe Connect
- 7-day hold for refunds
- Minimum payout: $50

#### Task 3.3.1: Stripe Connect Integration
**Duration:** 5 days

```python
# backend/services/payout_service.py

class PayoutService:
    """Handle tutor payouts via Stripe Connect"""

    async def create_connected_account(
        self,
        tutor_id: int,
        country: str = "US"
    ) -> str:
        """Create Stripe Connect account for tutor"""

        tutor = await tutor_repo.get_by_id(tutor_id)

        account = stripe.Account.create(
            type="express",
            country=country,
            email=tutor.user.email,
            capabilities={
                "transfers": {"requested": True}
            },
            metadata={
                "tutor_id": tutor_id
            }
        )

        await tutor_repo.update(
            tutor_id,
            stripe_account_id=account.id
        )

        return account.id

    async def process_weekly_payouts(self):
        """Process payouts for completed lessons"""

        # Get lessons completed in past week
        cutoff = datetime.now() - timedelta(days=7)
        lessons = await lesson_repo.get_completed_unpaid(cutoff)

        # Group by tutor
        payouts_by_tutor = {}

        for lesson in lessons:
            tutor_id = lesson.tutor_id

            if tutor_id not in payouts_by_tutor:
                payouts_by_tutor[tutor_id] = []

            payouts_by_tutor[tutor_id].append(lesson)

        # Process payouts
        for tutor_id, tutor_lessons in payouts_by_tutor.items():
            total_payout = sum(l.tutor_payout for l in tutor_lessons)

            if total_payout >= 50:  # Minimum payout
                await self._send_payout(tutor_id, total_payout, tutor_lessons)

    async def _send_payout(
        self,
        tutor_id: int,
        amount: float,
        lessons: List[TutorLesson]
    ):
        """Send payout to tutor"""

        tutor = await tutor_repo.get_by_id(tutor_id)

        transfer = stripe.Transfer.create(
            amount=int(amount * 100),  # Convert to cents
            currency="usd",
            destination=tutor.stripe_account_id,
            metadata={
                "tutor_id": tutor_id,
                "lesson_ids": [l.id for l in lessons]
            }
        )

        # Update lessons as paid
        for lesson in lessons:
            await lesson_repo.update(
                lesson.id,
                payment_status='paid',
                payout_id=transfer.id
            )

        # Send notification
        await notification_service.send_payout_notification(
            tutor_id=tutor_id,
            amount=amount
        )
```

**Acceptance Criteria:**
- [ ] Stripe Connect integration
- [ ] Automatic payouts working
- [ ] Payout history tracking
- [ ] Tax documentation

---

## 🤝 Phase 4: Partnerships & Additional Revenue (Ongoing)

### Priority: MEDIUM
**Target:** $5,000-10,000 MRR
**Effort:** Ongoing
**Dependencies:** Established user base

### 4.1 Affiliate Program

**Commission Structure:**
- 20% recurring commission for first 12 months
- Cookie duration: 90 days
- Minimum payout: $100

#### Implementation:
- Partner dashboard
- Unique referral links
- Real-time tracking
- Automated payouts

### 4.2 Educational Partnerships

**Target Partners:**
- Language schools in Czech Republic
- Universities with Czech programs
- Corporate training providers
- Immigration services
- Czech cultural organizations

**Partnership Models:**
- Revenue share (10-15%)
- White-label solution
- Co-marketing agreements
- Student discounts

### 4.3 Content Marketplace

**Lesson Packs:**
- Tutors create premium lesson content
- $5-$20 per pack
- Platform takes 30% commission
- Types: themed conversations, grammar drills, cultural lessons

### 4.4 Certification & Testing

**Services:**
- Practice tests for official Czech exams
- Internal proficiency certificates
- Corporate assessment tools

**Pricing:**
- Practice test: $20 per attempt
- Official certificate: $50
- Corporate assessment: Custom pricing

---

## 📊 Financial Projections

### Year 1 Revenue Breakdown

| Revenue Stream | Q1 | Q2 | Q3 | Q4 | Total |
|----------------|-----|-----|-----|-----|-------|
| Individual Subscriptions | $1.5k | $6k | $14k | $28k | $49.5k |
| B2B/Enterprise | $0 | $1k | $3k | $5k | $9k |
| Marketplace | $0 | $0 | $500 | $1k | $1.5k |
| Partnerships | $500 | $1k | $500 | $1k | $3k |
| **Total MRR** | $2k | $8k | $18k | $35k | **$63k ARR** |

### Year 2 Revenue Breakdown

| Revenue Stream | Q1 | Q2 | Q3 | Q4 | Total |
|----------------|-----|-----|-----|-----|-------|
| Individual Subscriptions | $45k | $65k | $80k | $100k | $290k |
| B2B/Enterprise | $8k | $12k | $16k | $22k | $58k |
| Marketplace | $1.5k | $2k | $3k | $4k | $10.5k |
| Partnerships | $500 | $1k | $1k | $1.5k | $4k |
| **Total MRR** | $55k | $80k | $100k | $127.5k | **$1.45M ARR** |

### Cost Structure (Monthly at Scale)

| Category | Year 1 Avg | Year 2 Avg |
|----------|-----------|-----------|
| Infrastructure (AWS/Railway) | $500 | $2,000 |
| OpenAI API | $1,500 | $6,000 |
| Stripe Fees (2.9%) | $200 | $3,000 |
| Salaries (2-3 people) | $20,000 | $35,000 |
| Marketing | $2,000 | $10,000 |
| Support & Tools | $500 | $2,000 |
| **Total Costs** | **$24,700** | **$58,000** |

### Profitability Timeline

- **Month 9:** Break-even
- **Month 12:** $10k profit/month
- **Month 18:** $22k profit/month
- **Month 24:** $70k profit/month

---

## 📈 Key Metrics Dashboard

### Track Monthly:
- MRR (Monthly Recurring Revenue)
- ARR (Annual Recurring Revenue)
- CAC (Customer Acquisition Cost)
- LTV (Lifetime Value)
- Churn Rate
- Conversion Rate (Free → Paid)
- ARPU (Average Revenue Per User)

### Target Metrics:
- LTV:CAC ratio: > 3:1
- Gross Margin: > 75%
- Monthly Churn: < 5%
- Net Revenue Retention: > 100%

---

## 🚀 Go-to-Market Strategy

### Phase 1-2: Product-Led Growth
- Viral Telegram bot
- Free tier with strong value
- Word of mouth
- Content marketing (blog, YouTube)

### Phase 3-4: Sales-Led Growth
- Enterprise sales team
- Partnerships with language schools
- Industry conferences
- Paid advertising (Google, Facebook)

### Marketing Budget Allocation:
- Content Marketing: 30%
- Paid Acquisition: 40%
- Partnerships: 20%
- Events & PR: 10%

---

**Next Steps:**
1. Implement Phase 1: Freemium Model
2. Set up analytics tracking
3. A/B test pricing
4. Launch beta program
5. Iterate based on conversion data

**Document Owner:** Growth Team
**Last Updated:** December 7, 2025
