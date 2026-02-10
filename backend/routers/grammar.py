"""
Router for grammar rules API.

Provides endpoints for:
- Browsing grammar rules and categories
- Getting daily rule for a user
- User grammar progress
"""

import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_session
from backend.db.grammar_repository import GrammarRepository
from backend.services.grammar_service import GrammarService

router = APIRouter(prefix="/api/v1/grammar", tags=["grammar"])


# === Pydantic Models ===


class GrammarRuleResponse(BaseModel):
    """Grammar rule response."""
    id: int
    code: str
    category: str
    subcategory: str | None = None
    level: str
    title_cs: str
    rule_cs: str
    explanation_cs: str | None = None
    examples: list[dict[str, Any]] | None = None
    mnemonic: str | None = None
    common_mistakes: list[dict[str, Any]] | None = None
    source_ref: str | None = None


class CategoryResponse(BaseModel):
    """Category info."""
    category: str
    count: int


class DailyRuleResponse(BaseModel):
    """Daily rule for user."""
    rule: GrammarRuleResponse | None = None
    message: str | None = None


class ProgressSummary(BaseModel):
    """User grammar progress summary."""
    total_rules: int
    practiced_rules: int
    mastered_rules: int
    weak_rules: int
    average_accuracy: float


class RuleProgressResponse(BaseModel):
    """Progress on a single rule."""
    rule_id: int
    rule_code: str
    rule_title: str
    times_shown: int
    times_practiced: int
    mastery_level: int
    correct_count: int
    incorrect_count: int
    accuracy: float


# === Dependencies ===


def get_grammar_service(
    session: AsyncSession = Depends(get_session),
) -> GrammarService:
    """Create GrammarService with repository."""
    repo = GrammarRepository(session)
    return GrammarService(grammar_repo=repo)


# === Endpoints ===


@router.get("/categories", response_model=list[CategoryResponse])
async def get_categories(
    service: GrammarService = Depends(get_grammar_service),
) -> list[CategoryResponse]:
    """Get all grammar rule categories with counts."""
    categories = await service.grammar_repo.get_all_categories()
    return [CategoryResponse(**c) for c in categories]


