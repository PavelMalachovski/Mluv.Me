"""
Router for language learning mini-games.

Endpoints для мини-игр.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.services.game_service import GameService, GAMES
from backend.services.openai_client import OpenAIClient
from backend.config import Settings, get_settings

router = APIRouter(prefix="/api/v1/games", tags=["games"])


# === Pydantic Models ===

class GameInfo(BaseModel):
    """Информация об игре."""
    id: str
    name_cs: str
    name_ru: str
    description_cs: str
    description_ru: str
    reward_stars: int
    time_limit_seconds: int


class StartGameRequest(BaseModel):
    """Запрос на начало игры."""
    user_id: int = Field(..., description="ID пользователя")
    level: str = Field("beginner", description="Уровень сложности")


class StartGameResponse(BaseModel):
    """Ответ на начало игры."""
    game_id: str
    game_type: str
    name_cs: str
    question: dict
    time_limit_seconds: int
    reward_stars: int


class SubmitAnswerRequest(BaseModel):
    """Запрос на отправку ответа."""
    user_id: int = Field(..., description="ID пользователя")
    answer: str = Field(..., description="Ответ пользователя")


class SubmitAnswerResponse(BaseModel):
    """Результат игры."""
    is_correct: bool
    correct_answer: str
    user_answer: str
    stars_earned: int
    base_stars: int
    bonus_stars: int
    time_seconds: float
    time_bonus_percent: int


class LeaderboardEntry(BaseModel):
    """Запись в лидерборде."""
    user_id: int
    total_stars: int
    games_played: int
    best_time: float


# === Dependencies ===

def get_openai_client(settings: Annotated[Settings, Depends(get_settings)]) -> OpenAIClient:
    """Get OpenAI client."""
    return OpenAIClient(settings)


def get_game_service(
    openai_client: Annotated[OpenAIClient, Depends(get_openai_client)]
) -> GameService:
    """Get game service."""
    return GameService(openai_client)


# === Endpoints ===

@router.get("/available", response_model=list[GameInfo])
async def get_available_games(
    game_service: GameService = Depends(get_game_service),
):
    """
    Получить список всех доступных игр.
    """
    return game_service.get_available_games()


@router.get("/{game_type}")
async def get_game_details(game_type: str):
    """
    Получить детальную информацию об игре.
    """
    if game_type not in GAMES:
        raise HTTPException(status_code=404, detail="Game not found")

    game = GAMES[game_type]
    return {
        "id": game_type,
        **game,
    }


@router.post("/start/{game_type}", response_model=StartGameResponse)
async def start_game(
    game_type: str,
    request: StartGameRequest,
    game_service: GameService = Depends(get_game_service),
):
    """
    Начать новую игру.
    """
    try:
        result = await game_service.start_game(
            user_id=request.user_id,
            game_type=game_type,
            level=request.level,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/submit", response_model=SubmitAnswerResponse)
async def submit_answer(
    request: SubmitAnswerRequest,
    game_service: GameService = Depends(get_game_service),
):
    """
    Отправить ответ на текущую игру.
    """
    try:
        result = await game_service.submit_answer(
            user_id=request.user_id,
            answer=request.answer,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/leaderboard/{game_type}", response_model=list[LeaderboardEntry])
async def get_leaderboard(
    game_type: str,
    limit: int = Query(10, le=100),
    game_service: GameService = Depends(get_game_service),
):
    """
    Получить лидерборд для игры.
    """
    if game_type not in GAMES:
        raise HTTPException(status_code=404, detail="Game not found")

    return game_service.get_leaderboard(game_type, limit)


@router.delete("/cancel/{user_id}")
async def cancel_game(
    user_id: int,
    game_service: GameService = Depends(get_game_service),
):
    """
    Отменить активную игру.
    """
    cancelled = game_service.cancel_game(user_id)
    if not cancelled:
        raise HTTPException(status_code=404, detail="No active game to cancel")

    return {"status": "cancelled"}
