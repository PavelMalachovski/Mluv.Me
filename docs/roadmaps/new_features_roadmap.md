# New Features Roadmap

**Project:** Mluv.Me
**Last Updated:** December 7, 2025
**Status:** Ready for Implementation
**Expected Timeline:** 16-20 weeks
**Priority:** HIGH

---

## 📊 Executive Summary

This roadmap outlines the development of major new features to expand Mluv.Me's capabilities and market reach. Key initiatives include:
- **Web UI Platform** for desktop learning
- **Adaptive Learning System** for personalized education
- **Advanced Personalization** features
- **Enhanced Telegram Features**

**Expected Outcomes:**
- 2-3x increase in user engagement
- 50% improvement in learning outcomes
- New user segments (desktop users, advanced learners)
- Foundation for premium features

---

## 🎯 Goals & Success Metrics

### Primary Goals
1. Launch production-ready Web UI with 10,000+ MAU
2. Implement adaptive learning with measurable improvement in outcomes
3. Increase daily active usage by 40%
4. Enable multi-platform experience (Telegram + Web)

### Key Performance Indicators (KPIs)
| Metric | Baseline | 6 Month Target | 12 Month Target |
|--------|----------|----------------|-----------------|
| Platform MAU | Telegram only | +10k Web users | +50k Web users |
| Avg. Session Time | 8 min | 12 min | 15 min |
| Learning Velocity | baseline | +25% | +50% |
| Feature Adoption Rate | N/A | 60% | 75% |
| User Retention (D30) | 35% | 45% | 55% |

---

## 🌐 Phase 1: Web UI Implementation (6-8 weeks)

### Priority: CRITICAL
**Impact:** Market expansion, premium justification
**Effort:** 6-8 weeks
**Dependencies:** Backend API extensions

### 1.1 Technology Stack Setup

#### Task 1.1.1: Next.js Project Initialization
**Duration:** 2 days

```bash
# Initialize Next.js 14+ project
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend

# Install core dependencies
npm install @tanstack/react-query axios zustand zod
npm install @radix-ui/react-* lucide-react
npm install recharts date-fns
```

```json
// frontend/package.json
{
  "name": "mluv-me-web",
  "version": "1.0.0",
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "@tanstack/react-query": "^5.28.0",
    "axios": "^1.6.8",
    "recharts": "^2.12.0",
    "tailwindcss": "^3.4.0",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-tabs": "^1.0.4",
    "lucide-react": "^0.365.0",
    "zustand": "^4.5.2",
    "zod": "^3.22.4",
    "date-fns": "^3.6.0"
  }
}
```

**Project Structure:**
```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── callback/page.tsx
│   ├── dashboard/
│   │   ├── page.tsx
│   │   ├── analytics/page.tsx
│   │   ├── lessons/page.tsx
│   │   └── vocabulary/page.tsx
│   ├── api/
│   │   └── auth/route.ts
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── ui/              # shadcn/ui components
│   └── features/
│       ├── LessonCard.tsx
│       ├── ProgressChart.tsx
│       └── VocabularyList.tsx
├── lib/
│   ├── api-client.ts
│   ├── auth.ts
│   └── types.ts
├── public/
├── styles/
└── next.config.js
```

**Acceptance Criteria:**
- [ ] Next.js dev server running
- [ ] TypeScript configuration complete
- [ ] Tailwind CSS working
- [ ] shadcn/ui components installed

#### Task 1.1.2: Backend API Extensions
**Duration:** 3 days

