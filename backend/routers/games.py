"""
Router for grammar-based mini-games.

5 gramatických her založených na Internetové jazykové příručce.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.services.game_service import GameService, GAMES
from backend.services.grammar_service import GrammarService
from backend.db.grammar_repository import GrammarRepository
from backend.db.database import get_session
from backend.config import Settings, get_settings
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/games", tags=["games"])


# === Pydantic Models ===

class GameInfo(BaseModel):
    """Game information."""
    id: str
    name_cs: str
    description_cs: str
    reward_stars: int
    time_limit_seconds: int


class StartGameRequest(BaseModel):
    """Start game request."""
    user_id: int = Field(..., description="User ID")
    level: str = Field("beginner", description="beginner|intermediate|advanced|native")


class StartGameResponse(BaseModel):
    """Start game response."""
    game_id: str
    game_type: str
    name_cs: str
    question: dict
    time_limit_seconds: int
    reward_stars: int


class SubmitAnswerRequest(BaseModel):
    """Submit answer request."""
    user_id: int = Field(..., description="User ID")
    answer: str = Field(..., description="User answer")


class SubmitAnswerResponse(BaseModel):
    """Game result."""
    is_correct: bool
    correct_answer: str
    user_answer: str
    stars_earned: int
    base_stars: int
    bonus_stars: int
    time_seconds: float
    time_bonus_percent: int


class LeaderboardEntry(BaseModel):
    """Leaderboard entry."""
    user_id: int
    total_stars: int
    games_played: int
    best_time: float


# === Dependencies ===

async def get_game_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GameService:
    """Get game service with grammar support."""
    repo = GrammarRepository(session)
    grammar_service = GrammarService(repo)
    return GameService(grammar_service)


# === Endpoints ===

@router.get("/available", response_model=list[GameInfo])
async def get_available_games(
    game_service: GameService = Depends(get_game_service),
):
    """Get list of available grammar games."""
    return game_service.get_available_games()


@router.get("/{game_type}")
async def get_game_details(game_type: str):
    """Get details about a specific game."""
    if game_type not in GAMES:
        raise HTTPException(status_code=404, detail="Game not found")

    game = GAMES[game_type]
    return {
        "id": game_type,
        "name_cs": game["name_cs"],
        "description_cs": game["description_cs"],
        "reward_stars": game["reward_stars"],
        "time_limit_seconds": game["time_limit_seconds"],
    }


@router.post("/start/{game_type}", response_model=StartGameResponse)
async def start_game(
    game_type: str,
    request: StartGameRequest,
    game_service: GameService = Depends(get_game_service),
):
    """Start a new grammar game."""
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
    """Submit an answer for the active game."""
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
    """Get leaderboard for a game type."""
    if game_type not in GAMES:
        raise HTTPException(status_code=404, detail="Game not found")

    return game_service.get_leaderboard(game_type, limit)


@router.delete("/cancel/{user_id}")
async def cancel_game(
    user_id: int,
    game_service: GameService = Depends(get_game_service),
):
    """Cancel an active game."""
    cancelled = game_service.cancel_game(user_id)
    if not cancelled:
        raise HTTPException(status_code=404, detail="No active game to cancel")

    return {"status": "cancelled"}
