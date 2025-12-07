# Refactoring & Technical Debt Roadmap

**Project:** Mluv.Me
**Last Updated:** December 7, 2025
**Status:** Ready for Implementation
**Expected Timeline:** 6-8 weeks
**Priority:** MEDIUM

---

## 📊 Executive Summary

This roadmap addresses technical debt and implements code quality improvements to ensure long-term maintainability and scalability. Focus areas include:
- **Code Organization** - Clean Architecture refinement
- **Type Safety** - Complete type coverage
- **Configuration Management** - Environment-based configs
- **API Versioning** - Future-proof API design
- **Documentation** - Comprehensive project docs

**Expected Outcomes:**
- 50% reduction in bugs
- 30% faster onboarding for new developers
- Improved code maintainability
- Better testability

---

## 🎯 Goals & Success Metrics

### Primary Goals
1. Achieve 100% type hint coverage
2. Eliminate all hardcoded values
3. Implement proper API versioning
4. Organize code by domain
5. Complete comprehensive documentation

### Key Metrics
| Metric | Current | Target |
|--------|---------|--------|
| Type Coverage | ~60% | 100% |
| Code Duplication | ~15% | <5% |
| Cyclomatic Complexity | Med-High | Low-Med |
| Documentation Coverage | ~40% | 90% |
| Linter Warnings | 50+ | 0 |

---

## 🏗️ Phase 1: Code Organization & Architecture (3 weeks)

### Priority: HIGH
**Impact:** Developer productivity, code maintainability
**Effort:** 3 weeks

### 1.1 Domain-Driven Design Structure

#### Task 1.1.1: Reorganize Project Structure
**Duration:** 5 days

**Current Structure:**
```
backend/
  models/
    user.py
    message.py
    stats.py
    word.py
  services/
    correction_engine.py
    gamification.py
    honzik_personality.py
    openai_client.py
  routers/
    lesson.py
    stats.py
    users.py
    words.py
```

**Proposed DDD Structure:**
```
backend/
  domain/
    # User Domain
    user/
      models/
        user.py
        user_settings.py
        session.py
      services/
        user_service.py
        auth_service.py
      repositories/
        user_repository.py
      schemas/
        user_schemas.py
      routers/
        user_router.py

    # Learning Domain
    learning/
      models/
        message.py
        proficiency.py
        exercise.py
      services/
        correction_engine.py
        honzik_personality.py
        adaptive_learning.py
      repositories/
        message_repository.py
        proficiency_repository.py
      schemas/
        lesson_schemas.py
      routers/
        lesson_router.py

    # Gamification Domain
    gamification/
      models/
        stats.py
        stars.py
        achievement.py
      services/
        gamification_service.py
        challenge_service.py
      repositories/
        stats_repository.py
      schemas/
        stats_schemas.py
      routers/
        stats_router.py

    # Vocabulary Domain
    vocabulary/
      models/
        saved_word.py
      services/
        srs_service.py
        word_service.py
      repositories/
        word_repository.py
      schemas/
        word_schemas.py
      routers/
        word_router.py

  # Shared Infrastructure
  infrastructure/
    database/
      database.py
      base_repository.py
    cache/
      redis_client.py
      cache_service.py
    messaging/
      email_service.py
      notification_service.py
    external/
      openai_client.py
      stripe_client.py

  # Application Layer
  api/
    dependencies.py
    middleware/
    exceptions.py

  config.py
  main.py
```

**Migration Script:**
```python
# scripts/migrate_to_ddd.py

import os
import shutil
from pathlib import Path

def migrate_to_ddd():
    """Migrate existing structure to DDD"""

    # Create new directory structure
    domains = ['user', 'learning', 'gamification', 'vocabulary']
    subdirs = ['models', 'services', 'repositories', 'schemas', 'routers']

    for domain in domains:
        for subdir in subdirs:
            Path(f'backend/domain/{domain}/{subdir}').mkdir(
                parents=True,
                exist_ok=True
            )

    # Create __init__.py files
    # ... (implementation details)

    # Move files to new locations
    file_mapping = {
        'backend/models/user.py': 'backend/domain/user/models/user.py',
        'backend/services/gamification.py': 'backend/domain/gamification/services/gamification_service.py',
        # ... complete mapping
    }

    for old_path, new_path in file_mapping.items():
        if os.path.exists(old_path):
            shutil.move(old_path, new_path)
            print(f'Moved: {old_path} -> {new_path}')

    # Update imports
    update_imports()

def update_imports():
    """Update all import statements"""
    # Use tools like rope or automated refactoring
    pass

if __name__ == '__main__':
    migrate_to_ddd()
```