@router.get("/rules", response_model=list[GrammarRuleResponse])
async def get_rules(
    service: GrammarService = Depends(get_grammar_service),
    category: str | None = Query(None, description="Filter by category"),
    level: str | None = Query(None, description="Filter by level: A1, A2, B1, B2"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[GrammarRuleResponse]:
    """Get grammar rules with optional filters."""
    rules = await service.grammar_repo.get_rules_by_category(
        category=category,
        level=level,
        limit=limit,
        offset=offset,
    )
    return [
        GrammarRuleResponse(
            id=r.id,
            code=r.code,
            category=r.category,
            subcategory=r.subcategory,
            level=r.level,
            title_cs=r.title_cs,
            rule_cs=r.rule_cs,
            explanation_cs=r.explanation_cs,
            examples=json.loads(r.examples) if r.examples else None,
            mnemonic=r.mnemonic,
            common_mistakes=json.loads(r.common_mistakes) if r.common_mistakes else None,
            source_ref=r.source_ref,
        )
        for r in rules
    ]


@router.get("/rules/count")
async def get_rules_count(
    service: GrammarService = Depends(get_grammar_service),
    category: str | None = Query(None),
    level: str | None = Query(None),
) -> dict[str, int]:
    """Get total count of grammar rules."""
    count = await service.grammar_repo.count_rules(category=category, level=level)
    return {"count": count}


@router.get("/rules/{rule_id}", response_model=GrammarRuleResponse)
async def get_rule(
    rule_id: int,
    service: GrammarService = Depends(get_grammar_service),
) -> GrammarRuleResponse:
    """Get a specific grammar rule by ID."""
    rule = await service.grammar_repo.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Pravidlo nenalezeno")
    return GrammarRuleResponse(
        id=rule.id,
        code=rule.code,
        category=rule.category,
        subcategory=rule.subcategory,
        level=rule.level,
        title_cs=rule.title_cs,
        rule_cs=rule.rule_cs,
        explanation_cs=rule.explanation_cs,
        examples=json.loads(rule.examples) if rule.examples else None,
        mnemonic=rule.mnemonic,
        common_mistakes=json.loads(rule.common_mistakes) if rule.common_mistakes else None,
        source_ref=rule.source_ref,
    )


@router.get("/daily-rule/{user_id}", response_model=DailyRuleResponse)
async def get_daily_rule(
    user_id: int,
    service: GrammarService = Depends(get_grammar_service),
) -> DailyRuleResponse:
    """Get today's grammar rule for a user (prioritizes unseen/weak rules)."""
    rule_data = await service.get_daily_rule(user_id)
    if not rule_data:
        return DailyRuleResponse(message="Žádná pravidla k zobrazení")

    rule = await service.grammar_repo.get_rule_by_id(rule_data["rule_id"])
    if not rule:
        return DailyRuleResponse(message="Pravidlo nenalezeno")

    return DailyRuleResponse(
        rule=GrammarRuleResponse(
            id=rule.id,
            code=rule.code,
            category=rule.category,
            subcategory=rule.subcategory,
            level=rule.level,
            title_cs=rule.title_cs,
            rule_cs=rule.rule_cs,
            explanation_cs=rule.explanation_cs,
            examples=json.loads(rule.examples) if rule.examples else None,
            mnemonic=rule.mnemonic,
            common_mistakes=json.loads(rule.common_mistakes) if rule.common_mistakes else None,
            source_ref=rule.source_ref,
        ),
    )


@router.get("/progress/{user_id}", response_model=ProgressSummary)
async def get_progress(
    user_id: int,
    service: GrammarService = Depends(get_grammar_service),
) -> ProgressSummary:
    """Get user's grammar progress summary."""
    summary = await service.get_progress_summary(user_id)
    return ProgressSummary(**summary)


@router.get("/progress/{user_id}/details", response_model=list[RuleProgressResponse])
async def get_progress_details(
    user_id: int,
    service: GrammarService = Depends(get_grammar_service),
) -> list[RuleProgressResponse]:
    """Get detailed per-rule progress for a user."""
    progress_list = await service.grammar_repo.get_user_progress(user_id)
    results = []
    for p in progress_list:
        rule = await service.grammar_repo.get_rule_by_id(p.grammar_rule_id)
        if rule:
            results.append(
                RuleProgressResponse(
                    rule_id=rule.id,
                    rule_code=rule.code,
                    rule_title=rule.title_cs,
                    times_shown=p.times_shown,
                    times_practiced=p.times_practiced,
                    mastery_level=p.mastery_level,
                    correct_count=p.correct_count,
                    incorrect_count=p.incorrect_count,
                    accuracy=p.accuracy,
                )
            )
    return results


# === Admin endpoint for seeding (temporary) ===

@router.post("/admin/seed")
async def seed_grammar_rules_endpoint(
    session: AsyncSession = Depends(get_session),
    secret: str = Query(..., description="Admin secret key"),
) -> dict:
    """
    Seed grammar rules from the built-in data.
    Requires admin secret key for security.
    """
    import os
    admin_secret = os.getenv("ADMIN_SECRET", "mluv-seed-2026")
    
    if secret != admin_secret:
        raise HTTPException(status_code=403, detail="Invalid secret")
    
    from backend.models.grammar import GrammarRule
    from backend.data.grammar_seed_data import GRAMMAR_RULES
    from sqlalchemy import select
    
    inserted = 0
    updated = 0
    
    for rule_data in GRAMMAR_RULES:
        # Ensure is_active is set (server_default doesn't apply via ORM)
        rule_data["is_active"] = True
        
        # Check if rule already exists
        result = await session.execute(
            select(GrammarRule).where(GrammarRule.code == rule_data["code"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing rule
            for key, value in rule_data.items():
                if key != "code":
                    setattr(existing, key, value)
            updated += 1
        else:
            # Insert new rule
            rule = GrammarRule(**rule_data)
            session.add(rule)
            inserted += 1
    
    await session.commit()
    
    return {
        "status": "success",
        "inserted": inserted,
        "updated": updated,
        "total_rules": len(GRAMMAR_RULES),
    }
