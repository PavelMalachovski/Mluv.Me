"""
Scenario Service for role-play scenarios.

Реализует интерактивные мини-диалоги для реальных ситуаций:
- V hospodě (в пабе)
- U lékaře (у врача)
- Na cizinecké policii (в полиции для иностранцев)
- Pracovní pohovor (собеседование)
- И другие...
"""

import json
from datetime import datetime, timezone
from typing import Literal

import structlog

from backend.services.openai_client import OpenAIClient

logger = structlog.get_logger(__name__)

# Типы
ScenarioId = Literal[
    "v_hospode",
    "u_lekare",
    "na_cizinecke_policii",
    "pracovni_pohovor",
    "pronajem_bytu",
    "v_tramvaji",
    "v_obchode",
    "telefonni_hovor",
]

CzechLevel = Literal["beginner", "intermediate", "advanced", "native"]

# Определение всех сценариев
SCENARIOS = {
    "v_hospode": {
        "name_cs": "🍺 V hospodě",
        "name_ru": "В пабе",
        "level": "A1-A2",
        "min_level": "beginner",
        "situation_cs": "Objednáváš pivo a jídlo v typické české hospodě.",
        "situation_ru": "Ты заказываешь пиво и еду в типичном чешском пабе.",
        "honzik_role": "Číšník (barman)",
        "user_role": "Zákazník",
        "steps": 5,
        "vocabulary": [
            "pivo", "plzeň", "ležák", "tmavé", "světlé",
            "jídlo", "svíčková", "knedlíky", "guláš",
            "platit", "účet", "hotově", "kartou",
        ],
        "hints": [
            "Zkus říct: 'Dobrý den, jedno pivo, prosím.'",
            "Zeptej se na jídlo: 'Co máte k jídlu?'",
            "Objednej si konkrétní jídlo.",
            "Popros o účet: 'Účet, prosím.'",
            "Rozluč se: 'Děkuji, na shledanou!'",
        ],
        "success_achievement": "🍺 Hospodský znalec",
        "reward_stars": 10,
    },
    "u_lekare": {
        "name_cs": "🏥 U lékaře",
        "name_ru": "У врача",
        "level": "A2-B1",
        "min_level": "beginner",
        "situation_cs": "Přišel jsi k lékaři s bolestí hlavy.",
        "situation_ru": "Ты пришёл к врачу с головной болью.",
        "honzik_role": "Lékař",
        "user_role": "Pacient",
        "steps": 6,
        "vocabulary": [
            "bolest", "hlava", "teplota", "kašel", "rýma",
            "lék", "recept", "neschopenka", "pojištění",
            "vyšetření", "diagnóza",
        ],
        "hints": [
            "Pozdrav a řekni, co tě trápí.",
            "Popiš své příznaky podrobněji.",
            "Odpověz na otázky lékaře.",
            "Zeptej se, co máš dělat.",
            "Zeptej se na léky.",
            "Poděkuj a rozluč se.",
        ],
        "success_achievement": "🏥 Zdravotní expert",
        "reward_stars": 15,
    },
    "na_cizinecke_policii": {
        "name_cs": "🏦 Na cizinecké policii",
        "name_ru": "В полиции для иностранцев",
        "level": "B1",
        "min_level": "intermediate",
        "situation_cs": "Podáváš žádost o povolení k pobytu (ВНЖ).",
        "situation_ru": "Ты подаёшь заявление на ВНЖ.",
        "honzik_role": "Úředník na cizinecké policii",
        "user_role": "Žadatel o pobyt",
        "steps": 7,
        "vocabulary": [
            "pobyt", "vízum", "doklady", "pas", "formulář",
            "žádost", "potvrzení", "fotografie", "poplatek",
            "přechodný", "trvalý", "prodloužení",
        ],
        "hints": [
            "Pozdrav a řekni, proč jsi přišel.",
            "Předlož své dokumenty.",
            "Odpověz na dotazy úředníka.",
            "Zeptej se na postup a termíny.",
            "Zeptej se na poplatky.",
            "Zeptej se, kdy dostaneš odpověď.",
            "Poděkuj a rozluč se.",
        ],
        "success_achievement": "🏦 Úřední mistr",
        "reward_stars": 20,
    },
    "pracovni_pohovor": {
        "name_cs": "💼 Pracovní pohovor",
        "name_ru": "Собеседование на работу",
        "level": "B1-B2",
        "min_level": "intermediate",
        "situation_cs": "Jsi na pracovním pohovoru pro pozici programátora.",
        "situation_ru": "Ты на собеседовании на позицию программиста.",
        "honzik_role": "HR manažer",
        "user_role": "Uchazeč o práci",
        "steps": 6,
        "vocabulary": [
            "zkušenosti", "vzdělání", "praxe", "dovednosti",
            "plat", "benefity", "tým", "projekt",
            "motivace", "kariéra", "nástroje",
        ],
        "hints": [
            "Představ se a řekni něco o sobě.",
            "Popiš své pracovní zkušenosti.",
            "Vysvětli své dovednosti.",
            "Odpověz, proč chceš tuto práci.",
            "Zeptej se na mzdu a benefity.",
            "Poděkuj za pohovor.",
        ],
        "success_achievement": "💼 Kariérní profesionál",
        "reward_stars": 20,
    },
    "pronajem_bytu": {
        "name_cs": "🏠 Pronájem bytu",
        "name_ru": "Аренда квартиры",
        "level": "A2-B1",
        "min_level": "beginner",
        "situation_cs": "Prohlížíš si byt k pronájmu a mluvíš s majitelem.",
        "situation_ru": "Ты осматриваешь квартиру для аренды и разговариваешь с хозяином.",
        "honzik_role": "Majitel bytu",
        "user_role": "Zájemce o pronájem",
        "steps": 5,
        "vocabulary": [
            "byt", "pokoj", "kuchyň", "koupelna", "balkon",
            "nájem", "kauce", "energie", "smlouva",
            "vybavený", "dispozice",
        ],
        "hints": [
            "Pozdrav a řekni, že máš zájem o byt.",
            "Zeptej se na detaily bytu.",
            "Zeptej se na cenu a poplatky.",
            "Zeptej se na podmínky pronájmu.",
            "Řekni, že máš zájem/nemáš zájem.",
        ],
        "success_achievement": "🏠 Realitní znalec",
        "reward_stars": 15,
    },
    "v_tramvaji": {
        "name_cs": "🚋 V tramvaji",
        "name_ru": "В трамвае",
        "level": "A1",
        "min_level": "beginner",
        "situation_cs": "Potřebuješ koupit lístek a zeptat se na cestu.",
        "situation_ru": "Тебе нужно купить билет и узнать дорогу.",
        "honzik_role": "Spolucestující / Řidič",
        "user_role": "Cestující",
        "steps": 4,
        "vocabulary": [
            "lístek", "jízdenka", "zastávka", "přestup",
            "směr", "linka", "validátor", "automat",
        ],
        "hints": [
            "Zeptej se, jak koupit lístek.",
            "Zeptej se na cestu do konkrétního místa.",
            "Zeptej se, kde máš vystoupit.",
            "Poděkuj za pomoc.",
        ],
        "success_achievement": "🚋 Cestovetl",
        "reward_stars": 10,
    },
    "v_obchode": {
        "name_cs": "🛒 V obchodě",
        "name_ru": "В магазине",
        "level": "A1-A2",
        "min_level": "beginner",
        "situation_cs": "Nakupuješ v malém českém obchodě.",
        "situation_ru": "Ты делаешь покупки в маленьком чешском магазине.",
        "honzik_role": "Prodavač",
        "user_role": "Zákazník",
        "steps": 4,
        "vocabulary": [
            "koupit", "hledat", "kolik", "stojí",
            "velikost", "barva", "slevu", "pokladna",
            "platit", "vrátit", "taška",
        ],
        "hints": [
            "Pozdrav a řekni, co hledáš.",
            "Zeptej se na cenu nebo velikost.",
            "Rozhoduj se, jestli to koupíš.",
            "Zaplať a rozluč se.",
        ],
        "success_achievement": "🛒 Nakupovací guru",
        "reward_stars": 10,
    },
    "telefonni_hovor": {
        "name_cs": "📞 Telefonní hovor",
        "name_ru": "Телефонный звонок",
        "level": "B1",
        "min_level": "intermediate",
        "situation_cs": "Voláš na úřad nebo do firmy, abys něco vyřídil.",
        "situation_ru": "Ты звонишь в учреждение или фирму, чтобы что-то решить.",
        "honzik_role": "Operátor / Sekretářka",
        "user_role": "Volající",
        "steps": 5,
        "vocabulary": [
            "volat", "přepojit", "zavolat zpět", "linka",
            "informace", "schůzka", "termín", "rezervace",
            "vzkaz", "číslo",
        ],
        "hints": [
            "Pozdrav a představ se.",
            "Řekni, proč voláš.",
            "Odpověz na dotazy operátora.",
            "Dohodněte se na řešení.",
            "Poděkuj a rozluč se.",
        ],
        "success_achievement": "📞 Telefonní mistr",
        "reward_stars": 15,
    },
}