**Acceptance Criteria:**
- [ ] New directory structure created
- [ ] All files migrated
- [ ] Imports updated throughout project
- [ ] Tests still passing
- [ ] Documentation updated

### 1.2 Configuration Management

#### Task 1.2.1: Environment-Based Configuration
**Duration:** 3 days

```python
# backend/config/base.py

from pydantic_settings import BaseSettings
from typing import Optional

class BaseConfig(BaseSettings):
    """Base configuration shared across environments"""

    # Application
    APP_NAME: str = "Mluv.Me"
    APP_VERSION: str = "1.0.0"

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_RECYCLE: int = 3600

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_ORG_ID: Optional[str] = None

    # Telegram
    TELEGRAM_BOT_TOKEN: str

    # Security
    SECRET_KEY: str
    ENCRYPTION_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = True
```

```python
# backend/config/development.py

from backend.config.base import BaseConfig

class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""

    DEBUG: bool = True
    TESTING: bool = False

    # Logging
    LOG_LEVEL: str = "DEBUG"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000"
    ]

    # Cache
    CACHE_ENABLED: bool = True
    CACHE_TTL_DEFAULT: int = 300  # Shorter for dev

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = False
```

```python
# backend/config/production.py

from backend.config.base import BaseConfig

class ProductionConfig(BaseConfig):
    """Production environment configuration"""

    DEBUG: bool = False
    TESTING: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"

    # CORS
    CORS_ORIGINS: list[str] = [
        "https://mluv.me",
        "https://app.mluv.me"
    ]

    # Cache
    CACHE_ENABLED: bool = True
    CACHE_TTL_DEFAULT: int = 3600

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # Security
    SECURE_SSL_REDIRECT: bool = True
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "strict"
```

```python
# backend/config/__init__.py

import os
from backend.config.base import BaseConfig
from backend.config.development import DevelopmentConfig
from backend.config.production import ProductionConfig
from backend.config.testing import TestingConfig

def get_settings() -> BaseConfig:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development")

    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }

    config_class = config_map.get(env, DevelopmentConfig)
    return config_class()

settings = get_settings()
```

**Acceptance Criteria:**
- [ ] Separate configs for each environment
- [ ] No hardcoded values in code
- [ ] Environment variable validation
- [ ] Easy to switch environments
- [ ] Secure secret management

### 1.3 API Versioning

#### Task 1.3.1: Implement API Versioning Strategy
**Duration:** 4 days

```python
# backend/api/v1/__init__.py

from fastapi import APIRouter
from backend.domain.user.routers import user_router
from backend.domain.learning.routers import lesson_router
from backend.domain.gamification.routers import stats_router
from backend.domain.vocabulary.routers import word_router

api_v1_router = APIRouter(prefix="/api/v1")

# Register all v1 routes
api_v1_router.include_router(
    user_router.router,
    prefix="/users",
    tags=["users"]
)

api_v1_router.include_router(
    lesson_router.router,
    prefix="/lessons",
    tags=["lessons"]
)

api_v1_router.include_router(
    stats_router.router,
    prefix="/stats",
    tags=["statistics"]
)

api_v1_router.include_router(
    word_router.router,
    prefix="/words",
    tags=["vocabulary"]
)
```

```python
# backend/api/versioning.py

from fastapi import Header, HTTPException
from typing import Optional

class APIVersion:
    """API version management"""

    SUPPORTED_VERSIONS = ["1", "2"]
    DEFAULT_VERSION = "1"

    @staticmethod
    def get_version_from_header(
        api_version: Optional[str] = Header(None, alias="X-API-Version")
    ) -> str:
        """Extract and validate API version from header"""

        version = api_version or APIVersion.DEFAULT_VERSION

        if version not in APIVersion.SUPPORTED_VERSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported API version. Supported: {', '.join(APIVersion.SUPPORTED_VERSIONS)}"
            )

        return version

# Usage in endpoints
@router.get("/lessons/history")
async def get_lesson_history(
    api_version: str = Depends(APIVersion.get_version_from_header)
):
    """Get lesson history (version-aware endpoint)"""

    if api_version == "1":
        return await get_history_v1()
    elif api_version == "2":
        return await get_history_v2()
```

