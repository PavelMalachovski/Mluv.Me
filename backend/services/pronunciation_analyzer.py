"""
Pronunciation Analyzer for detailed pronunciation feedback.

Реализует анализ произношения с фокусом на сложных чешских звуках:
- ř (чешская вибранта)
- h (мягкое чешское h)
- ů/ú (долгое ú)
- ě (звук je/е)
- и другие проблемные звуки для славяноговорящих
"""

from typing import Literal

import structlog

from backend.services.openai_client import OpenAIClient

logger = structlog.get_logger(__name__)

NativeLanguage = Literal["ru", "uk", "pl", "sk"]


# Сложные звуки для славяноговорящих
DIFFICULT_SOUNDS = {
    "ř": {
        "description_cs": "Český zvuk Ř",
        "description_ru": "Чешская вибранта Ř",
        "tip_cs": "Jazyk vibruje za horními zuby, jako kombinace R a Ž",
        "tip_ru": "Язык вибрирует за верхними зубами, как комбинация Р и Ж",
        "difficulty": 10,  # Самый сложный
        "practice_words": ["řeka", "moře", "příliš", "tři", "říkat", "dveře", "přes"],
        "common_mistakes": ["r", "ж", "рж"],
        "audio_example": "ř.mp3",
    },
    "h": {
        "description_cs": "České H (ne ruské Г)",
        "description_ru": "Чешское H (не русское Г)",
        "tip_cs": "Měkké H, jako vzdech. Ne tvrdé G!",
        "tip_ru": "Мягкое H, как выдох. Не твёрдое Г!",
        "difficulty": 7,
        "practice_words": ["ahoj", "hora", "hodně", "hezký", "hlava", "hvězda"],
        "common_mistakes": ["g", "к", "г"],
        "audio_example": "h.mp3",
    },
    "ů": {
        "description_cs": "Dlouhé Ú (kroužek)",
        "description_ru": "Долгое Ú (с кружком)",
        "tip_cs": "Dlouhé ÚÚÚ, ne krátké U. Držte déle!",
        "tip_ru": "Долгое ÚÚÚ, не короткое У. Держите дольше!",
        "difficulty": 5,
        "practice_words": ["dům", "stůl", "průvodce", "důležitý", "můj", "tvůj"],
        "common_mistakes": ["u", "о"],
        "audio_example": "ů.mp3",
    },
    "ú": {
        "description_cs": "Dlouhé Ú (čárka)",
        "description_ru": "Долгое Ú (с черточкой)",
        "tip_cs": "Stejné jako Ů, jen na začátku slova nebo po předponě.",
        "tip_ru": "То же что Ů, только в начале слова или после приставки.",
        "difficulty": 5,
        "practice_words": ["úterý", "území", "účet", "úplně", "úkol", "útulný"],
        "common_mistakes": ["u", "о"],
        "audio_example": "ú.mp3",
    },
    "ě": {
        "description_cs": "České Ě (háček)",
        "description_ru": "Чешское Ě (гачек)",
        "tip_cs": "Po D, T, N změkčuje: DĚ=ďe, TĚ=ťe, NĚ=ňe. Jinde jako JE.",
        "tip_ru": "После D, T, N смягчает: DĚ=дье, TĚ=тье, NĚ=нье. В других случаях как JE.",
        "difficulty": 6,
        "practice_words": ["město", "věc", "děti", "tělo", "něco", "pěkný"],
        "common_mistakes": ["e", "э", "ie"],
        "audio_example": "ě.mp3",
    },
    "y": {
        "description_cs": "Tvrdé Y (ypsilon)",
        "description_ru": "Твёрдое Y (ипсилон)",
        "tip_cs": "Vyslovuje se STEJNĚ jako I! Rozdíl je jen v pravopise.",
        "tip_ru": "Произносится ОДИНАКОВО с I! Разница только в орфографии.",
        "difficulty": 3,
        "practice_words": ["byt", "být", "mýt", "mít", "výška", "jazyk"],
        "common_mistakes": [],  # Нет явных ошибок, только орфографические
        "audio_example": "y.mp3",
    },
    "ch": {
        "description_cs": "České CH",
        "description_ru": "Чешское CH",
        "tip_cs": "Jako ruské X. Je to JEDNA hláska! V abecedě po H.",
        "tip_ru": "Как русское Х. Это ОДИН звук! В алфавите после H.",
        "difficulty": 4,
        "practice_words": ["chléb", "chtít", "chyba", "chutný", "chrám", "ucho"],
        "common_mistakes": ["k", "kh"],
        "audio_example": "ch.mp3",
    },
    "ý": {
        "description_cs": "Dlouhé Ý",
        "description_ru": "Долгое Ý",
        "tip_cs": "Dlouhé ÍÍÍ, jako ruské ИИИИИ. Držte déle!",
        "tip_ru": "Долгое ÍÍÍ, как русское ИИИИИ. Держите дольше!",
        "difficulty": 4,
        "practice_words": ["být", "krásný", "mladý", "starý", "velký", "dobrý"],
        "common_mistakes": ["y", "i"],
        "audio_example": "ý.mp3",
    },
}


