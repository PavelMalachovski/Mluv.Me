"""
Seasonal Service for time-limited events.

Реализует сезонные события с особыми достижениями и словарём.
"""

from datetime import datetime
from typing import Literal

import structlog

logger = structlog.get_logger(__name__)

# Сезонные события
SEASONAL_EVENTS = {
    "christmas": {
        "name_cs": "🎄 Vánoční výzva",
        "name_ru": "🎄 Рождественский вызов",
        "dates": ("12-20", "12-31"),  # MM-DD
        "description_cs": "Oslav české Vánoce a nauč se vánoční slovíčka!",
        "description_ru": "Отпразднуй чешское Рождество и выучи рождественские слова!",
        "vocabulary": [
            {"word": "Vánoce", "translation": "Рождество"},
            {"word": "dárek", "translation": "подарок"},
            {"word": "stromeček", "translation": "ёлочка"},
            {"word": "kapr", "translation": "карп"},
            {"word": "cukroví", "translation": "печенье"},
            {"word": "Štědrý večer", "translation": "Сочельник"},
            {"word": "koleda", "translation": "колядка"},
            {"word": "betlém", "translation": "вертеп"},
            {"word": "hvězda", "translation": "звезда"},
            {"word": "anděl", "translation": "ангел"},
        ],
        "achievement": {
            "name_cs": "🎄 Vánoční mluvčí",
            "name_ru": "🎄 Рождественский оратор",
            "description_cs": "Naučil ses 10 vánočních slovíček!",
            "requirement": 10,
        },
        "bonus_stars": 50,
        "theme_color": "#c41e3a",
    },
    "easter": {
        "name_cs": "🐣 Velikonoční výzva",
        "name_ru": "🐣 Пасхальный вызов",
        "dates": ("04-01", "04-15"),
        "description_cs": "Oslav české Velikonoce!",
        "description_ru": "Отпразднуй чешскую Пасху!",
        "vocabulary": [
            {"word": "Velikonoce", "translation": "Пасха"},
            {"word": "kraslice", "translation": "расписное яйцо"},
            {"word": "pomlázka", "translation": "плётка (пасхальная)"},
            {"word": "beránek", "translation": "барашек (торт)"},
            {"word": "jaro", "translation": "весна"},
            {"word": "mazanec", "translation": "пасхальная сдоба"},
            {"word": "zajíček", "translation": "зайчик"},
            {"word": "kuřátko", "translation": "цыплёнок"},
        ],
        "achievement": {
            "name_cs": "🐣 Velikonoční znalec",
            "name_ru": "🐣 Пасхальный знаток",
            "description_cs": "Naučil ses 8 velikonočních slovíček!",
            "requirement": 8,
        },
        "bonus_stars": 40,
        "theme_color": "#ffd700",
    },
    "october_fest": {
        "name_cs": "🍺 Pivní festival",
        "name_ru": "🍺 Пивной фестиваль",
        "dates": ("09-15", "10-03"),
        "description_cs": "Oslavuj české pivo a hospodskou kulturu!",
        "description_ru": "Празднуй чешское пиво и культуру пабов!",
        "vocabulary": [
            {"word": "pivo", "translation": "пиво"},
            {"word": "hospoda", "translation": "паб"},
            {"word": "ležák", "translation": "лагер"},
            {"word": "točené", "translation": "разливное"},
            {"word": "půllitr", "translation": "поллитра (кружка)"},
            {"word": "přípitek", "translation": "тост"},
            {"word": "na zdraví", "translation": "за здоровье"},
            {"word": "pěna", "translation": "пена"},
            {"word": "čepovat", "translation": "разливать"},
        ],
        "achievement": {
            "name_cs": "🍺 Pivní znalec",
            "name_ru": "🍺 Знаток пива",
            "description_cs": "Stal ses expertem na pivní slovíčka!",
            "requirement": 9,
        },
        "bonus_stars": 45,
        "theme_color": "#f39c12",
    },
    "summer": {
        "name_cs": "☀️ Letní výzva",
        "name_ru": "☀️ Летний вызов",
        "dates": ("07-01", "08-31"),
        "description_cs": "Užij si české léto a nauč se letní fráze!",
        "description_ru": "Насладись чешским летом и выучи летние фразы!",
        "vocabulary": [
            {"word": "léto", "translation": "лето"},
            {"word": "dovolená", "translation": "отпуск"},
            {"word": "koupání", "translation": "купание"},
            {"word": "pláž", "translation": "пляж"},
            {"word": "zmrzlina", "translation": "мороженое"},
            {"word": "slunce", "translation": "солнце"},
            {"word": "vedro", "translation": "жара"},
        ],
        "achievement": {
            "name_cs": "☀️ Letní cestovatel",
            "name_ru": "☀️ Летний путешественник",
            "description_cs": "Připraven na české léto!",
            "requirement": 7,
        },
        "bonus_stars": 35,
        "theme_color": "#ff6b35",
    },
    "new_year": {
        "name_cs": "🎆 Novoroční výzva",
        "name_ru": "🎆 Новогодний вызов",
        "dates": ("01-01", "01-07"),
        "description_cs": "Začni nový rok s češtinou!",
        "description_ru": "Начни новый год с чешским!",
        "vocabulary": [
            {"word": "Nový rok", "translation": "Новый год"},
            {"word": "předsevzetí", "translation": "новогоднее обещание"},
            {"word": "ohňostroj", "translation": "фейерверк"},
            {"word": "silvestr", "translation": "канун Нового года"},
            {"word": "přípitek", "translation": "тост"},
            {"word": "štěstí", "translation": "счастье"},
        ],
        "achievement": {
            "name_cs": "🎆 Novoroční mluvčí",
            "name_ru": "🎆 Новогодний оратор",
            "description_cs": "Vstoupil jsi do nového roku s češtinou!",
            "requirement": 6,
        },
        "bonus_stars": 30,
        "theme_color": "#9b59b6",
    },
}