```python
# backend/main.py

from fastapi import FastAPI
from backend.api.v1 import api_v1_router
from backend.api.v2 import api_v2_router  # Future

app = FastAPI(
    title="Mluv.Me API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Register versioned routers
app.include_router(api_v1_router)
# app.include_router(api_v2_router)  # When ready

# Version-specific OpenAPI schemas
@app.get("/openapi/v1.json")
async def get_v1_openapi():
    """Get OpenAPI schema for v1"""
    return api_v1_router.openapi()
```

**Acceptance Criteria:**
- [ ] URL-based versioning working
- [ ] Header-based versioning optional
- [ ] Separate OpenAPI docs per version
- [ ] Deprecation warnings for old versions
- [ ] Version negotiation working

---

## 🔧 Phase 2: Code Quality & Type Safety (2 weeks)

### Priority: HIGH
**Impact:** Bug reduction, IDE support
**Effort:** 2 weeks

### 2.1 Complete Type Hints

#### Task 2.1.1: Add Missing Type Hints
**Duration:** 5 days

```python
# Example: backend/services/correction_engine.py

from typing import Dict, List, Optional, Any, Tuple
from backend.domain.learning.models.message import Message
from backend.domain.user.models.user_settings import UserSettings

class CorrectionEngine:
    """AI-powered Czech language correction engine"""

    def __init__(self, openai_client: OpenAIClient) -> None:
        self.openai_client = openai_client

    async def process_honzik_response(
        self,
        response: Dict[str, Any],
        user_text: str
    ) -> Dict[str, Any]:
        """Process Honzík's response and extract corrections"""

        return {
            "honzik_response": str(response.get("honzik_response", "")),
            "user_mistakes": list(response.get("user_mistakes", [])),
            "suggestions": list(response.get("suggestions", [])),
            "correctness_score": int(response.get("correctness_score", 0))
        }

    async def analyze_message(
        self,
        user_text: str,
        settings: UserSettings,
        history: List[Message]
    ) -> Tuple[str, List[str], int]:
        """
        Analyze user message and return corrections

        Args:
            user_text: User's Czech message
            settings: User's learning settings
            history: Previous conversation messages

        Returns:
            Tuple of (response_text, mistakes, score)
        """
        response = await self._call_gpt4(user_text, settings, history)
        processed = await self.process_honzik_response(response, user_text)

        return (
            processed["honzik_response"],
            processed["user_mistakes"],
            processed["correctness_score"]
        )
```

**Type Checking with mypy:**
```bash
# Run mypy on entire project
mypy backend/ --strict

# Configuration in pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
disallow_subclassing_any = true
disallow_untyped_calls = true
disallow_untyped_decorators = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
```

**Acceptance Criteria:**
- [ ] mypy --strict passes with 0 errors
- [ ] All functions have type hints
- [ ] All class attributes typed
- [ ] Generic types used appropriately
- [ ] Type stubs for external libraries

### 2.2 Remove Hardcoded Values

#### Task 2.2.1: Extract Constants
**Duration:** 2 days

```python
# backend/domain/learning/constants.py

from enum import Enum

class CzechLevel(str, Enum):
    """Czech proficiency levels"""
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

class CorrectionLevel(str, Enum):
    """Correction detail levels"""
    MINIMAL = "minimal"
    MODERATE = "moderate"
    DETAILED = "detailed"

class MessageLimits:
    """Message-related limits and defaults"""
    HISTORY_LIMIT_DEFAULT = 10
    HISTORY_LIMIT_MAX = 100
    MAX_MESSAGE_LENGTH = 5000
    MAX_AUDIO_SIZE_MB = 10

    @classmethod
    def get_history_limit(cls, user_tier: str) -> int:
        """Get history limit based on user tier"""
        limits = {
            "free": 10,
            "pro": 50,
            "expert": 100
        }
        return limits.get(user_tier, cls.HISTORY_LIMIT_DEFAULT)

class OpenAIModels:
    """OpenAI model identifiers"""
    GPT_4O = "gpt-4o"
    GPT_35_TURBO = "gpt-3.5-turbo"
    WHISPER = "whisper-1"
    TTS = "tts-1"

    @classmethod
    def get_analysis_model(cls, czech_level: CzechLevel) -> str:
        """Select appropriate model based on level"""
        if czech_level in [CzechLevel.A1, CzechLevel.A2]:
            return cls.GPT_35_TURBO
        return cls.GPT_4O

class HonzikPersonalities:
    """Honzík personality types"""
    ENCOURAGING = "encouraging"
    STRICT = "strict"
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
```

