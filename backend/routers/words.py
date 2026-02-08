"""
Saved words endpoints.
Сохраненные слова пользователя.
"""

import structlog
from datetime import date, datetime
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.db.database import get_session
from backend.db.repositories import UserRepository, SavedWordRepository
from backend.schemas.translation import (
    WordTranslationRequest,
    WordTranslationResponse,
    SaveWordRequest,
)
from backend.services.translation_service import TranslationService
from backend.services.spaced_repetition_service import SpacedRepetitionService
from backend.models.word import SavedWord

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/words", tags=["words"])


def get_translation_service() -> TranslationService:
    """Dependency для сервиса перевода."""
    return TranslationService()


@router.get(
    "/{telegram_id}",
    summary="Получить сохраненные слова",
    description="Получить список сохраненных слов пользователя",
)
async def get_saved_words(
    telegram_id: int,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
):
    """
    Получить сохраненные слова пользователя.

    Args:
        telegram_id: Telegram ID пользователя
        limit: Максимальное количество слов
        session: Database session

    Returns:
        Список сохраненных слов

    Raises:
        HTTPException: Если пользователь не найден
    """
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(telegram_id)

    if not user:
        logger.warning("user_not_found", telegram_id=telegram_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_id {telegram_id} not found",
        )

    word_repo = SavedWordRepository(session)
    words = await word_repo.get_by_user_id(user.id, limit=limit)

    return [
        {
            "id": word.id,
            "word_czech": word.word_czech,
            "translation": word.translation,
            "context_sentence": word.context_sentence,
            "phonetics": word.phonetics,
            "times_reviewed": word.times_reviewed,
            "created_at": word.created_at.isoformat() if word.created_at else None,
        }
        for word in words
    ]


