"""
Lesson router - обработка голосовых сообщений.

Реализует полный pipeline:
1. Прием аудио файла
2. STT (Whisper) → транскрипция
3. Анализ и ответ Хонзика (GPT)
4. TTS → голосовой ответ
5. Сохранение в БД
6. Геймификация
"""

import io
import structlog
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

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/v1/lessons", tags=["lessons"])


def get_openai_client(settings: Settings = Depends(get_settings)) -> OpenAIClient:
    """Dependency для OpenAI клиента."""
    return OpenAIClient(settings)


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
        # 3. STT - транскрипция
        log.info("starting_transcription")
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = audio.filename or "audio.ogg"

        transcript = await openai_client.transcribe_audio(
            audio_file=audio_file, language="cs"
        )

        log.info("transcription_completed", transcript_length=len(transcript))

        # 4. Получаем историю разговора (последние 5 сообщений)
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

        # 5. Анализ Хонзика
        log.info("generating_honzik_response")

        honzik_response = await honzik.generate_response(
            user_text=transcript,
            level=user.level,
            style=user.settings.conversation_style,
            corrections_level=user.settings.corrections_level,
            ui_language=user.ui_language,
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
            ui_language=user.ui_language,
        )

        # 7. TTS - генерация голосового ответа
        log.info("generating_speech")

        voice_speed = openai_client.get_voice_speed_mapping(
            user.settings.voice_speed
        )

        audio_response = await openai_client.generate_speech(
            text=processed["honzik_response"],
            voice=settings.tts_voice,
            speed=voice_speed,
        )

        log.info("speech_generated", audio_size_bytes=len(audio_response))

        # 8. Сохранение сообщений в БД
        log.info("saving_messages")

        # Сообщение пользователя
        user_message = await message_repo.create(
            user_id=user.id,
            role="user",
            text=processed["corrected_text"],
            transcript_raw=transcript,
            transcript_normalized=processed["corrected_text"],
            audio_file_path=None,  # TODO: сохранять в storage
            correctness_score=processed["correctness_score"],
            words_total=processed["words_total"],
            words_correct=processed["words_correct"],
        )

        # Сообщение Хонзика
        assistant_message = await message_repo.create(
            user_id=user.id,
            role="assistant",
            text=processed["honzik_response"],
            audio_file_path=None,  # TODO: сохранять в storage
        )

        # 9. Обновление статистики
        log.info("updating_statistics")

        stats_repo = StatsRepository(db)
        user_date = gamification.get_user_date(user.settings.timezone)

        # Обновляем daily_stats
        await stats_repo.update_daily(
            user_id=user.id,
            date_value=user_date,
            messages_count=(
                await stats_repo.get_or_create_daily(user.id, user_date)
            ).messages_count
            + 1,
            words_said=(
                await stats_repo.get_or_create_daily(user.id, user_date)
            ).words_said
            + processed["words_total"],
        )

        # 10. Геймификация
        log.info("processing_gamification")

        gamification_result = await gamification.process_message_gamification(
            db=db,
            user_id=user.id,
            correctness_score=processed["correctness_score"],
            timezone_str=user.settings.timezone,
        )

        await db.commit()

        log.info(
            "voice_message_processed_successfully",
            stars_earned=gamification_result["stars_earned"],
            streak=gamification_result["current_streak"],
        )

        # 11. Формируем ответ
        return LessonProcessResponse(
            transcript=transcript,
            honzik_response_text=processed["honzik_response"],
            honzik_response_audio=audio_response,
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

