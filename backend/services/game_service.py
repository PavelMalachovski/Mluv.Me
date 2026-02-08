"""
Game Service for language learning mini-games.

Реализует 5 мини-игр для изучения чешского:
- Slovní hádanka (Угадай слово)
- Doplň písmeno (Вставь букву)
- Rychlá odpověď (Быстрый ответ)
- Sestav větu (Собери предложение)
- Co slyšíš? (Что слышишь?)
"""

import random
import json
from datetime import datetime
from typing import Literal
from dataclasses import dataclass

import structlog

from backend.services.openai_client import OpenAIClient

logger = structlog.get_logger(__name__)

# Типы игр
GameType = Literal[
    "slovni_hadanka",
    "dopln_pismeno",
    "rychla_odpoved",
    "sestav_vetu",
    "co_slyses",
]

CzechLevel = Literal["beginner", "intermediate", "advanced", "native"]


# Определения игр
GAMES = {
    "slovni_hadanka": {
        "name_cs": "🎯 Slovní hádanka",
        "name_ru": "Угадай слово",
        "description_cs": "Uhádni slovo podle popisu.",
        "description_ru": "Угадай слово по описанию.",
        "reward_stars": 3,
        "time_limit_seconds": 60,
        "difficulty_multiplier": 1.0,
    },
    "dopln_pismeno": {
        "name_cs": "🔤 Doplň písmeno",
        "name_ru": "Вставь букву",
        "description_cs": "Doplň chybějící písmeno ve slově.",
        "description_ru": "Вставь пропущенную букву в слово.",
        "reward_stars": 2,
        "time_limit_seconds": 30,
        "difficulty_multiplier": 0.8,
    },
    "rychla_odpoved": {
        "name_cs": "🎭 Rychlá odpověď",
        "name_ru": "Быстрый ответ",
        "description_cs": "Odpověz na otázku za 10 sekund!",
        "description_ru": "Ответь на вопрос за 10 секунд!",
        "reward_stars": 5,
        "time_limit_seconds": 10,
        "difficulty_multiplier": 1.5,
    },
    "sestav_vetu": {
        "name_cs": "🧩 Sestav větu",
        "name_ru": "Собери предложение",
        "description_cs": "Sestav větu ze slov ve správném pořadí.",
        "description_ru": "Собери предложение из слов в правильном порядке.",
        "reward_stars": 4,
        "time_limit_seconds": 45,
        "difficulty_multiplier": 1.2,
    },
    "co_slyses": {
        "name_cs": "👂 Co slyšíš?",
        "name_ru": "Что слышишь?",
        "description_cs": "Napiš slovo, které uslyšíš.",
        "description_ru": "Напиши слово, которое услышишь.",
        "reward_stars": 3,
        "time_limit_seconds": 30,
        "difficulty_multiplier": 1.0,
    },
}


