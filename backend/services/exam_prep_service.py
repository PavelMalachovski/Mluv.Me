"""
Exam Preparation Service for official Czech language exams.

Подготовка к официальным экзаменам:
- A1 (ВНЖ) - Povolení k pobytu
- A2 (ПМЖ) - Trvalý pobyt
- B1 (Гражданство) - Státní občanství
"""

from datetime import datetime, timezone
from typing import Literal
import random

import structlog

from backend.services.openai_client import OpenAIClient

logger = structlog.get_logger(__name__)

ExamLevel = Literal["a1_vnzh", "a2_pmzh", "b1_citizenship"]


# Определения экзаменов
EXAMS = {
    "a1_vnzh": {
        "name_cs": "Čeština pro ВНЖ (A1)",
        "name_ru": "Чешский для ВНЖ (A1)",
        "official_name": "Zkouška z českého jazyka pro získání povolení k trvalému pobytu (A1)",
        "description_cs": "Základní komunikace pro život v Česku.",
        "description_ru": "Базовая коммуникация для жизни в Чехии.",
        "modules": [
            {"id": "listening", "name_cs": "Poslech", "name_ru": "Аудирование", "questions": 10},
            {"id": "reading", "name_cs": "Čtení", "name_ru": "Чтение", "questions": 10},
            {"id": "writing", "name_cs": "Psaní", "name_ru": "Письмо", "questions": 3},
            {"id": "speaking", "name_cs": "Mluvení", "name_ru": "Говорение", "questions": 3},
        ],
        "passing_score": 60,
        "duration_minutes": 60,
        "fee_czk": 2000,
        "study_weeks": 8,
    },
    "a2_pmzh": {
        "name_cs": "Čeština pro ПМЖ (A2)",
        "name_ru": "Чешский для ПМЖ (A2)",
        "official_name": "Zkouška z českého jazyka pro získání trvalého pobytu (A2)",
        "description_cs": "Pokročilejší komunikace pro trvalý pobyt.",
        "description_ru": "Продвинутая коммуникация для постоянного проживания.",
        "modules": [
            {"id": "listening", "name_cs": "Poslech", "name_ru": "Аудирование", "questions": 15},
            {"id": "reading", "name_cs": "Čtení", "name_ru": "Чтение", "questions": 15},
            {"id": "writing", "name_cs": "Psaní", "name_ru": "Письмо", "questions": 5},
            {"id": "speaking", "name_cs": "Mluvení", "name_ru": "Говорение", "questions": 4},
        ],
        "passing_score": 60,
        "duration_minutes": 90,
        "fee_czk": 2500,
        "study_weeks": 16,
    },
    "b1_citizenship": {
        "name_cs": "Čeština pro občanství (B1)",
        "name_ru": "Чешский для гражданства (B1)",
        "official_name": "Zkouška z českého jazyka pro účely udělování státního občanství ČR (B1)",
        "description_cs": "Pokročilá komunikace pro získání občanství.",
        "description_ru": "Продвинутая коммуникация для получения гражданства.",
        "modules": [
            {"id": "listening", "name_cs": "Poslech", "name_ru": "Аудирование", "questions": 20},
            {"id": "reading", "name_cs": "Čtení", "name_ru": "Чтение", "questions": 20},
            {"id": "writing", "name_cs": "Psaní", "name_ru": "Письмо", "questions": 5},
            {"id": "speaking", "name_cs": "Mluvení", "name_ru": "Говорение", "questions": 5},
        ],
        "passing_score": 60,
        "duration_minutes": 120,
        "fee_czk": 3000,
        "study_weeks": 24,
    },
}


