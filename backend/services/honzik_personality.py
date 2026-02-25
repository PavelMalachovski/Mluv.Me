"""
Systém postav pro výuku češtiny.

Postavy:
- Honzík: veselý Čech, kamarádský, tykání, široké zájmy (kultura, sport, jídlo, cestování...)
- Paní Nováková: profesionální úřednice, vykání, spisovná čeština, pomoc s dokumenty a úřady

Optimalizace oproti předchozí verzi:
- Kompaktnější prompty (~350 tokenů místo ~600) → rychlejší odpovědi
- Podpora více postav přes parametr `character`
- Rozšířené zájmy Honzíka (nejen pivo a klobásky)
- Odstraněno zbytečné `optimize_conversation_history` (historie je už omezena na 5 zpráv)
"""

import json
from functools import lru_cache

import structlog

from backend.services.openai_client import OpenAIClient
from backend.services.cache_service import cache_service
from backend.services.model_selector import model_selector

logger = structlog.get_logger(__name__)

# --- TTS voice mapping per character ---
CHARACTER_TTS_VOICE = {
    "honzik": "alloy",      # male, friendly
    "novakova": "nova",      # female, professional
}


class HonzikPersonality:
    """
    Systém postav – generuje odpovědi v roli vybrané postavy.

    Attributes:
        openai_client: Klient pro práci s OpenAI API
    """

    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client
        self.logger = logger.bind(service="honzik_personality")

    # ------------------------------------------------------------------
    # Prompt building (cached per unique param combo)
    # ------------------------------------------------------------------

    @staticmethod
    @lru_cache(maxsize=128)
    def _get_base_prompt(
        character: str,
        level: str,
        corrections_level: str,
        native_language: str,
        style: str,
    ) -> str:
        """
        Sestavit systémový prompt pro vybranou postavu.

        Cachováno přes lru_cache — stejná kombinace parametrů → stejný prompt.
        """
        # --- Level descriptions (shared) ---
        level_descriptions = {
            "beginner": "Začátečník (A2-B1). Používej jednoduchá slova a krátké věty.",
            "intermediate": "Středně pokročilý (B1-B2). Běžné idiomy, složitější gramatika.",
            "advanced": "Pokročilý (B2-C1). Pokročilá slovní zásoba, idiomy, odborné termíny.",
            "native": "Rodilý mluvčí (C2). Všechny jazykové prostředky, složité idiomy.",
        }

        # --- Corrections descriptions (shared) ---
        corrections_descriptions = {
            "minimal": "Opravuj POUZE kritické chyby bránící porozumění. Ignoruj drobnosti.",
            "balanced": "Opravuj důležité chyby a občas vysvětli pravidlo. Balancuj učení a konverzaci.",
            "detailed": "Opravuj VŠECHNY chyby s podrobným vysvětlením. Věnuj pozornost i interpunkci a stylu.",
        }

        # --- Native language name (expanded for all supported languages) ---
        native_lang_names = {
            "ru": "ruština", "uk": "ukrajinština", "pl": "polština", "sk": "slovenčina",
            "vi": "vietnamština", "hi": "hindština", "en": "angličtina", "de": "němčina",
            "fr": "francouzština", "es": "španělština", "it": "italština", "pt": "portugalština",
            "zh": "čínština", "ja": "japonština", "ko": "korejština", "tr": "turečtina",
            "ar": "arabština", "bg": "bulharština", "hr": "chorvatština", "ro": "rumunština",
            "hu": "maďarština", "nl": "holandština", "sv": "švédština", "da": "dánština",
            "fi": "finština", "no": "norština", "el": "řečtina", "he": "hebrejština",
            "th": "thajština", "id": "indonéština", "tl": "tagalogština", "mn": "mongolština",
            "ka": "gruzínština", "az": "ázerbájdžánština", "kk": "kazaština",
            "uz": "uzbečtina", "ky": "kyrgyzština", "tg": "tádžičtina",
            "be": "běloruština", "sr": "srbština", "sl": "slovinština",
            "lt": "litevština", "lv": "lotyšština", "et": "estonština",
            "sq": "albánština", "hy": "arménština", "fa": "perština",
            "bn": "bengálština", "pa": "paňdžábština", "my": "myanmarština",
            "lo": "laoština", "sw": "svahilština",
        }
        native_lang_name = native_lang_names.get(native_language, native_language)

        level_desc = level_descriptions.get(level, level_descriptions["beginner"])
        corrections_desc = corrections_descriptions.get(corrections_level, corrections_descriptions["balanced"])

        # --- Grammar rules block (only for detailed corrections) ---
        grammar_block = ""
        if corrections_level == "detailed":
            grammar_block = (
                "\nGRAMATIKA: Odkazuj na konkrétní pravidla ÚJČ – "
                "vyjmenovaná slova, bě/bje, mě/mně, i/y, čárky, velká písmena, "
                "skloňování, časování, shoda přísudku s podmětem."
            )

        # --- CHARACTER-SPECIFIC PERSONALITY ---
        if character == "novakova":
            return _build_novakova_prompt(style, level_desc, corrections_desc, native_lang_name, grammar_block)
        else:
            return _build_honzik_prompt(style, level_desc, corrections_desc, native_lang_name, grammar_block)

    def _format_conversation_history(
        self, history: list[dict[str, str]]
    ) -> str:
        if not history:
            return ""

        formatted = []
        # Show only the last 4 exchanges as context
        for msg in history[-4:]:
            role = "Student" if msg["role"] == "user" else "Postava"
            formatted.append(f"{role}: {msg['text']}")

        return "\n".join(formatted)

    # ------------------------------------------------------------------
    # Main generation method
    # ------------------------------------------------------------------

    async def generate_response(
        self,
        user_text: str,
        level: str,
        style: str,
        corrections_level: str,
        native_language: str,
        conversation_history: list[dict[str, str]] | None = None,
        character: str = "honzik",
    ) -> dict:
        """
        Vygenerovat odpověď vybrané postavy s opravami a hodnocením.

        Args:
            user_text: Text uživatele v češtině
            level: Úroveň češtiny (beginner/intermediate/advanced/native)
            style: Styl konverzace (friendly/tutor/casual)
            corrections_level: Úroveň oprav (minimal/balanced/detailed)
            native_language: Rodný jazyk uživatele (ISO 639-1)
            conversation_history: Historie konverzace (posledních 5 zpráv)
            character: Postava (honzik/novakova)

        Returns:
            dict: { "honzik_response", "corrected_text", "mistakes", "correctness_score", "suggestion" }
        """
        self.logger.info(
            "generating_response",
            character=character,
            level=level,
            style=style,
            corrections_level=corrections_level,
            native_language=native_language,
            user_text_length=len(user_text),
        )

        if conversation_history is None:
            conversation_history = []

        # Cache ONLY the first greeting (no conversation history)
        should_cache = len(conversation_history) == 0

        if should_cache:
            settings_dict = {
                "czech_level": level,
                "correction_level": corrections_level,
                "conversation_style": style,
                "native_language": native_language,
                "character": character,
            }
            cached_response = await cache_service.get_cached_honzik_response(
                user_text, settings_dict
            )
            if cached_response:
                self.logger.info("using_cached_greeting", character=character)
                return cached_response

        # Build prompt
        system_prompt = self._get_base_prompt(
            character=character,
            level=level,
            corrections_level=corrections_level,
            native_language=native_language,
            style=style,
        )

        # Build user message (history included only when present)
        if conversation_history:
            history_text = self._format_conversation_history(conversation_history)
            user_prompt = (
                f"Historie konverzace (pro kontext):\n{history_text}\n\n"
                f"NOVÁ ZPRÁVA STUDENTA (odpověz POUZE na tuto zprávu): {user_text}\n\n"
                "Analyzuj NOVOU zprávu studenta a odpověz JSON."
            )
        else:
            user_prompt = (
                f"Nová zpráva studenta: {user_text}\n\n"
                "Analyzuj zprávu studenta a odpověz JSON."
            )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # --- SPEED OPTIMIZATION: skip optimize_conversation_history ---
        # History is already limited to 5 messages (~500 tokens max).
        # Running tiktoken on every request wastes ~100-200ms for no benefit.

        # Select optimal model
        selected_model, model_reason = model_selector.select_model(
            user_text=user_text,
            czech_level=level,
            corrections_level=corrections_level,
            history_length=len(conversation_history),
        )

        self.logger.info(
            "model_selected",
            model=selected_model,
            reason=model_reason,
            character=character,
        )

        try:
            # Generate response (max_tokens=400 prevents overly long answers)
            response_text = await self.openai_client.generate_chat_completion(
                messages=messages,
                json_mode=True,
                model=selected_model,
                max_tokens=400,
            )

            # Parse JSON
            response_data = json.loads(response_text)

            # Validate required fields
            required_fields = [
                "honzik_response",
                "corrected_text",
                "mistakes",
                "correctness_score",
                "suggestion",
            ]

            for field in required_fields:
                if field not in response_data:
                    self.logger.error("missing_field", field=field)
                    raise ValueError(f"Missing required field: {field}")

            # Validate score
            score = response_data["correctness_score"]
            if not isinstance(score, (int, float)) or not (0 <= score <= 100):
                response_data["correctness_score"] = max(0, min(100, int(score)))

            # Fallback for empty corrected_text
            if not response_data.get("corrected_text"):
                response_data["corrected_text"] = user_text

            self.logger.info(
                "response_generated",
                character=character,
                correctness_score=response_data["correctness_score"],
                mistakes_count=len(response_data["mistakes"]),
            )

            # Cache first greeting
            if should_cache:
                await cache_service.cache_honzik_response(
                    user_text, settings_dict, response_data
                )

            return response_data

        except json.JSONDecodeError as e:
            self.logger.error("json_decode_error", error=str(e), response_text=response_text[:200])
            raise ValueError(f"Invalid JSON response from GPT: {e}")

        except Exception as e:
            self.logger.error("response_failed", error=str(e), character=character)
            raise

    # ------------------------------------------------------------------
    # Welcome messages
    # ------------------------------------------------------------------

    def get_welcome_message(self, character: str = "honzik") -> str:
        """Uvítací zpráva vybrané postavy."""
        if character == "novakova":
            return (
                "Dobrý den! 🇨🇿 Jsem paní Nováková.\n\n"
                "Pomohu Vám s češtinou – zejména s formální komunikací, "
                "úředními záležitostmi a spisovným jazykem.\n\n"
                "📋 Dokumenty, formuláře, e-maily úřadům\n"
                "🏛️ Cizinecká policie, povolení k pobytu\n"
                "💼 Pracovní komunikace\n\n"
                "Jak Vám mohu pomoci? ✉️"
            )
        return (
            "Ahoj! 🇨🇿 Jsem Honzík – tvůj veselý český kamarád!\n\n"
            "Pomohu ti naučit se česky přes živou konverzaci. "
            "Mluv se mnou česky a já tě budu opravovat a podporovat!\n\n"
            "🏙️ Praha, česká kultura, sport, jídlo, cestování...\n"
            "Pojďme si popovídat! Napiš mi nebo pošli hlasovou zprávu 🎤"
        )

    @staticmethod
    def get_tts_voice(character: str = "honzik") -> str:
        """Vrátit TTS hlas pro postavu."""
        return CHARACTER_TTS_VOICE.get(character, "alloy")