```python
# backend/routers/web_auth.py

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
import hashlib
import hmac

router = APIRouter(prefix="/api/v1/web/auth", tags=["web_auth"])

class TelegramAuthData(BaseModel):
    id: int
    first_name: str
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str

@router.post("/telegram")
async def telegram_web_auth(
    auth_data: TelegramAuthData,
    response: Response
):
    """Verify Telegram Login Widget data and create session"""

    # Verify hash
    if not verify_telegram_auth(auth_data):
        raise HTTPException(status_code=403, detail="Invalid auth data")

    # Get or create user
    user = await user_repo.get_by_telegram_id(auth_data.id)
    if not user:
        user = await user_repo.create(
            telegram_id=auth_data.id,
            first_name=auth_data.first_name,
            username=auth_data.username
        )

    # Create session
    session_token = generate_session_token()
    await session_repo.create(
        user_id=user.id,
        session_token=session_token,
        device_type="web_app"
    )

    # Set httpOnly cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=30 * 24 * 60 * 60  # 30 days
    )

    return {
        "user": user.to_dict(),
        "access_token": session_token
    }

def verify_telegram_auth(auth_data: TelegramAuthData) -> bool:
    """Verify Telegram auth data hash"""
    check_string = "\n".join([
        f"{k}={v}"
        for k, v in sorted(auth_data.dict(exclude={"hash"}).items())
        if v is not None
    ])

    secret_key = hashlib.sha256(
        settings.TELEGRAM_BOT_TOKEN.encode()
    ).digest()

    expected_hash = hmac.new(
        secret_key,
        check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    return expected_hash == auth_data.hash
```

```python
# backend/routers/web_lessons.py

@router.post("/api/v1/web/lessons/text")
async def process_text_message(
    text: str,
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Process text input (no audio) for web users"""

    # Get user settings
    settings = await settings_repo.get_by_user_id(user_id)

    # Process with Honzík
    response = await honzik_service.process_text_message(
        user_text=text,
        settings=settings,
        conversation_history=await get_conversation_history(user_id)
    )

    # Save message
    await message_repo.create(
        user_id=user_id,
        user_text=text,
        honzik_text=response["honzik_response"],
        correctness_score=response["correctness_score"]
    )

    # Update stats
    stars = await gamification_service.calculate_stars(
        response["correctness_score"]
    )

    return {
        "honzik_text": response["honzik_response"],
        "user_mistakes": response["user_mistakes"],
        "suggestions": response["suggestions"],
        "stars_earned": stars,
        "correctness_score": response["correctness_score"]
    }

@router.get("/api/v1/web/lessons/history")
async def get_lesson_history(
    user_id: int,
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Paginated lesson history with audio URLs"""

    offset = (page - 1) * limit
    messages = await message_repo.get_by_user_paginated(
        user_id,
        offset=offset,
        limit=limit
    )

    total = await message_repo.count_by_user(user_id)

    return {
        "messages": [msg.to_dict() for msg in messages],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }
```

**Acceptance Criteria:**
- [ ] Telegram auth endpoint working
- [ ] Session management implemented
- [ ] Text lesson processing endpoint
- [ ] Lesson history pagination
- [ ] API documentation updated

### 1.2 Core UI Components

#### Task 1.2.1: Authentication Flow
**Duration:** 3 days

```typescript
// frontend/lib/telegram-auth.ts

interface TelegramUser {
  id: number;
  first_name: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

declare global {
  interface Window {
    Telegram?: {
      Login?: {
        auth: (options: {
          bot_id: string;
          request_access?: string;
          lang?: string;
        }, callback: (user: TelegramUser | false) => void) => void;
      };
    };
  }
}

export async function loginWithTelegram(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (!window.Telegram?.Login) {
      reject(new Error('Telegram Login Widget not loaded'));
      return;
    }

    window.Telegram.Login.auth(
      {
        bot_id: process.env.NEXT_PUBLIC_TELEGRAM_BOT_ID!,
        request_access: 'write',
      },
      async (user) => {
        if (!user) {
          reject(new Error('Login cancelled'));
          return;
        }

        try {
          const response = await fetch('/api/v1/web/auth/telegram', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(user),
            credentials: 'include'
          });

          if (!response.ok) {
            throw new Error('Authentication failed');
          }

          const data = await response.json();
          // Store user data in Zustand store
          useAuthStore.setState({ user: data.user, isAuthenticated: true });

          resolve();
        } catch (error) {
          reject(error);
        }
      }
    );
  });
}
```

```tsx
// frontend/app/(auth)/login/page.tsx

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { loginWithTelegram } from '@/lib/telegram-auth';

export default function LoginPage() {
  const router = useRouter();

  useEffect(() => {
    // Load Telegram Login Widget script
    const script = document.createElement('script');
    script.src = 'https://telegram.org/js/telegram-widget.js?22';
    script.async = true;
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  const handleLogin = async () => {
    try {
      await loginWithTelegram();
      router.push('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md space-y-8 p-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold">Mluv.Me</h1>
          <p className="mt-2 text-gray-600">
            Learn Czech with AI-powered conversations
          </p>
        </div>

        <Button
          onClick={handleLogin}
          className="w-full"
          size="lg"
        >
          <svg className="mr-2 h-5 w-5" viewBox="0 0 24 24">
            {/* Telegram icon */}
          </svg>
          Login with Telegram
        </Button>
      </div>
    </div>
  );
}
```

