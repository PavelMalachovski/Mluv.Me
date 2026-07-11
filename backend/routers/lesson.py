"""
Lesson router — обработка голосовых и текстовых сообщений.

Pipeline (общий для голоса и текста, см. _run_lesson):
1. Валидация пользователя, квоты и входных данных
2. STT (Whisper) — только для голоса, параллельно с загрузкой истории
3. Ответ Хонзика (GPT, JSON) — с кешем типичных фраз
4. TTS — параллельно с записью в БД; при include_audio=False
   прогревается в фоне, чтобы последующий запрос /tts был мгновенным
5. Сохранение сообщений, новых слов, статистики и геймификации
"""

import asyncio
import base64
import io

import structlog
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import Settings, get_settings
from backend.db.database import get_session
from backend.db.repositories import (
    MessageRepository,
    SavedWordRepository,
    StatsRepository,
    UserRepository,
)
from backend.models.word import SavedWord
from backend.schemas.lesson import (
    CorrectionSchema,
    DailyChallengeSchema,
    LessonProcessResponse,
    MistakeSchema,
)
from backend.services.cache_service import cache_service
from backend.services.correction_engine import CorrectionEngine
from backend.services.gamification import GamificationService
from backend.services.honzik_personality import HonzikPersonality
from backend.services.openai_client import OpenAIClient
from backend.services.subscription_service import SubscriptionService
from backend.services.tts_service import get_or_generate_tts, prewarm_tts

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/v1/lessons", tags=["lessons"])


# Default user settings when UserSettings is None (new user without settings row)
_DEFAULT_SETTINGS = {
    "conversation_style": "friendly",
    "corrections_level": "balanced",
    "timezone": "Europe/Prague",
    "voice_speed": "normal",
    "character": "honzik",
}


def _s(user, attr: str):
    """Safe access to user.settings attributes with defaults."""
    if user.settings is not None:
        return getattr(user.settings, attr, _DEFAULT_SETTINGS.get(attr))
    return _DEFAULT_SETTINGS.get(attr)


# Global singleton for OpenAI client (avoids recreating on each request)
_openai_client: OpenAIClient | None = None


