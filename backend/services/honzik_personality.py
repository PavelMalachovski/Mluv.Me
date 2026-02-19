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
from functools import lru_cache
from typing import Literal

import structlog

from backend.services.openai_client import OpenAIClient
from backend.services.cache_service import cache_service
from backend.services.model_selector import model_selector

logger = structlog.get_logger(__name__)

# Типы для параметров
ConversationStyle = Literal["friendly", "tutor", "casual"]
CorrectionsLevel = Literal["minimal", "balanced", "detailed"]
CzechLevel = Literal["beginner", "intermediate", "advanced", "native"]
NativeLanguage = Literal["ru", "uk", "pl", "sk"]


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

    @staticmethod
    @lru_cache(maxsize=64)
    def _get_base_prompt(
        level: CzechLevel,
        corrections_level: CorrectionsLevel,
        native_language: NativeLanguage,
        style: ConversationStyle,
    ) -> str:
        """
        Получить базовый промпт Хонзика с учётом параметров.

        Новая концепция: полное погружение в чешский язык.
        - Весь интерфейс на чешском
        - Объяснения ошибок на простом чешском + перевод на родной язык

        Args:
            level: Уровень чешского языка студента
            corrections_level: Уровень детализации исправлений
            native_language: Родной язык пользователя (для объяснений)
            style: Стиль общения Хонзика

        Returns:
            str: Системный промпт для GPT
        """
        # Описание уровней на чешском с указанием словарного запаса
        level_descriptions = {
            "beginner": "Začátečník (A2-B1) - učí se základy. Používej jednoduchá slova a fráze z úrovně A2-B1. "
                       "Vyhni se složitým výrazům a odborným termínům. Mluv jednoduše a jasně.",
            "intermediate": "Středně pokročilý (B1-B2) - už rozumí základům. Používej slova z úrovně B1-B2. "
                          "Můžeš použít běžné idiomy a složitější gramatické struktury.",
            "advanced": "Pokročilý (B2-C1) - mluví dobře, potřebuje praxi. Používej pokročilou slovní zásobu z úrovně B2-C1. "
                       "Můžeš používat složitější výrazy, idiomy a odborné termíny.",
            "native": "Rodilý mluvčí (C2) - perfekcionismus. Používej nejpokročilejší slovní zásobu na úrovni C2. "
                     "Můžeš používat všechny jazykové prostředky včetně složitých idiomů a odborných termínů.",
        }

        # Описание стилей общения с напоминанием о постоянстве
        style_descriptions = {
            "friendly": "Buď přátelský a povzbuzující. Minimum technických vysvětlení, "
                       "maximum pozitivity. Pokračuj v konverzaci přirozeně. "
                       "DŮLEŽITÉ: Vždy dodržuj tento styl - NEMĚŇ ho během konverzace!",
            "tutor": "Buď jako učitel - strukturované rady, vysvětlení gramatických pravidel, "
                    "doporučení pro výslovnost. Více technických detailů. "
                    "DŮLEŽITÉ: Vždy dodržuj tento styl - NEMĚŇ ho během konverzace!",
            "casual": "Buď neformální jako kamarád v hospodě. Minimum oprav (jen kritické), "
                     "maximum legrace a přirozené konverzace. Mluv o pivu a klobáskách! "
                     "DŮLEŽITÉ: Vždy dodržuj tento styl - NEMĚŇ ho během konverzace!",
        }

        # Описание уровней исправлений
        corrections_descriptions = {
            "minimal": "Opravuj POUZE kritické chyby, které VÝRAZNĚ brání porozumění. "
                      "IGNORUJ: drobné gramatické chyby, chybějící čárky, volbu slov (pokud je význam jasný), "
                      "malé chyby v koncovkách, pokud nebrání porozumění. "
                      "Opravuj POUZE: zásadní gramatické chyby, které mění význam, "
                      "chyby v základních slovech, které brání porozumění celé větě. "
                      "Důležitá je plynulá konverzace, ne perfektní gramatika!",
            "balanced": "Opravuj důležité chyby a občas vysvětli pravidlo. "
                       "Balanc mezi učením a konverzací. Opravuj chyby, které ovlivňují význam nebo jsou časté.",
            "detailed": "Opravuj VŠECHNY chyby s podrobnými vysvětleními gramatických pravidel. "
                       "Pro pokročilé studenty hledající perfekcionismus. "
                       "Věnuj pozornost i drobným chybám v interpunkci a stylu.",
        }

        # Название родного языка для объяснений
        native_lang_names = {
            "ru": "ruština",
            "uk": "ukrajinština",
            "pl": "polština",
            "sk": "slovenština",
        }
        native_lang_name = native_lang_names.get(native_language, "ruština")

        # ==========================================
        # COMPACT prompt for minimal/balanced (saves ~800 tokens → 1-2 sec faster)
        # FULL prompt with grammar rules only for detailed corrections
        # ==========================================
        grammar_rules_block = ""
        if corrections_level == "detailed":
            grammar_rules_block = """
GRAMATICKÁ PRAVIDLA (Internetová jazyková příručka ÚJČ):
Když student udělá chybu, odkazuj na konkrétní pravidla:
- Vyjmenovaná slova (B, L, M, P, S, V, Z)
- Pravopis: bě/bje, mě/mně, ú/ů, i/y po obojetných souhláskách
- Interpunkce: čárky ve vedlejších větách, před a/ale
- Velká písmena: vlastní jména, přídavná jména od nich odvozená
- Tvarosloví: skloňování podstatných a přídavných jmen, časování sloves
- Skladba: slovosled, shoda přísudku s podmětem, předložky s/z, v/na
Když je to relevantní, zmíň mnemotechnickou pomůcku nebo příklad z příručky.
"""

        base_prompt = f"""Ty jsi Honzík - veselý Čech, který pomáhá učit se česky.
Jsi přátelský, vtipný, miluješ pivo 🍺, knedlíky 🥟 a hokej 🏒. Používáš výrazy jako Ahoj!, Nazdar!, Výborně!

STUDENT: {level_descriptions[level]}
Styl: {style} | Opravy: {corrections_level} | Rodný jazyk: {native_lang_name}

STYL: {style_descriptions[style]}

OPRAVY: {corrections_descriptions[corrections_level]}
Vysvětlení piš JEDNODUŠE česky na úrovni A2.
{grammar_rules_block}
ÚKOL: Analyzuj text, oprav chyby, ohodnoť 0-100, odpověz přirozeně jako Honzík. Buď pozitivní! Dodržuj styl a slovní zásobu studenta.

ODPOVĚZ JSON:
{{{{
  "honzik_response": "odpověď Honzíka v češtině",
  "corrected_text": "opravený text studenta",
  "mistakes": [{{{{
    "original": "špatný text",
    "corrected": "správný text",
    "explanation_cs": "vysvětlení česky max 15 slov"
  }}}}],
  "correctness_score": 85,
  "suggestion": "krátký tip v jednoduché češtině"
}}}}"""

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
        native_language: NativeLanguage,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> dict:
        """
        Сгенерировать ответ Хонзика с исправлениями и оценкой.

        Args:
            user_text: Текст пользователя на чешском
            level: Уровень чешского языка
            style: Стиль общения (friendly/tutor/casual)
            corrections_level: Уровень исправлений (minimal/balanced/detailed)
            native_language: Родной язык пользователя (ru/uk/pl/sk)
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
            native_language=native_language,
            user_text_length=len(user_text),
        )

        if conversation_history is None:
            conversation_history = []

        # Cache ONLY the first greeting message (when there's no conversation history)
        # This saves API calls for the same initial greeting
        should_cache = len(conversation_history) == 0

        if should_cache:
            settings_dict = {
                "czech_level": level,
                "correction_level": corrections_level,
                "conversation_style": style,
                "native_language": native_language,
            }
            cached_response = await cache_service.get_cached_honzik_response(
                user_text, settings_dict
            )
            if cached_response:
                self.logger.info("using_cached_honzik_greeting")
                return cached_response

        # Формируем промпт
        system_prompt = self._get_base_prompt(
            level=level,
            corrections_level=corrections_level,
            native_language=native_language,
            style=style,
        )

        # Only include history block when there's actual conversation history
        if conversation_history:
            history_text = self._format_conversation_history(conversation_history)
            user_prompt = (
                f"Přepis studenta: {user_text}\n\n"
                f"Historie konverzace (poslední 5 zpráv):\n{history_text}\n\n"
                "Analyzuj text studenta a odpověz ve formátu JSON podle instrukcí výše."
            )
        else:
            user_prompt = (
                f"Přepis studenta: {user_text}\n\n"
                "Analyzuj text studenta a odpověz ve formátu JSON podle instrukcí výše."
            )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Оптимизируем историю для уменьшения токенов
        optimized_messages = self.openai_client.optimize_conversation_history(
            messages,
            max_tokens=2000,  # Разумный лимит для контекста
        )

        # Логируем экономию токенов
        original_tokens = self.openai_client.estimate_messages_tokens(messages)
        optimized_tokens = self.openai_client.estimate_messages_tokens(optimized_messages)

        if original_tokens != optimized_tokens:
            self.logger.info(
                "tokens_optimized",
                original=original_tokens,
                optimized=optimized_tokens,
                saved=original_tokens - optimized_tokens,
            )

        # Выбираем оптимальную модель на основе анализа текста
        selected_model, model_reason = model_selector.select_model(
            user_text=user_text,
            czech_level=level,
            corrections_level=corrections_level,
            history_length=len(conversation_history),
        )

        self.logger.info(
            "model_selected_for_response",
            model=selected_model,
            reason=model_reason,
        )

        try:
            # Генерируем ответ от GPT в JSON mode
            # max_tokens=400 prevents GPT from generating overly long responses
            # Typical Honzík response is 150-300 tokens; 400 gives margin
            response_text = await self.openai_client.generate_chat_completion(
                messages=optimized_messages,
                json_mode=True,
                model=selected_model,
                max_tokens=400,
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

            # Fallback for corrected_text if None or empty
            if not response_data.get("corrected_text"):
                self.logger.warning(
                    "corrected_text_missing_using_original",
                    original_text=user_text[:50],
                )
                response_data["corrected_text"] = user_text

            self.logger.info(
                "honzik_response_generated",
                correctness_score=response_data["correctness_score"],
                mistakes_count=len(response_data["mistakes"]),
            )

            # Cache ONLY first greeting (no conversation history)
            if should_cache:
                await cache_service.cache_honzik_response(
                    user_text, settings_dict, response_data
                )
                self.logger.info("honzik_greeting_cached")

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

    def get_welcome_message(self) -> str:
        """
        Получить приветственное сообщение от Хонзика.

        Теперь всегда на чешском (Language Immersion).

        Returns:
            str: Приветственное сообщение на чешском
        """
        return (
            "Ahoj! 🇨🇿 Jsem Honzík - tvůj veselý český kamarád!\n\n"
            "Pomohu ti naučit se česky přes živou konverzaci. "
            "Mluv se mnou česky a já tě budu opravovat a podporovat!\n\n"
            "Miluji pivo 🍺, knedlíky 🥟, hokej 🏒 a Prahu ❤️\n\n"
            "Pojďme procvičovat! Pošli mi hlasovou zprávu v češtině! 🎤"
        )


