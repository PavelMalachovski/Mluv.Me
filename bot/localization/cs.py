"""
Česká lokalizace pro Telegram bota.

Všechny texty jsou v češtině pro uživatele, kteří preferují český interface.
"""

TEXTS_CS = {
    # Uvítání a onboarding
    "welcome": "Ahoj! Jsem Honzík 🇨🇿\n\n"
    "Pomohu ti naučit se česky přes živou konverzaci!\n\n"
    "🍺 Miluji pivo, knedlíky a hokej\n"
    "🗣️ Budu opravovat tvoje chyby a učit tě nová slova\n"
    "💬 Prostě se mnou mluv česky!\n\n"
    "Pojďme začít! Vyber jazyk rozhraní:",

    "language_selected": "Výborně! Teď vyber svoji úroveň češtiny:",

    "onboarding_complete": "Super! Jsme připraveni začít 🎉\n\n"
    "Pošli mi hlasovou zprávu v češtině a "
    "já ti pomohu zlepšit výslovnost a gramatiku!\n\n"
    "💡 Tip: Mluv hodně, neboj se chybovat - tak se učíš rychleji!",

    # Úrovně
    "level_beginner": "Začátečník",
    "level_intermediate": "Středně pokročilý",
    "level_advanced": "Pokročilý",
    "level_native": "Rodilý mluvčí",

    # Jazyky
    "lang_russian": "🇷🇺 Rusky",
    "lang_ukrainian": "🇺🇦 Ukrajinsky",
    "lang_czech": "🇨🇿 Česky",

    # Příkaz /help
    "help_header": "📚 Dostupné příkazy:\n\n",
    "help_commands": "⚙️ <b>Nastavení:</b>\n"
    "/level - Změnit úroveň češtiny\n"
    "/voice_speed - Rychlost hlasových odpovědí\n"
    "/corrections - Úroveň oprav\n"
    "/style - Styl komunikace Honzíka\n\n"
    "📊 <b>Pokrok:</b>\n"
    "/stats - Statistiky učení\n"
    "/saved - Uložená slova\n\n"
    "🔄 <b>Ostatní:</b>\n"
    "/reset - Začít novou konverzaci\n"
    "/help - Zobrazit tuto nápovědu",

    "help_tips": "\n\n💡 <b>Tipy od Honzíka:</b>\n\n"
    "🎤 Používej hlasové zprávy místo textu\n"
    "🤔 Neboj se chybovat - tak se učíš rychleji!\n"
    "🗣️ Mluv hodně a podrobně\n"
    "❤️ Ptej se na cokoliv - znám všechno o Česku!\n"
    "🍺 Pojďme si promluvit o pivu, knedlících nebo hokeji!",

    # Příkaz /stats
    "stats_header": "📊 <b>Tvoje statistiky:</b>\n\n",
    "stats_streak": "🔥 <b>Série:</b> {streak} {days}\n",
    "stats_words": "📝 <b>Slov řečeno:</b> {words}\n",
    "stats_correct": "✅ <b>Správných:</b> {correct}%\n",
    "stats_messages": "💬 <b>Zpráv:</b> {messages}\n",
    "stats_stars": "⭐ <b>Hvězd získáno:</b> {stars}\n",
    "stats_calendar": "\n📅 <b>Posledních 7 dní:</b>\n{calendar}",
    "days_1": "den",
    "days_2": "dny",
    "days_5": "dní",

    # Příkaz /saved
    "saved_header": "💾 <b>Uložená slova:</b>\n\n",
    "saved_word": "• {word} - {translation}\n",
    "saved_empty": "Zatím nemáš žádná uložená slova.\n\n"
    "Když budu opravovat tvoje chyby, můžeš si ukládat nová slova!",
    "saved_show_all": "📖 Zobrazit všechna ({count})",

    # Příkaz /reset
    "reset_confirm": "Opravdu chceš začít novou konverzaci?\n\n"
    "Předchozí zprávy budou smazány z kontextu, "
    "ale historie a statistiky zůstanou.",
    "reset_yes": "✅ Ano, začít novou konverzaci",
    "reset_no": "❌ Ne, pokračovat",
    "reset_done": "Hotovo! Začínáme novou konverzaci 🎉\n\n"
    "O čem si dnes promluvíme?",

    # Nastavení - úroveň
    "settings_level": "Vyber svoji úroveň češtiny:\n\n"
    "Aktuální: <b>{current}</b>",
    "settings_level_changed": "Úroveň změněna na: <b>{level}</b> ✅",

    # Nastavení - rychlost hlasu
    "settings_voice_speed": "Vyber rychlost hlasu Honzíka:\n\n"
    "Aktuální: <b>{current}</b>",
    "voice_speed_very_slow": "🐌 Velmi pomalu",
    "voice_speed_slow": "🚶 Pomalu",
    "voice_speed_normal": "🏃 Normálně",
    "voice_speed_native": "⚡ Jako rodilý",
    "settings_voice_speed_changed": "Rychlost změněna na: <b>{speed}</b> ✅",

    # Nastavení - úroveň oprav
    "settings_corrections": "Vyber úroveň oprav:\n\n"
    "Aktuální: <b>{current}</b>\n\n"
    "• <b>Minimální</b> - pouze kritické chyby\n"
    "• <b>Vyvážený</b> - vyvážený (doporučeno)\n"
    "• <b>Detailní</b> - všechny chyby s podrobným vysvětlením",
    "corrections_minimal": "📝 Minimální",
    "corrections_balanced": "⚖️ Vyvážený",
    "corrections_detailed": "📚 Detailní",
    "settings_corrections_changed": "Úroveň oprav změněna na: <b>{level}</b> ✅",

    # Nastavení - styl komunikace
    "settings_style": "Vyber styl komunikace Honzíka:\n\n"
    "Aktuální: <b>{current}</b>\n\n"
    "• <b>Přátelský</b> - přátelský, neformální\n"
    "• <b>Učitel</b> - jako učitel, více oprav\n"
    "• <b>Kamarád</b> - jako kamarád, minimum oprav",
    "style_friendly": "😊 Přátelský",
    "style_tutor": "👨‍🏫 Učitel",
    "style_casual": "🤝 Kamarád",
    "settings_style_changed": "Styl komunikace změněn na: <b>{style}</b> ✅",

    # Zpracování hlasových
    "voice_processing": "Honzík přemýšlí... 🤔",
    "voice_correctness": "✅ Správnost: {score}%",
    "voice_streak": "🔥 Série: {streak}",
    "voice_stars_earned": "⭐ Hvězd získáno: +{stars}",

    # Opravy
    "corrections_header": "\n📝 <b>Opravy:</b>\n\n",
    "correction_item": "❌ <i>{original}</i>\n✅ <b>{corrected}</b>\n"
    "💡 {explanation}\n",
    "no_corrections": "🎉 Výborně! Žádné chyby!",
    "suggestion": "\n💭 <b>Tip:</b> {suggestion}",

    # Chyby
    "error_general": "Jejda! Něco se pokazilo 😅\n\n"
    "Zkus to znovu za pár sekund.",
    "error_voice_too_long": "To je příliš dlouhá zpráva! 😅\n\n"
    "Zkus něco kratšího (do 60 sekund).",
    "error_no_audio": "Tohle nemůžu zpracovat.\n\n"
    "Pošli mi hlasovou zprávu v češtině!",
    "error_backend": "Honzík je dočasně nedostupný 🔧\n\n"
    "Už na tom pracujeme, zkus později!",

    # Transkripce
    "show_transcript": "📄 Zobrazit přepis",
    "transcript_text": "📄 <b>Přepis:</b>\n\n{text}",

    # Textová odpověď Honzíka
    "btn_show_text": "📝 Text",
    "btn_open_webui": "🌐 Přejít na WEBUI",
    "honzik_text_response": "📝 <b>Text odpovědi Honzíka:</b>\n\n{text}",

    # Ukládání slov
    "save_word": "💾 Uložit slovo",
    "word_saved": "Slovo uloženo! 💾",

    # Tlačítka
    "btn_back": "« Zpět",
    "btn_cancel": "❌ Zrušit",

    # Překlad slov
    "translate_usage": "Použití: <code>/translate &lt;slovo&gt;</code>\n\n"
    "Příklad: <code>/translate ahoj</code>",
    "translate_result": "📖 <b>Překlad:</b>\n\n"
    "🇨🇿 <b>{word}</b> → 🇷🇺 <b>{translation}</b>",
    "translate_error": "Nepodařilo se přeložit slovo 😅\n\n"
    "Zkus znovu nebo použij tlačítko 'Přejít na WEBUI'.",
    "phonetics": "Fonetika",

    # Ostatní
    "already_registered": "Už jsi zaregistrovaný!\n\n"
    "Použij /help pro zobrazení co umím.",

    # Detekce jazyka (Týden 2)
    "language_detected_notice": "🎧 Slyšel jsem, že jsi mluvil {lang_name}. "
    "Rozuměl jsem ti, ale odpovím česky! 🇨🇿",
}