# Банк упражнений по модулям
EXERCISE_BANK = {
    "listening": {
        "a1": [
            {
                "audio_text": "Dobrý den. Jmenuji se Pavel. Jsem z Prahy.",
                "question": "Jak se jmenuje muž?",
                "options": ["Pavel", "Petr", "Martin", "Jakub"],
                "correct": 0,
            },
            {
                "audio_text": "Rád piju pivo a jím svíčkovou.",
                "question": "Co rád pije muž?",
                "options": ["víno", "pivo", "čaj", "kávu"],
                "correct": 1,
            },
            {
                "audio_text": "Tramvaj číslo 22 jede na Malostranské náměstí.",
                "question": "Kam jede tramvaj?",
                "options": ["Na letiště", "Do centra", "Na Malostranské náměstí", "Na hlavní nádraží"],
                "correct": 2,
            },
        ],
    },
    "reading": {
        "a1": [
            {
                "text": "Ahoj! Jmenuji se Anna. Jsem studentka. Bydlím v Brně. Rád čtu knihy a jezdím na kole.",
                "question": "Kde bydlí Anna?",
                "options": ["V Praze", "V Brně", "V Ostravě", "V Plzni"],
                "correct": 1,
            },
            {
                "text": "Restaurace je otevřena od 11:00 do 22:00. V neděli je zavřeno.",
                "question": "Kdy je restaurace zavřená?",
                "options": ["V sobotu", "V pondělí", "V neděli", "Ve středu"],
                "correct": 2,
            },
        ],
    },
    "writing": {
        "a1": [
            {
                "task": "Napište krátký email. Představte se - jméno, věk, odkud jste, co děláte.",
                "hints": ["Začněte: Dobrý den,", "Napište 3-5 vět", "Zakončete: S pozdravem, ..."],
                "word_count": 50,
            },
            {
                "task": "Vyplňte formulář: jméno, příjmení, adresa, telefon.",
                "hints": ["Použijte velká písmena pro jména", "Formát telefonu: +420..."],
                "word_count": 30,
            },
        ],
    },
    "speaking": {
        "a1": [
            {
                "topic": "Představte se",
                "prompts": [
                    "Jak se jmenujete?",
                    "Odkud jste?",
                    "Jaké je vaše zaměstnání?",
                    "Co rádi děláte?",
                ],
                "duration_seconds": 60,
            },
            {
                "topic": "Nakupování",
                "prompts": [
                    "Co potřebujete koupit?",
                    "Kde nakupujete?",
                    "Kolik to stojí?",
                ],
                "duration_seconds": 45,
            },
        ],
    },
}