# Банк слов и предложений по уровням
VOCABULARY_BANK = {
    "beginner": {
        "words": [
            {"word": "pivo", "hint_cs": "Oblíbený český nápoj 🍺", "category": "drink"},
            {"word": "chleba", "hint_cs": "Jíme ho každý den", "category": "food"},
            {"word": "voda", "hint_cs": "Tekutina, kterou pijeme", "category": "drink"},
            {"word": "dům", "hint_cs": "Kde bydlíme", "category": "place"},
            {"word": "auto", "hint_cs": "Dopravní prostředek se 4 koly", "category": "transport"},
            {"word": "kniha", "hint_cs": "Čteme ji 📚", "category": "object"},
            {"word": "pes", "hint_cs": "Domácí mazlíček, štěká 🐕", "category": "animal"},
            {"word": "kočka", "hint_cs": "Domácí mazlíček, mňouká 🐱", "category": "animal"},
            {"word": "škola", "hint_cs": "Místo, kde se učíme", "category": "place"},
            {"word": "Praha", "hint_cs": "Hlavní město Česka 🏰", "category": "place"},
        ],
        "sentences": [
            {"sentence": "Jak se máš?", "translation_ru": "Как дела?"},
            {"sentence": "Mám se dobře.", "translation_ru": "У меня всё хорошо."},
            {"sentence": "Děkuji moc.", "translation_ru": "Большое спасибо."},
            {"sentence": "Jedno pivo, prosím.", "translation_ru": "Одно пиво, пожалуйста."},
            {"sentence": "Kde je zastávka?", "translation_ru": "Где остановка?"},
        ],
    },
    "intermediate": {
        "words": [
            {"word": "hospoda", "hint_cs": "Typické české místo pro pivo 🍺", "category": "place"},
            {"word": "knedlík", "hint_cs": "Příloha k svíčkové", "category": "food"},
            {"word": "krásný", "hint_cs": "Velmi hezký", "category": "adjective"},
            {"word": "důležitý", "hint_cs": "Velmi významný", "category": "adjective"},
            {"word": "cestovat", "hint_cs": "Jezdit do různých míst", "category": "verb"},
            {"word": "pomáhat", "hint_cs": "Asistovat někomu", "category": "verb"},
            {"word": "překvapení", "hint_cs": "Něco nečekaného", "category": "noun"},
            {"word": "společnost", "hint_cs": "Lidé kolem nás, nebo firma", "category": "noun"},
        ],
        "sentences": [
            {"sentence": "Rád bych si objednal svíčkovou.", "translation_ru": "Я бы хотел заказать свичкову."},
            {"sentence": "Můžete mi prosím pomoct?", "translation_ru": "Вы можете мне помочь?"},
            {"sentence": "Jak dlouho trvá cesta?", "translation_ru": "Сколько времени занимает дорога?"},
            {"sentence": "Máte nějakou slevu?", "translation_ru": "У вас есть скидка?"},
        ],
    },
    "advanced": {
        "words": [
            {"word": "překážka", "hint_cs": "Něco, co brání v cestě", "category": "noun"},
            {"word": "zodpovědnost", "hint_cs": "Odpovědnost za něco", "category": "noun"},
            {"word": "přehodnotit", "hint_cs": "Znovu promyslet", "category": "verb"},
            {"word": "prostřednictvím", "hint_cs": "Pomocí něčeho", "category": "preposition"},
            {"word": "záležitost", "hint_cs": "Věc nebo problém", "category": "noun"},
        ],
        "sentences": [
            {"sentence": "Bylo by možné přeložit schůzku na příští týden?", "translation_ru": "Можно ли перенести встречу на следующую неделю?"},
            {"sentence": "Rád bych vás upozornil na důležitý detail.", "translation_ru": "Хотел бы обратить ваше внимание на важную деталь."},
        ],
    },
    "native": {
        "words": [
            {"word": "přelétavý", "hint_cs": "Měnící často partnery nebo zájmy", "category": "adjective"},
            {"word": "rozhořčení", "hint_cs": "Silné pobouření", "category": "noun"},
            {"word": "zatraceně", "hint_cs": "Expresivní slovo pro zdůraznění", "category": "adverb"},
        ],
        "sentences": [
            {"sentence": "To je ale pěkná pakáž!", "translation_ru": "Ну и сброд! (разг.)"},
        ],
    },
}


@dataclass
class ActiveGame:
    """Активная игра пользователя."""
    game_id: str
    game_type: GameType
    user_id: int
    question: dict
    correct_answer: str
    started_at: datetime
    level: str