**Acceptance Criteria:**
- [ ] Telegram Login Widget integration
- [ ] Session cookie handling
- [ ] Redirect after login
- [ ] Error handling
- [ ] Loading states

#### Task 1.2.2: Dashboard Page
**Duration:** 4 days

```tsx
// frontend/app/dashboard/page.tsx

'use client';

import { useQuery } from '@tanstack/react-query';
import { ProgressChart } from '@/components/features/ProgressChart';
import { StatsCard } from '@/components/features/StatsCard';
import { RecentLessons } from '@/components/features/RecentLessons';
import { apiClient } from '@/lib/api-client';

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['user-stats'],
    queryFn: () => apiClient.get('/api/v1/stats/me'),
  });

  const { data: lessons } = useQuery({
    queryKey: ['recent-lessons'],
    queryFn: () => apiClient.get('/api/v1/web/lessons/history', {
      params: { limit: 5 }
    }),
  });

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatsCard
          title="Current Streak"
          value={stats?.streak || 0}
          icon="flame"
          trend="+2 from yesterday"
        />
        <StatsCard
          title="Total Stars"
          value={stats?.total_stars || 0}
          icon="star"
        />
        <StatsCard
          title="Czech Level"
          value={stats?.czech_level || 'A1'}
          icon="award"
        />
        <StatsCard
          title="Messages Today"
          value={stats?.messages_today || 0}
          icon="message-circle"
        />
      </div>

      {/* Progress Chart */}
      <div className="rounded-lg border p-6">
        <h2 className="mb-4 text-xl font-semibold">Progress Over Time</h2>
        <ProgressChart data={stats?.progress_data} />
      </div>

      {/* Recent Lessons */}
      <div className="rounded-lg border p-6">
        <h2 className="mb-4 text-xl font-semibold">Recent Lessons</h2>
        <RecentLessons lessons={lessons?.messages} />
      </div>
    </div>
  );
}
```

```tsx
// frontend/components/features/ProgressChart.tsx

'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { format } from 'date-fns';

interface ProgressChartProps {
  data: Array<{
    date: string;
    correctness_score: number;
    messages_count: number;
  }>;
}

export function ProgressChart({ data }: ProgressChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="date"
          tickFormatter={(date) => format(new Date(date), 'MMM dd')}
        />
        <YAxis />
        <Tooltip
          labelFormatter={(date) => format(new Date(date), 'PPP')}
        />
        <Line
          type="monotone"
          dataKey="correctness_score"
          stroke="#8884d8"
          strokeWidth={2}
          name="Correctness Score"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

**Acceptance Criteria:**
- [ ] Dashboard loads user data
- [ ] Charts display correctly
- [ ] Stats cards interactive
- [ ] Recent lessons list
- [ ] Responsive design

#### Task 1.2.3: Practice Interface
**Duration:** 5 days

```tsx
// frontend/app/dashboard/practice/page.tsx

'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { apiClient } from '@/lib/api-client';

