"""
Українська локалізація для Telegram бота.
"""

TEXTS_UK = {
    # Вітання та онбординг
    "welcome": "Привіт! Я Хонзік 🇨🇿\n\n"
    "Я допоможу тобі вивчити чеську мову через живе спілкування!\n\n"
    "🍺 Люблю пиво, кнедлики та хокей\n"
    "🗣️ Буду виправляти твої помилки та навчати новим словам\n"
    "💬 Просто говори зі мною чеською!\n\n"
    "Давай почнемо! Обери мову інтерфейсу:",
    "language_selected": "Чудово! Тепер обери свій рівень чеської мови:",
    "onboarding_complete": "Супер! Ми готові почати 🎉\n\n"
    "Надішли мені голосове повідомлення чеською, "
    "і я допоможу тобі покращити вимову та граматику!\n\n"
    "💡 Порада: Говори детально, не бійся помилятися - так вчаться швидше!",
    # Рівні
    "level_beginner": "Začátečník (Початківець)",
    "level_intermediate": "Středně pokročilý (Середній)",
    "level_advanced": "Pokročilý (Просунутий)",
    "level_native": "Rodilý (Носій)",
    # Мови
    "lang_russian": "🇷🇺 Русский",
    "lang_ukrainian": "🇺🇦 Українська",
    "lang_czech": "🇨🇿 Čeština",
    # Команда /help
    "help_header": "📚 Доступні команди:\n\n",
    "help_commands": "⚙️ <b>Налаштування:</b>\n"
    "/level - Змінити рівень чеської\n"
    "/voice_speed - Швидкість голосових відповідей\n"
    "/corrections - Рівень виправлень\n"
    "/style - Стиль спілкування Хонзіка\n\n"
    "📊 <b>Прогрес:</b>\n"
    "/stats - Статистика навчання\n"
    "/saved - Збережені слова\n\n"
    "🌟 <b>Підписка:</b>\n"
    "/subscribe - Pro доступ (необмежені повідомлення)\n"
    "/plan - Поточний план та скасування підписки\n\n"
    "🔄 <b>Інше:</b>\n"
    "/reset - Почати нову розмову\n"
    "/help - Показати цю довідку",
    "help_tips": "\n\n💡 <b>Поради від Хонзіка:</b>\n\n"
    "🎤 Використовуй голосові повідомлення замість тексту\n"
    "🤔 Не бійся помилятися - так вчаться швидше!\n"
    "🗣️ Говори багато й детально\n"
    "❤️ Питай про що завгодно - я знаю все про Чехію!\n"
    "🍺 Давай обговоримо пиво, кнедлики або хокей!",
    # Команда /stats
    "stats_header": "📊 <b>Твоя статистика:</b>\n\n",
    "stats_streak": "🔥 <b>Streak:</b> {streak} {days}\n",
    "stats_words": "📝 <b>Слів сказано:</b> {words}\n",
    "stats_correct": "✅ <b>Правильних:</b> {correct}%\n",
    "stats_messages": "💬 <b>Повідомлень:</b> {messages}\n",
    "stats_stars": "⭐ <b>Зірок зароблено:</b> {stars}\n",
    "stats_calendar": "\n📅 <b>Останні 7 днів:</b>\n{calendar}",
    "days_1": "день",
    "days_2": "дні",
    "days_5": "днів",
    # Команда /saved
    "saved_header": "💾 <b>Збережені слова:</b>\n\n",
    "saved_word": "• {word} - {translation}\n",
    "saved_empty": "У тебе поки немає збережених слів.\n\n"
    "Коли я буду виправляти твої помилки, "
    "ти зможеш зберігати нові слова!",
    "saved_show_all": "📖 Показати всі ({count})",
    # Команда /reset
    "reset_confirm": "Ти впевнений, що хочеш почати нову розмову?\n\n"
    "Попередні повідомлення будуть видалені з контексту, "
    "але історія та статистика збережуться.",
    "reset_yes": "✅ Так, почати нову розмову",
    "reset_no": "❌ Ні, продовжити поточну",
    "reset_done": "Готово! Починаємо нову розмову 🎉\n\n" "Про що поговоримо сьогодні?",
    # Налаштування - рівень
    "settings_level": "Обери свій рівень чеської:\n\n" "Поточний: <b>{current}</b>",
    "settings_level_changed": "Рівень змінено на: <b>{level}</b> ✅",
    # Налаштування - швидкість голосу
    "settings_voice_speed": "Обери швидкість голосу Хонзіка:\n\n"
    "Поточна: <b>{current}</b>",
    "voice_speed_very_slow": "🐌 Velmi pomalu (Дуже повільно)",
    "voice_speed_slow": "🚶 Pomalu (Повільно)",
    "voice_speed_normal": "🏃 Normálně (Нормально)",
    "voice_speed_native": "⚡ Rodilý (Як носій)",
    "settings_voice_speed_changed": "Швидкість змінено на: <b>{speed}</b> ✅",
    # Налаштування - рівень виправлень
    "settings_corrections": "Обери рівень виправлень:\n\n"
    "Поточний: <b>{current}</b>\n\n"
    "• <b>Minimální</b> - тільки критичні помилки\n"
    "• <b>Vyvážený</b> - збалансований (рекомендується)\n"
    "• <b>Detailní</b> - всі помилки з детальними поясненнями",
    "corrections_minimal": "📝 Minimální",
    "corrections_balanced": "⚖️ Vyvážený",
    "corrections_detailed": "📚 Detailní",
    "settings_corrections_changed": "Рівень виправлень змінено на: <b>{level}</b> ✅",
    # Налаштування - стиль спілкування
    "settings_style": "Обери стиль спілкування Хонзіка:\n\n"
    "Поточний: <b>{current}</b>\n\n"
    "• <b>Přátelský</b> - дружній, неформальний\n"
    "• <b>Učitel</b> - як репетитор, більше виправлень\n"
    "• <b>Kamarád</b> - як друг, мінімум виправлень",
    "style_friendly": "😊 Přátelský",
    "style_tutor": "👨‍🏫 Učitel",
    "style_casual": "🤝 Kamarád",
    "settings_style_changed": "Стиль спілкування змінено на: <b>{style}</b> ✅",
    # Обробка голосових
    "voice_processing": "Хонзік думає... 🤔",
    "voice_correctness": "✅ Правильність: {score}%",
    "voice_streak": "🔥 Streak: {streak}",
    "voice_stars_earned": "⭐ Зароблено зірок: +{stars}",
    # Виправлення
    "corrections_header": "\n📝 <b>Виправлення:</b>\n\n",
    "correction_item": "❌ <i>{original}</i>\n✅ <b>{corrected}</b>\n"
    "💡 {explanation}\n",
    "no_corrections": "🎉 Чудово! Помилок не знайдено!",
    "suggestion": "\n💬 <b>Tip:</b> {suggestion}",
    # Помилки
    "error_general": "Ой! Щось пішло не так 😅\n\n"
    "Спробуй ще раз через кілька секунд.",
    "error_voice_too_long": "Це занадто довге повідомлення! 😅\n\n"
    "Спробуй записати щось коротше (до 60 секунд).",
    "error_no_audio": "Не можу обробити це повідомлення.\n\n"
    "Надішли мені голосове повідомлення чеською!",
    "error_backend": "Хонзік тимчасово недоступний 🔧\n\n"
    "Ми вже працюємо над цим, спробуй пізніше!",
    # Транскрипція
    "show_transcript": "📄 Показати транскрипцію",
    "transcript_text": "📄 <b>Транскрипція:</b>\n\n{text}",
    # Текстова відповідь Хонзіка
    "btn_show_text": "📝 Text",
    "btn_show_opravy": "📝 Opravy",
    "btn_menu": "📱 Menu",
    "honzik_text_response": "📝 <b>Текст відповіді Хонзіка:</b>\n\n{text}",
    # Збереження слів
    "save_word": "💾 Зберегти слово",
    "word_saved": "Слово збережено! 💾",
    # Кнопки
    "btn_back": "« Назад",
    "btn_cancel": "❌ Скасувати",
    # Переклад слів
    "translate_usage": "Використання: <code>/translate &lt;слово&gt;</code>\n\n"
    "Приклад: <code>/translate ahoj</code>",
    "translate_result": "📖 <b>Переклад:</b>\n\n"
    "🇨🇿 <b>{word}</b> → 🇺🇦 <b>{translation}</b>",
    "translate_error": "Не вдалося перекласти слово 😅\n\n"
    "Спробуй ще раз або використай кнопку 'Menu' для інтерактивного перекладу.",
    "phonetics": "Фонетика",
    # Star Shop
    "shop_header": "⭐ <b>Star Shop</b> — У тебе {stars}⭐",
    "shop_streak_shield": "Streak Shield",
    "shop_streak_shield_desc": "Захистить твій streak на 1 пропущений день",
    "shop_trial_premium": "Pro на 1 день",
    "shop_trial_premium_desc": "Безлімітний доступ на 24 години",
    "shop_scenarios_header": "Розблокування сценаріїв",
    "shop_purchase_success": "✅ <b>{item}</b> придбано за {cost}⭐\n\nЗалишилось: {remaining}⭐",
    "shop_insufficient_stars": "❌ Недостатньо зірок.\nПотрібно {cost}⭐, у тебе {available}⭐",
    "shop_shield_already_active": "🛡 Streak Shield вже активний!",
    "shop_already_pro": "💎 У тебе вже є Pro доступ!",
    "shop_scenario_unlocked": "🎭 Сценарій <b>{scenario}</b> розблоковано за {cost}⭐!\nЗалишилось: {remaining}⭐",
    # Інше
    "already_registered": "Ти вже зареєстрований!\n\n"
    "Використовуй /help щоб дізнатися що я вмію.",
}