class ExamPrepService:
    """
    Сервис подготовки к экзаменам.

    Предоставляет учебный план, упражнения и пробные тесты.
    """

    def __init__(self, openai_client: OpenAIClient | None = None):
        self.openai_client = openai_client
        self.logger = logger.bind(service="exam_prep_service")

        # In-memory прогресс (в продакшене заменить на БД)
        self._user_progress: dict[int, dict] = {}

    def get_available_exams(self) -> list[dict]:
        """
        Получить список доступных экзаменов.
        """
        return [
            {
                "id": exam_id,
                "name_cs": exam["name_cs"],
                "name_ru": exam["name_ru"],
                "official_name": exam["official_name"],
                "description_cs": exam["description_cs"],
                "description_ru": exam["description_ru"],
                "modules": exam["modules"],
                "passing_score": exam["passing_score"],
                "duration_minutes": exam["duration_minutes"],
                "fee_czk": exam["fee_czk"],
                "study_weeks": exam["study_weeks"],
            }
            for exam_id, exam in EXAMS.items()
        ]

    def get_study_plan(
        self,
        user_id: int,
        exam_id: ExamLevel,
        start_date: datetime | None = None,
    ) -> dict:
        """
        Получить персонализированный учебный план.

        Args:
            user_id: ID пользователя
            exam_id: ID экзамена
            start_date: Дата начала подготовки

        Returns:
            dict: Учебный план по неделям
        """
        if exam_id not in EXAMS:
            raise ValueError(f"Unknown exam: {exam_id}")

        exam = EXAMS[exam_id]
        weeks = exam["study_weeks"]

        if start_date is None:
            start_date = datetime.now(timezone.utc)

        # Генерируем план по неделям
        weekly_plan = []
        modules = exam["modules"]

        for week in range(1, weeks + 1):
            # Распределяем модули по неделям
            focus_module = modules[(week - 1) % len(modules)]

            weekly_plan.append({
                "week": week,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "focus_module": focus_module["name_cs"],
                "tasks": [
                    f"Procvičuj {focus_module['name_cs']} - 30 minut denně",
                    "Naučte se 10 nových slovíček",
                    "Poslechněte 1 podcast v češtině",
                ],
                "goal": f"Zvládnout základy modulu {focus_module['name_cs']}",
            })

        # Сохраняем прогресс
        self._user_progress[user_id] = {
            "exam_id": exam_id,
            "started_at": start_date.isoformat(),
            "current_week": 1,
            "completed_exercises": 0,
        }

        return {
            "exam_id": exam_id,
            "exam_name": exam["name_cs"],
            "total_weeks": weeks,
            "weekly_plan": weekly_plan,
            "tips": [
                "Procvičujte každý den alespoň 30 minut",
                "Používejte Honzíka pro konverzační praxi",
                "Sledujte české filmy s titulky",
            ],
        }

    async def get_practice_exercise(
        self,
        user_id: int,
        module: str,
        level: str = "a1",
    ) -> dict:
        """
        Получить упражнение для практики.

        Args:
            user_id: ID пользователя
            module: Тип модуля (listening, reading, writing, speaking)
            level: Уровень (a1, a2, b1)

        Returns:
            dict: Упражнение
        """
        if module not in EXERCISE_BANK:
            raise ValueError(f"Unknown module: {module}")

        exercises = EXERCISE_BANK[module].get(level, EXERCISE_BANK[module].get("a1", []))

        if not exercises:
            return {"error": "No exercises available"}

        exercise = random.choice(exercises)

        return {
            "module": module,
            "level": level,
            "exercise": exercise,
            "exercise_type": "multiple_choice" if "options" in exercise else "open",
        }

    def submit_exercise_answer(
        self,
        user_id: int,
        exercise: dict,
        answer: str | int,
    ) -> dict:
        """
        Проверить ответ на упражнение.

        Args:
            user_id: ID пользователя
            exercise: Упражнение
            answer: Ответ пользователя

        Returns:
            dict: Результат
        """
        is_correct = False

        if "options" in exercise:
            # Multiple choice
            correct_idx = exercise.get("correct", 0)
            is_correct = answer == correct_idx

        # Обновляем прогресс
        if user_id in self._user_progress:
            self._user_progress[user_id]["completed_exercises"] += 1

        return {
            "is_correct": is_correct,
            "correct_answer": exercise.get("options", [])[exercise.get("correct", 0)]
                if "options" in exercise else None,
            "user_answer": answer,
            "explanation": "Správně!" if is_correct else "Zkus to znovu!",
        }

    async def generate_mock_test(
        self,
        user_id: int,
        exam_id: ExamLevel,
    ) -> dict:
        """
        Сгенерировать пробный тест.

        Args:
            user_id: ID пользователя
            exam_id: ID экзамена

        Returns:
            dict: Пробный тест
        """
        if exam_id not in EXAMS:
            raise ValueError(f"Unknown exam: {exam_id}")

        exam = EXAMS[exam_id]

        # Собираем вопросы из всех модулей
        test_questions = []
        level = exam_id.split("_")[0]  # a1, a2, b1

        for module in exam["modules"]:
            module_id = module["id"]
            if module_id in EXERCISE_BANK:
                exercises = EXERCISE_BANK[module_id].get(level, EXERCISE_BANK[module_id].get("a1", []))
                for ex in exercises[:module["questions"]]:
                    test_questions.append({
                        "module": module_id,
                        "module_name": module["name_cs"],
                        **ex,
                    })

        return {
            "exam_id": exam_id,
            "exam_name": exam["name_cs"],
            "questions": test_questions,
            "total_questions": len(test_questions),
            "duration_minutes": exam["duration_minutes"],
            "passing_score": exam["passing_score"],
        }

    def get_user_progress(self, user_id: int) -> dict | None:
        """Получить прогресс пользователя."""
        return self._user_progress.get(user_id)
