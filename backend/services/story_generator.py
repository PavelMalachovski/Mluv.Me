"""
Story Generator Service for personalized Czech stories.

Генерирует персонализированные истории на чешском.
"""

import json
from typing import Literal

import structlog

from backend.services.openai_client import OpenAIClient

logger = structlog.get_logger(__name__)

CzechLevel = Literal["beginner", "intermediate", "advanced", "native"]


# Темы историй
STORY_THEMES = {
    "adventure": {
        "name_cs": "🏔️ Dobrodružství",
        "name_ru": "🏔️ Приключение",
        "prompts": ["cestování", "horská túra", "záhada", "hledání pokladu"],
    },
    "daily_life": {
        "name_cs": "🏠 Každodenní život",
        "name_ru": "🏠 Повседневная жизнь",
        "prompts": ["nakupování", "v hospodě", "na návštěvě", "den v Praze"],
    },
    "humor": {
        "name_cs": "😂 Humor",
        "name_ru": "😂 Юмор",
        "prompts": ["vtipná příhoda", "komická situace", "český humor"],
    },
    "romance": {
        "name_cs": "❤️ Romantika",
        "name_ru": "❤️ Романтика",
        "prompts": ["první setkání", "romantická večeře", "výlet ve dvou"],
    },
    "history": {
        "name_cs": "🏰 Historie",
        "name_ru": "🏰 История",
        "prompts": ["Praha ve středověku", "české legendy", "historické osobnosti"],
    },
}


class StoryGenerator:
    """
    Генератор персонализированных историй на чешском.

    Создаёт истории адаптированные под уровень пользователя.
    """

    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client
        self.logger = logger.bind(service="story_generator")

    def get_available_themes(self) -> list[dict]:
        """Получить доступные темы."""
        return [
            {
                "id": theme_id,
                "name_cs": theme["name_cs"],
                "name_ru": theme["name_ru"],
            }
            for theme_id, theme in STORY_THEMES.items()
        ]

    async def generate_story(
        self,
        user_id: int,
        theme: str = "daily_life",
        level: CzechLevel = "beginner",
        word_count: int = 150,
        user_vocabulary: list[str] | None = None,
    ) -> dict:
        """
        Сгенерировать персонализированную историю.

        Args:
            user_id: ID пользователя
            theme: Тема истории
            level: Уровень чешского
            word_count: Желаемая длина
            user_vocabulary: Слова которые знает пользователь

        Returns:
            dict: История с вопросами и словарём
        """
        self.logger.info(
            "generating_story",
            user_id=user_id,
            theme=theme,
            level=level,
            word_count=word_count,
        )

        # Определяем сложность языка
        level_instructions = {
            "beginner": "Používej POUZE jednoduchou slovní zásobu úrovně A1-A2. Krátké věty, jasná slovesa. Max 10 slov na větu.",
            "intermediate": "Používej slovní zásobu úrovně B1-B2. Můžeš používat složitější gramatiku.",
            "advanced": "Používej pokročilou slovní zásobu B2-C1. Složitější větná stavba.",
            "native": "Piš jako pro rodilého mluvčího. Idiomy, složité struktury.",
        }

        theme_info = STORY_THEMES.get(theme, STORY_THEMES["daily_life"])

        # Формируем промпт
        vocabulary_hint = ""
        if user_vocabulary:
            vocabulary_hint = f"\n\nPoužij tato slova, která student zná: {', '.join(user_vocabulary[:10])}"

        system_prompt = f"""Jsi český spisovatel. Napiš krátký příběh v češtině.

ÚROVEŇ: {level_instructions[level]}
TÉMA: {theme_info['name_cs']} - {', '.join(theme_info['prompts'][:2])}
DÉLKA: přibližně {word_count} slov
{vocabulary_hint}

Odpověz ve formátu JSON:
{{
  "title": "Název příběhu",
  "story": "Text příběhu v češtině...",
  "vocabulary": [
    {{"word": "slovo", "translation_ru": "перевод", "example": "příklad ve větě"}}
  ],
  "questions": [
    {{"question_cs": "Otázka k příběhu?", "answer_cs": "Krátká odpověď"}}
  ],
  "moral": "Ponaučení z příběhu (volitelné)"
}}

Pravidla:
- Příběh musí být zajímavý a pozitivní
- Vyber 5-7 důležitých slov pro slovníček
- Přidej 3 jednoduché otázky k příběhu
"""

        try:
            response_text = await self.openai_client.generate_chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Napiš příběh na téma: {theme}"},
                ],
                json_mode=True,
                model="gpt-4o-mini",
            )

            response_data = json.loads(response_text)

            self.logger.info(
                "story_generated",
                user_id=user_id,
                title=response_data.get("title", "Untitled"),
            )

            return {
                "title": response_data.get("title", "Příběh"),
                "story": response_data.get("story", ""),
                "theme": theme,
                "level": level,
                "vocabulary": response_data.get("vocabulary", []),
                "questions": response_data.get("questions", []),
                "moral": response_data.get("moral"),
                "word_count": len(response_data.get("story", "").split()),
            }

        except Exception as e:
            self.logger.error("story_generation_failed", error=str(e))
            raise

    async def generate_continuation(
        self,
        story: str,
        level: CzechLevel = "beginner",
    ) -> dict:
        """
        Сгенерировать продолжение истории.

        Args:
            story: Начало истории
            level: Уровень чешского

        Returns:
            dict: Продолжение истории
        """
        level_instructions = {
            "beginner": "Používej jednoduchou slovní zásobu A1-A2.",
            "intermediate": "Používej slovní zásobu B1-B2.",
            "advanced": "Používej pokročilou slovní zásobu B2-C1.",
            "native": "Piš jako rodilý mluvčí.",
        }

        system_prompt = f"""Pokračuj v příběhu v češtině.

ÚROVEŇ: {level_instructions[level]}

Pravidla:
- Zachovej styl a úroveň původního příběhu
- Přidej zajímavý zvrat
- Délka: 50-100 slov

Odpověz ve formátu JSON:
{{
  "continuation": "Pokračování příběhu...",
  "new_vocabulary": [
    {{"word": "slovo", "translation_ru": "перевод"}}
  ]
}}
"""

        try:
            response_text = await self.openai_client.generate_chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Původní příběh:\n{story}\n\nPokračuj..."},
                ],
                json_mode=True,
                model="gpt-4o-mini",
            )

            response_data = json.loads(response_text)

            return {
                "continuation": response_data.get("continuation", ""),
                "new_vocabulary": response_data.get("new_vocabulary", []),
            }

        except Exception as e:
            self.logger.error("continuation_generation_failed", error=str(e))
            raise
