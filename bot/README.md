# 🤖 Mluv.Me Telegram Bot

Telegram бот для практики чешского языка с AI-персонажем Хонзиком.

---

## 📁 Структура

```
bot/
├── main.py              # Главный файл запуска бота
├── config.py           # Конфигурация (Pydantic Settings)
├── handlers/           # Обработчики команд и сообщений
│   ├── __init__.py    # Главный роутер
│   ├── start.py       # /start и онбординг
│   ├── voice.py       # Обработка голосовых
│   └── commands.py    # Все команды
├── keyboards/          # Inline клавиатуры
│   ├── __init__.py
│   ├── onboarding.py  # Клавиатуры для онбординга
│   └── settings.py    # Клавиатуры настроек
├── localization/       # Локализация
│   ├── __init__.py    # Функции локализации
│   ├── ru.py         # Русские тексты
│   └── uk.py         # Украинские тексты
└── services/          # Сервисы
    ├── __init__.py
    └── api_client.py  # HTTP клиент к backend
```

---

## 🚀 Запуск

### Локально

```bash
# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
export TELEGRAM_BOT_TOKEN=your_token
export BACKEND_API_URL=http://localhost:8000

# Запустить бота
python bot/main.py
```

### Railway

Бот автоматически запускается вместе с backend через `Dockerfile`.

---

## 🎮 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Начать обучение с Хонзиком |
| `/help` | Справка и советы |
| `/stats` | Моя статистика |
| `/saved` | Сохраненные слова |
| `/level` | Изменить уровень чешского |
| `/voice_speed` | Скорость голоса Хонзика |
| `/corrections` | Уровень исправлений |
| `/style` | Стиль общения |
| `/reset` | Начать новый разговор |

---

## 🌍 Локализация

Бот поддерживает 2 языка интерфейса:
- 🇷🇺 Русский
- 🇺🇦 Українська

Целевой язык обучения:
- 🇨🇿 Чешский

---

## 🏗️ Архитектура

### Принципы
- **Тонкие handlers** - вся логика в backend
- **Middleware pattern** - для внедрения зависимостей
- **Type hints** - везде для IDE support
- **Async/await** - для всех I/O операций
- **Error handling** - graceful обработка ошибок

### Handlers
- `start.py` - Онбординг flow (язык → уровень → регистрация)
- `voice.py` - Обработка голосовых (STT через backend)
- `commands.py` - Все команды (help, stats, settings)

### Services
- `api_client.py` - HTTP клиент к backend API
  - Все методы async
  - Автоматическое управление сессией
  - Error logging

### Keyboards
- `onboarding.py` - Выбор языка и уровня
- `settings.py` - Настройки (скорость, стиль, исправления)

### Localization
- `get_text(key, language)` - Получить текст
- `get_days_word(count, language)` - Склонение слова "день"

---

## 🔧 Конфигурация

### Переменные окружения

```env
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
BACKEND_API_URL=http://localhost:8000
ENVIRONMENT=development
LOG_LEVEL=INFO
WEBHOOK_URL=  # Опционально для Railway
```

### Режимы работы
- **Polling** (по умолчанию) - для локальной разработки
- **Webhook** (опционально) - для production на Railway

---

## 📝 Логирование

Все события логируются в JSON формате через `structlog`:

```json
{
  "event": "voice_processed",
  "telegram_id": 123456,
  "score": 85,
  "streak": 3,
  "timestamp": "2025-12-06T..."
}
```

### Основные события
- `onboarding_started` - пользователь начал онбординг
- `user_registered` - пользователь зарегистрирован
- `voice_processed` - голосовое обработано
- `level_changed` - изменен уровень
- `conversation_reset` - сброшен контекст

---

## 🧪 Тестирование

### Локальное тестирование

1. Запусти backend:
   ```bash
   cd backend
   uvicorn backend.main:app --reload
   ```

2. Запусти бота:
   ```bash
   python bot/main.py
   ```

3. Открой бота в Telegram и отправь `/start`

### Smoke tests
- ✅ /start запускает онбординг
- ✅ Выбор языка работает
- ✅ Выбор уровня создает пользователя
- ✅ Голосовые обрабатываются
- ✅ Все команды отвечают

---

## 🐛 Troubleshooting

### Бот не отвечает
1. Проверь `TELEGRAM_BOT_TOKEN`
2. Проверь логи: `python bot/main.py`
3. Убедись что backend запущен

### Backend недоступен
1. Проверь `BACKEND_API_URL`
2. Проверь что backend работает: `curl http://localhost:8000/health`

### Голосовые не работают
1. Проверь OpenAI API в backend
2. Проверь формат аудио (должен быть ogg)
3. Проверь timeout (30 секунд)

---

## 📚 Документация

- [WEEK3_SUMMARY.md](../docs/WEEK3_SUMMARY.md) - Полный обзор Week 3
- [BOTFATHER_SETUP.md](../docs/BOTFATHER_SETUP.md) - Настройка BotFather
- [DEPLOYMENT_CHECKLIST.md](../docs/DEPLOYMENT_CHECKLIST.md) - Чеклист деплоя

---

## 🎯 TODO

- [ ] Добавить inline кнопки "Показать транскрипцию"
- [ ] Добавить inline кнопку "Сохранить слово"
- [ ] Реализовать календарь streak
- [ ] Добавить приветственное аудио от Хонзика
- [ ] Webhook режим для Railway

---

## 🙌 Contribution

При добавлении новых фич:
1. Добавь handler в `handlers/`
2. Добавь локализацию в `localization/ru.py` и `uk.py`
3. Добавь клавиатуру если нужно в `keyboards/`
4. Обнови документацию

---

**Na zdraví! 🍺**