class SeasonalService:
    """
    Сервис для сезонных событий и достижений.
    """

    def __init__(self):
        self.logger = logger.bind(service="seasonal_service")

        # In-memory прогресс пользователей (в продакшене заменить на БД)
        self._user_progress: dict[int, dict[str, dict]] = {}

    def get_active_event(self) -> dict | None:
        """
        Получить текущее активное событие.

        Returns:
            dict | None: Активное событие или None
        """
        today = datetime.utcnow()
        current_date = today.strftime("%m-%d")

        for event_id, event in SEASONAL_EVENTS.items():
            start_date, end_date = event["dates"]

            # Проверяем, попадает ли текущая дата в диапазон
            if self._is_date_in_range(current_date, start_date, end_date):
                self.logger.info(
                    "active_event_found",
                    event_id=event_id,
                )
                return {
                    "id": event_id,
                    "name_cs": event["name_cs"],
                    "name_ru": event["name_ru"],
                    "description_cs": event["description_cs"],
                    "description_ru": event["description_ru"],
                    "vocabulary_count": len(event["vocabulary"]),
                    "bonus_stars": event["bonus_stars"],
                    "theme_color": event["theme_color"],
                    "achievement": event["achievement"],
                }

        return None

    def get_event_vocabulary(self, event_id: str) -> list[dict]:
        """
        Получить словарь события.

        Args:
            event_id: ID события

        Returns:
            list: Список слов
        """
        if event_id not in SEASONAL_EVENTS:
            return []

        return SEASONAL_EVENTS[event_id]["vocabulary"]

    def learn_word(
        self,
        user_id: int,
        event_id: str,
        word: str,
    ) -> dict:
        """
        Отметить слово как изученное.

        Args:
            user_id: ID пользователя
            event_id: ID события
            word: Изученное слово

        Returns:
            dict: Статус прогресса
        """
        if event_id not in SEASONAL_EVENTS:
            raise ValueError(f"Unknown event: {event_id}")

        # Инициализируем прогресс если нет
        if user_id not in self._user_progress:
            self._user_progress[user_id] = {}
        if event_id not in self._user_progress[user_id]:
            self._user_progress[user_id][event_id] = {
                "learned_words": [],
                "achievement_earned": False,
            }

        progress = self._user_progress[user_id][event_id]

        # Добавляем слово если ещё не изучено
        if word not in progress["learned_words"]:
            progress["learned_words"].append(word)

        event = SEASONAL_EVENTS[event_id]
        total_words = len(event["vocabulary"])
        learned_count = len(progress["learned_words"])

        # Проверяем достижение
        achievement_earned = False
        if (
            not progress["achievement_earned"]
            and learned_count >= event["achievement"]["requirement"]
        ):
            progress["achievement_earned"] = True
            achievement_earned = True
            self.logger.info(
                "seasonal_achievement_earned",
                user_id=user_id,
                event_id=event_id,
                achievement=event["achievement"]["name_cs"],
            )

        return {
            "learned_count": learned_count,
            "total_count": total_words,
            "progress_percent": round(learned_count / total_words * 100),
            "achievement_earned": achievement_earned,
            "achievement": event["achievement"] if achievement_earned else None,
            "bonus_stars": event["bonus_stars"] if achievement_earned else 0,
        }

    def get_user_progress(
        self,
        user_id: int,
        event_id: str,
    ) -> dict | None:
        """
        Получить прогресс пользователя в событии.

        Args:
            user_id: ID пользователя
            event_id: ID события

        Returns:
            dict | None: Прогресс или None
        """
        if user_id not in self._user_progress:
            return None
        if event_id not in self._user_progress[user_id]:
            return None

        progress = self._user_progress[user_id][event_id]
        event = SEASONAL_EVENTS[event_id]

        return {
            "event_id": event_id,
            "learned_words": progress["learned_words"],
            "learned_count": len(progress["learned_words"]),
            "total_count": len(event["vocabulary"]),
            "achievement_earned": progress["achievement_earned"],
        }

    def get_all_events(self) -> list[dict]:
        """
        Получить список всех событий.

        Returns:
            list: Все события с информацией о статусе
        """
        today = datetime.utcnow()
        current_date = today.strftime("%m-%d")

        events = []
        for event_id, event in SEASONAL_EVENTS.items():
            start_date, end_date = event["dates"]
            is_active = self._is_date_in_range(current_date, start_date, end_date)

            events.append({
                "id": event_id,
                "name_cs": event["name_cs"],
                "name_ru": event["name_ru"],
                "dates": event["dates"],
                "is_active": is_active,
                "vocabulary_count": len(event["vocabulary"]),
                "bonus_stars": event["bonus_stars"],
                "theme_color": event["theme_color"],
            })

        return events

    def _is_date_in_range(
        self,
        current: str,
        start: str,
        end: str,
    ) -> bool:
        """Проверить, находится ли дата в диапазоне (формат MM-DD)."""
        # Простая проверка для не-переходящих годовых диапазонов
        if start <= end:
            return start <= current <= end
        else:
            # Для диапазонов через новый год (например, 12-20 to 01-07)
            return current >= start or current <= end