export default function PracticePage() {
  const [userText, setUserText] = useState('');
  const [response, setResponse] = useState<any>(null);

  const sendMessage = useMutation({
    mutationFn: (text: string) =>
      apiClient.post('/api/v1/web/lessons/text', { text }),
    onSuccess: (data) => {
      setResponse(data);
      setUserText('');
    },
  });

  return (
    <div className="container mx-auto max-w-4xl p-6">
      <h1 className="mb-6 text-3xl font-bold">Practice Czech</h1>

      <div className="space-y-6">
        {/* Conversation History */}
        <div className="space-y-4 rounded-lg border p-4">
          {response && (
            <>
              {/* User Message */}
              <div className="flex justify-end">
                <div className="max-w-[80%] rounded-lg bg-blue-500 p-3 text-white">
                  {userText}
                </div>
              </div>

              {/* Honzík Response */}
              <div className="flex justify-start">
                <div className="max-w-[80%] rounded-lg bg-gray-100 p-3">
                  <p className="mb-2">{response.honzik_text}</p>

                  {response.user_mistakes.length > 0 && (
                    <div className="mt-2 border-t pt-2">
                      <p className="font-semibold text-sm">Mistakes:</p>
                      <ul className="list-disc pl-4 text-sm">
                        {response.user_mistakes.map((mistake, i) => (
                          <li key={i}>{mistake}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-sm">⭐ {response.stars_earned} stars</span>
                    <span className="text-sm text-gray-600">
                      Score: {response.correctness_score}%
                    </span>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="space-y-3">
          <Textarea
            value={userText}
            onChange={(e) => setUserText(e.target.value)}
            placeholder="Type your Czech message here..."
            rows={4}
            className="resize-none"
          />
          <Button
            onClick={() => sendMessage.mutate(userText)}
            disabled={!userText.trim() || sendMessage.isPending}
            className="w-full"
          >
            {sendMessage.isPending ? 'Sending...' : 'Send Message'}
          </Button>
        </div>
      </div>
    </div>
  );
}
```

**Acceptance Criteria:**
- [ ] Text input working
- [ ] Real-time response display
- [ ] Mistake highlighting
- [ ] Stars display
- [ ] Conversation history

### 1.3 Deployment

#### Task 1.3.1: Vercel Deployment Setup
**Duration:** 1 day

```javascript
// frontend/next.config.js

module.exports = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_TELEGRAM_BOT_ID: process.env.NEXT_PUBLIC_TELEGRAM_BOT_ID,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
    ];
  },
};
```

```yaml
# vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "env": {
    "NEXT_PUBLIC_API_URL": "@api-url",
    "NEXT_PUBLIC_TELEGRAM_BOT_ID": "@telegram-bot-id"
  }
}
```

**Deployment Steps:**
1. Connect GitHub repo to Vercel
2. Configure environment variables
3. Set custom domain (app.mluv.me)
4. Enable automatic deployments
5. Configure CORS on backend

**Acceptance Criteria:**
- [ ] Frontend deployed to Vercel
- [ ] Custom domain configured
- [ ] SSL certificate active
- [ ] Environment variables set
- [ ] CI/CD pipeline working

---

## 🧠 Phase 2: Adaptive Learning System (4 weeks)

### Priority: HIGH
**Impact:** Personalized learning, better outcomes
**Effort:** 4 weeks
**Dependencies:** Phase 1

### 2.1 User Proficiency Tracking

#### Task 2.1.1: Database Schema
**Duration:** 2 days

```python
# alembic/versions/20251210_adaptive_learning.py

def upgrade():
    # User proficiency table
    op.create_table(
        'user_proficiency',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('assessed_at', sa.DateTime(), nullable=False),

        # Overall metrics
        sa.Column('overall_score', sa.Float()),
        sa.Column('improvement_rate', sa.Float()),

        # Detailed breakdown
        sa.Column('grammar_score', sa.Float()),
        sa.Column('vocabulary_score', sa.Float()),
        sa.Column('pronunciation_score', sa.Float()),
        sa.Column('fluency_score', sa.Float()),

        # Weak areas (JSON)
        sa.Column('weak_grammar_topics', sa.JSON()),
        sa.Column('weak_vocabulary_categories', sa.JSON()),

        sa.Column('suggested_level', sa.String(10)),
        sa.Column('confidence', sa.Float())  # Confidence in assessment
    )

    # Personalized exercises
    op.create_table(
        'personalized_exercises',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('exercise_type', sa.String(50)),
        sa.Column('topic', sa.String(100)),
        sa.Column('difficulty', sa.String(10)),
        sa.Column('content', sa.JSON()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True)
    )
```

**Acceptance Criteria:**
- [ ] Migration runs successfully
- [ ] Tables created with indexes
- [ ] Models defined in SQLAlchemy
- [ ] Relationships configured

#### Task 2.1.2: Proficiency Calculation Engine
**Duration:** 5 days

```python
# backend/services/adaptive_learning.py

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np

class AdaptiveLearningEngine:
    """Analyzes user performance and adjusts learning path"""

    def __init__(self):
        self.message_repo = MessageRepository()
        self.proficiency_repo = ProficiencyRepository()

    async def calculate_user_proficiency(
        self,
        user_id: int,
        window_days: int = 7
    ) -> UserProficiency:
        """
        Analyze recent performance and calculate proficiency metrics
        """
        # Get recent messages
        cutoff_date = datetime.now() - timedelta(days=window_days)
        messages = await self.message_repo.get_by_user_since(
            user_id,
            cutoff_date
        )

        if not messages:
            return None

        # Calculate overall score
        scores = [m.correctness_score for m in messages if m.correctness_score]
        overall_score = np.mean(scores) if scores else 0

        # Calculate improvement rate (linear regression)
        improvement_rate = self._calculate_improvement_trend(messages)

        # Analyze specific areas
        grammar_issues = self._extract_grammar_issues(messages)
        vocabulary_issues = self._extract_vocabulary_issues(messages)

        # Calculate sub-scores
        grammar_score = self._calculate_grammar_score(messages)
        vocabulary_score = self._calculate_vocabulary_score(messages)

        # Suggest level
        suggested_level = self._suggest_level(overall_score, improvement_rate)

        # Create proficiency record
        proficiency = UserProficiency(
            user_id=user_id,
            assessed_at=datetime.now(),
            overall_score=overall_score,
            improvement_rate=improvement_rate,
            grammar_score=grammar_score,
            vocabulary_score=vocabulary_score,
            weak_grammar_topics=grammar_issues,
            weak_vocabulary_categories=vocabulary_issues,
            suggested_level=suggested_level,
            confidence=self._calculate_confidence(len(messages))
        )

        await self.proficiency_repo.create(proficiency)
        return proficiency

    def _calculate_improvement_trend(
        self,
        messages: List[Message]
    ) -> float:
        """Calculate learning velocity using linear regression"""
        if len(messages) < 2:
            return 0.0

        # Sort by date
        sorted_msgs = sorted(messages, key=lambda m: m.created_at)

        # Prepare data
        x = np.arange(len(sorted_msgs))
        y = np.array([m.correctness_score for m in sorted_msgs])

        # Linear regression
        slope, _ = np.polyfit(x, y, 1)

        return float(slope)

    def _extract_grammar_issues(
        self,
        messages: List[Message]
    ) -> List[str]:
        """Identify recurring grammar problems"""
        issues = {}

        for msg in messages:
            if not msg.user_mistakes:
                continue

            for mistake in msg.user_mistakes:
                # Parse mistake type (e.g., "cases", "past_tense")
                issue_type = self._categorize_grammar_mistake(mistake)
                issues[issue_type] = issues.get(issue_type, 0) + 1

        # Return top 5 issues
        sorted_issues = sorted(
            issues.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [issue[0] for issue in sorted_issues[:5]]

    def _categorize_grammar_mistake(self, mistake: str) -> str:
        """Categorize grammar mistake into topic"""
        mistake_lower = mistake.lower()

        if any(word in mistake_lower for word in ['genitiv', 'akuzativ', 'lokál']):
            return 'cases'
        elif any(word in mistake_lower for word in ['minulý čas', 'past tense']):
            return 'past_tense'
        elif 'slovosled' in mistake_lower or 'word order' in mistake_lower:
            return 'word_order'
        elif 'člen' in mistake_lower or 'article' in mistake_lower:
            return 'articles'
        else:
            return 'other'

    def _calculate_grammar_score(self, messages: List[Message]) -> float:
        """Calculate grammar-specific score"""
        grammar_scores = []

        for msg in messages:
            if msg.user_mistakes:
                # More mistakes = lower score
                mistake_penalty = len(msg.user_mistakes) * 5
                score = max(0, msg.correctness_score - mistake_penalty)
                grammar_scores.append(score)
            else:
                grammar_scores.append(msg.correctness_score)

        return np.mean(grammar_scores) if grammar_scores else 0

    def _suggest_level(
        self,
        overall_score: float,
        improvement_rate: float
    ) -> str:
        """Suggest appropriate Czech level"""
        if overall_score >= 90 and improvement_rate >= 0:
            return 'C2'
        elif overall_score >= 80:
            return 'C1'
        elif overall_score >= 70:
            return 'B2'
        elif overall_score >= 60:
            return 'B1'
        elif overall_score >= 50:
            return 'A2'
        else:
            return 'A1'

    def _calculate_confidence(self, message_count: int) -> float:
        """Calculate confidence in assessment based on data points"""
        # More messages = higher confidence
        if message_count >= 50:
            return 1.0
        elif message_count >= 20:
            return 0.8
        elif message_count >= 10:
            return 0.6
        else:
            return 0.4
```

**Acceptance Criteria:**
- [ ] Proficiency calculation working
- [ ] Grammar issue detection
- [ ] Vocabulary tracking
- [ ] Level suggestion accurate
- [ ] Unit tests passing

### 2.2 Personalized Exercises

#### Task 2.2.1: Exercise Generation
**Duration:** 4 days

```python
# backend/services/exercise_generator.py

class ExerciseGenerator:
    """Generate personalized exercises based on weak areas"""

    async def generate_targeted_exercises(
        self,
        user_id: int,
        proficiency: UserProficiency
    ) -> List[PersonalizedExercise]:
        """Create exercises targeting user's weak areas"""
        exercises = []

        # Grammar exercises
        if proficiency.weak_grammar_topics:
            for topic in proficiency.weak_grammar_topics[:3]:
                exercise = await self._generate_grammar_exercise(
                    user_id,
                    topic,
                    proficiency.suggested_level
                )
                exercises.append(exercise)

        # Vocabulary exercises
        if proficiency.weak_vocabulary_categories:
            for category in proficiency.weak_vocabulary_categories[:2]:
                exercise = await self._generate_vocabulary_exercise(
                    user_id,
                    category,
                    proficiency.suggested_level
                )
                exercises.append(exercise)

        return exercises

    async def _generate_grammar_exercise(
        self,
        user_id: int,
        topic: str,
        level: str
    ) -> PersonalizedExercise:
        """Generate grammar exercise using GPT-4o"""

        prompt = f"""
        Create a Czech grammar exercise for {level} level focusing on {topic}.

        Format:
        {{
            "instruction": "Exercise instruction in Czech",
            "examples": ["example1", "example2"],
            "questions": [
                {{
                    "question": "Sentence with blank: Jdu ___ školy.",
                    "options": ["do", "od", "ze", "z"],
                    "correct_answer": "ze",
                    "explanation": "Use 'ze' (genitive) after 'jdu' for movement from."
                }}
            ]
        }}
        """

        response = await openai_client.generate_chat_completion([
            {"role": "system", "content": "You are a Czech language teacher."},
            {"role": "user", "content": prompt}
        ])

        content = json.loads(response["content"])

        return PersonalizedExercise(
            user_id=user_id,
            exercise_type="grammar",
            topic=topic,
            difficulty=level,
            content=content
        )
```

**Acceptance Criteria:**
- [ ] Exercises generated correctly
- [ ] Appropriate difficulty level
- [ ] Variety of exercise types
- [ ] Quality validation

### 2.3 Dynamic Difficulty Adjustment

#### Task 2.3.1: Honzík Adaptation
**Duration:** 3 days

```python
# backend/services/honzik_personality.py - Update

def _build_system_prompt(
    self,
    settings: UserSettings,
    proficiency: Optional[UserProficiency] = None
) -> str:
    """Build adaptive system prompt"""

    base_prompt = self._get_base_prompt(settings.czech_level)

    # Add adaptive sections
    if proficiency:
        if proficiency.weak_grammar_topics:
            base_prompt += f"""

            The user struggles with: {', '.join(proficiency.weak_grammar_topics)}.
            Gently incorporate these topics in conversation and provide extra help.
            """

        if proficiency.improvement_rate > 0.1:
            base_prompt += """

            The user is making great progress! Be encouraging and slightly increase difficulty.
            """
        elif proficiency.improvement_rate < -0.1:
            base_prompt += """

            The user is struggling. Simplify your language and provide more support.
            """

    # Personalization
    if settings.preferred_topics:
        base_prompt += f"""

        User enjoys topics: {', '.join(settings.preferred_topics)}.
        Try to steer conversation toward these interests.
        """

    if settings.learning_style == 'visual':
        base_prompt += """

        User learns best visually. Use more descriptive language and examples.
        """

    return base_prompt
```

**Acceptance Criteria:**
- [ ] Prompt adapts to proficiency
- [ ] Difficulty adjusts dynamically
- [ ] Personalization working
- [ ] A/B test shows improvement

---

## 🎨 Phase 3: Enhanced Personalization (3 weeks)

### Priority: MEDIUM
**Impact:** User engagement, retention
**Effort:** 3 weeks
**Dependencies:** Phase 2

### 3.1 Learning Style Preferences

#### Task 3.1.1: Extended User Settings
**Duration:** 2 days

```python
# alembic/versions/20251215_learning_preferences.py

def upgrade():
    op.add_column(
        'user_settings',
        sa.Column('learning_style', sa.String(20), default='balanced')
    )
    op.add_column(
        'user_settings',
        sa.Column('preferred_topics', sa.JSON())
    )
    op.add_column(
        'user_settings',
        sa.Column('focus_areas', sa.JSON())
    )
    op.add_column(
        'user_settings',
        sa.Column('exercise_frequency', sa.String(20), default='daily')
    )
    op.add_column(
        'user_settings',
        sa.Column('challenge_difficulty', sa.String(20), default='moderate')
    )
```

**Acceptance Criteria:**
- [ ] Schema updated
- [ ] UI for settings added
- [ ] Validation working
- [ ] Defaults set correctly

### 3.2 Spaced Repetition System

#### Task 3.2.1: SRS Implementation
**Duration:** 5 days

```python
# backend/services/srs_service.py

class SpacedRepetitionService:
    """Implement SM-2 algorithm for vocabulary review"""

    def calculate_next_review(
        self,
        word: SavedWord,
        score: int  # 0-5 (SM-2 scale)
    ) -> tuple[datetime, int, float]:
        """
        Calculate next review date, interval, and ease factor

        SM-2 Algorithm:
        - Score >= 3: Correct, increase interval
        - Score < 3: Incorrect, reset interval
        """
        if score >= 3:  # Correct response
            if word.repetitions == 0:
                interval = 1
            elif word.repetitions == 1:
                interval = 6
            else:
                interval = round(word.interval * word.ease_factor)

            repetitions = word.repetitions + 1
            ease = word.ease_factor + (
                0.1 - (5 - score) * (0.08 + (5 - score) * 0.02)
            )
        else:  # Incorrect response
            interval = 1
            repetitions = 0
            ease = word.ease_factor

        # Ensure minimum ease factor
        ease = max(1.3, ease)

        # Calculate next review date
        next_date = datetime.now() + timedelta(days=interval)

        return next_date, interval, ease

    async def get_words_due_for_review(
        self,
        user_id: int
    ) -> List[SavedWord]:
        """Get vocabulary due for review today"""
        return await word_repo.get_due_words(
            user_id,
            before_date=datetime.now()
        )

    async def process_review_result(
        self,
        word_id: int,
        score: int
    ):
        """Update word based on review result"""
        word = await word_repo.get_by_id(word_id)

        next_date, interval, ease = self.calculate_next_review(word, score)

        await word_repo.update(
            word_id,
            next_review_date=next_date,
            interval=interval,
            ease_factor=ease,
            repetitions=word.repetitions + (1 if score >= 3 else -word.repetitions),
            last_review_score=score
        )
```

**Acceptance Criteria:**
- [ ] SM-2 algorithm implemented
- [ ] Review scheduling working
- [ ] Telegram command for reviews
- [ ] Web UI for reviews
- [ ] Statistics tracking

---

## 📱 Phase 4: Enhanced Telegram Features (2 weeks)

### Priority: MEDIUM
**Impact:** Improved mobile experience
**Effort:** 2 weeks
**Dependencies:** None

### 4.1 Inline Keyboards & Rich Interactions

#### Task 4.1.1: Interactive Lesson Feedback
**Duration:** 3 days

```python
# bot/handlers/voice.py - Enhanced

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@router.message(F.voice)
async def handle_voice_message(message: Message, api_client: APIClient):
    """Process voice with interactive feedback"""

    # ... existing processing ...

    # Create interactive keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📊 Details",
                callback_data=f"lesson_details:{message_id}"
            ),
            InlineKeyboardButton(
                text="🔊 Listen Again",
                callback_data=f"replay_audio:{message_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="💾 Save Words",
                callback_data=f"save_words:{message_id}"
            ),
            InlineKeyboardButton(
                text="❓ Explain Mistake",
                callback_data=f"explain_mistake:{message_id}:0"
            )
        ]
    ])

    await message.answer(
        response_text,
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("explain_mistake:"))
async def explain_mistake(callback: CallbackQuery, api_client: APIClient):
    """Provide detailed explanation of a specific mistake"""
    _, message_id, mistake_index = callback.data.split(":")

    # Get message details
    msg = await api_client.get_message(message_id)
    mistake = msg.user_mistakes[int(mistake_index)]

    # Generate detailed explanation
    explanation = await api_client.explain_mistake(mistake)

    await callback.message.answer(
        f"📚 Detailed Explanation:\n\n{explanation}"
    )
    await callback.answer()