class GameService:
    """
    Сервис для языковых мини-игр.

    Управляет играми, подсчётом очков и лидербордом.
    """

    def __init__(self, openai_client: OpenAIClient | None = None):
        """
        Инициализация игрового сервиса.

        Args:
            openai_client: Клиент OpenAI для генерации динамического контента
        """
        self.openai_client = openai_client
        self.logger = logger.bind(service="game_service")

        # In-memory хранилище активных игр
        self._active_games: dict[int, ActiveGame] = {}

        # In-memory лидерборд (в продакшене заменить на БД)
        self._leaderboard: dict[str, list[dict]] = {
            game_type: [] for game_type in GAMES
        }

    def get_available_games(self) -> list[dict]:
        """
        Получить список всех доступных игр.

        Returns:
            list: Список игр с информацией
        """
        return [
            {
                "id": game_id,
                "name_cs": info["name_cs"],
                "name_ru": info["name_ru"],
                "description_cs": info["description_cs"],
                "description_ru": info["description_ru"],
                "reward_stars": info["reward_stars"],
                "time_limit_seconds": info["time_limit_seconds"],
            }
            for game_id, info in GAMES.items()
        ]

    async def start_game(
        self,
        user_id: int,
        game_type: GameType,
        level: CzechLevel = "beginner",
    ) -> dict:
        """
        Начать новую игру.

        Args:
            user_id: ID пользователя
            game_type: Тип игры
            level: Уровень сложности

        Returns:
            dict: Информация об игре с вопросом
        """
        if game_type not in GAMES:
            raise ValueError(f"Unknown game type: {game_type}")

        game_info = GAMES[game_type]
        game_id = f"{user_id}_{game_type}_{datetime.utcnow().timestamp()}"

        # Генерируем вопрос в зависимости от типа игры
        question, correct_answer = await self._generate_question(
            game_type, level
        )

        # Сохраняем активную игру
        active_game = ActiveGame(
            game_id=game_id,
            game_type=game_type,
            user_id=user_id,
            question=question,
            correct_answer=correct_answer,
            started_at=datetime.utcnow(),
            level=level,
        )
        self._active_games[user_id] = active_game

        self.logger.info(
            "game_started",
            user_id=user_id,
            game_type=game_type,
            level=level,
        )

        return {
            "game_id": game_id,
            "game_type": game_type,
            "name_cs": game_info["name_cs"],
            "question": question,
            "time_limit_seconds": game_info["time_limit_seconds"],
            "reward_stars": game_info["reward_stars"],
        }

    async def submit_answer(
        self,
        user_id: int,
        answer: str,
    ) -> dict:
        """
        Отправить ответ на текущую игру.

        Args:
            user_id: ID пользователя
            answer: Ответ пользователя

        Returns:
            dict: Результат с оценкой
        """
        if user_id not in self._active_games:
            raise ValueError("No active game for this user")

        active_game = self._active_games[user_id]
        game_info = GAMES[active_game.game_type]

        # Проверяем время
        elapsed = (datetime.utcnow() - active_game.started_at).total_seconds()
        time_bonus = max(0, 1 - elapsed / game_info["time_limit_seconds"])

        # Проверяем ответ
        is_correct = self._check_answer(
            answer.strip().lower(),
            active_game.correct_answer.lower(),
            active_game.game_type,
        )

        # Рассчитываем награду
        base_stars = game_info["reward_stars"] if is_correct else 0
        bonus_stars = int(base_stars * time_bonus * 0.5) if is_correct else 0
        total_stars = base_stars + bonus_stars

        # Обновляем лидерборд
        if is_correct:
            self._update_leaderboard(
                active_game.game_type,
                user_id,
                total_stars,
                elapsed,
            )

        # Удаляем активную игру
        del self._active_games[user_id]

        self.logger.info(
            "game_completed",
            user_id=user_id,
            game_type=active_game.game_type,
            is_correct=is_correct,
            stars_earned=total_stars,
            time_seconds=elapsed,
        )

        return {
            "is_correct": is_correct,
            "correct_answer": active_game.correct_answer,
            "user_answer": answer,
            "stars_earned": total_stars,
            "base_stars": base_stars,
            "bonus_stars": bonus_stars,
            "time_seconds": round(elapsed, 1),
            "time_bonus_percent": round(time_bonus * 100),
        }

    def get_leaderboard(
        self,
        game_type: GameType,
        limit: int = 10,
    ) -> list[dict]:
        """
        Получить лидерборд для игры.

        Args:
            game_type: Тип игры
            limit: Количество записей

        Returns:
            list: Топ игроков
        """
        if game_type not in self._leaderboard:
            return []

        return sorted(
            self._leaderboard[game_type],
            key=lambda x: (-x["total_stars"], x["best_time"]),
        )[:limit]

    async def _generate_question(
        self,
        game_type: GameType,
        level: CzechLevel,
    ) -> tuple[dict, str]:
        """
        Сгенерировать вопрос для игры.

        Returns:
            tuple: (question_dict, correct_answer)
        """
        vocab = VOCABULARY_BANK.get(level, VOCABULARY_BANK["beginner"])

        if game_type == "slovni_hadanka":
            # Угадай слово по описанию
            word_data = random.choice(vocab["words"])
            return {
                "type": "guess_word",
                "hint": word_data["hint_cs"],
                "category": word_data["category"],
                "word_length": len(word_data["word"]),
            }, word_data["word"]

        elif game_type == "dopln_pismeno":
            # Вставь букву
            word_data = random.choice(vocab["words"])
            word = word_data["word"]
            # Убираем случайную букву
            idx = random.randint(0, len(word) - 1)
            hidden_letter = word[idx]
            display = word[:idx] + "_" + word[idx + 1:]
            return {
                "type": "fill_letter",
                "word_with_gap": display,
                "hint": word_data["hint_cs"],
                "missing_position": idx,
            }, hidden_letter

        elif game_type == "rychla_odpoved":
            # Быстрый ответ
            question_templates = [
                {"q": "Jak se řekne 'hello' česky?", "a": "ahoj"},
                {"q": "Jaké je hlavní město Česka?", "a": "praha"},
                {"q": "Co pijeme v hospodě? 🍺", "a": "pivo"},
                {"q": "Jak se řekne 'thank you' česky?", "a": "děkuji"},
                {"q": "Kolik má Česko 🇨🇿 obyvatel? (v milionech)", "a": "10"},
            ]
            q = random.choice(question_templates)
            return {
                "type": "quick_answer",
                "question": q["q"],
            }, q["a"]

        elif game_type == "sestav_vetu":
            # Собери предложение
            if vocab["sentences"]:
                sentence_data = random.choice(vocab["sentences"])
                words = sentence_data["sentence"].replace("?", " ?").replace(".", " .").replace(",", " ,").split()
                shuffled = words.copy()
                random.shuffle(shuffled)
                return {
                    "type": "build_sentence",
                    "words": shuffled,
                    "word_count": len(words),
                    "translation_hint": sentence_data.get("translation_ru", ""),
                }, sentence_data["sentence"]
            else:
                # Fallback
                return {
                    "type": "build_sentence",
                    "words": ["Jak", "se", "máš", "?"],
                    "word_count": 4,
                }, "Jak se máš?"

        elif game_type == "co_slyses":
            # Что слышишь - используется с TTS
            word_data = random.choice(vocab["words"])
            return {
                "type": "listen_write",
                "word": word_data["word"],  # Будет преобразовано в аудио
                "category": word_data["category"],
                "hint": f"Kategorija: {word_data['category']}",
            }, word_data["word"]

        return {"type": "unknown"}, ""

    def _check_answer(
        self,
        user_answer: str,
        correct_answer: str,
        game_type: GameType,
    ) -> bool:
        """Проверить правильность ответа."""
        # Нормализуем ответы
        user_norm = user_answer.strip().lower()
        correct_norm = correct_answer.strip().lower()

        if game_type == "sestav_vetu":
            # Для предложений убираем пробелы перед пунктуацией
            user_clean = user_norm.replace(" ?", "?").replace(" .", ".").replace(" ,", ",")
            correct_clean = correct_norm.replace(" ?", "?").replace(" .", ".").replace(" ,", ",")
            return user_clean == correct_clean

        # Для остальных игр - точное совпадение
        return user_norm == correct_norm

    def _update_leaderboard(
        self,
        game_type: GameType,
        user_id: int,
        stars: int,
        time_seconds: float,
    ):
        """Обновить лидерборд."""
        leaderboard = self._leaderboard[game_type]

        # Ищем существующую запись
        existing = next((x for x in leaderboard if x["user_id"] == user_id), None)

        if existing:
            existing["total_stars"] += stars
            existing["games_played"] += 1
            if time_seconds < existing["best_time"]:
                existing["best_time"] = time_seconds
        else:
            leaderboard.append({
                "user_id": user_id,
                "total_stars": stars,
                "games_played": 1,
                "best_time": time_seconds,
            })

    def cancel_game(self, user_id: int) -> bool:
        """Отменить активную игру."""
        if user_id in self._active_games:
            del self._active_games[user_id]
            return True
        return False
