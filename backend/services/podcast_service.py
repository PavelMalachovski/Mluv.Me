"""
Podcast Service for Honzík's AI-generated podcasts.

Генерирует еженедельные подкасты адаптированные под уровень пользователя.
"""

import json
from datetime import datetime, timezone
from typing import Literal

import structlog

from backend.services.openai_client import OpenAIClient

logger = structlog.get_logger(__name__)

CzechLevel = Literal["beginner", "intermediate", "advanced", "native"]


# Темы подкастов
PODCAST_THEMES = {
    "news": {
        "name_cs": "📰 Zprávy",
        "name_ru": "📰 Новости",
        "description_cs": "Jednoduché české zprávy",
    },
    "culture": {
        "name_cs": "🎭 Kultura",
        "name_ru": "🎭 Культура",
        "description_cs": "České tradice a kultura",
    },
    "travel": {
        "name_cs": "✈️ Cestování",
        "name_ru": "✈️ Путешествия",
        "description_cs": "Tipy na výlety po Česku",
    },
    "food": {
        "name_cs": "🍽️ Jídlo",
        "name_ru": "🍽️ Еда",
        "description_cs": "České recepty a restaurace",
    },
    "history": {
        "name_cs": "🏰 Historie",
        "name_ru": "🏰 История",
        "description_cs": "Příběhy z české historie",
    },
    "language": {
        "name_cs": "📚 Čeština",
        "name_ru": "📚 Чешский язык",
        "description_cs": "Tipy pro učení češtiny",
    },
}


class PodcastService:
    """
    Сервис для AI-генерируемых подкастов Хонзика.

    Создаёт еженедельные эпизоды адаптированные под уровень.
    """

    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client
        self.logger = logger.bind(service="podcast_service")

        # In-memory хранилище эпизодов (в продакшене заменить на БД)
        self._episodes: list[dict] = []
        self._user_listened: dict[int, list[str]] = {}

    def get_available_themes(self) -> list[dict]:
        """Получить доступные темы подкастов."""
        return [
            {
                "id": theme_id,
                "name_cs": theme["name_cs"],
                "name_ru": theme["name_ru"],
                "description_cs": theme["description_cs"],
            }
            for theme_id, theme in PODCAST_THEMES.items()
        ]

    async def generate_episode(
        self,
        theme: str = "news",
        level: CzechLevel = "beginner",
        duration_minutes: int = 5,
    ) -> dict:
        """
        Сгенерировать эпизод подкаста.

        Args:
            theme: Тема подкаста
            level: Уровень чешского
            duration_minutes: Длительность в минутах

        Returns:
            dict: Эпизод с текстом, словарём и аудио
        """
        self.logger.info(
            "generating_podcast_episode",
            theme=theme,
            level=level,
            duration=duration_minutes,
        )

        theme_info = PODCAST_THEMES.get(theme, PODCAST_THEMES["news"])

        # Рассчитываем количество слов (~150 слов/минуту для медленной речи)
        target_words = duration_minutes * 100  # Медленнее для учащихся

        level_instructions = {
            "beginner": "Mluv VELMI POMALU a používej POUZE jednoducho slovní zásobu A1-A2. Krátké věty. Opakuj důležitá slova.",
            "intermediate": "Mluv středně rychle, slovní zásoba B1-B2. Můžeš používat složitější struktury.",
            "advanced": "Mluv přirozeně, pokročilá slovní zásoba B2-C1.",
            "native": "Mluv jako rodilý mluvčí, běžné tempo.",
        }

        system_prompt = f"""Jsi Honzík - veselý český podcaster. Napiš skript pro podcast.

TÉMA: {theme_info['name_cs']} - {theme_info['description_cs']}
ÚROVEŇ: {level_instructions[level]}
DÉLKA: přibližně {target_words} slov

Pravidla:
- Začni pozdravem: "Ahoj! Tady Honzík s novým podcastem!"
- Buď přátelský a povzbuzující
- Používej typické české výrazy
- Zakonči: "To je pro dnešek vše! Měj se hezky a uč se česky! 🇨🇿"

Odpověz ve formátu JSON:
{{
  "title": "Název epizody",
  "script": "Celý text podcastu...",
  "sections": [
    {{"title": "Název sekce", "text": "Text sekce", "duration_seconds": 60}}
  ],
  "vocabulary": [
    {{"word": "slovo", "translation_ru": "перевод", "context": "jak se používá"}}
  ],
  "quiz": [
    {{"question": "Otázka?", "answer": "Odpověď"}}
  ]
}}
"""

        try:
            response_text = await self.openai_client.generate_chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Vytvoř podcast na téma: {theme}"},
                ],
                json_mode=True,
                model="gpt-4o-mini",
            )

            response_data = json.loads(response_text)

            episode_id = f"ep_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

            episode = {
                "id": episode_id,
                "title": response_data.get("title", f"Podcast o {theme}"),
                "theme": theme,
                "theme_name": theme_info["name_cs"],
                "level": level,
                "script": response_data.get("script", ""),
                "sections": response_data.get("sections", []),
                "vocabulary": response_data.get("vocabulary", []),
                "quiz": response_data.get("quiz", []),
                "duration_minutes": duration_minutes,
                "word_count": len(response_data.get("script", "").split()),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            # Сохраняем эпизод
            self._episodes.append(episode)

            self.logger.info(
                "podcast_episode_generated",
                episode_id=episode_id,
                title=episode["title"],
            )

            return episode

        except Exception as e:
            self.logger.error("podcast_generation_failed", error=str(e))
            raise

    async def generate_audio(
        self,
        episode_id: str,
        script: str,
        speed: float = 0.85,  # Медленнее для учащихся
    ) -> bytes | None:
        """
        Сгенерировать аудио для эпизода.

        Args:
            episode_id: ID эпизода
            script: Текст скрипта
            speed: Скорость речи (0.25 - 4.0)

        Returns:
            bytes | None: Аудио данные или None
        """
        try:
            audio = await self.openai_client.generate_speech(
                text=script,
                voice="onyx",  # Мужской голос для Хонзика
                speed=speed,
                use_cache=False,  # Не кешируем длинные подкасты
            )

            self.logger.info(
                "podcast_audio_generated",
                episode_id=episode_id,
                audio_size=len(audio),
            )

            return audio

        except Exception as e:
            self.logger.error("podcast_audio_failed", error=str(e))
            return None

    def get_available_episodes(
        self,
        user_id: int | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """
        Получить список доступных эпизодов.

        Args:
            user_id: ID пользователя (для фильтрации прослушанных)
            limit: Максимальное количество

        Returns:
            list: Список эпизодов
        """
        episodes = sorted(
            self._episodes,
            key=lambda x: x["created_at"],
            reverse=True,
        )[:limit]

        listened = self._user_listened.get(user_id, []) if user_id else []

        return [
            {
                **ep,
                "is_listened": ep["id"] in listened,
            }
            for ep in episodes
        ]

    def mark_as_listened(
        self,
        user_id: int,
        episode_id: str,
    ) -> bool:
        """Отметить эпизод как прослушанный."""
        if user_id not in self._user_listened:
            self._user_listened[user_id] = []

        if episode_id not in self._user_listened[user_id]:
            self._user_listened[user_id].append(episode_id)
            return True

        return False

    def get_episode(self, episode_id: str) -> dict | None:
        """Получить эпизод по ID."""
        for ep in self._episodes:
            if ep["id"] == episode_id:
                return ep
        return None