```

**Acceptance Criteria:**
- [ ] Interactive keyboards working
- [ ] Callback handlers implemented
- [ ] Smooth user experience
- [ ] Error handling

### 4.2 Daily Challenges

#### Task 4.2.1: Challenge System
**Duration:** 4 days

```python
# backend/models/challenge.py

class DailyChallenge(Base):
    __tablename__ = "daily_challenges"

    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, index=True)
    challenge_type = Column(String(50))
    difficulty = Column(String(10))
    content = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserChallengeProgress(Base):
    __tablename__ = "user_challenge_progress"

    user_id = Column(Integer, ForeignKey('users.id'))
    challenge_id = Column(Integer, ForeignKey('daily_challenges.id'))
    completed = Column(Boolean, default=False)
    score = Column(Integer)
    completed_at = Column(DateTime, nullable=True)
```

```python
# backend/tasks/challenges.py

@celery_app.task
def generate_daily_challenge():
    """Generate new daily challenge"""

    challenge_types = ['vocabulary', 'grammar', 'conversation']
    challenge_type = random.choice(challenge_types)

    # Generate challenge content using GPT-4o
    content = await challenge_generator.generate(
        challenge_type=challenge_type,
        difficulty='mixed'  # Different difficulty for different levels
    )

    # Save to database
    await challenge_repo.create(
        date=datetime.now().date(),
        challenge_type=challenge_type,
        difficulty='mixed',
        content=content
    )