@router.post(
    "/{telegram_id}/reset-context",
    summary="Сбросить контекст разговора",
    description="Очистить историю сообщений для нового разговора",
)
async def reset_conversation(
    telegram_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Сбросить контекст разговора пользователя.

    Args:
        telegram_id: Telegram ID пользователя
        session: Database session

    Returns:
        Статус успешности

    Raises:
        HTTPException: Если пользователь не найден
    """
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(telegram_id)

    if not user:
        logger.warning("user_not_found", telegram_id=telegram_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_id {telegram_id} not found",
        )

    # В будущем здесь можно пометить сообщения как "archived"
    # Пока просто возвращаем success
    logger.info("conversation_reset", telegram_id=telegram_id, user_id=user.id)

    return {"status": "success", "message": "Conversation context reset"}


@router.post(
    "",
    summary="Сохранить слово",
    description="Сохранить переведенное слово в словарь пользователя",
)
async def save_word(
    request: SaveWordRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Сохранить слово в словарь пользователя.

    Args:
        request: Запрос с данными слова
        session: Database session

    Returns:
        Сохраненное слово

    Raises:
        HTTPException: Если пользователь не найден
    """
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(request.user_id)

    if not user:
        logger.warning("user_not_found", user_id=request.user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {request.user_id} not found",
        )

    word_repo = SavedWordRepository(session)
    saved_word = await word_repo.create(
        user_id=request.user_id,
        word_czech=request.word_czech,
        translation=request.translation,
        context_sentence=request.context_sentence,
        phonetics=request.phonetics,
    )

    await session.commit()

    logger.info(
        "word_saved",
        user_id=request.user_id,
        word=request.word_czech,
    )

    return {
        "id": saved_word.id,
        "word_czech": saved_word.word_czech,
        "translation": saved_word.translation,
        "context_sentence": saved_word.context_sentence,
        "phonetics": saved_word.phonetics,
        "times_reviewed": saved_word.times_reviewed,
        "created_at": saved_word.created_at.isoformat() if saved_word.created_at else None,
    }


@router.delete(
    "/{word_id}",
    summary="Удалить слово",
    description="Удалить сохраненное слово из словаря",
)
async def delete_word(
    word_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Удалить сохраненное слово.

    Args:
        word_id: ID слова
        session: Database session

    Returns:
        Статус успешности

    Raises:
        HTTPException: Если слово не найдено
    """
    word_repo = SavedWordRepository(session)
    deleted = await word_repo.delete(word_id)

    if not deleted:
        logger.warning("word_not_found", word_id=word_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Word with id {word_id} not found",
        )

    logger.info("word_deleted", word_id=word_id)

    return {"status": "success", "message": "Word deleted"}


@router.post(
    "/translate",
    response_model=WordTranslationResponse,
    summary="Перевести слово",
    description="Перевести чешское слово на русский или украинский язык",
)
async def translate_word(
    request: WordTranslationRequest,
    translation_service: TranslationService = Depends(get_translation_service),
):
    """
    Перевести слово с чешского на целевой язык.

    Args:
        request: Запрос с словом и целевым языком
        translation_service: Сервис перевода

    Returns:
        WordTranslationResponse: Перевод слова

    Raises:
        HTTPException: При ошибках перевода
    """
    try:
        result = await translation_service.translate_word(
            word=request.word, target_language=request.target_language
        )

        return WordTranslationResponse(
            word=request.word,
            translation=result["translation"],
            target_language=request.target_language,
            phonetics=result.get("phonetics"),
        )

    except ValueError as e:
        logger.warning(
            "translation_request_failed",
            word=request.word,
            target_language=request.target_language,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        logger.error(
            "translation_error",
            word=request.word,
            target_language=request.target_language,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to translate word",
        )


# ============= Spaced Repetition Endpoints =============

class ReviewAnswerRequest(BaseModel):
    """Request for submitting a review answer."""
    quality: int  # 0=again, 1=hard, 2=good, 3=easy


def get_sr_service() -> SpacedRepetitionService:
    """Dependency для сервиса spaced repetition."""
    return SpacedRepetitionService()


@router.get(
    "/{telegram_id}/review",
    summary="Получить слова для повторения",
    description="Получить слова, которые необходимо повторить сегодня (Spaced Repetition)",
)
async def get_words_for_review(
    telegram_id: int,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    """
    Получить слова для повторения по SR алгоритму.

    Args:
        telegram_id: Telegram ID пользователя
        limit: Максимальное количество слов
        session: Database session

    Returns:
        Список слов для повторения
    """
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(telegram_id)

    if not user:
        logger.warning("user_not_found", telegram_id=telegram_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_id {telegram_id} not found",
        )

    # Query words due for review
    today = date.today()
    query = (
        select(SavedWord)
        .where(
            SavedWord.user_id == user.id,
            (SavedWord.next_review_date <= today) | (SavedWord.next_review_date.is_(None))
        )
        .order_by(SavedWord.next_review_date.asc().nullsfirst())
        .limit(limit)
    )

    result = await session.execute(query)
    words = result.scalars().all()

    return {
        "words": [
            {
                "id": word.id,
                "word_czech": word.word_czech,
                "translation": word.translation,
                "context_sentence": word.context_sentence,
                "phonetics": word.phonetics,
                "ease_factor": word.ease_factor,
                "interval_days": word.interval_days,
                "sr_review_count": word.sr_review_count,
                "mastery_level": word.mastery_level,
            }
            for word in words
        ],
        "total_due": len(words),
        "estimated_minutes": SpacedRepetitionService().estimate_review_time(len(words)),
    }


@router.post(
    "/{word_id}/answer",
    summary="Отправить ответ на повторение",
    description="Отправить качество ответа для обновления SR параметров",
)
async def submit_review_answer(
    word_id: int,
    request: ReviewAnswerRequest,
    session: AsyncSession = Depends(get_session),
    sr_service: SpacedRepetitionService = Depends(get_sr_service),
):
    """
    Обработать ответ пользователя и обновить SR параметры.

    Args:
        word_id: ID слова
        request: Качество ответа (0-3)
        session: Database session
        sr_service: SR сервис

    Returns:
        Обновленные параметры слова
    """
    # Validate quality
    if request.quality not in [0, 1, 2, 3]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quality must be 0 (again), 1 (hard), 2 (good), or 3 (easy)",
        )

    # Get word
    query = select(SavedWord).where(SavedWord.id == word_id)
    result = await session.execute(query)
    word = result.scalar_one_or_none()

    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Word with id {word_id} not found",
        )

    # Calculate new SR parameters
    new_ef, new_interval, next_date = sr_service.calculate_next_review(
        quality=request.quality,
        current_ease_factor=word.ease_factor,
        current_interval=word.interval_days,
        review_count=word.sr_review_count,
    )

    # Update word
    word.ease_factor = new_ef
    word.interval_days = new_interval
    word.next_review_date = next_date
    word.sr_review_count += 1
    word.times_reviewed += 1
    word.last_reviewed_at = datetime.now()
    word.add_quality_rating(request.quality)

    await session.commit()

    logger.info(
        "sr_answer_submitted",
        word_id=word_id,
        quality=request.quality,
        new_interval=new_interval,
        next_review=next_date.isoformat(),
    )

    return {
        "id": word.id,
        "word_czech": word.word_czech,
        "new_ease_factor": new_ef,
        "new_interval_days": new_interval,
        "next_review_date": next_date.isoformat(),
        "sr_review_count": word.sr_review_count,
        "mastery_level": word.mastery_level,
    }


@router.get(
    "/{telegram_id}/review-stats",
    summary="Получить статистику повторения",
    description="Получить статистику spaced repetition для пользователя",
)
async def get_review_stats(
    telegram_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Получить статистику SR для пользователя.

    Args:
        telegram_id: Telegram ID пользователя
        session: Database session

    Returns:
        Статистика повторения
    """
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(telegram_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_id {telegram_id} not found",
        )

    today = date.today()

    # Get all words for user
    query = select(SavedWord).where(SavedWord.user_id == user.id)
    result = await session.execute(query)
    all_words = result.scalars().all()

    # Calculate stats
    total_words = len(all_words)
    due_today = sum(1 for w in all_words if w.is_due_for_review)
    mastery_breakdown = {
        "new": 0,
        "learning": 0,
        "familiar": 0,
        "known": 0,
        "mastered": 0,
    }

    for word in all_words:
        level = word.mastery_level
        if level in mastery_breakdown:
            mastery_breakdown[level] += 1

    return {
        "total_words": total_words,
        "due_today": due_today,
        "mastery_breakdown": mastery_breakdown,
        "next_review_in_days": min(
            [(w.next_review_date - today).days for w in all_words if w.next_review_date and w.next_review_date > today],
            default=0
        ),
    }