**Usage:**
```python
# Before (hardcoded)
messages = await message_repo.get_recent_by_user(user_id, limit=10)

# After (using constant)
from backend.domain.learning.constants import MessageLimits

limit = MessageLimits.get_history_limit(user.subscription.tier)
messages = await message_repo.get_recent_by_user(user_id, limit=limit)
```

**Acceptance Criteria:**
- [ ] All magic numbers extracted
- [ ] All hardcoded strings in constants
- [ ] Enums for fixed sets of values
- [ ] Configuration for environment-specific values
- [ ] No grep results for TODO or FIXME

### 2.3 Error Handling Improvements

#### Task 2.3.1: Standardized Exception Hierarchy
**Duration:** 3 days

```python
# backend/api/exceptions.py

from typing import Optional, Dict, Any

class MluvMeException(Exception):
    """Base exception for all Mluv.Me errors"""

    def __init__(
        self,
        message: str,
        code: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

# Domain-specific exceptions
class UserException(MluvMeException):
    """User-related errors"""
    pass

class UserNotFoundException(UserException):
    """User not found"""
    def __init__(self, user_id: int):
        super().__init__(
            message=f"User {user_id} not found",
            code="USER_NOT_FOUND",
            details={"user_id": user_id}
        )

class LearningException(MluvMeException):
    """Learning/lesson-related errors"""
    pass

class MessageLimitExceededException(LearningException):
    """Daily message limit exceeded"""
    def __init__(self, limit: int):
        super().__init__(
            message=f"Daily message limit of {limit} exceeded",
            code="MESSAGE_LIMIT_EXCEEDED",
            details={"limit": limit}
        )

class PaymentException(MluvMeException):
    """Payment-related errors"""
    pass

class SubscriptionRequiredException(PaymentException):
    """Feature requires active subscription"""
    def __init__(self, feature: str, required_tier: str):
        super().__init__(
            message=f"{feature} requires {required_tier} subscription",
            code="SUBSCRIPTION_REQUIRED",
            details={
                "feature": feature,
                "required_tier": required_tier
            }
        )

# External service exceptions
class ExternalServiceException(MluvMeException):
    """External service errors"""
    pass

class OpenAIException(ExternalServiceException):
    """OpenAI API errors"""
    pass

class StripeException(ExternalServiceException):
    """Stripe API errors"""
    pass
```

```python
# backend/api/middleware/error_handler.py

from fastapi import Request, status
from fastapi.responses import JSONResponse
from backend.api.exceptions import MluvMeException

async def error_handler_middleware(request: Request, call_next):
    """Global error handling middleware"""

    try:
        response = await call_next(request)
        return response

    except MluvMeException as exc:
        # Application-specific errors
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )

    except Exception as exc:
        # Unexpected errors
        logger.exception("Unexpected error", exc_info=exc)

        if settings.DEBUG:
            # Include stack trace in development
            import traceback
            trace = traceback.format_exc()
        else:
            trace = None

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "trace": trace
                }
            }
        )
```

**Acceptance Criteria:**
- [ ] Exception hierarchy defined
- [ ] All exceptions inherit from base
- [ ] Consistent error responses
- [ ] Proper HTTP status codes
- [ ] Error details included

---

## 📝 Phase 3: Documentation & Standards (2 weeks)

### Priority: MEDIUM
**Impact:** Developer onboarding, maintenance
**Effort:** 2 weeks

### 3.1 Code Documentation

#### Task 3.1.1: Docstring Standards
**Duration:** 5 days

