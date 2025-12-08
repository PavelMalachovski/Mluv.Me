# Telegram Web App Setup для Mluv.Me

**Цель**: Сделать Web UI доступным прямо в Telegram через кнопку Menu

## 🎯 Что такое Telegram Web App?

Telegram Web App (Mini App) - это веб-интерфейс, который открывается **внутри Telegram** без перехода в браузер.

**Примеры**:
- Chatty English Tutor - кнопка Menu открывает интерфейс
- Notcoin, Hamster Combat и другие игры
- Web-интерфейсы ботов прямо в чате

## 📋 Настройка через BotFather

### 1. Откройте BotFather

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/mybots`
3. Выберите вашего бота **@mluvme_bot** (или как он называется)

### 2. Настройте Menu Button

1. Выберите **Bot Settings**
2. Выберите **Menu Button**
3. Отправьте:
   - **Button Text**: `Open App` или `Открыть приложение` или `🎓 Учить чешский`
   - **URL**: `https://mluvme-production.up.railway.app`

### 3. Альтернатива: Web App кнопка в сообщениях

Можно также добавлять кнопки с Web App прямо в сообщения бота.

## 💻 Интеграция в код бота

### Вариант 1: Menu Button (рекомендуется)

Уже настроено через BotFather, ничего менять в коде не нужно!

После настройки кнопка Menu автоматически появится в интерфейсе чата.

### Вариант 2: Inline кнопки в сообщениях

Добавить кнопку "Открыть Web UI" в приветственное сообщение:

```python
# bot/handlers/start.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

def get_web_app_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой Web App."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎓 Открыть Web UI",
                web_app=WebAppInfo(url="https://mluvme-production.up.railway.app")
            )
        ],
        [
            InlineKeyboardButton(
                text="ℹ️ Помощь",
                callback_data="help"
            )
        ]
    ])

@router.message(CommandStart())
async def command_start_handler(message: Message, api_client: APIClient) -> None:
    """Обработчик команды /start."""
    telegram_id = message.from_user.id

    user = await api_client.get_user(telegram_id)

    if user:
        # Пользователь уже зарегистрирован
        language = user.get("ui_language", "ru")
        await message.answer(
            get_text("already_registered", language),
            reply_markup=get_web_app_keyboard()  # ← Добавили кнопку!
        )
        return

    # ... остальной код онбординга
```

### Вариант 3: Кнопка в меню команд

```python
# bot/handlers/commands.py
from aiogram.types import BotCommand, BotCommandScopeDefault

commands = [
    BotCommand(command="start", description="Начать работу"),
    BotCommand(command="help", description="Помощь"),
    BotCommand(command="webapp", description="🎓 Открыть Web UI"),
]

# При старте бота:
await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
```

## 🔧 Требования к Web UI

Telegram Web App имеет особенности:

### 1. Telegram Web App SDK

Добавьте в ваш Next.js `<head>`:

```html
<!-- frontend/app/layout.tsx -->
<script src="https://telegram.org/js/telegram-web-app.js"></script>
```

### 2. Инициализация Telegram Web App

```typescript
// frontend/lib/telegram-web-app.ts
export interface TelegramWebApp {
  initData: string;
  initDataUnsafe: {
    user?: {
      id: number;
      first_name: string;
      last_name?: string;
      username?: string;
      language_code?: string;
    };
  };
  ready: () => void;
  expand: () => void;
  close: () => void;
  MainButton: {
    text: string;
    color: string;
    textColor: string;
    isVisible: boolean;
    isActive: boolean;
    show: () => void;
    hide: () => void;
    onClick: (callback: () => void) => void;
  };
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp;
    };
  }
}

export const useTelegramWebApp = () => {
  if (typeof window === 'undefined') return null;
  return window.Telegram?.WebApp || null;
};
```

### 3. Использование в компонентах

```typescript
// frontend/app/page.tsx
'use client';

import { useEffect } from 'react';
import { useTelegramWebApp } from '@/lib/telegram-web-app';

export default function HomePage() {
  const webApp = useTelegramWebApp();

  useEffect(() => {
    if (webApp) {
      // Готов к работе
      webApp.ready();

      // Развернуть на весь экран
      webApp.expand();

      // Получить данные пользователя
      const user = webApp.initDataUnsafe.user;
      console.log('Telegram User:', user);

      // Показать кнопку внизу
      webApp.MainButton.text = 'Начать урок';
      webApp.MainButton.show();
      webApp.MainButton.onClick(() => {
        // Действие при клике
        router.push('/dashboard/practice');
      });
    }
  }, [webApp]);

  return (
    <div>
      <h1>Mluv.Me - Учим чешский</h1>
      {/* ... */}
    </div>
  );
}
```

## 🎨 Стилизация под Telegram

Telegram Web App автоматически передает цветовую схему:

```typescript
const themeParams = webApp?.themeParams;

// Используйте цвета Telegram
const colors = {
  bg: themeParams?.bg_color || '#ffffff',
  text: themeParams?.text_color || '#000000',
  button: themeParams?.button_color || '#3390ec',
  buttonText: themeParams?.button_text_color || '#ffffff',
};
```

## 📱 Тестирование

### 1. Локально (не сработает)

Web App работает только с HTTPS! Локальный `http://localhost` **не работает**.

### 2. На Railway (production)

1. Откройте вашего бота в Telegram
2. Нажмите кнопку **Menu** (☰) возле поля ввода
3. Должен открыться Web UI

### 3. Проверка данных

Web App передает `initData` - зашифрованную строку с данными пользователя.

**Важно**: Проверяйте подпись на backend!

```python
# backend/routers/web_auth.py
import hmac
import hashlib
from urllib.parse import parse_qsl

def validate_telegram_web_app_data(init_data: str, bot_token: str) -> dict:
    """Проверка подписи Telegram Web App."""
    parsed_data = dict(parse_qsl(init_data))

    hash_value = parsed_data.pop('hash', None)
    if not hash_value:
        raise ValueError("No hash in init_data")

    # Создаем check string
    check_string = '\n'.join(f"{k}={v}" for k, v in sorted(parsed_data.items()))

    # Создаем secret key
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode(),
        digestmod=hashlib.sha256
    ).digest()

    # Проверяем подпись
    calculated_hash = hmac.new(
        key=secret_key,
        msg=check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    if calculated_hash != hash_value:
        raise ValueError("Invalid hash")

    return parsed_data
```

## 🚀 Быстрый старт

### Минимальная настройка (5 минут):

1. **BotFather** → Menu Button → URL: `https://mluvme-production.up.railway.app`

2. **Добавить SDK** в `frontend/app/layout.tsx`:
```typescript
<script src="https://telegram.org/js/telegram-web-app.js"></script>
```

3. **Тестировать**: откройте бота → нажмите Menu

Готово! Web UI откроется прямо в Telegram! 🎉

## 📚 Документация

- [Telegram Web Apps](https://core.telegram.org/bots/webapps)
- [Bot API - Web Apps](https://core.telegram.org/bots/api#webapps)
- [Примеры Web Apps](https://github.com/telegram-mini-apps)

---

## Текущий статус

- ✅ Backend API работает: `https://mluvme-production.up.railway.app/api/health`
- ✅ Frontend собран и развернут
- ✅ Reverse proxy настроен
- ⏳ **TODO**: Настроить Menu Button в BotFather
- ⏳ **TODO**: Добавить Telegram Web App SDK в frontend
- ⏳ **TODO**: Проверить подпись initData на backend

**Следующий шаг**: Откройте @BotFather и настройте Menu Button! 🚀
