"""
Личность Хонзика - веселого типичного чеха, помогающего учить чешский язык.

Реализует:
- Базовый промпт с характером Хонзика
- 3 стиля общения (Friendly, Tutor, Casual)
- 3 уровня исправлений (Minimal, Balanced, Detailed)
- Поддержка русского и украинского языков для объяснений
- Контекст разговора (последние 5 сообщений)
"""

import json
from typing import Literal

import structlog

from backend.services.openai_client import OpenAIClient

logger = structlog.get_logger(__name__)

# Типы для параметров
ConversationStyle = Literal["friendly", "tutor", "casual"]
CorrectionsLevel = Literal["minimal", "balanced", "detailed"]
CzechLevel = Literal["beginner", "intermediate", "advanced", "native"]
UILanguage = Literal["ru", "uk"]


class HonzikPersonality:
    """
    Личность Хонзика - веселого чеха, который помогает учить чешский.

    Attributes:
        openai_client: Клиент для работы с OpenAI API
    """

    def __init__(self, openai_client: OpenAIClient):
        """
        Инициализация личности Хонзика.

        Args:
            openai_client: Клиент OpenAI для генерации ответов
        """
        self.openai_client = openai_client
        self.logger = logger.bind(service="honzik_personality")

    def _get_base_prompt(
        self,
        level: CzechLevel,
        corrections_level: CorrectionsLevel,
        ui_language: UILanguage,
        style: ConversationStyle,
    ) -> str:
        """
        Получить базовый промпт Хонзика с учётом параметров.

        Args:
            level: Уровень чешского языка студента
            corrections_level: Уровень детализации исправлений
            ui_language: Язык интерфейса (ru или uk)
            style: Стиль общения Хонзика

        Returns:
            str: Системный промпт для GPT
        """
        # Описание уровней на чешском
        level_descriptions = {
            "beginner": "Začátečník - učí se základy",
            "intermediate": "Středně pokročilý - už rozumí základům",
            "advanced": "Pokročilý - mluví dobře, potřebuje praxi",
            "native": "Rodilý mluvčí - perfekcionismus",
        }

        # Описание стилей общения
        style_descriptions = {
            "friendly": "Buď přátelský a povzbuzující. Minimum technických vysvětlení, "
                       "maximum pozitivity. Pokračuj v konverzaci přirozeně.",
            "tutor": "Buď jako učitel - strukturované rady, vysvětlení gramatických pravidel, "
                    "doporučení pro výslovnost. Více technických detailů.",
            "casual": "Buď neformální jako kamarád v hospodě. Minimum oprav (jen kritické), "
                     "maximum legrace a přirozené konverzace. Mluv o pivu a klobáskách!",
        }

        # Описание уровней исправлений
        corrections_descriptions = {
            "minimal": "Opravuj POUZE kritické chyby, které brání porozumění. "
                      "Většinu chyb ignoruj, důležitá je plynulá konverzace.",
            "balanced": "Opravuj důležité chyby a občas vysvětli pravidlo. "
                       "Balanc mezi učením a konverzací.",
            "detailed": "Opravuj VŠECHNY chyby s podrobnými vysvětleními gramatických pravidel. "
                       "Pro pokročilé studenty hledající perfekcionismus.",
        }

        # Язык для объяснений
        explanation_lang = "ruštině" if ui_language == "ru" else "ukrajinštině"

        base_prompt = f"""Ty jsi Honzík - typický veselý Čech, který pomáhá lidem učit se česky.

TVOJE CHARAKTERISTIKA:
- Jsi přátelský, vtipný a dobrosrdečný Čech
- Miluješ české pivo 🍺, knedlíky 🥟 a hokej 🏒
- Rád vyprávíš zajímavé příběhy o Praze a České republice
- Znáš všechny české tradice a svátky
- Jsi trochu ironický, ale vždy podporující
- Používáš typické české výrazy (Ahoj!, Nazdar!, Výborně!, Prima!)

INFORMACE O STUDENTOVI:
- Úroveň češtiny: {level_descriptions[level]}
- Styl konverzace: {style}
- Úroveň oprav: {corrections_level}
- Jazyk vysvětlení: {explanation_lang}

TVŮJ STYL KOMUNIKACE:
{style_descriptions[style]}

JAK OPRAVOVAT CHYBY:
{corrections_descriptions[corrections_level]}

TVŮJ ÚKOL:
1. Analyzuj text studenta v češtině
2. Identifikuj gramatické a výslovnostní chyby podle úrovně oprav
3. Poskytni opravy s vysvětlením v jazyce studenta ({explanation_lang})
4. Ohodnoť správnost od 0-100 (0 = hodně chyb, 100 = perfektní)
5. Odpověz přirozeně jako Honzík a pokračuj v zajímavé konverzaci
6. Buď pozitivní a povzbuzující!

ODPOVĚZ VE FORMÁTU JSON:
{{
  "honzik_response": "Tvoje odpověď jako Honzík v češtině - přirozená konverzace",
  "corrected_text": "Opravený text studenta (pokud byly chyby)",
  "mistakes": [
    {{
      "original": "špatný text",
      "corrected": "správný text",
      "explanation": "vysvětlení v jazyce studenta ({explanation_lang}) proč je to špatně"
    }}
  ],
  "correctness_score": 85,
  "suggestion": "jeden krátký tip pro studenta v jazyce studenta"
}}

Pamatuj: Buď Honzík - veselý, přátelský Čech, který miluje svou zemi a rád pomáhá! 🇨🇿"""

        return base_prompt

    def _format_conversation_history(
        self, history: list[dict[str, str]]
    ) -> str:
        """
        Форматировать историю разговора для контекста.

        Args:
            history: Список сообщений {"role": "user/assistant", "text": "..."}

        Returns:
            str: Отформатированная история
        """
        if not history:
            return "Žádná předchozí historie."

        formatted = []
        for msg in history[-5:]:  # Только последние 5 сообщений
            role = "Student" if msg["role"] == "user" else "Honzík"
            formatted.append(f"{role}: {msg['text']}")

        return "\n".join(formatted)

    async def generate_response(
        self,
        user_text: str,
        level: CzechLevel,
        style: ConversationStyle,
        corrections_level: CorrectionsLevel,
        ui_language: UILanguage,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> dict:
        """
        Сгенерировать ответ Хонзика с исправлениями и оценкой.

        Args:
            user_text: Текст пользователя на чешском
            level: Уровень чешского языка
            style: Стиль общения (friendly/tutor/casual)
            corrections_level: Уровень исправлений (minimal/balanced/detailed)
            ui_language: Язык интерфейса (ru/uk)
            conversation_history: История разговора (последние 5 сообщений)

        Returns:
            dict: {
                "honzik_response": str,
                "corrected_text": str,
                "mistakes": list[dict],
                "correctness_score": int,
                "suggestion": str
            }

        Raises:
            ValueError: При некорректном JSON ответе от GPT
            APIError: При ошибке OpenAI API
        """
        self.logger.info(
            "generating_honzik_response",
            level=level,
            style=style,
            corrections_level=corrections_level,
            ui_language=ui_language,
            user_text_length=len(user_text),
        )

        if conversation_history is None:
            conversation_history = []

        # Формируем промпт
        system_prompt = self._get_base_prompt(
            level=level,
            corrections_level=corrections_level,
            ui_language=ui_language,
            style=style,
        )

        # Добавляем историю в промпт
        history_text = self._format_conversation_history(conversation_history)

        user_prompt = f"""Přepis studenta: {user_text}

Historie konverzace (poslední 5 zpráv):
{history_text}

Analyzuj text studenta a odpověz ve formátu JSON podle instrukcí výše."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            # Генерируем ответ от GPT в JSON mode
            response_text = await self.openai_client.generate_chat_completion(
                messages=messages,
                json_mode=True,
            )

            # Парсим JSON
            response_data = json.loads(response_text)

            # Валидация обязательных полей
            required_fields = [
                "honzik_response",
                "corrected_text",
                "mistakes",
                "correctness_score",
                "suggestion",
            ]

            for field in required_fields:
                if field not in response_data:
                    self.logger.error(
                        "missing_field_in_response",
                        field=field,
                        response=response_data,
                    )
                    raise ValueError(f"Missing required field: {field}")

            # Валидация score
            score = response_data["correctness_score"]
            if not isinstance(score, (int, float)) or not (0 <= score <= 100):
                self.logger.warning(
                    "invalid_score",
                    score=score,
                )
                response_data["correctness_score"] = max(0, min(100, int(score)))

            self.logger.info(
                "honzik_response_generated",
                correctness_score=response_data["correctness_score"],
                mistakes_count=len(response_data["mistakes"]),
            )

            return response_data

        except json.JSONDecodeError as e:
            self.logger.error(
                "json_decode_error",
                error=str(e),
                response_text=response_text[:200],
            )
            raise ValueError(f"Invalid JSON response from GPT: {e}")

        except Exception as e:
            self.logger.error(
                "honzik_response_failed",
                error=str(e),
            )
            raise

    def get_welcome_message(self, ui_language: UILanguage) -> str:
        """
        Получить приветственное сообщение от Хонзика.

        Args:
            ui_language: Язык интерфейса (ru/uk)

        Returns:
            str: Приветственное сообщение
        """
        messages = {
            "ru": (
                "Ahoj! 🇨🇿 Я Хонзик - твой веселый чешский друг!\n\n"
                "Я помогу тебе выучить чешский язык через живое общение. "
                "Говори со мной по-чешски, и я буду тебя поправлять и поддерживать!\n\n"
                "Люблю пиво 🍺, кнедлики 🥟, хоккей 🏒 и Прагу ❤️\n\n"
                "Давай практиковать! Отправь мне голосовое сообщение на чешском! 🎤"
            ),
            "uk": (
                "Ahoj! 🇨🇿 Я Хонзік - твій веселий чеський друг!\n\n"
                "Я допоможу тобі вивчити чеську мову через живе спілкування. "
                "Говори зі мною чеською, і я буду тебе виправляти та підтримувати!\n\n"
                "Люблю пиво 🍺, кнедлики 🥟, хокей 🏒 і Прагу ❤️\n\n"
                "Давай практикувати! Надішли мені голосове повідомлення чеською! 🎤"
            ),
        }
        return messages[ui_language]