def get_openai_client(settings: Settings = Depends(get_settings)) -> OpenAIClient:
    """Dependency для OpenAI клиента (Singleton pattern)."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient(settings)
    return _openai_client


def get_honzik_personality(
    openai_client: OpenAIClient = Depends(get_openai_client),
) -> HonzikPersonality:
    """Dependency для Хонзика."""
    return HonzikPersonality(openai_client)


def get_correction_engine() -> CorrectionEngine:
    """Dependency для движка исправлений."""
    return CorrectionEngine()


def get_gamification_service(
    db: AsyncSession = Depends(get_session),
) -> GamificationService:
    """Dependency для сервиса геймификации."""
    stats_repo = StatsRepository(db)
    user_repo = UserRepository(db)
    return GamificationService(stats_repo, user_repo)


async def _get_user_or_404(db: AsyncSession, telegram_id: int):
    """Найти пользователя по Telegram ID или вернуть 404."""
    user = await UserRepository(db).get_by_telegram_id(telegram_id)
    if not user:
        logger.error("user_not_found", user_id=telegram_id)
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def _check_quota(sub_svc: SubscriptionService, user_id: int, kind: str) -> None:
    """Проверить дневную квоту (voice/text), 429 при исчерпании."""
    quota = await sub_svc.check_quota(user_id, kind)
    if not quota["allowed"]:
        noun = "hlasových" if kind == "voice" else "textových"
        raise HTTPException(
            status_code=429,
            detail={
                "error": "daily_limit_reached",
                "message": f"Denní limit {noun} zpráv vyčerpán",
                "plan": quota["plan"],
                "used": quota["used"],
                "limit": quota["limit"],
            },
        )


async def _save_new_words(
    db: AsyncSession,
    user_id: int,
    honzik_response: dict,
    log,
) -> int:
    """
    Extract and save new vocabulary words from the GPT response.

    Deduplicates against existing saved words for this user.
    Returns the number of words saved.
    """
    new_words = honzik_response.get("new_words")
    if not new_words or not isinstance(new_words, list):
        return 0

    word_repo = SavedWordRepository(db)
    saved_count = 0

    for word_data in new_words[:3]:  # Max 3 per message
        word_czech = (word_data.get("word_czech") or "").strip()
        translation = (word_data.get("translation") or "").strip()
        if not word_czech or not translation:
            continue

        # Check for duplicate
        existing = await db.execute(
            select(SavedWord).where(
                SavedWord.user_id == user_id,
                SavedWord.word_czech == word_czech,
            )
        )
        if existing.scalar_one_or_none():
            continue

        try:
            await word_repo.create(
                user_id=user_id,
                word_czech=word_czech,
                translation=translation,
                context_sentence=word_data.get("context_sentence"),
            )
            saved_count += 1
        except Exception as e:
            log.warning("save_new_word_failed", word=word_czech, error=str(e))

    if saved_count:
        log.info("new_words_saved", count=saved_count, user_id=user_id)
    return saved_count


async def _run_lesson(
    *,
    db: AsyncSession,
    user,
    transcript: "str | asyncio.Task[str]",
    quota_kind: str,
    include_audio: bool,
    openai_client: OpenAIClient,
    honzik: HonzikPersonality,
    correction_engine: CorrectionEngine,
    gamification: GamificationService,
    sub_svc: SubscriptionService,
    log,
) -> LessonProcessResponse:
    """
    Общий pipeline урока для голосовых и текстовых сообщений.

    Args:
        transcript: Готовый текст пользователя или задача STT (Whisper),
            запущенная параллельно с загрузкой истории.
        quota_kind: "voice" или "text" — какую дневную квоту инкрементировать.
        include_audio: Генерировать TTS в этом запросе. При False озвучка
            прогревается в фоне для последующего запроса /tts.
    """
    # 1. История разговора (грузится, пока STT ещё может работать)
    message_repo = MessageRepository(db)
    recent_messages = await message_repo.get_user_messages(user_id=user.id, limit=10)
    conversation_history = [
        {"role": msg.role, "text": msg.text or msg.transcript_raw or ""}
        for msg in reversed(recent_messages)  # От старых к новым
    ]

    if isinstance(transcript, asyncio.Task):
        transcript = await transcript

    log.info(
        "input_ready",
        transcript_length=len(transcript),
        history_messages=len(conversation_history),
    )

    # 2. Ответ Хонзика: кеш типичных фраз или GPT
    honzik_response = await cache_service.get_cached_common_phrase(
        transcript, user.level, _s(user, "conversation_style")
    )
    if honzik_response:
        log.info("using_cached_common_phrase", phrase=transcript[:30], level=user.level)
    else:
        honzik_response = await honzik.generate_response(
            user_text=transcript,
            level=user.level,
            style=_s(user, "conversation_style"),
            corrections_level=_s(user, "corrections_level"),
            native_language=user.native_language,
            conversation_history=conversation_history,
            character=_s(user, "character"),
        )

    log.info(
        "honzik_response_generated",
        correctness_score=honzik_response["correctness_score"],
    )

    # 3. Обработка исправлений
    processed = correction_engine.process_honzik_response(
        response=honzik_response,
        original_text=transcript,
        native_language=user.native_language,
    )

    # 4. TTS: параллельно с записью в БД (самый долгий шаг — 2-4 сек).
    #    При include_audio=False — прогрев в фоне: бот запросит /tts
    #    через секунду и получит аудио из кеша/уже идущей генерации.
    reply_text = processed["honzik_response"]
    voice = HonzikPersonality.get_tts_voice(_s(user, "character"))
    speed = openai_client.get_voice_speed_mapping(_s(user, "voice_speed"))

    tts_task = None
    if include_audio:
        tts_task = asyncio.create_task(
            get_or_generate_tts(openai_client, reply_text, voice, speed)
        )
    else:
        prewarm_tts(openai_client, reply_text, voice, speed)

    # 5. БД: сообщения, новые слова, статистика, геймификация
    #    (последовательно — одна AsyncSession не поддерживает конкурентный доступ)
    await message_repo.create(
        user_id=user.id,
        role="user",
        text=processed["corrected_text"],
        transcript_raw=transcript,
        transcript_normalized=processed["corrected_text"],
        audio_file_path=None,
        correctness_score=processed["correctness_score"],
        words_total=processed["words_total"],
        words_correct=processed["words_correct"],
    )
    await message_repo.create(
        user_id=user.id,
        role="assistant",
        text=reply_text,
        audio_file_path=None,
    )
    await _save_new_words(db, user.id, honzik_response, log)

    stats_repo = StatsRepository(db)
    user_date = gamification.get_user_date(_s(user, "timezone"))
    daily_stats = await stats_repo.get_or_create_daily(user.id, user_date)
    await stats_repo.update_daily(
        user_id=user.id,
        date_value=user_date,
        messages_count=daily_stats.messages_count + 1,
        words_said=daily_stats.words_said + processed["words_total"],
        correct_percent=processed["correctness_score"],
    )
    gamification_result = await gamification.process_message_gamification(
        db=db,
        user_id=user.id,
        correctness_score=processed["correctness_score"],
        timezone_str=_s(user, "timezone"),
    )

    # 6. Кешируем ответ на типичную фразу (Redis)
    if cache_service.is_common_phrase(transcript):
        await cache_service.cache_common_phrase(
            transcript,
            user.level,
            _s(user, "conversation_style"),
            honzik_response,
        )

    # 7. Ждём TTS (если запускали) и фиксируем транзакцию
    audio_response = await tts_task if tts_task else None

    await db.commit()
    await sub_svc.increment_usage(user.id, quota_kind)

    log.info(
        "lesson_processing_completed",
        audio_size=len(audio_response) if audio_response else 0,
        stars_earned=gamification_result["stars_earned"],
        streak=gamification_result["current_streak"],
    )

    audio_base64 = (
        base64.b64encode(audio_response).decode("utf-8") if audio_response else ""
    )

    return LessonProcessResponse(
        transcript=transcript,
        honzik_response_text=reply_text,
        honzik_response_transcript=reply_text,
        honzik_response_audio=audio_base64,
        corrections=CorrectionSchema(
            corrected_text=processed["corrected_text"],
            mistakes=[
                MistakeSchema(**mistake) for mistake in honzik_response["mistakes"]
            ],
            correctness_score=processed["correctness_score"],
            suggestion=honzik_response["suggestion"],
        ),
        formatted_mistakes=processed["formatted_mistakes"],
        formatted_suggestion=processed["formatted_suggestion"],
        stars_earned=gamification_result["stars_earned"],
        total_stars=gamification_result["total_stars"],
        current_streak=gamification_result["current_streak"],
        max_streak=gamification_result["max_streak"],
        daily_challenge=DailyChallengeSchema(**gamification_result["daily_challenge"]),
        words_total=processed["words_total"],
        words_correct=processed["words_correct"],
        detected_language="cs",
        language_notice=None,
    )


async def _run_lesson_safe(settings: Settings, db: AsyncSession, log, **kwargs):
    """Обёртка _run_lesson с единой обработкой ошибок и rollback."""
    try:
        return await _run_lesson(db=db, log=log, **kwargs)
    except ValueError as e:
        log.error("validation_error", error=str(e), exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        log.error(
            "processing_error", error=str(e), error_type=type(e).__name__, exc_info=True
        )
        await db.rollback()

        detail = f"Failed to process message: {str(e)}"
        if settings.is_development:
            import traceback

            detail += f"\n\nTraceback:\n{traceback.format_exc()}"

        raise HTTPException(status_code=500, detail=detail)


@router.post("/process", response_model=LessonProcessResponse)
async def process_voice_message(
    user_id: int = Form(..., description="Telegram ID пользователя"),
    audio: UploadFile = File(..., description="Аудио файл (ogg, mp3, wav)"),
    include_audio: bool = Form(
        True, description="Генерировать ли голосовой ответ Хонзика"
    ),
    db: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
    openai_client: OpenAIClient = Depends(get_openai_client),
    honzik: HonzikPersonality = Depends(get_honzik_personality),
    correction_engine: CorrectionEngine = Depends(get_correction_engine),
    gamification: GamificationService = Depends(get_gamification_service),
):
    """
    Обработать голосовое сообщение: STT → ответ Хонзика → TTS → БД.

    STT запускается параллельно с загрузкой истории разговора.
    """
    log = logger.bind(user_id=user_id)
    log.info("processing_voice_message", filename=audio.filename)

    user = await _get_user_or_404(db, user_id)

    sub_svc = SubscriptionService(db)
    await _check_quota(sub_svc, user.id, "voice")

    # Валидация аудио
    if not audio.content_type or not any(
        fmt in audio.content_type for fmt in ["audio", "ogg", "mpeg", "wav"]
    ):
        log.error("invalid_audio_format", content_type=audio.content_type)
        raise HTTPException(status_code=400, detail="Invalid audio format")

    audio_bytes = await audio.read()

    max_size = 5 * 1024 * 1024  # ~60 секунд ogg с запасом
    if len(audio_bytes) > max_size:
        log.error("audio_too_large", size_bytes=len(audio_bytes))
        raise HTTPException(status_code=400, detail="Audio file too large (max 5MB)")

    log.info("audio_validated", size_bytes=len(audio_bytes))

    # STT в фоне — история разговора загрузится параллельно внутри _run_lesson
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = audio.filename or "audio.ogg"
    stt_task = asyncio.create_task(
        openai_client.transcribe_audio(audio_file=audio_file, language="cs")
    )

    return await _run_lesson_safe(
        settings,
        db,
        log,
        user=user,
        transcript=stt_task,
        quota_kind="voice",
        include_audio=include_audio,
        openai_client=openai_client,
        honzik=honzik,
        correction_engine=correction_engine,
        gamification=gamification,
        sub_svc=sub_svc,
    )


@router.post("/process/text", response_model=LessonProcessResponse)
async def process_text_message(
    user_id: int = Form(..., description="Telegram ID пользователя"),
    text: str = Form(..., description="Текст сообщения на чешском"),
    include_audio: bool = Form(True, description="Включить голосовой ответ Хонзика"),
    db: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
    openai_client: OpenAIClient = Depends(get_openai_client),
    honzik: HonzikPersonality = Depends(get_honzik_personality),
    correction_engine: CorrectionEngine = Depends(get_correction_engine),
    gamification: GamificationService = Depends(get_gamification_service),
):
    """
    Обработать текстовое сообщение: ответ Хонзика → TTS (опционально) → БД.

    Отличие от голосового — нет этапа STT, поэтому быстрее на 1-2 секунды.
    """
    log = logger.bind(user_id=user_id, mode="text")
    log.info("processing_text_message", text_length=len(text))

    user = await _get_user_or_404(db, user_id)

    sub_svc = SubscriptionService(db)
    await _check_quota(sub_svc, user.id, "text")

    # Валидация текста
    text = text.strip()
    if len(text) < 2:
        log.error("text_too_short", text_length=len(text))
        raise HTTPException(status_code=400, detail="Text too short (min 2 chars)")
    if len(text) > 2000:
        log.error("text_too_long", text_length=len(text))
        raise HTTPException(status_code=400, detail="Text too long (max 2000 chars)")

    return await _run_lesson_safe(
        settings,
        db,
        log,
        user=user,
        transcript=text,
        quota_kind="text",
        include_audio=include_audio,
        openai_client=openai_client,
        honzik=honzik,
        correction_engine=correction_engine,
        gamification=gamification,
        sub_svc=sub_svc,
    )


@router.post("/tts")
async def generate_tts_for_text(
    user_id: int = Form(..., description="Telegram ID пользователя"),
    text: str = Form(..., description="Текст для озвучивания"),
    db: AsyncSession = Depends(get_session),
    openai_client: OpenAIClient = Depends(get_openai_client),
):
    """
    Отдельный TTS endpoint — генерирует аудио для готового текста.

    Используется ботом во втором шаге: после получения анализа (без аудио)
    запрашивается озвучка отдельно, чтобы správnost пришла мгновенно.
    Благодаря прогреву в /process аудио обычно уже в кеше или генерируется.
    """
    log = logger.bind(user_id=user_id, mode="tts")

    user = await _get_user_or_404(db, user_id)

    voice = HonzikPersonality.get_tts_voice(_s(user, "character"))
    speed = openai_client.get_voice_speed_mapping(_s(user, "voice_speed"))

    audio = await get_or_generate_tts(openai_client, text, voice, speed)
    log.info("tts_ready", audio_size=len(audio))

    return {"audio": base64.b64encode(audio).decode("utf-8")}