# ======================================================================
# Character prompt builders (module-level for clarity)
# ======================================================================

def _build_honzik_prompt(
    style: str,
    level_desc: str,
    corrections_desc: str,
    native_lang_name: str,
    grammar_block: str,
) -> str:
    """Sestavit prompt pro Honzíka – veselého Čecha se širokými zájmy."""

    style_descriptions = {
        "friendly": "Buď přátelský a povzbuzující. Minimum technických vysvětlení, maximum pozitivity.",
        "tutor": "Buď jako učitel – strukturované rady, vysvětlení gramatiky, tipy na výslovnost.",
        "casual": "Buď neformální jako kamarád. Minimum oprav (jen kritické), maximum legrace a přirozené konverzace.",
    }

    style_desc = style_descriptions.get(style, style_descriptions["friendly"])

    return f"""Jsi Honzík – veselý a zvídavý Čech z Prahy. Tykáš studentovi.
Jsi přátelský, vtipný, rád sdílíš zajímavosti o české kultuře a životě v Česku.

TVOJE ZÁJMY (přizpůsob tématu konverzace):
🏙️ Praha a české města, 🎭 kultura: kino, divadlo, hudba (Smetana, Dvořák, i moderní kapely)
🍽️ Česká kuchyně: svíčková, vepřo-knedlo-zelo, trdelník, české pivo
⚽ Sport: hokej, fotbal, tenis, 🌍 cestování: hrady, zámky, Krkonoše, Šumava
📚 Studentský život, české zvyky, 🗓️ svátky: Vánoce, Velikonoce, Mikuláš
💼 Práce, byrokracie, úřady, 🚇 MHD v Praze, vlaky, Lítačka
🛒 Každodenní život: nakupování, bydlení, sousedé

STUDENT: {level_desc}
STYL: {style_desc}
OPRAVY: {corrections_desc}
Rodný jazyk studenta: {native_lang_name} – vysvětlení piš jednoduše česky na úrovni A2.
{grammar_block}

ŽIVÁ KONVERZACE – DŮLEŽITÉ:
- Odpovídej VÝHRADNĚ na POSLEDNÍ zprávu studenta, ne na starší zprávy z historie.
- Historie slouží JEN jako kontext, abys věděl, o čem jste mluvili.
- VŽDY UKONČI svou odpověď OTÁZKOU – ptej se studenta na jeho názor, zkušenosti, plány.
- Otázky formuluj přirozeně, propojuj je s tématem konverzace.
- Příklady otázek: "A ty jsi už někdy byl v Praze?", "Co rád jíš?", "Jak se ti líbí v Česku?"
- Cíl: student má chuť odpovědět a pokračovat v konverzaci.

ÚKOL: Analyzuj text, oprav chyby, ohodnoť 0-100, odpověz jako Honzík. Buď pozitivní!

SLOVÍČKA: V odpovědi použij 1-3 zajímavá/užitečná česká slova vhodná pro úroveň studenta. Zahrň je do pole new_words s překladem do {native_lang_name}.

ODPOVĚZ POUZE PLATNÝM JSON:
{{{{
  "honzik_response": "tvá odpověď v češtině",
  "corrected_text": "opravený text studenta",
  "mistakes": [{{{{"original":"chyba","corrected":"správně","explanation_cs":"vysvětlení max 15 slov"}}}}],
  "correctness_score": 85,
  "suggestion": "krátký tip česky",
  "new_words": [{{{{"word_czech":"české slovo","translation":"překlad do {native_lang_name}","context_sentence":"příkladová věta"}}}}]
}}}}"""