```python
# backend/domain/learning/services/correction_engine.py

from typing import Dict, List
from backend.domain.learning.models.message import Message

class CorrectionEngine:
    """
    AI-powered Czech language correction engine.

    This service handles all interactions with the OpenAI API for
    analyzing user messages, providing corrections, and generating
    Honzík's personality-driven responses.

    Attributes:
        openai_client: Client for OpenAI API interactions
        cache_service: Service for caching responses

    Example:
        >>> engine = CorrectionEngine(openai_client)
        >>> response = await engine.analyze_message(
        ...     user_text="Já jsem Czech učit",
        ...     settings=user_settings,
        ...     history=[]
        ... )
        >>> print(response["correctness_score"])
        65
    """

    def __init__(
        self,
        openai_client: OpenAIClient,
        cache_service: Optional[CacheService] = None
    ) -> None:
        """
        Initialize the correction engine.

        Args:
            openai_client: Configured OpenAI API client
            cache_service: Optional cache service for response caching
        """
        self.openai_client = openai_client
        self.cache_service = cache_service

    async def analyze_message(
        self,
        user_text: str,
        settings: UserSettings,
        history: List[Message]
    ) -> Dict[str, Any]:
        """
        Analyze user's Czech message and provide corrections.

        This method:
        1. Checks cache for previous similar analysis
        2. Constructs conversation context from history
        3. Calls GPT-4o with Honzík personality prompt
        4. Extracts mistakes and calculates correctness score
        5. Caches the response for future use

        Args:
            user_text: The Czech text to analyze (max 5000 chars)
            settings: User's learning preferences and level
            history: Previous messages for context (max 10)

        Returns:
            Dictionary containing:
            - honzik_response (str): Honzík's reply
            - user_mistakes (List[str]): List of identified mistakes
            - suggestions (List[str]): Improvement suggestions
            - correctness_score (int): Score from 0-100

        Raises:
            OpenAIException: If API call fails
            ValueError: If user_text is empty or too long

        Example:
            >>> result = await engine.analyze_message(
            ...     user_text="Dobrý den, jak se máte?",
            ...     settings=UserSettings(czech_level="A2"),
            ...     history=[]
            ... )
            >>> print(result["correctness_score"])
            95
        """
        # Implementation...
```

**Documentation Generator:**
```bash
# Generate API documentation
pdoc backend --html --output-dir docs/api

# Configuration in pyproject.toml
[tool.pdoc]
docformat = "google"
```

**Acceptance Criteria:**
- [ ] All public methods documented
- [ ] Google-style docstrings
- [ ] Examples in docstrings
- [ ] Type hints match docs
- [ ] Auto-generated API docs

### 3.2 Architecture Documentation

#### Task 3.2.1: ADR (Architecture Decision Records)
**Duration:** 3 days

```markdown
# docs/architecture/decisions/0001-use-fastapi-framework.md

# 1. Use FastAPI as Web Framework

**Date:** 2025-01-15
**Status:** Accepted
**Deciders:** Development Team

## Context

We need a modern, high-performance web framework for our language learning platform that:
- Supports async/await for concurrent request handling
- Provides automatic API documentation
- Has strong type checking with Python type hints
- Offers good developer experience

## Decision

We will use FastAPI as our primary web framework.

## Rationale

**Pros:**
- Built-in async support for high concurrency
- Automatic OpenAPI/Swagger documentation
- Pydantic integration for request/response validation
- Excellent performance (comparable to Node.js and Go)
- Active community and good documentation
- Type hint-based development with IDE support

**Cons:**
- Smaller ecosystem compared to Flask/Django
- Learning curve for developers new to async Python
- Less mature than older frameworks

## Alternatives Considered

### Flask
- More mature ecosystem
- Simpler learning curve
- But: Limited async support, manual validation

### Django
- Comprehensive "batteries included"
- Admin panel out of the box
- But: Heavier, opinionated, not async-first

### Starlette (FastAPI's foundation)
- More lightweight
- But: Less structure, no automatic docs

## Consequences

**Positive:**
- Fast development with auto-generated docs
- Type safety reduces bugs
- Good performance for AI API calls

**Negative:**
- Team needs async/await training
- Some third-party integrations may lack async support

## Implementation Notes

- Use `async def` for all route handlers
- Leverage Pydantic models for validation
- Enable OpenAPI docs at `/docs`
```

**Template for New ADRs:**
```markdown
# docs/architecture/decisions/NNNN-title.md

# N. [Short title of solved problem]

**Date:** YYYY-MM-DD
**Status:** [Proposed | Accepted | Deprecated | Superseded]
**Deciders:** [List of people involved]

## Context
[What is the issue that we're seeing that is motivating this decision?]

## Decision
[What is the change that we're proposing and/or doing?]

## Rationale
[Why did we choose this option?]

## Alternatives Considered
[What other options did we look at?]

## Consequences
[What becomes easier or more difficult to do because of this change?]

## Implementation Notes
[Any specific details about how to implement this decision]
```

**Acceptance Criteria:**
- [ ] ADRs for major decisions created
- [ ] Template for new ADRs
- [ ] Index of all ADRs
- [ ] Decision review process

### 3.3 API Documentation

#### Task 3.3.1: Enhanced OpenAPI Schemas
**Duration:** 2 days

```python
# backend/api/v1/__init__.py

from fastapi import APIRouter

api_v1_router = APIRouter(
    prefix="/api/v1",
    responses={
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": "Request validation failed",
                            "details": {"field": "value"}
                        }
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "UNAUTHORIZED",
                            "message": "Authentication required"
                        }
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "INTERNAL_ERROR",
                            "message": "An unexpected error occurred"
                        }
                    }
                }
            }
        }
    }
)
```