```

**Acceptance Criteria:**
- [ ] Daily challenges generated
- [ ] User progress tracked
- [ ] Telegram notifications
- [ ] Leaderboard integration

---

## 📊 Success Metrics & Monitoring

### Phase 1: Web UI
- **Metric:** Web MAU
- **Target:** 10,000 users by Month 6
- **Monitoring:** Google Analytics, Mixpanel

### Phase 2: Adaptive Learning
- **Metric:** Learning improvement rate
- **Target:** +25% over baseline
- **Monitoring:** Custom analytics dashboard

### Phase 3: Personalization
- **Metric:** Feature adoption rate
- **Target:** 60% of active users
- **Monitoring:** Feature flags, usage tracking

### Phase 4: Enhanced Telegram
- **Metric:** Daily engagement
- **Target:** +40% session time
- **Monitoring:** Bot analytics, user surveys

---

## 💰 Cost Analysis

| Phase | Dev Cost | Op Cost/mo | Expected Impact |
|-------|----------|------------|-----------------|
| Web UI | $15,000 | $25 | +10k users, 2x conversion |
| Adaptive Learning | $12,000 | $10 | +25% outcomes, retention |
| Personalization | $9,000 | $5 | +40% engagement |
| Enhanced Telegram | $6,000 | $0 | +30% satisfaction |
| **Total** | **$42,000** | **$40/mo** | **Significant growth** |

**ROI Timeline:** 6-9 months

---

## 📚 Technical Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | Next.js 14, React 18 | Web application |
| UI Library | shadcn/ui, Tailwind | Components, styling |
| State Management | Zustand, React Query | Client state, server cache |
| Charts | Recharts | Data visualization |
| Auth | Telegram Login Widget | Authentication |
| Deployment | Vercel | Hosting, CI/CD |

---

**Next Actions:**
1. Review and prioritize phases
2. Allocate development team
3. Set up project board
4. Begin Phase 1: Web UI
5. Weekly demos and feedback

**Document Owner:** Product Team
**Last Updated:** December 7, 2025
