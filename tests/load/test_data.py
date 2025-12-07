"""
Тестовые данные для load testing.

Содержит реалистичные примеры чешских фраз для тестирования.
"""

import random

# Примеры чешских фраз разного уровня сложности
CZECH_PHRASES_BEGINNER = [
    "Ahoj, jak se máš?",
    "Děkuji, mám se dobře.",
    "Jak se jmenuješ?",
    "Jmenuji se Jan.",
    "Kolik je hodin?",
    "Je osm hodin.",
    "Kde je nádraží?",
    "Mluvíš anglicky?",
    "Nerozumím.",
    "Prosím, pomoc!",
]

CZECH_PHRASES_INTERMEDIATE = [
    "Rád bych si objednal pivo, prosím.",
    "Kde najdu nejlepší knedlíky v Praze?",
    "Jak dlouho trvá cesta do centra?",
    "Můžete mi doporučit dobrou restauraci?",
    "Včera jsem byl v národním muzeu.",
    "Chci si koupit lístek na vlak.",
    "Pracuji jako programátor v Praze.",
    "Učím se česky už šest měsíců.",
    "V neděli půjdu na hokejový zápas.",
    "Miluji českou kuchyni a pivo!",
]

CZECH_PHRASES_ADVANCED = [
    "Domnívám se, že česká literatura má bohatou tradici a významný vliv na evropskou kulturu.",
    "Pokud bych měl možnost, určitě bych navštívil všechny historické hrady v České republice.",
    "Ekonomická situace v zemi se zlepšuje díky růstu technologického sektoru.",
    "Zajímalo by mě, jaký je váš názor na současnou politickou situaci?",
    "Nedávno jsem dokončil čtení knihy od Milana Kundery, která mě velice zaujala.",
    "Architektura Prahy je úchvatná, zejména barokní a gotické stavby.",
    "Byl bych rád, kdybychom mohli diskutovat o této otázce podrobněji.",
    "Myslím si, že je důležité zachovat tradiční české hodnoty i v moderní době.",
]


def get_random_phrase(level: str = "beginner") -> str:
    """
    Получить случайную чешскую фразу по уровню.

    Args:
        level: Уровень сложности (beginner, intermediate, advanced)

    Returns:
        str: Случайная фраза
    """
    phrases_map = {
        "beginner": CZECH_PHRASES_BEGINNER,
        "intermediate": CZECH_PHRASES_INTERMEDIATE,
        "advanced": CZECH_PHRASES_ADVANCED,
        "native": CZECH_PHRASES_ADVANCED,
    }

    phrases = phrases_map.get(level, CZECH_PHRASES_BEGINNER)
    return random.choice(phrases)


def get_random_user_settings() -> dict:
    """
    Получить случайные настройки пользователя для тестов.

    Returns:
        dict: Настройки пользователя
    """
    return {
        "ui_language": random.choice(["ru", "uk"]),
        "level": random.choice(["beginner", "intermediate", "advanced"]),
        "conversation_style": random.choice(["friendly", "tutor", "casual"]),
        "voice_speed": random.choice(["very_slow", "slow", "normal", "native"]),
        "corrections_level": random.choice(["minimal", "balanced", "detailed"]),
    }
