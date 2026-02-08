"""
Router for role-play scenarios.

Endpoints для управления ролевыми сценариями.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_session
from backend.services.scenario_service import ScenarioService, SCENARIOS
from backend.services.openai_client import OpenAIClient
from backend.config import Settings, get_settings

router = APIRouter(prefix="/api/v1/scenarios", tags=["scenarios"])


# === Pydantic Models ===

class ScenarioInfo(BaseModel):
    """Информация о сценарии."""
    id: str
    name_cs: str
    name_ru: str
    level: str
    steps: int
    reward_stars: int
    is_unlocked: bool
    vocabulary_count: int


class StartScenarioRequest(BaseModel):
    """Запрос на начало сценария."""
    user_id: int = Field(..., description="Telegram ID пользователя")
    level: str = Field("beginner", description="Уровень чешского языка")
    native_language: str = Field("ru", description="Родной язык пользователя")


class StartScenarioResponse(BaseModel):
    """Ответ на начало сценария."""
    scenario_id: str
    name_cs: str
    step: int
    total_steps: int
    honzik_message: str
    honzik_role: str
    user_role: str
    hint: str
    vocabulary: list[str]


class ContinueScenarioRequest(BaseModel):
    """Запрос на продолжение сценария."""
    user_id: int = Field(..., description="Telegram ID пользователя")
    text: str = Field(..., description="Текст пользователя на чешском")
    level: str = Field("beginner", description="Уровень чешского языка")
    native_language: str = Field("ru", description="Родной язык пользователя")


class CorrectionItem(BaseModel):
    """Исправление ошибки."""
    original: str
    corrected: str
    explanation_cs: str


class ContinueScenarioResponse(BaseModel):
    """Ответ на продолжение сценария."""
    scenario_id: str
    step: int
    total_steps: int
    honzik_message: str
    corrections: list[CorrectionItem]
    step_score: int
    hint: str
    is_completed: bool
    final_score: int | None = None
    reward_stars: int | None = None
    achievement: str | None = None


class ActiveScenarioResponse(BaseModel):
    """Информация об активном сценарии."""
    scenario_id: str
    name_cs: str
    step: int
    total_steps: int
    started_at: str
    completed: bool


# === Dependencies ===

def get_openai_client(settings: Annotated[Settings, Depends(get_settings)]) -> OpenAIClient:
    """Get OpenAI client."""
    return OpenAIClient(settings)


def get_scenario_service(
    openai_client: Annotated[OpenAIClient, Depends(get_openai_client)]
) -> ScenarioService:
    """Get scenario service."""
    return ScenarioService(openai_client)


# === Endpoints ===

@router.get("/available", response_model=list[ScenarioInfo])
async def get_available_scenarios(
    level: str = Query("beginner", description="User's Czech level"),
    scenario_service: ScenarioService = Depends(get_scenario_service),
):
    """
    Получить список доступных сценариев.

    Возвращает все сценарии с информацией о доступности для уровня пользователя.
    """
    return scenario_service.get_available_scenarios(level)


@router.get("/{scenario_id}")
async def get_scenario_details(scenario_id: str):
    """
    Получить детальную информацию о сценарии.

    Args:
        scenario_id: ID сценария
    """
    if scenario_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail="Scenario not found")

    scenario = SCENARIOS[scenario_id]
    return {
        "id": scenario_id,
        "name_cs": scenario["name_cs"],
        "name_ru": scenario["name_ru"],
        "level": scenario["level"],
        "situation_cs": scenario["situation_cs"],
        "situation_ru": scenario["situation_ru"],
        "honzik_role": scenario["honzik_role"],
        "user_role": scenario["user_role"],
        "steps": scenario["steps"],
        "vocabulary": scenario["vocabulary"],
        "hints": scenario["hints"],
        "reward_stars": scenario["reward_stars"],
        "success_achievement": scenario["success_achievement"],
    }


@router.post("/start/{scenario_id}", response_model=StartScenarioResponse)
async def start_scenario(
    scenario_id: str,
    request: StartScenarioRequest,
    scenario_service: ScenarioService = Depends(get_scenario_service),
):
    """
    Начать новый сценарий.

    Хонзик начинает диалог в соответствии со своей ролью в сценарии.
    """
    try:
        result = await scenario_service.start_scenario(
            user_id=request.user_id,
            scenario_id=scenario_id,
            user_level=request.level,
            native_language=request.native_language,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/continue", response_model=ContinueScenarioResponse)
async def continue_scenario(
    request: ContinueScenarioRequest,
    scenario_service: ScenarioService = Depends(get_scenario_service),
):
    """
    Продолжить активный сценарий.

    Пользователь отвечает на реплику Хонзика, получает исправления и следующий шаг.
    """
    try:
        result = await scenario_service.continue_scenario(
            user_id=request.user_id,
            user_text=request.text,
            user_level=request.level,
            native_language=request.native_language,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/active/{user_id}", response_model=ActiveScenarioResponse | None)
async def get_active_scenario(
    user_id: int,
    scenario_service: ScenarioService = Depends(get_scenario_service),
):
    """
    Получить активный сценарий пользователя.

    Returns None если нет активного сценария.
    """
    return scenario_service.get_active_scenario(user_id)


@router.delete("/cancel/{user_id}")
async def cancel_scenario(
    user_id: int,
    scenario_service: ScenarioService = Depends(get_scenario_service),
):
    """
    Отменить активный сценарий.

    Прогресс будет потерян.
    """
    cancelled = scenario_service.cancel_scenario(user_id)
    if not cancelled:
        raise HTTPException(status_code=404, detail="No active scenario to cancel")

    return {"status": "cancelled", "message": "Scenario cancelled successfully"}