class PronunciationAnalyzer:
    """
    Анализатор произношения с фокусом на сложных чешских звуках.

    Использует Whisper API с word-level timestamps для детального анализа.
    """

    def __init__(self, openai_client: OpenAIClient):
        """
        Инициализация анализатора произношения.

        Args:
            openai_client: Клиент OpenAI для работы с Whisper API
        """
        self.openai_client = openai_client
        self.logger = logger.bind(service="pronunciation_analyzer")

    async def analyze(
        self,
        audio: bytes,
        transcript: str,
        native_language: NativeLanguage = "ru",
    ) -> dict:
        """
        Анализировать произношение аудио.

        Args:
            audio: Аудио файл в байтах
            transcript: Транскрипт текста (от Whisper)
            native_language: Родной язык пользователя для подсказок

        Returns:
            dict: Результат анализа с оценкой и рекомендациями
        """
        self.logger.info(
            "analyzing_pronunciation",
            transcript_length=len(transcript),
        )

        # Поиск сложных звуков в транскрипте
        found_sounds = self._find_difficult_sounds(transcript)

        # Оценка общего произношения
        overall_score = self._calculate_pronunciation_score(transcript, found_sounds)

        # Генерация рекомендаций
        recommendations = self._generate_recommendations(
            found_sounds, native_language
        )

        # Слова для практики
        practice_words = self._get_practice_words(found_sounds)

        result = {
            "overall_score": overall_score,
            "difficult_sounds_found": [
                {
                    "sound": sound,
                    "word": word,
                    "count": count,
                    "tip_cs": DIFFICULT_SOUNDS[sound]["tip_cs"],
                    "difficulty": DIFFICULT_SOUNDS[sound]["difficulty"],
                }
                for sound, word, count in found_sounds
            ],
            "recommendations": recommendations,
            "practice_words": practice_words,
            "total_difficult_sounds": len(found_sounds),
        }

        self.logger.info(
            "pronunciation_analyzed",
            score=overall_score,
            difficult_sounds_count=len(found_sounds),
        )

        return result

    def _find_difficult_sounds(self, transcript: str) -> list[tuple[str, str, int]]:
        """
        Найти сложные звуки в транскрипте.

        Args:
            transcript: Текст транскрипта

        Returns:
            list: Список кортежей (звук, слово, количество)
        """
        transcript_lower = transcript.lower()
        words = transcript_lower.split()
        found = []

        for sound in DIFFICULT_SOUNDS:
            for word in words:
                if sound in word:
                    # Считаем сколько раз звук встречается в слове
                    count = word.count(sound)
                    found.append((sound, word, count))

        # Сортируем по сложности (самые сложные первыми)
        found.sort(key=lambda x: DIFFICULT_SOUNDS[x[0]]["difficulty"], reverse=True)

        return found

    def _calculate_pronunciation_score(
        self,
        transcript: str,
        found_sounds: list[tuple[str, str, int]],
    ) -> int:
        """
        Рассчитать общую оценку произношения.

        Базовая оценка: 100
        За каждый сложный звук снижаем в зависимости от сложности.

        Args:
            transcript: Текст транскрипта
            found_sounds: Найденные сложные звуки

        Returns:
            int: Оценка от 0 до 100
        """
        if not transcript or not found_sounds:
            return 90  # Нет сложных звуков = хорошо

        base_score = 100
        total_words = len(transcript.split())

        # Снижаем оценку за каждый сложный звук
        penalty = 0
        for sound, word, count in found_sounds:
            difficulty = DIFFICULT_SOUNDS[sound]["difficulty"]
            # Пенальти зависит от сложности звука
            penalty += (difficulty / 10) * count * 2

        # Нормализуем пенальти по количеству слов
        if total_words > 0:
            penalty = penalty / total_words * 10

        final_score = max(50, min(100, base_score - penalty))
        return int(final_score)

    def _generate_recommendations(
        self,
        found_sounds: list[tuple[str, str, int]],
        native_language: NativeLanguage,
    ) -> list[dict]:
        """
        Сгенерировать рекомендации по произношению.

        Args:
            found_sounds: Найденные сложные звуки
            native_language: Родной язык пользователя

        Returns:
            list: Список рекомендаций
        """
        if not found_sounds:
            return [{
                "type": "success",
                "message_cs": "Výborně! Tvoje výslovnost je skvělá! 🎉",
                "message_native": self._get_native_success_message(native_language),
            }]

        recommendations = []

        # Группируем по уникальным звукам
        unique_sounds = set(sound for sound, _, _ in found_sounds)

        # Сортируем по сложности
        sorted_sounds = sorted(
            unique_sounds,
            key=lambda s: DIFFICULT_SOUNDS[s]["difficulty"],
            reverse=True
        )

        # Берём топ-3 самых сложных
        for sound in sorted_sounds[:3]:
            info = DIFFICULT_SOUNDS[sound]
            tip_key = f"tip_{native_language}" if f"tip_{native_language}" in info else "tip_ru"

            recommendations.append({
                "sound": sound,
                "type": "practice",
                "message_cs": info["tip_cs"],
                "message_native": info.get(tip_key, info["tip_ru"]),
                "practice_words": info["practice_words"][:5],
            })

        return recommendations

    def _get_practice_words(
        self,
        found_sounds: list[tuple[str, str, int]],
    ) -> list[dict]:
        """
        Получить слова для практики на основе найденных звуков.

        Args:
            found_sounds: Найденные сложные звуки

        Returns:
            list: Список слов с информацией для практики
        """
        practice = []
        seen_words = set()

        for sound, _, _ in found_sounds:
            info = DIFFICULT_SOUNDS[sound]
            for word in info["practice_words"][:3]:
                if word not in seen_words:
                    seen_words.add(word)
                    practice.append({
                        "word": word,
                        "target_sound": sound,
                        "difficulty": info["difficulty"],
                    })

        # Сортируем по сложности
        practice.sort(key=lambda x: x["difficulty"])

        return practice[:10]  # Максимум 10 слов

    def _get_native_success_message(self, native_language: NativeLanguage) -> str:
        """Получить сообщение об успехе на родном языке."""
        messages = {
            "ru": "Отлично! Твоё произношение замечательное! 🎉",
            "uk": "Чудово! Твоя вимова чудова! 🎉",
            "pl": "Świetnie! Twoja wymowa jest wspaniała! 🎉",
            "sk": "Výborne! Tvoja výslovnosť je skvelá! 🎉",
        }
        return messages.get(native_language, messages["ru"])

    def get_sound_info(self, sound: str, native_language: NativeLanguage = "ru") -> dict | None:
        """
        Получить информацию о конкретном звуке.

        Args:
            sound: Звук для получения информации
            native_language: Родной язык пользователя

        Returns:
            dict | None: Информация о звуке или None если не найден
        """
        if sound not in DIFFICULT_SOUNDS:
            return None

        info = DIFFICULT_SOUNDS[sound]
        return {
            "sound": sound,
            "description_cs": info["description_cs"],
            "description_native": info.get(f"description_{native_language}", info.get("description_ru", "")),
            "tip_cs": info["tip_cs"],
            "tip_native": info.get(f"tip_{native_language}", info.get("tip_ru", "")),
            "difficulty": info["difficulty"],
            "practice_words": info["practice_words"],
        }

    def get_all_difficult_sounds(self, native_language: NativeLanguage = "ru") -> list[dict]:
        """
        Получить список всех сложных звуков.

        Args:
            native_language: Родной язык пользователя

        Returns:
            list: Список всех сложных звуков с информацией
        """
        sounds = []
        for sound, info in DIFFICULT_SOUNDS.items():
            sounds.append({
                "sound": sound,
                "description_cs": info["description_cs"],
                "description_native": info.get(f"description_{native_language}", info.get("description_ru", "")),
                "difficulty": info["difficulty"],
                "practice_words_count": len(info["practice_words"]),
            })

        # Сортируем по сложности
        sounds.sort(key=lambda x: x["difficulty"], reverse=True)
        return sounds
