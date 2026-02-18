"""
Lesson router - обработка голосовых сообщений.

Реализует полный pipeline с ПАРАЛЛЕЛЬНОЙ обработкой для ускорения в 2 раза:
1. Прием аудио файла
2. STT (Whisper) → транскрипция
3. Анализ и ответ Хонзика (GPT) - с использованием GPT-4o-mini для скорости
4. TTS → голосовой ответ (ПАРАЛЛЕЛЬНО с шагом 5-6)
5. Сохранение в БД (ПАРАЛЛЕЛЬНО)
6. Геймификация (ПАРАЛЛЕЛЬНО)

Оптимизации:
- GPT-4o-mini для beginners/intermediate (2x быстрее)
- Кеширование типичных фраз
- Параллельное выполнение TTS/DB/Gamification
"""

import asyncio
import base64
import io
import structlog
import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import Settings, get_settings
from backend.db.database import get_session
from backend.db.repositories import (
    UserRepository,
    MessageRepository,
    StatsRepository,
)
from backend.schemas.lesson import (
    LessonProcessResponse,
    CorrectionSchema,
    MistakeSchema,
    DailyChallengeSchema,
)
from backend.services.openai_client import OpenAIClient
from backend.services.honzik_personality import HonzikPersonality
from backend.services.correction_engine import CorrectionEngine
from backend.services.gamification import GamificationService
from backend.services.cache_service import cache_service

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/v1/lessons", tags=["lessons"])


# Default user settings when UserSettings is None (new user without settings row)
_DEFAULT_SETTINGS = {
    "conversation_style": "friendly",
    "corrections_level": "balanced",
    "timezone": "Europe/Prague",
    "voice_speed": "normal",
}


def _s(user, attr: str):
    """Safe access to user.settings attributes with defaults."""
    if user.settings is not None:
        return getattr(user.settings, attr, _DEFAULT_SETTINGS.get(attr))
    return _DEFAULT_SETTINGS.get(attr)


async def save_audio_file_async(audio_bytes: bytes, filepath: str) -> None:
    """
    Асинхронное сохранение аудио файла.

    Args:
        audio_bytes: Байты аудио файла
        filepath: Путь для сохранения
    """
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(audio_bytes)


async def read_audio_file_async(filepath: str) -> bytes:
    """
    Асинхронное чтение аудио файла.

    Args:
        filepath: Путь к файлу

    Returns:
        bytes: Содержимое файла
    """
    async with aiofiles.open(filepath, "rb") as f:
        return await f.read()


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