```python
# backend/domain/learning/routers/lesson_router.py

@router.post(
    "/process",
    response_model=LessonProcessResponse,
    status_code=status.HTTP_200_OK,
    summary="Process voice/text lesson",
    description="""
    Process a user's Czech language message (voice or text) and receive
    feedback from Honzík, our AI language tutor.

    **Process:**
    1. Transcribe audio (if voice message)
    2. Analyze Czech language correctness
    3. Generate personalized feedback
    4. Calculate stars earned
    5. Update user statistics

    **Rate Limits:**
    - Free tier: 5 requests per day
    - Pro tier: Unlimited

    **Response Time:** Typically 3-8 seconds
    """,
    responses={
        200: {
            "description": "Lesson processed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "honzik_text": "Skvěle! Your Czech is improving.",
                        "user_mistakes": ["'do školy' → 'do školy' (correct!)"],
                        "suggestions": ["Try using more past tense"],
                        "stars_earned": 15,
                        "correctness_score": 85
                    }
                }
            }
        },
        402: {
            "description": "Payment Required - Daily limit reached",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "MESSAGE_LIMIT_EXCEEDED",
                            "message": "Daily limit of 5 messages reached",
                            "details": {
                                "limit": 5,
                                "upgrade_url": "/subscription"
                            }
                        }
                    }
                }
            }
        }
    },
    tags=["lessons"]
)
async def process_lesson(...):
    """Implementation..."""
```

**Acceptance Criteria:**
- [ ] All endpoints documented
- [ ] Request/response examples
- [ ] Error responses documented
- [ ] Rate limits specified
- [ ] Authentication requirements clear

---

## 🧹 Phase 4: Code Cleanup & Standards (1 week)

### Priority: LOW
**Impact:** Code consistency
**Effort:** 1 week

### 4.1 Linting & Formatting

#### Task 4.1.1: Setup Pre-commit Hooks
**Duration:** 2 days

```yaml
# .pre-commit-config.yaml

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [
          "--max-line-length=100",
          "--extend-ignore=E203,W503"
        ]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: ["--strict"]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.6
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
```

```toml
# pyproject.toml

[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3

[tool.flake8]
max-line-length = 100
extend-ignore = ["E203", "W503"]
exclude = [".git", "__pycache__", "venv"]

[tool.bandit]
exclude_dirs = ["tests", "venv"]
skips = ["B101"]  # Skip assert_used in tests
```

**Installation:**
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

**Acceptance Criteria:**
- [ ] Pre-commit hooks installed
- [ ] All checks passing
- [ ] CI/CD integration
- [ ] Team trained on tools

---

## 📊 Success Metrics

### Code Quality Metrics (Track Weekly)
- **Type Coverage:** mypy --strict passing
- **Test Coverage:** > 80%
- **Linter Warnings:** 0
- **Code Duplication:** < 5%
- **Cyclomatic Complexity:** < 10 (average)

### Development Metrics
- **Build Time:** < 2 minutes
- **Test Suite Time:** < 5 minutes
- **New Developer Onboarding:** < 2 days
- **Bug Resolution Time:** < 24 hours

---

## 🚀 Implementation Timeline

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1-2 | DDD Structure | New folder structure, file migration |
| 3 | Configuration | Environment configs, settings management |
| 4 | Type Safety | Complete type hints, mypy passing |
| 5 | Error Handling | Exception hierarchy, error middleware |
| 6-7 | Documentation | Docstrings, ADRs, API docs |
| 8 | Code Cleanup | Linting, formatting, pre-commit hooks |

---

## 💰 Cost-Benefit Analysis

### Development Cost
- **Effort:** 6-8 weeks (1 developer full-time)
- **Cost:** ~$12,000-16,000

### Benefits
- **50% fewer bugs** → Saves ~10 hours/week debugging
- **30% faster feature development** → Better architecture
- **Faster onboarding** → New developers productive in 2 days vs 1 week
- **Better maintainability** → Long-term technical debt reduction

### ROI
- **Payback Period:** 3-4 months
- **Annual Savings:** ~$30,000 in developer time

---

**Next Steps:**
1. Prioritize refactoring tasks
2. Allocate development time
3. Set up tracking for metrics
4. Begin Phase 1: DDD Migration
5. Weekly progress reviews

**Document Owner:** Engineering Team
**Last Updated:** December 7, 2025
