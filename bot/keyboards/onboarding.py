"""
Клавиатуры для онбординга.

Language Immersion: UI на чешском, выбираем только родной язык.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.localization import get_text


# Full list of supported native languages
# Pinned first, then alphabetical by Czech name
NATIVE_LANGUAGES = [
    # --- Pinned ---
    ("ru", "🇷🇺 Ruština"),
    ("uk", "🇺🇦 Ukrajinština"),
    ("pl", "🇵🇱 Polština"),
    ("vi", "🇻🇳 Vietnamština"),
    ("hi", "🇮🇳 Hindština"),
    # --- Alphabetical ---
    ("af", "🇿🇦 Afrikánština"),
    ("sq", "🇦🇱 Albánština"),
    ("en", "🇬🇧 Angličtina"),
    ("ar", "🇸🇦 Arabština"),
    ("hy", "🇦🇲 Arménština"),
    ("az", "🇦🇿 Ázerbájdžánština"),
    ("be", "🇧🇾 Běloruština"),
    ("bn", "🇧🇩 Bengálština"),
    ("bg", "🇧🇬 Bulharština"),
    ("zh", "🇨🇳 Čínština"),
    ("da", "🇩🇰 Dánština"),
    ("et", "🇪🇪 Estonština"),
    ("fi", "🇫🇮 Finština"),
    ("fr", "🇫🇷 Francouzština"),
    ("ka", "🇬🇪 Gruzínština"),
    ("he", "🇮🇱 Hebrejština"),
    ("nl", "🇳🇱 Holandština"),
    ("hr", "🇭🇷 Chorvatština"),
    ("id", "🇮🇩 Indonéština"),
    ("ga", "🇮🇪 Irština"),
    ("it", "🇮🇹 Italština"),
    ("ja", "🇯🇵 Japonština"),
    ("kk", "🇰🇿 Kazaština"),
    ("ko", "🇰🇷 Korejština"),
    ("ky", "🇰🇬 Kyrgyzština"),
    ("lo", "🇱🇦 Laoština"),
    ("lt", "🇱🇹 Litevština"),
    ("lv", "🇱🇻 Lotyšština"),
    ("hu", "🇭🇺 Maďarština"),
    ("mn", "🇲🇳 Mongolština"),
    ("my", "🇲🇲 Myanmarština"),
    ("de", "🇩🇪 Němčina"),
    ("no", "🇳🇴 Norština"),
    ("pa", "🇮🇳 Paňdžábština"),
    ("fa", "🇮🇷 Perština"),
    ("pt", "🇵🇹 Portugalština"),
    ("ro", "🇷🇴 Rumunština"),
    ("el", "🇬🇷 Řečtina"),
    ("sk", "🇸🇰 Slovenčina"),
    ("sl", "🇸🇮 Slovinština"),
    ("sr", "🇷🇸 Srbština"),
    ("su", "🇮🇩 Sundánština"),
    ("sw", "🇰🇪 Svahilština"),
    ("es", "🇪🇸 Španělština"),
    ("sv", "🇸🇪 Švédština"),
    ("tg", "🇹🇯 Tádžičtina"),
    ("tl", "🇵🇭 Tagalogština"),
    ("th", "🇹🇭 Thajština"),
    ("tr", "🇹🇷 Turečtina"),
    ("uz", "🇺🇿 Uzbečtina"),
]


def get_native_language_keyboard(page: int = 0, per_page: int = 8, prefix: str = "native") -> InlineKeyboardMarkup:
    """
    Клавиатура выбора родного языка с пагинацией.

    Page 0 shows pinned languages (first 5).
    Subsequent pages show remaining languages in chunks.

    Args:
        page: Page number (0-based)
        per_page: Items per page  
        prefix: Callback data prefix (e.g. "native" or "onb_native")

    Returns:
        Inline клавиатура
    """
    pinned_count = 5

    if page == 0:
        # Show pinned languages
        langs = NATIVE_LANGUAGES[:pinned_count]
        has_more = len(NATIVE_LANGUAGES) > pinned_count
    else:
        start = pinned_count + (page - 1) * per_page
        end = start + per_page
        langs = NATIVE_LANGUAGES[start:end]
        has_more = end < len(NATIVE_LANGUAGES)

    # Build 2-column layout
    rows: list[list[InlineKeyboardButton]] = []
    for i in range(0, len(langs), 2):
        row = [
            InlineKeyboardButton(
                text=langs[i][1],
                callback_data=f"{prefix}:{langs[i][0]}",
            )
        ]
        if i + 1 < len(langs):
            row.append(
                InlineKeyboardButton(
                    text=langs[i + 1][1],
                    callback_data=f"{prefix}:{langs[i + 1][0]}",
                )
            )
        rows.append(row)

    # Navigation buttons
    nav_row: list[InlineKeyboardButton] = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(text="◀️ Zpět", callback_data=f"{prefix}_page:{page - 1}")
        )
    if has_more:
        label = "Další jazyky ▶️" if page == 0 else "Další ▶️"
        nav_row.append(
            InlineKeyboardButton(text=label, callback_data=f"{prefix}_page:{page + 1}")
        )
    if nav_row:
        rows.append(nav_row)

    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_language_keyboard() -> InlineKeyboardMarkup:
    """
    Legacy: клавиатура выбора языка (для обратной совместимости).

    Returns:
        Inline клавиатура
    """
    return get_native_language_keyboard()


def get_level_keyboard(prefix: str = "level") -> InlineKeyboardMarkup:
    """
    Клавиатура выбора уровня чешского.

    Language Immersion: Все тексты на чешском.

    Args:
        prefix: Callback data prefix (e.g. "level" or "onb_level")

    Returns:
        Inline клавиатура
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("level_beginner"),  # 🌱 Začátečník
                    callback_data=f"{prefix}:beginner",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("level_intermediate"),  # 📚 Středně pokročilý
                    callback_data=f"{prefix}:intermediate",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("level_advanced"),  # 🎓 Pokročilý
                    callback_data=f"{prefix}:advanced",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("level_native"),  # 🏆 Rodilý mluvčí
                    callback_data=f"{prefix}:native",
                )
            ],
        ]
    )
    return keyboard


