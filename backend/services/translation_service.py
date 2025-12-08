"""
Сервис для перевода слов с чешского на русский/украинский.
"""

import asyncio
import structlog
from deep_translator import GoogleTranslator

logger = structlog.get_logger(__name__)


class TranslationService:
    """Сервис для перевода слов."""

    # Маппинг языков для deep-translator
    LANGUAGE_MAP = {
        "ru": "russian",
        "uk": "ukrainian",
        "cs": "czech",
    }

    def __init__(self):
        """Инициализация сервиса перевода."""
        self.log = logger.bind(service="translation")

    async def translate_word(
        self, word: str, target_language: str = "ru"
    ) -> dict[str, str | None]:
        """
        Перевести слово с чешского на целевой язык.

        Args:
            word: Слово для перевода (чешское)
            target_language: Язык перевода (ru или uk)

        Returns:
            dict: Словарь с переводом и фонетикой
                {
                    "translation": "перевод",
                    "phonetics": "фонетика" или None
                }

        Raises:
            ValueError: Если язык не поддерживается
        """
        if target_language not in self.LANGUAGE_MAP:
            raise ValueError(
                f"Unsupported target language: {target_language}. "
                f"Supported: {list(self.LANGUAGE_MAP.keys())}"
            )

        try:
            # Создаем переводчик: чешский -> целевой язык
            target_lang = self.LANGUAGE_MAP[target_language]
            translator = GoogleTranslator(source="cs", target=target_lang)

            # Переводим слово (deep-translator синхронный, запускаем в executor)
            translation = await asyncio.to_thread(translator.translate, word)

            self.log.info(
                "word_translated",
                word=word,
                target_language=target_language,
                translation=translation,
            )

            return {
                "translation": translation,
                "phonetics": None,  # TODO: добавить фонетику если нужно
            }

        except Exception as e:
            self.log.error(
                "translation_error",
                word=word,
                target_language=target_language,
                error=str(e),
                exc_info=True,
            )
            raise ValueError(f"Failed to translate word: {str(e)}")

    async def translate_batch(
        self, words: list[str], target_language: str = "ru"
    ) -> list[dict[str, str | None]]:
        """
        Перевести несколько слов одновременно.

        Args:
            words: Список слов для перевода
            target_language: Язык перевода (ru или uk)

        Returns:
            list: Список словарей с переводами
        """
        results = []
        for word in words:
            try:
                result = await self.translate_word(word, target_language)
                results.append(result)
            except Exception as e:
                self.log.warning(
                    "batch_translation_skipped",
                    word=word,
                    error=str(e),
                )
                # Добавляем None для неудачных переводов
                results.append({"translation": None, "phonetics": None})

        return results