def _build_novakova_prompt(
    style: str,
    level_desc: str,
    corrections_desc: str,
    native_lang_name: str,
    grammar_block: str,
) -> str:
    """Sestavit prompt pro paní Novákovou – formální, spisovná čeština, vykání."""

    style_descriptions = {
        "friendly": "Buďte profesionální, ale laskavá. Vysvětlujte trpělivě a srozumitelně.",
        "tutor": "Buďte důkladná jako učitelka. Podrobně vysvětlujte gramatiku a formální obraty.",
        "casual": "Buďte profesionální, ale uvolněná. Stále vykejte, ale komunikujte přívětivě.",
    }

    style_desc = style_descriptions.get(style, style_descriptions["friendly"])

    return f"""Jste paní Nováková – profesionální a laskavá česká úřednice.
Mluvíte VÝHRADNĚ spisovnou češtinou. VŽDY vykáte studentovi (Vy, Vás, Vám, Váš).

VAŠE OBLASTI EXPERTISE:
📋 Úřady: cizinecká policie, povolení k pobytu, zaměstnanecká karta, živnostenský list
📝 Dokumenty: formuláře, žádosti, plné moci, výpisy z rejstříku trestů
🏛️ ČSSZ, zdravotní pojištění, číslo pojištěnce, daňové přiznání
💬 Formální komunikace: e-maily úřadům, dopisy zaměstnavateli, reklamace
🏠 Bydlení: nájemní smlouva, katastr, změna trvalého bydliště
💼 Práce: pracovní smlouva, výpověď, výplatní páska

STUDENT: {level_desc}
STYL: {style_desc}
OPRAVY: {corrections_desc}
Rodný jazyk studenta: {native_lang_name} – vysvětlení pište jednoduše česky.
Opravujte zejména: hovorové tvary → spisovné, tykání → vykání, nespisovné výrazy.
{grammar_block}

ŽIVÁ KONVERZACE – DŮLEŽITÉ:
- Odpovídejte VÝHRADNĚ na POSLEDNÍ zprávu studenta, ne na starší zprávy z historie.
- Historie slouží JEN jako kontext, abyste věděla, o čem jste mluvili.
- VŽDY UKONČETE svou odpověď OTÁZKOU – ptejte se studenta na jeho situaci, potřeby, plány.
- Otázky formulujte přirozeně a profesionálně, propojujte je s tématem.
- Příklady: "Potřebujete s tím ještě pomoci?", "Máte již všechny potřebné dokumenty?", "Kdy plánujete návštěvu úřadu?"
- Cíl: student má chuť odpovědět a pokračovat v konverzaci.

ÚKOL: Analyzujte text, opravte chyby, ohodnoťte 0-100, odpovězte jako paní Nováková. Vykejte!

SLOVÍČKA: V odpovědi použijte 1-3 zajímavá/užitečná česká slova vhodná pro úroveň studenta. Zahrňte je do pole new_words s překladem do {native_lang_name}.

ODPOVĚZTE POUZE PLATNÝM JSON:
{{{{
  "honzik_response": "Vaše odpověď ve spisovné češtině (vykání)",
  "corrected_text": "opravený text studenta",
  "mistakes": [{{{{"original":"chyba","corrected":"správně","explanation_cs":"vysvětlení max 15 slov"}}}}],
  "correctness_score": 85,
  "suggestion": "krátký tip ve spisovné češtině",
  "new_words": [{{{{"word_czech":"české slovo","translation":"překlad do {native_lang_name}","context_sentence":"příkladová věta"}}}}]
}}}}"""


