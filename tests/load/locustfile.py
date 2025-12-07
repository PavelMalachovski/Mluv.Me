"""
Locust load testing для Mluv.Me API.

Тестирует основные пользовательские потоки:
1. Обработка голосовых сообщений (главный flow)
2. Получение статистики пользователя
3. Работа с сохраненными словами
4. Получение профиля пользователя

Запуск:
    locust -f tests/load/locustfile.py --host=http://localhost:8000 --users=100 --spawn-rate=10

Для production:
    locust -f tests/load/locustfile.py --host=https://api.mluv.me --users=1000 --spawn-rate=50 --run-time=30m --html=load_test_report.html
"""

import random
import base64
import io
from locust import HttpUser, task, between, events
import structlog

logger = structlog.get_logger(__name__)

# Примерное аудио для тестов (пустой ogg файл, минимальный размер)
# В реальных тестах можно использовать настоящие тестовые аудио файлы
FAKE_AUDIO_BASE64 = "T2dnUwACAAAAAAAAAABVc2VyAAAAAAAAVGVzdAA="


class MluvMeUser(HttpUser):
    """
    Симуляция пользователя Mluv.Me.

    Поведение:
    - Регистрация/получение профиля
    - Отправка голосовых сообщений (основная нагрузка)
    - Периодическая проверка статистики
    - Работа с сохраненными словами
    """

    wait_time = between(2, 5)  # Пауза между запросами 2-5 секунд

    def on_start(self):
        """Инициализация пользователя при старте."""
        # Генерируем уникальный telegram_id для этого пользователя
        self.user_id = random.randint(100000, 999999)
        self.telegram_id = self.user_id

        logger.info("load_test_user_started", user_id=self.user_id)

        # Создаем/получаем пользователя
        self.setup_user()

    def setup_user(self):
        """Создать или получить пользователя."""
        # Пытаемся создать нового пользователя
        response = self.client.post(
            "/api/v1/users",
            json={
                "telegram_id": self.telegram_id,
                "first_name": f"LoadTestUser{self.user_id}",
                "ui_language": random.choice(["ru", "uk"]),
                "level": random.choice(["beginner", "intermediate", "advanced"]),
            },
            name="POST /api/v1/users (create user)",
        )

        if response.status_code in [200, 201]:
            logger.info("load_test_user_created", user_id=self.user_id)
        else:
            # Пользователь уже существует, это нормально
            logger.debug("load_test_user_exists", user_id=self.user_id)

    @task(10)
    def process_voice_message(self):
        """
        Основной flow - отправка голосового сообщения.

        Вес: 10 (самая частая операция)
        """
        # Создаем минимальный fake аудио файл
        audio_data = base64.b64decode(FAKE_AUDIO_BASE64)

        with self.client.post(
            "/api/v1/lessons/process",
            data={"user_id": self.telegram_id},
            files={"audio": ("test_audio.ogg", io.BytesIO(audio_data), "audio/ogg")},
            catch_response=True,
            name="POST /api/v1/lessons/process (main flow)",
        ) as response:
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    # Проверяем, что ответ содержит ключевые поля
                    required_fields = [
                        "transcript",
                        "honzik_response_text",
                        "corrections",
                        "stars_earned",
                        "current_streak",
                    ]
                    for field in required_fields:
                        if field not in json_response:
                            response.failure(f"Missing field: {field}")
                            return

                    response.success()
                except Exception as e:
                    response.failure(f"JSON parse error: {e}")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(3)
    def get_user_stats(self):
        """
        Получить статистику пользователя.

        Вес: 3
        """
        self.client.get(
            f"/api/v1/stats/summary",
            params={"user_id": self.telegram_id},
            name="GET /api/v1/stats/summary",
        )

    @task(2)
    def get_user_profile(self):
        """
        Получить профиль пользователя.

        Вес: 2
        """
        self.client.get(
            f"/api/v1/users/{self.telegram_id}",
            name="GET /api/v1/users/{telegram_id}",
        )

    @task(2)
    def get_saved_words(self):
        """
        Получить сохраненные слова.

        Вес: 2
        """
        self.client.get(
            f"/api/v1/words",
            params={"user_id": self.telegram_id, "limit": 10},
            name="GET /api/v1/words",
        )

    @task(1)
    def get_streak_calendar(self):
        """
        Получить streak календарь.

        Вес: 1
        """
        self.client.get(
            f"/api/v1/stats/streak",
            params={"user_id": self.telegram_id},
            name="GET /api/v1/stats/streak",
        )

    def on_stop(self):
        """Действия при остановке пользователя."""
        logger.info("load_test_user_stopped", user_id=self.user_id)


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Действия при старте теста."""
    logger.info("load_test_started", host=environment.host)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Действия при остановке теста."""
    logger.info("load_test_stopped", host=environment.host)

    # Логируем финальную статистику
    stats = environment.stats
    logger.info(
        "load_test_results",
        total_requests=stats.total.num_requests,
        total_failures=stats.total.num_failures,
        avg_response_time=stats.total.avg_response_time,
        min_response_time=stats.total.min_response_time,
        max_response_time=stats.total.max_response_time,
        requests_per_second=stats.total.total_rps,
    )