class ScenarioService:
    """
    Сервис для ролевых сценариев с Хонзиком.

    Attributes:
        openai_client: Клиент для работы с OpenAI API
    """

    def __init__(self, openai_client: OpenAIClient):
        """
        Инициализация сервиса сценариев.

        Args:
            openai_client: Клиент OpenAI для генерации ответов
        """
        self.openai_client = openai_client
        self.logger = logger.bind(service="scenario_service")

        # In-memory хранилище активных сценариев (в продакшене заменить на БД)
        self._active_scenarios: dict[int, dict] = {}
        self._MAX_ACTIVE_SCENARIOS = 500
        self._SCENARIO_TTL = 3600  # 1 hour

    def _cleanup_stale_scenarios(self):
        """Remove scenarios older than TTL and enforce max size."""
        import time as _time
        now = _time.time()
        expired = [
            uid for uid, s in self._active_scenarios.items()
            if now - s.get("_ts", 0) > self._SCENARIO_TTL
        ]
        for uid in expired:
            del self._active_scenarios[uid]
        while len(self._active_scenarios) > self._MAX_ACTIVE_SCENARIOS:
            oldest = min(self._active_scenarios, key=lambda k: self._active_scenarios[k].get("_ts", 0))
            del self._active_scenarios[oldest]

    async def _get_state(self, user_id: int) -> dict | None:
        """Get scenario state from in-memory store (or Redis if available)."""
        from backend.cache.redis_client import redis_client

        # Try Redis first
        state = await redis_client.get(f"scenario:{user_id}")
        if state:
            return state
        # Fallback to in-memory
        return self._active_scenarios.get(user_id)

    async def _set_state(self, user_id: int, state: dict) -> None:
        """Save scenario state to in-memory store and Redis."""
        import time as _time
        from backend.cache.redis_client import redis_client

        state["_ts"] = _time.time()
        self._active_scenarios[user_id] = state
        self._cleanup_stale_scenarios()
        await redis_client.set(f"scenario:{user_id}", state, ttl=self._SCENARIO_TTL)

    async def _delete_state(self, user_id: int) -> None:
        """Delete scenario state from in-memory store and Redis."""
        from backend.cache.redis_client import redis_client

        self._active_scenarios.pop(user_id, None)
        await redis_client.delete(f"scenario:{user_id}")

    def get_available_scenarios(self, user_level: CzechLevel) -> list[dict]:
        """
        Получить список доступных сценариев для уровня пользователя.

        Args:
            user_level: Уровень чешского языка пользователя

        Returns:
            list: Список доступных сценариев с базовой информацией
        """
        level_order = ["beginner", "intermediate", "advanced", "native"]
        user_level_idx = level_order.index(user_level)

        available = []
        for scenario_id, scenario in SCENARIOS.items():
            min_level_idx = level_order.index(scenario["min_level"])

            available.append({
                "id": scenario_id,
                "name_cs": scenario["name_cs"],
                "name_ru": scenario["name_ru"],
                "level": scenario["level"],
                "steps": scenario["steps"],
                "reward_stars": scenario["reward_stars"],
                "is_unlocked": user_level_idx >= min_level_idx,
                "vocabulary_count": len(scenario["vocabulary"]),
            })

        return available

    async def start_scenario(
        self,
        user_id: int,
        scenario_id: ScenarioId,
        user_level: CzechLevel,
        native_language: str = "ru",
    ) -> dict:
        """
        Начать новый сценарий.

        Args:
            user_id: ID пользователя
            scenario_id: ID сценария
            user_level: Уровень чешского языка
            native_language: Родной язык пользователя

        Returns:
            dict: Информация о начатом сценарии с первым сообщением Хонзика
        """
        if scenario_id not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario_id}")

        scenario = SCENARIOS[scenario_id]

        self.logger.info(
            "starting_scenario",
            user_id=user_id,
            scenario_id=scenario_id,
        )

        # Генерируем начальное сообщение от Хонзика в роли персонажа
        initial_message = await self._generate_scenario_message(
            scenario=scenario,
            user_level=user_level,
            native_language=native_language,
            step=1,
            conversation_history=[],
            user_message=None,
        )

        # Сохраняем состояние сценария в Redis
        state = {
            "scenario_id": scenario_id,
            "step": 1,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "conversation_history": [
                {"role": "assistant", "text": initial_message["honzik_message"]}
            ],
            "total_score": 0,
            "completed": False,
        }
        await self._set_state(user_id, state)

        return {
            "scenario_id": scenario_id,
            "name_cs": scenario["name_cs"],
            "step": 1,
            "total_steps": scenario["steps"],
            "honzik_message": initial_message["honzik_message"],
            "honzik_role": scenario["honzik_role"],
            "user_role": scenario["user_role"],
            "hint": scenario["hints"][0],
            "vocabulary": scenario["vocabulary"][:5],
        }

    async def continue_scenario(
        self,
        user_id: int,
        user_text: str,
        user_level: CzechLevel,
        native_language: str = "ru",
    ) -> dict:
        """
        Продолжить сценарий с ответом пользователя.

        Args:
            user_id: ID пользователя
            user_text: Текст пользователя на чешском
            user_level: Уровень чешского языка
            native_language: Родной язык пользователя

        Returns:
            dict: Ответ Хонзика и информация о прогрессе
        """
        state = await self._get_state(user_id)
        if not state:
            raise ValueError("No active scenario for this user")

        scenario = SCENARIOS[state["scenario_id"]]

        # Добавляем сообщение пользователя в историю
        state["conversation_history"].append({
            "role": "user",
            "text": user_text,
        })

        current_step = state["step"]
        is_last_step = current_step >= scenario["steps"]

        # Генерируем ответ Хонзика
        response = await self._generate_scenario_message(
            scenario=scenario,
            user_level=user_level,
            native_language=native_language,
            step=current_step,
            conversation_history=state["conversation_history"],
            user_message=user_text,
            is_last_step=is_last_step,
        )

        # Добавляем ответ в историю
        state["conversation_history"].append({
            "role": "assistant",
            "text": response["honzik_message"],
        })

        # Обновляем счёт
        state["total_score"] += response.get("step_score", 0)

        # Переходим к следующему шагу
        state["step"] += 1

        result = {
            "scenario_id": state["scenario_id"],
            "step": state["step"],
            "total_steps": scenario["steps"],
            "honzik_message": response["honzik_message"],
            "corrections": response.get("corrections", []),
            "step_score": response.get("step_score", 0),
            "hint": scenario["hints"][min(state["step"] - 1, len(scenario["hints"]) - 1)],
            "is_completed": is_last_step,
        }

        # Если сценарий завершён
        if is_last_step:
            state["completed"] = True
            result["final_score"] = state["total_score"]
            result["reward_stars"] = scenario["reward_stars"]
            result["achievement"] = scenario["success_achievement"]

            self.logger.info(
                "scenario_completed",
                user_id=user_id,
                scenario_id=state["scenario_id"],
                final_score=state["total_score"],
            )

        # Save updated state back to Redis
        await self._set_state(user_id, state)

        return result

    async def get_active_scenario(self, user_id: int) -> dict | None:
        """
        Получить активный сценарий пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            dict | None: Информация об активном сценарии или None
        """
        state = await self._get_state(user_id)
        if not state:
            return None

        state = await self._get_state(user_id)
        scenario = SCENARIOS[state["scenario_id"]]

        return {
            "scenario_id": state["scenario_id"],
            "name_cs": scenario["name_cs"],
            "step": state["step"],
            "total_steps": scenario["steps"],
            "started_at": state["started_at"],
            "completed": state["completed"],
        }

    async def cancel_scenario(self, user_id: int) -> bool:
        """
        Отменить активный сценарий.

        Args:
            user_id: ID пользователя

        Returns:
            bool: True если сценарий был отменён
        """
        state = await self._get_state(user_id)
        if state:
            await self._delete_state(user_id)
            self.logger.info("scenario_cancelled", user_id=user_id)
            return True
        return False

    async def _generate_scenario_message(
        self,
        scenario: dict,
        user_level: CzechLevel,
        native_language: str,
        step: int,
        conversation_history: list[dict],
        user_message: str | None,
        is_last_step: bool = False,
    ) -> dict:
        """
        Генерировать ответ Хонзика в контексте сценария.

        Args:
            scenario: Определение сценария
            user_level: Уровень чешского языка
            native_language: Родной язык пользователя
            step: Текущий шаг сценария
            conversation_history: История разговора
            user_message: Последнее сообщение пользователя
            is_last_step: Это последний шаг?

        Returns:
            dict: Ответ с сообщением, исправлениями и оценкой
        """
        # Формируем системный промпт для сценария
        level_vocab = {
            "beginner": "Používej jednoduchou slovní zásobu úrovně A1-A2.",
            "intermediate": "Používej slovní zásobu úrovně B1-B2.",
            "advanced": "Používej pokročilou slovní zásobu úrovně B2-C1.",
            "native": "Můžeš používat jakoukoliv slovní zásobu.",
        }

        native_lang_names = {
            "ru": "ruština",
            "uk": "ukrajinština",
            "pl": "polština",
            "sk": "slovenština",
        }
        native_lang_name = native_lang_names.get(native_language, "ruština")

        system_prompt = f"""Ty jsi Honzík a hraješ roli: {scenario['honzik_role']}.

SCÉNÁŘ: {scenario['name_cs']}
SITUACE: {scenario['situation_cs']}
TVOJE ROLE: {scenario['honzik_role']}
ROLE STUDENTA: {scenario['user_role']}
KROK: {step} z {scenario['steps']}

SLOVNÍ ZÁSOBA SCÉNÁŘE:
{', '.join(scenario['vocabulary'])}

ÚROVEŇ STUDENTA:
{level_vocab[user_level]}

{'TOTO JE POSLEDNÍ KROK! Ukonči scénář přirozeně a pochval studenta.' if is_last_step else ''}

TVŮJ ÚKOL:
1. Odpověz jako {scenario['honzik_role']} přirozeně v češtině
2. Pokračuj ve scénáři podle situace
3. Pokud student udělal chyby, oprav je (jednoduše v češtině)
4. Ohodnoť odpověď studenta 0-20 bodů
5. Buď podporující a vstřícný

ODPOVĚZ VE FORMÁTU JSON:
{{
  "honzik_message": "Tvoje odpověď jako {scenario['honzik_role']}",
  "corrections": [
    {{
      "original": "špatný text",
      "corrected": "správný text",
      "explanation_cs": "Jednoduché vysvětlení"
    }}
  ],
  "step_score": 15
}}

Poznámka: Rodný jazyk studenta je {native_lang_name}.
"""

        # Формируем пользовательское сообщение
        if user_message:
            user_prompt = f"Student řekl: {user_message}"
        else:
            user_prompt = f"Scénář právě začíná. Zahaj konverzaci jako {scenario['honzik_role']}."

        messages = [
            {"role": "system", "content": system_prompt},
        ]

        # Добавляем историю разговора
        for msg in conversation_history[-6:]:
            role = "assistant" if msg["role"] == "assistant" else "user"
            messages.append({"role": role, "content": msg["text"]})

        messages.append({"role": "user", "content": user_prompt})

        try:
            response_text = await self.openai_client.generate_chat_completion(
                messages=messages,
                json_mode=True,
                model="gpt-4o-mini",  # Быстрая модель для сценариев
            )

            response_data = json.loads(response_text)

            # Валидация и дефолты
            return {
                "honzik_message": response_data.get("honzik_message", "Pokračujeme..."),
                "corrections": response_data.get("corrections", []),
                "step_score": min(20, max(0, response_data.get("step_score", 10))),
            }

        except Exception as e:
            self.logger.error(
                "scenario_generation_failed",
                error=str(e),
            )
            return {
                "honzik_message": "Pokračujeme v konverzaci...",
                "corrections": [],
                "step_score": 10,
            }