@router.post("/process", response_model=LessonProcessResponse)
async def process_voice_message(
    user_id: int = Form(..., description="Telegram ID пользователя"),
    audio: UploadFile = File(..., description="Аудио файл (ogg, mp3, wav)"),
    db: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
    openai_client: OpenAIClient = Depends(get_openai_client),
    honzik: HonzikPersonality = Depends(get_honzik_personality),
    correction_engine: CorrectionEngine = Depends(get_correction_engine),
    gamification: GamificationService = Depends(get_gamification_service),
):
    """
    Обработать голосовое сообщение пользователя.

    Pipeline:
    1. Валидация аудио
    2. STT → транскрипция
    3. Анализ Хонзика → исправления и ответ
    4. TTS → голосовой ответ
    5. Сохранение в БД
    6. Геймификация (звезды, streak)

    Args:
        user_id: Telegram ID пользователя
        audio: Аудио файл
        db: Сессия БД
        settings: Настройки приложения
        openai_client: OpenAI клиент
        honzik: Личность Хонзика
        correction_engine: Движок исправлений
        gamification: Сервис геймификации

    Returns:
        LessonProcessResponse: Полный ответ с транскрипцией, исправлениями и аудио

    Raises:
        HTTPException: При ошибках валидации или обработки
    """
    log = logger.bind(user_id=user_id)
    log.info("processing_voice_message", filename=audio.filename)

    # 1. Валидация пользователя
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(user_id)

    if not user:
        log.error("user_not_found")
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Валидация аудио
    if not audio.content_type or not any(
        fmt in audio.content_type for fmt in ["audio", "ogg", "mpeg", "wav"]
    ):
        log.error("invalid_audio_format", content_type=audio.content_type)
        raise HTTPException(status_code=400, detail="Invalid audio format")

    # Читаем аудио в память
    audio_bytes = await audio.read()

    # Проверка размера (примерно 60 секунд = ~1MB для ogg)
    max_size = 5 * 1024 * 1024  # 5 MB
    if len(audio_bytes) > max_size:
        log.error("audio_too_large", size_bytes=len(audio_bytes))
        raise HTTPException(
            status_code=400, detail="Audio file too large (max 5MB)"
        )

    log.info("audio_validated", size_bytes=len(audio_bytes))

    try:
        # ========================================
        # PARALLEL: STT + history fetch run simultaneously
        # STT takes 1-3 sec, DB fetch takes 0.1-0.3 sec
        # Running in parallel saves ~0.5-1 sec per request
        # ========================================
        log.info("starting_parallel_stt_and_history")
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = audio.filename or "audio.ogg"

        message_repo = MessageRepository(db)

        # Launch STT in background while fetching conversation history
        stt_task = asyncio.create_task(
            openai_client.transcribe_audio(audio_file=audio_file, language="cs")
        )

        # Fetch history in parallel with STT
        recent_messages = await message_repo.get_user_messages(
            user_id=user.id, limit=10
        )

        # Format conversation history while STT is still running
        conversation_history = []
        for msg in reversed(recent_messages):  # От старых к новым
            conversation_history.append(
                {"role": msg.role, "text": msg.text or msg.transcript_raw or ""}
            )

        # Wait for STT to complete
        transcript = await stt_task
        detected_language = "cs"  # Всегда чешский

        log.info(
            "parallel_stt_and_history_completed",
            transcript_length=len(transcript),
            history_messages=len(conversation_history),
        )

        # 5. Проверка кеша для типичных фраз (УСКОРЕНИЕ!)
        # Для частых фраз вроде "ahoj", "dobrý den" - ответ мгновенный
        cached_response = await cache_service.get_cached_common_phrase(
            transcript,
            user.level,
            _s(user, "conversation_style"),
        )

        if cached_response:
            log.info(
                "using_cached_common_phrase",
                phrase=transcript[:30],
                level=user.level,
            )
            honzik_response = cached_response
        else:
            # 6. Анализ Хонзика (GPT-4o-mini для beginners/intermediate)
            log.info("generating_honzik_response")

            honzik_response = await honzik.generate_response(
                user_text=transcript,
                level=user.level,
                style=_s(user, "conversation_style"),
                corrections_level=_s(user, "corrections_level"),
                native_language=user.native_language,
                conversation_history=conversation_history,
            )

        log.info(
            "honzik_response_generated",
            correctness_score=honzik_response["correctness_score"],
        )

        # 6. Обработка исправлений
        processed = correction_engine.process_honzik_response(
            response=honzik_response,
            original_text=transcript,
            native_language=user.native_language,
        )

        # ========================================
        # ПАРАЛЛЕЛЬНАЯ ОБРАБОТКА для ускорения в 2 раза
        # TTS + DB + Gamification выполняются одновременно
        # ========================================

        log.info("starting_parallel_processing")

        voice_speed = openai_client.get_voice_speed_mapping(
            _s(user, "voice_speed")
        )

        # Определяем все задачи для параллельного выполнения
        async def generate_tts():
            """Генерация TTS с кешированием (ускорение на 2-4 сек для повторных фраз)"""
            text = processed["honzik_response"]
            voice = settings.tts_voice
            speed = voice_speed

            # Проверяем кеш сначала
            cached_audio = await cache_service.get_cached_tts(text, voice, speed)
            if cached_audio:
                log.info("tts_cache_hit", text_preview=text[:30])
                return cached_audio

            # Генерируем новое аудио
            audio = await openai_client.generate_speech(
                text=text,
                voice=voice,
                speed=speed,
            )

            # Сохраняем в кеш (30 дней)
            await cache_service.cache_tts(text, voice, speed, audio)
            return audio

        async def save_messages():
            """Сохранение сообщений в БД"""
            # Сообщение пользователя
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
            # Сообщение Хонзика
            await message_repo.create(
                user_id=user.id,
                role="assistant",
                text=processed["honzik_response"],
                audio_file_path=None,
            )

        async def update_stats_and_gamification():
            """Обновление статистики и геймификации"""
            stats_repo = StatsRepository(db)
            user_date = gamification.get_user_date(_s(user, "timezone"))

            # Обновляем daily_stats
            daily_stats = await stats_repo.get_or_create_daily(user.id, user_date)
            await stats_repo.update_daily(
                user_id=user.id,
                date_value=user_date,
                messages_count=daily_stats.messages_count + 1,
                words_said=daily_stats.words_said + processed["words_total"],
                correct_percent=processed["correctness_score"],
            )

            # Геймификация
            return await gamification.process_message_gamification(
                db=db,
                user_id=user.id,
                correctness_score=processed["correctness_score"],
                timezone_str=_s(user, "timezone"),
            )

        # ========================================
        # ОПТИМИЗИРОВАННАЯ ОБРАБОТКА
        # TTS запускаем параллельно (самый долгий - 2-4 сек)
        # DB операции выполняем последовательно (SQLAlchemy ограничение)
        # ========================================
        log.info("starting_optimized_processing")

        # 1. Запускаем TTS в фоне (не блокирует)
        tts_task = asyncio.create_task(generate_tts())

        # 2. Пока TTS генерируется, выполняем DB операции последовательно
        await save_messages()
        gamification_result = await update_stats_and_gamification()

        # 3. Кешируем если типичная фраза (Redis, не DB)
        if cache_service.is_common_phrase(transcript):
            await cache_service.cache_common_phrase(
                transcript,
                user.level,
                _s(user, "conversation_style"),
                honzik_response,
            )

        # 4. Ждём завершения TTS
        audio_response = await tts_task

        await db.commit()

        log.info(
            "optimized_processing_completed",
            audio_size=len(audio_response),
            stars_earned=gamification_result["stars_earned"],
            streak=gamification_result["current_streak"],
        )

        # 11. Формируем ответ
        # Кодируем аудио в base64 для передачи через JSON
        audio_base64 = base64.b64encode(audio_response).decode('utf-8')

        return LessonProcessResponse(
            transcript=transcript,
            honzik_response_text=processed["honzik_response"],
            honzik_response_transcript=processed["honzik_response"],  # Same as text for now
            honzik_response_audio=audio_base64,
            corrections=CorrectionSchema(
                corrected_text=processed["corrected_text"],
                mistakes=[
                    MistakeSchema(**mistake)
                    for mistake in honzik_response["mistakes"]
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
            daily_challenge=DailyChallengeSchema(
                **gamification_result["daily_challenge"]
            ),
            words_total=processed["words_total"],
            words_correct=processed["words_correct"],
            # Неделя 2: Определение языка
            detected_language=detected_language,
            language_notice=None,
        )

    except ValueError as e:
        log.error("validation_error", error=str(e), exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        await db.rollback()
        raise

    except Exception as e:
        log.error(
            "processing_error",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        await db.rollback()

        # Return more detailed error in development
        import traceback
        detail = f"Failed to process voice message: {str(e)}"
        if settings.is_development:
            detail += f"\n\nTraceback:\n{traceback.format_exc()}"

        raise HTTPException(
            status_code=500,
            detail=detail,
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
    Обработать текстовое сообщение пользователя.

    В отличие от голосового:
    1. НЕТ этапа STT (текст уже есть)
    2. Опционально TTS (можно отключить для экономии)
    3. Быстрее на 1-2 секунды

    Args:
        user_id: Telegram ID пользователя
        text: Текст сообщения на чешском
        include_audio: Генерировать ли голосовой ответ
        db: Сессия БД
        settings: Настройки приложения
        openai_client: OpenAI клиент
        honzik: Личность Хонзика
        correction_engine: Движок исправлений
        gamification: Сервис геймификации

    Returns:
        LessonProcessResponse: Полный ответ с исправлениями и опционально аудио

    Raises:
        HTTPException: При ошибках валидации или обработки
    """
    log = logger.bind(user_id=user_id, mode="text")
    log.info("processing_text_message", text_length=len(text))

    # 1. Валидация пользователя
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(user_id)

    if not user:
        log.error("user_not_found")
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Валидация текста
    text = text.strip()
    if len(text) < 2:
        log.error("text_too_short", text_length=len(text))
        raise HTTPException(status_code=400, detail="Text too short (min 2 chars)")

    if len(text) > 2000:
        log.error("text_too_long", text_length=len(text))
        raise HTTPException(status_code=400, detail="Text too long (max 2000 chars)")

    log.info("text_validated", text_length=len(text))

    try:
        # 3. Получаем историю разговора (последние 10 сообщений)
        message_repo = MessageRepository(db)
        recent_messages = await message_repo.get_user_messages(
            user_id=user.id, limit=10
        )

        # Форматируем историю для Хонзика
        conversation_history = []
        for msg in reversed(recent_messages):  # От старых к новым
            conversation_history.append(
                {"role": msg.role, "text": msg.text or msg.transcript_raw or ""}
            )

        # 4. Проверка кеша для типичных фраз
        cached_response = await cache_service.get_cached_common_phrase(
            text,
            user.level,
            _s(user, "conversation_style"),
        )

        if cached_response:
            log.info(
                "using_cached_common_phrase",
                phrase=text[:30],
                level=user.level,
            )
            honzik_response = cached_response
        else:
            # 5. Анализ Хонзика (без STT - быстрее!)
            log.info("generating_honzik_response")

            honzik_response = await honzik.generate_response(
                user_text=text,
                level=user.level,
                style=_s(user, "conversation_style"),
                corrections_level=_s(user, "corrections_level"),
                native_language=user.native_language,
                conversation_history=conversation_history,
            )

        log.info(
            "honzik_response_generated",
            correctness_score=honzik_response["correctness_score"],
        )

        # 6. Обработка исправлений
        processed = correction_engine.process_honzik_response(
            response=honzik_response,
            original_text=text,
            native_language=user.native_language,
        )

        # ========================================
        # ПАРАЛЛЕЛЬНАЯ ОБРАБОТКА
        # TTS (опционально) + DB + Gamification
        # ========================================

        log.info("starting_parallel_processing")

        # Определяем все задачи
        async def generate_tts():
            """Генерация TTS с кешированием (если включено)"""
            if not include_audio:
                return None

            voice_speed = openai_client.get_voice_speed_mapping(
                _s(user, "voice_speed")
            )
            text = processed["honzik_response"]
            voice = settings.tts_voice
            speed = voice_speed

            # Проверяем кеш сначала
            cached_audio = await cache_service.get_cached_tts(text, voice, speed)
            if cached_audio:
                log.info("tts_cache_hit", text_preview=text[:30])
                return cached_audio

            # Генерируем новое аудио
            audio = await openai_client.generate_speech(
                text=text,
                voice=voice,
                speed=speed,
            )

            # Сохраняем в кеш (30 дней)
            await cache_service.cache_tts(text, voice, speed, audio)
            return audio

        async def save_messages():
            """Сохранение сообщений в БД"""
            # Сообщение пользователя
            await message_repo.create(
                user_id=user.id,
                role="user",
                text=processed["corrected_text"],
                transcript_raw=text,  # Для текстовых - оригинальный текст
                transcript_normalized=processed["corrected_text"],
                audio_file_path=None,
                correctness_score=processed["correctness_score"],
                words_total=processed["words_total"],
                words_correct=processed["words_correct"],
            )
            # Сообщение Хонзика
            await message_repo.create(
                user_id=user.id,
                role="assistant",
                text=processed["honzik_response"],
                audio_file_path=None,
            )

        async def update_stats_and_gamification():
            """Обновление статистики и геймификации"""
            stats_repo = StatsRepository(db)
            user_date = gamification.get_user_date(_s(user, "timezone"))

            # Обновляем daily_stats
            daily_stats = await stats_repo.get_or_create_daily(user.id, user_date)
            await stats_repo.update_daily(
                user_id=user.id,
                date_value=user_date,
                messages_count=daily_stats.messages_count + 1,
                words_said=daily_stats.words_said + processed["words_total"],
                correct_percent=processed["correctness_score"],
            )

            # Геймификация
            return await gamification.process_message_gamification(
                db=db,
                user_id=user.id,
                correctness_score=processed["correctness_score"],
                timezone_str=_s(user, "timezone"),
            )

        # Запускаем TTS в фоне
        tts_task = asyncio.create_task(generate_tts())

        # DB операции последовательно
        await save_messages()
        gamification_result = await update_stats_and_gamification()

        # Кешируем если типичная фраза
        if cache_service.is_common_phrase(text):
            await cache_service.cache_common_phrase(
                text,
                user.level,
                _s(user, "conversation_style"),
                honzik_response,
            )

        # Ждём завершения TTS
        audio_response = await tts_task

        await db.commit()

        # Кодируем аудио в base64 (если есть)
        audio_base64 = ""
        if audio_response:
            audio_base64 = base64.b64encode(audio_response).decode('utf-8')
            log.info("tts_generated", audio_size=len(audio_response))
        else:
            log.info("tts_skipped")

        log.info(
            "text_processing_completed",
            stars_earned=gamification_result["stars_earned"],
            streak=gamification_result["current_streak"],
        )

        # Формируем ответ
        return LessonProcessResponse(
            transcript=text,  # Для текстовых - это и есть "транскрипт"
            honzik_response_text=processed["honzik_response"],
            honzik_response_transcript=processed["honzik_response"],
            honzik_response_audio=audio_base64,  # Пустая строка если include_audio=False
            corrections=CorrectionSchema(
                corrected_text=processed["corrected_text"],
                mistakes=[
                    MistakeSchema(**mistake)
                    for mistake in honzik_response["mistakes"]
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
            daily_challenge=DailyChallengeSchema(
                **gamification_result["daily_challenge"]
            ),
            words_total=processed["words_total"],
            words_correct=processed["words_correct"],
            detected_language="cs",  # Для текста - предполагаем чешский
            language_notice=None,
        )

    except ValueError as e:
        log.error("validation_error", error=str(e), exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    except HTTPException:
        await db.rollback()
        raise

    except Exception as e:
        log.error(
            "text_processing_error",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        await db.rollback()

        detail = f"Failed to process text message: {str(e)}"
        if settings.is_development:
            import traceback
            detail += f"\n\nTraceback:\n{traceback.format_exc()}"

        raise HTTPException(
            status_code=500,
            detail=detail,
        )

