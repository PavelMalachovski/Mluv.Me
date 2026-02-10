"""
Seed script for grammar rules from Internetová jazyková příručka (ÚJČ).

Kontekt je přeformulovaný a zjednodušený pro úrovně A1–B2.
Veškerý obsah je v češtině (Czech immersion).

Usage:
    python -m scripts.seed_grammar_rules
    # or
    python scripts/seed_grammar_rules.py
"""

import asyncio
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.database import AsyncSessionLocal, init_db
from backend.models.grammar import GrammarRule


# ═══════════════════════════════════════════════════════════════════
#  GRAMMAR RULES DATA
#  Based on: Internetová jazyková příručka (prirucka.ujc.cas.cz)
#  Reformulated and simplified for Czech learners (A1–B2)
# ═══════════════════════════════════════════════════════════════════

GRAMMAR_RULES = [

    # ───────────────────────────────────────────────────────────────
    #  KATEGORIE: vyslovnost (Výslovnost)
    # ───────────────────────────────────────────────────────────────
    {
        "code": "vyslovnost_r_hackem",
        "category": "vyslovnost",
        "subcategory": "souhlásky",
        "level": "A1",
        "title_cs": "Výslovnost ř",
        "rule_cs": "Hláska ř je typicky česká. Jazyk se dotýká horního patra a vibruje. Ř není ani r, ani ž — je to speciální zvuk.",
        "explanation_cs": "Při správné výslovnosti ř se špička jazyka lehce dotýká alveolárního výstupku za horními zuby a současně vibruje. Ř se vyslovuje jako znělé na začátku slova před samohláskou (řeka) a jako neznělé na konci slova nebo před neznělou souhláskou (keř, při).",
        "examples": json.dumps([
            {"correct": "řeka [ržeka]", "incorrect": "řeka [reka] nebo [žeka]", "note_cs": "Ř není r ani ž."},
            {"correct": "tři [trži]", "incorrect": "tři [tri]", "note_cs": "Ř před í se vyslovuje nezněle."},
            {"correct": "moře [morže]", "incorrect": "moře [more]", "note_cs": "Ř uprostřed slova."}
        ]),
        "mnemonic": "Zkus říct rychle 'rž' dohromady — to je zvuk ř!",
        "common_mistakes": json.dumps([
            {"wrong": "říkat jako [r]", "right": "říkat [rž]", "why_cs": "Ř je kombinace r a ž, ne pouhé r."},
            {"wrong": "říkat jako [ž]", "right": "říkat [rž]", "why_cs": "Ř obsahuje vibraci r, nestačí jen ž."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "Jak se správně vyslovuje 'řeka'?", "answer": "ržeka", "options": ["reka", "žeka", "ržeka", "reka"]},
            {"type": "choose", "question": "Které slovo obsahuje ř?", "answer": "přítel", "options": ["pritel", "přítel", "přitel", "pritel"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Výslovnost",
        "sort_order": 1,
    },
    {
        "code": "vyslovnost_h_ch",
        "category": "vyslovnost",
        "subcategory": "souhlásky",
        "level": "A1",
        "title_cs": "Rozdíl mezi h a ch",
        "rule_cs": "H je znělá hláska (hlasivky vibrují): hora, hotel. Ch je neznělá hláska (hlasivky nevibrují): chléb, chyba. H a ch jsou dva různé zvuky!",
        "explanation_cs": "V češtině je h a ch odlišné. H se vyslovuje jako znělá hrtanová hláska (podobně jako anglické h v 'hello'). Ch je neznělá zadopatrová hláska (podobně jako německé ch v 'Bach').",
        "examples": json.dumps([
            {"correct": "hora (h — znělé)", "incorrect": "hora (ch)", "note_cs": "H je znělé, ch je neznělé."},
            {"correct": "chléb (ch — neznělé)", "incorrect": "chléb (h)", "note_cs": "Ch se vyslovuje vzadu v ústech."}
        ]),
        "mnemonic": "H = hlasivky vibrují (hora). Ch = hlasivky nevibrují (chléb).",
        "common_mistakes": json.dumps([
            {"wrong": "zaměňovat h a ch", "right": "h ≠ ch", "why_cs": "Jsou to dva rozdílné zvuky v češtině."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "Která hláska je znělá?", "answer": "h", "options": ["h", "ch"]},
            {"type": "choose", "question": "Ve slově 'chyba' je:", "answer": "ch (neznělé)", "options": ["h (znělé)", "ch (neznělé)"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Výslovnost",
        "sort_order": 2,
    },
    {
        "code": "vyslovnost_e_hackem",
        "category": "vyslovnost",
        "subcategory": "samohlásky",
        "level": "A1",
        "title_cs": "Výslovnost ě",
        "rule_cs": "Písmeno ě mění výslovnost předchozí souhlásky: dě = [ďe], tě = [ťe], ně = [ňe]. Po b, p, v, f se ě vyslovuje jako [je]: běh = [bjeh].",
        "explanation_cs": "Ě samo o sobě nemá vlastní zvuk. Změkčuje předchozí souhlásku (d→ď, t→ť, n→ň) nebo se po retnicích (b, p, v, f) čte jako je.",
        "examples": json.dumps([
            {"correct": "děti [ďeťi]", "incorrect": "děti [deti]", "note_cs": "D před ě se čte jako ď."},
            {"correct": "běh [bjeh]", "incorrect": "běh [beh]", "note_cs": "B před ě se čte jako bje."},
            {"correct": "věc [vjec]", "incorrect": "věc [vec]", "note_cs": "V před ě se čte jako vje."}
        ]),
        "mnemonic": "D, T, N + ě = ď, ť, ň. B, P, V, F + ě = bje, pje, vje, fje.",
        "common_mistakes": json.dumps([
            {"wrong": "deti", "right": "děti [ďeťi]", "why_cs": "Ě změkčuje předchozí d na ď."},
            {"wrong": "beh", "right": "běh [bjeh]", "why_cs": "Po b se ě čte jako je."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "Jak se vyslovuje 'děda'?", "answer": "ďeda", "options": ["deda", "ďeda", "djeda"]},
            {"type": "choose", "question": "Jak se vyslovuje 'pět'?", "answer": "pjet", "options": ["pet", "pjet", "ťep"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Výslovnost",
        "sort_order": 3,
    },
    {
        "code": "vyslovnost_skupiny_souhlasek",
        "category": "vyslovnost",
        "subcategory": "souhlásky",
        "level": "A2",
        "title_cs": "Skupiny souhlásek a spodoba znělosti",
        "rule_cs": "V češtině se souhlásky ve skupinách přizpůsobují v znělosti. Znělá + neznělá → obě neznělé: lod' + ka = [lotka]. Neznělá + znělá → obě znělé: prosba = [prozba].",
        "explanation_cs": "Spodoba znělosti je automatický jev. Poslední souhláska ve skupině určuje znělost celé skupiny. Na konci slova se znělé souhlásky vyslovují neznělě: had = [hat].",
        "examples": json.dumps([
            {"correct": "lodka [lotka]", "incorrect": "lodka [lodka]", "note_cs": "D se před k vyslovuje neznělě jako t."},
            {"correct": "prosba [prozba]", "incorrect": "prosba [prosba]", "note_cs": "S se před b vyslovuje znělé jako z."},
            {"correct": "had [hat]", "incorrect": "had [had]", "note_cs": "Na konci slova d zní jako t."}
        ]),
        "mnemonic": "Poslední souhláska ve skupině je šéf — ostatní se přizpůsobí!",
        "common_mistakes": None,
        "exercise_data": json.dumps([
            {"type": "choose", "question": "Jak se vyslovuje 'když'?", "answer": "gdyž", "options": ["kdyš", "gdyž", "když"]},
            {"type": "choose", "question": "Jak se vyslovuje 'rok' v 'v roce'?", "answer": "v [v] roce", "options": ["f [f] roce", "v [v] roce"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Výslovnost",
        "sort_order": 4,
    },
    {
        "code": "vyslovnost_dlouhe_samohlasky",
        "category": "vyslovnost",
        "subcategory": "samohlásky",
        "level": "A1",
        "title_cs": "Krátké a dlouhé samohlásky",
        "rule_cs": "V češtině rozlišujeme krátké (a, e, i/y, o, u) a dlouhé (á, é, í/ý, ó, ú/ů) samohlásky. Délka mění význam slova: dal (he gave) × dál (further).",
        "explanation_cs": "Dlouhé samohlásky se značí čárkou (á, é, í, ó, ú) nebo kroužkem (ů). Ú se píše na začátku slova (úkol), ů uprostřed a na konci (dům, domů). Výslovnost ú a ů je stejná.",
        "examples": json.dumps([
            {"correct": "dal (dal) × dál (dále)", "incorrect": "", "note_cs": "Délka mění význam."},
            {"correct": "být (existovat) × bit (udeřen)", "incorrect": "", "note_cs": "Í/ý vs i/y."},
            {"correct": "dům × dum (neexistuje)", "incorrect": "", "note_cs": "Ů značí dlouhé u."}
        ]),
        "mnemonic": "Čárka nebo kroužek = dlouhý zvuk. Dávej pozor — mění význam!",
        "common_mistakes": json.dumps([
            {"wrong": "nevyslovovat délku", "right": "rozlišovat krátké a dlouhé", "why_cs": "Délka samohlásky mění význam slova."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "Co znamená 'být'?", "answer": "existovat", "options": ["existovat", "udeřen"]},
            {"type": "choose", "question": "Kde se píše ů (s kroužkem)?", "answer": "uprostřed a na konci slova", "options": ["na začátku slova", "uprostřed a na konci slova"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Výslovnost",
        "sort_order": 5,
    },

    # ───────────────────────────────────────────────────────────────
    #  KATEGORIE: pravopis_hlasky (Pravopis – hláska a písmeno)
    # ───────────────────────────────────────────────────────────────
    {
        "code": "vyjmenovana_slova_b",
        "category": "pravopis_hlasky",
        "subcategory": "vyjmenovaná slova",
        "level": "A2",
        "title_cs": "Vyjmenovaná slova po B",
        "rule_cs": "Po B píšeme Y/Ý v těchto slovech a jejich odvozeninách: být, bydlit, obyvatel, byt, příbytek, nábytek, dobytek, obyčej, bystrý, bylina, kobyla, býk, babyka.",
        "explanation_cs": "Vyjmenovaná slova jsou výjimky z pravidla, že po B se běžně píše i/í. Musíme si je zapamatovat. Y/Ý píšeme i ve všech slovech odvozených: být → bývat, bydlit → bydliště, obydlí.",
        "examples": json.dumps([
            {"correct": "bydlit, bydliště, obydlí", "incorrect": "bidlit, bidliště", "note_cs": "Bydlit je vyjmenované slovo po B."},
            {"correct": "býk, býčí", "incorrect": "bík, bíčí", "note_cs": "Býk patří mezi vyjmenovaná slova po B."},
            {"correct": "příbytek, nábytek", "incorrect": "příbitek, nábitek", "note_cs": "Odvozeno od 'být'."},
            {"correct": "bít (udeřit)", "incorrect": "být (udeřit)", "note_cs": "Bít (udeřit) ≠ být (existovat)!"}
        ]),
        "mnemonic": "Být, bydlit, obyvatel, byt, příbytek, nábytek, dobytek, obyčej, bystrý, bylina, kobyla, býk, babyka — zapamatuj si řadu!",
        "common_mistakes": json.dumps([
            {"wrong": "bidlím v Praze", "right": "bydlím v Praze", "why_cs": "Bydlit je vyjmenované slovo → y."},
            {"wrong": "nabítek", "right": "nábytek", "why_cs": "Odvozeno od 'být' → y."},
            {"wrong": "običej", "right": "obyčej", "why_cs": "Obyčej je vyjmenované slovo po B."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "b_dlit — doplň i nebo y:", "answer": "y", "options": ["i", "y"]},
            {"type": "choose", "question": "nab_tek — doplň i nebo y:", "answer": "y", "options": ["i", "y"]},
            {"type": "choose", "question": "b_t (existovat) — doplň i nebo y:", "answer": "ý", "options": ["í", "ý"]},
            {"type": "choose", "question": "b_t (udeřit) — doplň i nebo y:", "answer": "í", "options": ["í", "ý"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz/?id=100",
        "sort_order": 10,
    },
    {
        "code": "vyjmenovana_slova_l",
        "category": "pravopis_hlasky",
        "subcategory": "vyjmenovaná slova",
        "level": "A2",
        "title_cs": "Vyjmenovaná slova po L",
        "rule_cs": "Po L píšeme Y/Ý v těchto slovech: slyšet, mlýn, blýskat se, polykat, vzlykat, plynout, plýtvat, lysý, lýtko, lýko, lyže, pelyněk, plyš.",
        "explanation_cs": "Y/Ý píšeme i ve všech slovech odvozených: slyšet → slýchat, nedoslýchavý; mlýn → mlynář; lysý → lysina.",
        "examples": json.dumps([
            {"correct": "slyšet, slýchat", "incorrect": "slišet, slíchat", "note_cs": "Slyšet je vyjmenované slovo po L."},
            {"correct": "mlýn, mlynář", "incorrect": "mlín, mlinář", "note_cs": "Ale pozor: mlít (sloveso) se píše s í!"},
            {"correct": "lyže, lyžovat", "incorrect": "liže, ližovat", "note_cs": "Lyže je vyjmenované slovo po L."},
            {"correct": "líný (adj.)", "incorrect": "lýný", "note_cs": "Líný NENÍ vyjmenované slovo — píšeme i."}
        ]),
        "mnemonic": "Slyšel mlynář blýskání, polykal lyžec plynový — lysý lýtkový lyžař plýtval pelyňkem na plyši.",
        "common_mistakes": json.dumps([
            {"wrong": "slišet", "right": "slyšet", "why_cs": "Slyšet je vyjmenované slovo → y."},
            {"wrong": "mlít vs mlýn", "right": "mlít (sloveso) × mlýn (budova)", "why_cs": "Mlít a mlýn nejsou příbuzná slova!"}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "sl_šet — doplň i nebo y:", "answer": "y", "options": ["i", "y"]},
            {"type": "choose", "question": "ml_n — doplň i nebo y:", "answer": "ý", "options": ["í", "ý"]},
            {"type": "choose", "question": "l_že — doplň i nebo y:", "answer": "y", "options": ["i", "y"]},
            {"type": "choose", "question": "l_ný (lenivý) — doplň i nebo y:", "answer": "í", "options": ["í", "ý"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz/?id=100",
        "sort_order": 11,
    },
    {
        "code": "vyjmenovana_slova_m",
        "category": "pravopis_hlasky",
        "subcategory": "vyjmenovaná slova",
        "level": "A2",
        "title_cs": "Vyjmenovaná slova po M",
        "rule_cs": "Po M píšeme Y/Ý: my, mýt (umývat), myslit, mýlit se, hmyz, myš, hlemýžď, mýtit, zamykat, smýkat, dmýchat, chmýří, mýto.",
        "explanation_cs": "Pozor na rozdíl: mýt (umývat) × mít (vlastnit). My (zájmeno) × mi (krátký tvar 3. p.).",
        "examples": json.dumps([
            {"correct": "mýdlo (od mýt)", "incorrect": "mídlo", "note_cs": "Mýdlo je odvozeno od mýt (umývat)."},
            {"correct": "myslit, myšlenka", "incorrect": "mislit, mišlenka", "note_cs": "Myslit je vyjmenované slovo."},
            {"correct": "my (zájmeno, 1. os. mn. č.)", "incorrect": "mi (to je 3. pád)", "note_cs": "My × mi mají různý význam."},
            {"correct": "mít rád (vlastnit)", "incorrect": "mýt rád", "note_cs": "Mít (vlastnit) se píše s í!"}
        ]),
        "mnemonic": "My se mýt nemýlíme — hmyz i myš v hlemýždím mýtu zamykáme.",
        "common_mistakes": json.dumps([
            {"wrong": "mýt rád", "right": "mít rád", "why_cs": "Mít (vlastnit) ≠ mýt (umývat)."},
            {"wrong": "Dej mi to (zájmeno)", "right": "Dej mi → 3. pád, krátký tvar", "why_cs": "Mi je krátký tvar zájmena já (3. pád)."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "m_dlo — doplň i nebo y:", "answer": "ý", "options": ["í", "ý"]},
            {"type": "choose", "question": "m_t rád — doplň i nebo y:", "answer": "í", "options": ["í", "ý"]},
            {"type": "choose", "question": "m_š (zvíře) — doplň i nebo y:", "answer": "y", "options": ["i", "y"]},
            {"type": "choose", "question": "M_ jsme přátelé — doplň i nebo y:", "answer": "y", "options": ["i", "y"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz/?id=100",
        "sort_order": 12,
    },
    {
        "code": "vyjmenovana_slova_p",
        "category": "pravopis_hlasky",
        "subcategory": "vyjmenovaná slova",
        "level": "A2",
        "title_cs": "Vyjmenovaná slova po P",
        "rule_cs": "Po P píšeme Y/Ý: pýcha, pytel, pysk, netopýr, slepýš, pyl, kopyto, klopýtat, třpytit se, zpytovat, pykat, pýr, pýřit se.",
        "explanation_cs": "Odvozená slova: pýcha → pyšný, pytel → pytlovina, kopyto → sudokopytník.",
        "examples": json.dumps([
            {"correct": "pýcha, pyšný", "incorrect": "pícha, pišný", "note_cs": "Pýcha je vyjmenované slovo po P."},
            {"correct": "pytel, pytlovina", "incorrect": "pitel, pitlovina", "note_cs": "Pytel patří do řady."},
            {"correct": "písnička", "incorrect": "pýsnička", "note_cs": "Písnička NENÍ vyjmenované — píšeme i."}
        ]),
        "mnemonic": "Pyšný pytel na pysku netopýra — slepýš s pylem klopýtá třpytivě zpytuje.",
        "common_mistakes": json.dumps([
            {"wrong": "pišný", "right": "pyšný", "why_cs": "Odvozeno od pýcha → y."},
            {"wrong": "pýsnička", "right": "písnička", "why_cs": "Písnička není vyjmenované slovo."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "p_šný — doplň i nebo y:", "answer": "y", "options": ["i", "y"]},
            {"type": "choose", "question": "p_tel — doplň i nebo y:", "answer": "y", "options": ["i", "y"]},
            {"type": "choose", "question": "p_snička — doplň i nebo y:", "answer": "í", "options": ["í", "ý"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz/?id=100",
        "sort_order": 13,
    },
    {
        "code": "vyjmenovana_slova_s",
        "category": "pravopis_hlasky",
        "subcategory": "vyjmenovaná slova",
        "level": "A2",
        "title_cs": "Vyjmenovaná slova po S",
        "rule_cs": "Po S píšeme Y/Ý: syn, sytý, sýr, syrový, sychravý, sýkora, sýček, sysel, syčet, sypat.",
        "explanation_cs": "Odvozená slova: syn → synovec, sytý → nasytit se, sýr → syreček, sypat → sýpka.",
        "examples": json.dumps([
            {"correct": "syn, synovec", "incorrect": "sin, sinovec", "note_cs": "Syn je vyjmenované slovo po S."},
            {"correct": "sýr, syreček", "incorrect": "sír, sireček", "note_cs": "Sýr patří do řady."},
            {"correct": "sirup", "incorrect": "syrup", "note_cs": "Sirup NENÍ vyjmenované — píšeme i!"}
        ]),
        "mnemonic": "Sytý syn sýr syreček — sychravý sýček sysel syčí sype.",
        "common_mistakes": json.dumps([
            {"wrong": "syrup", "right": "sirup", "why_cs": "Sirup není vyjmenované slovo — cizí slovo s i."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "s_n — doplň i nebo y:", "answer": "y", "options": ["i", "y"]},
            {"type": "choose", "question": "s_rup — doplň i nebo y:", "answer": "i", "options": ["i", "y"]},
            {"type": "choose", "question": "s_reček — doplň i nebo y:", "answer": "y", "options": ["i", "y"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz/?id=100",
        "sort_order": 14,
    },
    {
        "code": "vyjmenovana_slova_v",
        "category": "pravopis_hlasky",
        "subcategory": "vyjmenovaná slova",
        "level": "A2",
        "title_cs": "Vyjmenovaná slova po V",
        "rule_cs": "Po V píšeme Y/Ý: vy (zájmeno), vysoký, výt, výskat, zvykat, žvýkat, vydra, výr, vyžle, povyk, výheň. A předpona vy-/vý- (vždy s y!).",
        "explanation_cs": "Předpona vy-/vý- se vždy píše s Y: vyběhnout, výborný, vysvětlit, výsledek. Toto je nejužitečnější pravidlo — předpona vy- je velmi častá!",
        "examples": json.dumps([
            {"correct": "vyběhnout, výsledek", "incorrect": "viběhnout, vísledek", "note_cs": "Předpona vy-/vý- → vždy y."},
            {"correct": "vysoký, výška", "incorrect": "visoký, víška", "note_cs": "Vysoký je vyjmenované slovo."},
            {"correct": "vidět", "incorrect": "vydět", "note_cs": "Vidět NENÍ vyjmenované — 'vi' je součást kořene!"}
        ]),
        "mnemonic": "Předpona VY- = vždy Y! Vyběhni ven z výšky a uvidíš výsledek.",
        "common_mistakes": json.dumps([
            {"wrong": "vísledek", "right": "výsledek", "why_cs": "Předpona vý- → vždy y."},
            {"wrong": "vidět → vydět?", "right": "vidět (s i)", "why_cs": "Vi- v 'vidět' není předpona, je to kořen."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "v_běhnout — doplň i nebo y:", "answer": "y", "options": ["i", "y"]},
            {"type": "choose", "question": "v_dět — doplň i nebo y:", "answer": "i", "options": ["i", "y"]},
            {"type": "choose", "question": "v_soký — doplň i nebo y:", "answer": "y", "options": ["i", "y"]},
            {"type": "choose", "question": "v_sledek — doplň i nebo y:", "answer": "ý", "options": ["í", "ý"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz/?id=100",
        "sort_order": 15,
    },
    {
        "code": "vyjmenovana_slova_z",
        "category": "pravopis_hlasky",
        "subcategory": "vyjmenovaná slova",
        "level": "A2",
        "title_cs": "Vyjmenovaná slova po Z",
        "rule_cs": "Po Z píšeme Y/Ý: brzy, jazyk, nazývat se.",
        "explanation_cs": "Po Z je vyjmenovaných slov nejméně. Odvozená: jazyk → jazýček, jazykověda; nazývat → vyzývat, ozývat se.",
        "examples": json.dumps([
            {"correct": "jazyk, jazykový", "incorrect": "jazik, jazikový", "note_cs": "Jazyk je vyjmenované slovo po Z."},
            {"correct": "brzy", "incorrect": "brzi", "note_cs": "Brzy patří do řady."},
            {"correct": "zima", "incorrect": "zyma", "note_cs": "Zima NENÍ vyjmenované — píšeme i."}
        ]),
        "mnemonic": "Brzy se jazykem nazýváme — jen tři slova po Z!",
        "common_mistakes": json.dumps([
            {"wrong": "jazik", "right": "jazyk", "why_cs": "Jazyk je vyjmenované slovo po Z."},
            {"wrong": "zyma", "right": "zima", "why_cs": "Zima není vyjmenované slovo."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "jaz_k — doplň i nebo y:", "answer": "y", "options": ["i", "y"]},
            {"type": "choose", "question": "brz_ — doplň i nebo y:", "answer": "y", "options": ["i", "y"]},
            {"type": "choose", "question": "z_ma — doplň i nebo y:", "answer": "i", "options": ["i", "y"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz/?id=100",
        "sort_order": 16,
    },
    {
        "code": "pravopis_be_bje",
        "category": "pravopis_hlasky",
        "subcategory": "bě/bje",
        "level": "A2",
        "title_cs": "Psaní bě × bje",
        "rule_cs": "Píšeme bě: oběd, běžet, svědomí. Píšeme bje jen tam, kde b je na konci předpony a je na začátku kořene: objem, objektivní, subjekt.",
        "explanation_cs": "Bje se vyskytuje jen na švu předpony (ob-, sub-) a kořene začínajícího na je-. Ve všech ostatních případech píšeme bě.",
        "examples": json.dumps([
            {"correct": "oběd, oběh", "incorrect": "objed, objeh", "note_cs": "Bě — kořen začíná na bě."},
            {"correct": "objem, objekt", "incorrect": "oběm, obět", "note_cs": "Bje — předpona ob- + kořen jem/jekt."},
            {"correct": "běhat, běžet", "incorrect": "bjehat, bježet", "note_cs": "Bě — v kořeni slova."}
        ]),
        "mnemonic": "Bje = ob + je (objem, objekt). Jinak vždy bě!",
        "common_mistakes": json.dumps([
            {"wrong": "objed", "right": "oběd", "why_cs": "Kořen je 'běd', ne 'jed'. Píšeme oběd."},
            {"wrong": "obět", "right": "oběť (dar) / objekt (předmět)", "why_cs": "Oběť (dar) má bě; objekt má bje."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "o_ěd/bjed — jak napíšete 'oběd'?", "answer": "oběd", "options": ["oběd", "objed"]},
            {"type": "choose", "question": "o_ekt — jak napíšete 'objekt'?", "answer": "objekt", "options": ["oběkt", "objekt"]},
            {"type": "choose", "question": "o_em (množství prostoru) — bě nebo bje?", "answer": "objem", "options": ["oběm", "objem"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Pravopis",
        "sort_order": 20,
    },
    {
        "code": "pravopis_me_mne",
        "category": "pravopis_hlasky",
        "subcategory": "mě/mně",
        "level": "A2",
        "title_cs": "Psaní mě × mně",
        "rule_cs": "Mně = kde slyšíme [mňe] a můžeme nahradit 'tobě/sobě': Dej mně to = Dej tobě to. Mě = kde můžeme nahradit 'tebe/sebe': Vidíš mě = Vidíš tebe.",
        "explanation_cs": "Mně je 3. pád (komu? čemu?) a lokál 6. pád (o kom? o čem?). Mě je 2. pád (koho? čeho?) a 4. pád (koho? co?). Jednoduchý test: nahraď za tobě/tebe.",
        "examples": json.dumps([
            {"correct": "Řekni mně to. (= Řekni tobě to.)", "incorrect": "Řekni mě to.", "note_cs": "3. pád → mně (komu?)"},
            {"correct": "Vidíš mě? (= Vidíš tebe?)", "incorrect": "Vidíš mně?", "note_cs": "4. pád → mě (koho?)"},
            {"correct": "Vzpomínej na mě. (= na tebe)", "incorrect": "Vzpomínej na mně.", "note_cs": "4. pád → mě (na koho?)"},
            {"correct": "Po mně nic nezůstane. (= po tobě)", "incorrect": "Po mě nic nezůstane.", "note_cs": "6. pád → mně (po kom?)"}
        ]),
        "mnemonic": "Nahraď za TOBĚ → mně. Nahraď za TEBE → mě.",
        "common_mistakes": json.dumps([
            {"wrong": "Řekni mě to", "right": "Řekni mně to", "why_cs": "3. pád: komu? → mně (= tobě)."},
            {"wrong": "Vidíš mně?", "right": "Vidíš mě?", "why_cs": "4. pád: koho? → mě (= tebe)."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "Dej ___ to. (komu?)", "answer": "mně", "options": ["mě", "mně"]},
            {"type": "choose", "question": "Vidíš ___? (koho?)", "answer": "mě", "options": ["mě", "mně"]},
            {"type": "choose", "question": "Bez ___ to nejde. (bez koho?)", "answer": "mě", "options": ["mě", "mně"]},
            {"type": "choose", "question": "Po ___ nikdo nepřišel. (po kom?)", "answer": "mně", "options": ["mě", "mně"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Pravopis",
        "sort_order": 21,
    },
    {
        "code": "pravopis_u_u_krouz",
        "category": "pravopis_hlasky",
        "subcategory": "ú/ů",
        "level": "A1",
        "title_cs": "Psaní ú × ů",
        "rule_cs": "Ú (s čárkou) píšeme na začátku slova: úkol, úterý, účet. Ů (s kroužkem) píšeme uprostřed a na konci slova: dům, průvodce, domů.",
        "explanation_cs": "Výslovnost ú a ů je stejná — obojí je dlouhé u. Rozdíl je historický (kroužek vznikl ze staročeského 'uo'). Výjimky: některá přejatá slova mohou mít ú uprostřed (múza, túra).",
        "examples": json.dumps([
            {"correct": "úkol, účet, úterý", "incorrect": "ůkol, ůčet, ůterý", "note_cs": "Na začátku slova vždy ú."},
            {"correct": "dům, průvodce, domů", "incorrect": "dúm, prúvodce, domú", "note_cs": "Uprostřed a na konci vždy ů."},
            {"correct": "půl, stůl, vůle", "incorrect": "púl, stúl, vúle", "note_cs": "Uprostřed slova → ů."}
        ]),
        "mnemonic": "Ú na Úvod (začátek slova), Ů Uvnitř (uprostřed/konec).",
        "common_mistakes": json.dumps([
            {"wrong": "ůkol", "right": "úkol", "why_cs": "Na začátku slova vždy ú s čárkou."},
            {"wrong": "dúm", "right": "dům", "why_cs": "Uprostřed slova vždy ů s kroužkem."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "_kol — ú nebo ů?", "answer": "ú", "options": ["ú", "ů"]},
            {"type": "choose", "question": "d_m — ú nebo ů?", "answer": "ů", "options": ["ú", "ů"]},
            {"type": "choose", "question": "dom_ — ú nebo ů?", "answer": "ů", "options": ["ú", "ů"]},
            {"type": "choose", "question": "_terý — ú nebo ů?", "answer": "ú", "options": ["ú", "ů"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Pravopis",
        "sort_order": 22,
    },

    # ───────────────────────────────────────────────────────────────
    #  KATEGORIE: pravopis_interpunkce (Pravopis – interpunkce)
    # ───────────────────────────────────────────────────────────────
    {
        "code": "carka_vedlejsi_vety",
        "category": "pravopis_interpunkce",
        "subcategory": "čárka",
        "level": "A2",
        "title_cs": "Čárka před vedlejší větou",
        "rule_cs": "Vedlejší větu oddělujeme čárkou. Vedlejší věta začíná spojkou: že, aby, protože, když, který, kde, jak, co, než, zatímco.",
        "explanation_cs": "Čárku píšeme před spojkou, která uvozuje vedlejší větu: Vím, že to zvládneš. Řekl, aby přišel. Dům, který stojí na kopci, je starý.",
        "examples": json.dumps([
            {"correct": "Myslím, že máš pravdu.", "incorrect": "Myslím že máš pravdu.", "note_cs": "Čárka před 'že'."},
            {"correct": "Řekl, aby přišel brzy.", "incorrect": "Řekl aby přišel brzy.", "note_cs": "Čárka před 'aby'."},
            {"correct": "Člověk, který mluví česky, je šťastný.", "incorrect": "Člověk který mluví česky je šťastný.", "note_cs": "Čárka ze obou stran vedlejší věty."}
        ]),
        "mnemonic": "Vidíš spojku (že, aby, protože, když, který)? → Čárka před ní!",
        "common_mistakes": json.dumps([
            {"wrong": "Myslím že ano.", "right": "Myslím, že ano.", "why_cs": "Čárka vždy před 'že'."},
            {"wrong": "Nevím kdy přijde.", "right": "Nevím, kdy přijde.", "why_cs": "Čárka před tázací spojkou ve vedlejší větě."}
        ]),
        "exercise_data": json.dumps([
            {"type": "transform", "question": "Řekl že přijde zítra.", "answer": "Řekl, že přijde zítra."},
            {"type": "transform", "question": "Nevím kde bydlí.", "answer": "Nevím, kde bydlí."},
            {"type": "transform", "question": "Dům který stojí na kopci je starý.", "answer": "Dům, který stojí na kopci, je starý."},
            {"type": "transform", "question": "Myslím že máš pravdu.", "answer": "Myslím, že máš pravdu."}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Interpunkce",
        "sort_order": 30,
    },
    {
        "code": "carka_pred_a_ale",
        "category": "pravopis_interpunkce",
        "subcategory": "čárka",
        "level": "B1",
        "title_cs": "Čárka před a, ale, nebo",
        "rule_cs": "Před 'ale' a 'avšak' píšeme čárku VŽDY. Před 'a' píšeme čárku jen když spojuje dvě věty s různými podměty nebo má odporovací význam.",
        "explanation_cs": "Bez čárky: koupil chléb a mlíko (dva předměty). S čárkou: Přišel domů, a uviděl překvapení (dva různé děje). Před 'ale' vždy čárka: je malý, ale silný.",
        "examples": json.dumps([
            {"correct": "Je malý, ale silný.", "incorrect": "Je malý ale silný.", "note_cs": "Před 'ale' vždy čárka."},
            {"correct": "Koupil chléb a mlíko.", "incorrect": "Koupil chléb, a mlíko.", "note_cs": "Dva předměty jednoho podmětu → bez čárky."},
            {"correct": "Přišel domů, a uviděl překvapení.", "incorrect": "Přišel domů a uviděl překvapení.", "note_cs": "Dvě věty → s čárkou (ale obě jsou přijatelné)."}
        ]),
        "mnemonic": "ALE = VŽDY čárka. A = záleží na kontextu.",
        "common_mistakes": json.dumps([
            {"wrong": "Je hezky ale studené.", "right": "Je hezky, ale studené.", "why_cs": "Před 'ale' vždy čárka — vyjadřuje rozpor."}
        ]),
        "exercise_data": json.dumps([
            {"type": "transform", "question": "Je hezky ale studené.", "answer": "Je hezky, ale studené."},
            {"type": "choose", "question": "Koupil chléb _ mlíko. (čárka?)", "answer": "a (bez čárky)", "options": ["a (bez čárky)", ", a (s čárkou)"]},
            {"type": "transform", "question": "Chtěl přijít ale nemohl.", "answer": "Chtěl přijít, ale nemohl."}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Interpunkce",
        "sort_order": 31,
    },

    # ───────────────────────────────────────────────────────────────
    #  KATEGORIE: pravopis_velka_pismena (Pravopis – velká písmena)
    # ───────────────────────────────────────────────────────────────
    {
        "code": "velka_pismena_obecne",
        "category": "pravopis_velka_pismena",
        "subcategory": "obecné zásady",
        "level": "A2",
        "title_cs": "Velká písmena – obecné zásady",
        "rule_cs": "Velké písmeno píšeme: 1) na začátku věty, 2) u vlastních jmen (Praha, Novák), 3) u názvů institucí (Karlova univerzita). Malé písmeno: funkce (prezident), jazyky (čeština), dny (pondělí), měsíce (leden).",
        "explanation_cs": "Na rozdíl od angličtiny se v češtině nepíše velké písmeno u dnů v týdnu, měsíců, jazyků ani funkcí. Velké písmeno se píše jen u prvního slova víceslovných názvů: Severní ledový oceán.",
        "examples": json.dumps([
            {"correct": "v pondělí, v lednu", "incorrect": "v Pondělí, v Lednu", "note_cs": "Dny a měsíce s malým písmenem."},
            {"correct": "mluvím česky", "incorrect": "mluvím Česky", "note_cs": "Jazyky s malým písmenem."},
            {"correct": "Karlova univerzita", "incorrect": "karlova univerzita", "note_cs": "Oficiální název → velké písmeno."},
            {"correct": "prezident republiky", "incorrect": "Prezident republiky", "note_cs": "Funkce s malým písmenem."}
        ]),
        "mnemonic": "Čeština není angličtina — dny, měsíce, jazyky s malým!",
        "common_mistakes": json.dumps([
            {"wrong": "v Pondělí", "right": "v pondělí", "why_cs": "Dny v týdnu se píšou s malým písmenem."},
            {"wrong": "mluvím Česky", "right": "mluvím česky", "why_cs": "Jazyky se píšou s malým písmenem."},
            {"wrong": "Prezident republiky", "right": "prezident republiky", "why_cs": "Funkce se píšou s malým písmenem."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "Jak napíšeme 'pondělí'?", "answer": "pondělí (malé)", "options": ["Pondělí (velké)", "pondělí (malé)"]},
            {"type": "choose", "question": "Jak napíšeme 'prezident'?", "answer": "prezident (malé)", "options": ["Prezident (velké)", "prezident (malé)"]},
            {"type": "choose", "question": "Jak napíšeme 'Karlova univerzita'?", "answer": "Karlova univerzita", "options": ["Karlova univerzita", "karlova univerzita", "Karlova Univerzita"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz/?id=180",
        "sort_order": 40,
    },
    {
        "code": "velka_pismena_zemepisna",
        "category": "pravopis_velka_pismena",
        "subcategory": "zeměpisné názvy",
        "level": "B1",
        "title_cs": "Velká písmena – zeměpisné názvy",
        "rule_cs": "Velké písmeno u všech slov zeměpisného jména: Severní Amerika, Tichý oceán, Orlické hory. Ale: severní Evropa (přídavné jméno není součástí jména, jen směr).",
        "explanation_cs": "Pokud je přídavné jméno součástí oficiálního názvu, píšeme velké písmeno (Severní Amerika). Pokud jen popisuje polohu, píšeme malé (severní Čechy, jižní Morava).",
        "examples": json.dumps([
            {"correct": "Severní Amerika", "incorrect": "severní Amerika", "note_cs": "Severní je součástí oficiálního názvu."},
            {"correct": "severní Evropa", "incorrect": "Severní Evropa", "note_cs": "'severní' jen popisuje polohu."},
            {"correct": "Orlické hory", "incorrect": "orlické hory", "note_cs": "Oficiální zeměpisný název."}
        ]),
        "mnemonic": "Oficiální název → Velké. Jen směr/poloha → malé.",
        "common_mistakes": json.dumps([
            {"wrong": "severní Amerika", "right": "Severní Amerika", "why_cs": "Severní je součástí oficiálního názvu kontinentu."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "_everní Amerika", "answer": "S (velké)", "options": ["S (velké)", "s (malé)"]},
            {"type": "choose", "question": "_everní Evropa (jen směr)", "answer": "s (malé)", "options": ["S (velké)", "s (malé)"]},
            {"type": "choose", "question": "_rlické hory", "answer": "O (velké)", "options": ["O (velké)", "o (malé)"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz/?id=180",
        "sort_order": 41,
    },

    # ───────────────────────────────────────────────────────────────
    #  KATEGORIE: tvaroslovi_podstatna (Tvarosloví – podstatná jména)
    # ───────────────────────────────────────────────────────────────
    {
        "code": "podstatna_rod",
        "category": "tvaroslovi_podstatna",
        "subcategory": "rod",
        "level": "A1",
        "title_cs": "Rod podstatných jmen",
        "rule_cs": "Každé podstatné jméno má rod: mužský (ten muž, ten hrad), ženský (ta žena, ta ulice) nebo střední (to město, to moře). Rod se nedá vždy poznat z koncovky!",
        "explanation_cs": "Pomůcka: ten (mužský), ta (ženský), to (střední). Mužský rod se dělí na životný (ten muž) a neživotný (ten hrad). Pozor na výjimky: tramvaj (ženská), předseda (mužský!).",
        "examples": json.dumps([
            {"correct": "ten stůl (muž. neživ.)", "incorrect": "", "note_cs": "Končí na souhlásku → typicky mužský neživotný."},
            {"correct": "ta škola (žen.)", "incorrect": "", "note_cs": "Končí na -a → typicky ženský."},
            {"correct": "to auto (stř.)", "incorrect": "", "note_cs": "Končí na -o → typicky střední."},
            {"correct": "ta tramvaj (žen.!)", "incorrect": "ten tramvaj", "note_cs": "Tramvaj je ženského rodu (výjimka)."}
        ]),
        "mnemonic": "TEN-TA-TO: ten pro mužský, ta pro ženský, to pro střední.",
        "common_mistakes": json.dumps([
            {"wrong": "ten tramvaj", "right": "ta tramvaj", "why_cs": "Tramvaj je ženského rodu."},
            {"wrong": "ta předseda", "right": "ten předseda", "why_cs": "Předseda je mužského rodu (i když končí na -a)."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "___ škola", "answer": "ta", "options": ["ten", "ta", "to"]},
            {"type": "choose", "question": "___ město", "answer": "to", "options": ["ten", "ta", "to"]},
            {"type": "choose", "question": "___ stůl", "answer": "ten", "options": ["ten", "ta", "to"]},
            {"type": "choose", "question": "___ tramvaj", "answer": "ta", "options": ["ten", "ta", "to"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 50,
    },
    {
        "code": "podstatna_vzor_pan",
        "category": "tvaroslovi_podstatna",
        "subcategory": "skloňování",
        "level": "A1",
        "title_cs": "Vzor 'pán' (mužský životný)",
        "rule_cs": "Podstatná jména mužského rodu životná, končící na souhlásku, se skloňují podle vzoru 'pán': pán, muž → pána, muže (2. p.), pánovi, muži (3. p.).",
        "explanation_cs": "Vzor pán: 1.p. pán, 2.p. pána, 3.p. pánovi/pánu, 4.p. pána, 5.p. pane!, 6.p. o pánovi/pánu, 7.p. pánem. Podobně: student → studenta → studentovi.",
        "examples": json.dumps([
            {"correct": "Vidím pána. (4. pád)", "incorrect": "Vidím pán.", "note_cs": "4. pád životného = 2. pád."},
            {"correct": "Dám to studentovi. (3. pád)", "incorrect": "Dám to student.", "note_cs": "3. pád: -ovi."},
            {"correct": "Pane profesore! (5. pád)", "incorrect": "Pán profesore!", "note_cs": "5. pád (oslovení): -e."}
        ]),
        "mnemonic": "Vzor PÁN: pán-pána-pánovi-pána-pane!-o pánovi-pánem.",
        "common_mistakes": json.dumps([
            {"wrong": "Vidím student.", "right": "Vidím studenta.", "why_cs": "U životných: 4. pád = 2. pád (studenta)."}
        ]),
        "exercise_data": json.dumps([
            {"type": "fill_gap", "question": "Vidím ___. (student, 4. p.)", "answer": "studenta"},
            {"type": "fill_gap", "question": "Dám to ___. (profesor, 3. p.)", "answer": "profesorovi"},
            {"type": "choose", "question": "5. pád od 'pán' je:", "answer": "pane!", "options": ["pán!", "pane!", "páne!"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 51,
    },
    {
        "code": "podstatna_vzor_zena",
        "category": "tvaroslovi_podstatna",
        "subcategory": "skloňování",
        "level": "A1",
        "title_cs": "Vzor 'žena' (ženský rod na -a)",
        "rule_cs": "Podstatná jména ženského rodu na -a se skloňují podle vzoru 'žena': žena → ženy (2. p.), ženě (3. p.), ženu (4. p.), ženo! (5. p.).",
        "explanation_cs": "Vzor žena: 1.p. žena, 2.p. ženy, 3.p. ženě, 4.p. ženu, 5.p. ženo!, 6.p. o ženě, 7.p. ženou. Podobně: škola → školy, škole, školu.",
        "examples": json.dumps([
            {"correct": "Vidím ženu. (4. pád)", "incorrect": "Vidím žena.", "note_cs": "4. pád: -u."},
            {"correct": "Jdu do školy. (2. pád)", "incorrect": "Jdu do škola.", "note_cs": "2. pád: -y."},
            {"correct": "Řekni to ženě. (3. pád)", "incorrect": "Řekni to žena.", "note_cs": "3. pád: -ě."}
        ]),
        "mnemonic": "Vzor ŽENA: žena-ženy-ženě-ženu-ženo!-o ženě-ženou.",
        "common_mistakes": json.dumps([
            {"wrong": "Jdu do škola", "right": "Jdu do školy", "why_cs": "2. pád: škola → školy (-y)."}
        ]),
        "exercise_data": json.dumps([
            {"type": "fill_gap", "question": "Jdu do ___. (škola, 2. p.)", "answer": "školy"},
            {"type": "fill_gap", "question": "Vidím ___. (žena, 4. p.)", "answer": "ženu"},
            {"type": "fill_gap", "question": "Řekni to ___. (maminka, 3. p.)", "answer": "mamince"}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 52,
    },
    {
        "code": "podstatna_vzor_mesto",
        "category": "tvaroslovi_podstatna",
        "subcategory": "skloňování",
        "level": "A1",
        "title_cs": "Vzor 'město' (střední rod na -o)",
        "rule_cs": "Podstatná jména středního rodu na -o se skloňují podle vzoru 'město': město → města (2. p.), městu (3. p.), město (4. p. = 1. p.).",
        "explanation_cs": "Vzor město: 1.p. město, 2.p. města, 3.p. městu, 4.p. město, 5.p. město!, 6.p. o městě/městu, 7.p. městem. Podobně: auto → auta, autu, auto.",
        "examples": json.dumps([
            {"correct": "Bydlím v centru města. (2. p.)", "incorrect": "v centru město", "note_cs": "2. pád: -a."},
            {"correct": "Jedu do města. (2. p.)", "incorrect": "Jedu do město.", "note_cs": "2. pád: město → města."},
            {"correct": "Ze slova 'auto': auta (2. p.)", "incorrect": "auto (2. p.)", "note_cs": "2. pád: auto → auta."}
        ]),
        "mnemonic": "Vzor MĚSTO: město-města-městu-město-město!-o městě-městem.",
        "common_mistakes": None,
        "exercise_data": json.dumps([
            {"type": "fill_gap", "question": "Jedu do ___. (město, 2. p.)", "answer": "města"},
            {"type": "fill_gap", "question": "Nemám ___. (auto, 4. p.)", "answer": "auto"},
            {"type": "fill_gap", "question": "Mluvíme o ___. (kino, 6. p.)", "answer": "kině|kinu"}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 53,
    },
    {
        "code": "podstatna_7pad",
        "category": "tvaroslovi_podstatna",
        "subcategory": "7. pád",
        "level": "A2",
        "title_cs": "Sedmý pád (instrumentál)",
        "rule_cs": "7. pád odpovídá na otázku 'kým? čím? s kým? s čím?'. Koncovky: muž. -em/-ou, žen. -ou/-í, stř. -em/-ím. S předložkami: s, za, nad, pod, před, mezi.",
        "explanation_cs": "7. pád se často užívá s předložkou 's' (s kamarádem), ale i bez předložky (píšu tužkou = čím?).",
        "examples": json.dumps([
            {"correct": "Jdu s kamarádem.", "incorrect": "Jdu s kamarád.", "note_cs": "7. pád: kamarád → kamarádem."},
            {"correct": "Píšu tužkou.", "incorrect": "Píšu tužka.", "note_cs": "7. pád: tužka → tužkou."},
            {"correct": "Jedu autem.", "incorrect": "Jedu auto.", "note_cs": "7. pád: auto → autem."}
        ]),
        "mnemonic": "KÝM? ČÍM? → 7. pád. Předložky: s, za, nad, pod, před, mezi.",
        "common_mistakes": json.dumps([
            {"wrong": "Jdu s kamarád", "right": "Jdu s kamarádem", "why_cs": "Po 's' je vždy 7. pád."},
            {"wrong": "Jedu s auto", "right": "Jedu autem", "why_cs": "Auto v 7. pádu → autem."}
        ]),
        "exercise_data": json.dumps([
            {"type": "fill_gap", "question": "Jdu s ___. (kamarád)", "answer": "kamarádem"},
            {"type": "fill_gap", "question": "Píšu ___. (tužka)", "answer": "tužkou"},
            {"type": "fill_gap", "question": "Cestuju ___. (vlak)", "answer": "vlakem"},
            {"type": "fill_gap", "question": "Bydlím s ___. (rodina)", "answer": "rodinou"}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 54,
    },

    # ───────────────────────────────────────────────────────────────
    #  KATEGORIE: tvaroslovi_pridavna
    # ───────────────────────────────────────────────────────────────
    {
        "code": "pridavna_tvrda_mekka",
        "category": "tvaroslovi_pridavna",
        "subcategory": "tvrdá a měkká",
        "level": "A2",
        "title_cs": "Tvrdá a měkká přídavná jména",
        "rule_cs": "Tvrdá přídavná jména mají koncovky -ý/-á/-é (mladý, mladá, mladé). Měkká přídavná jména mají koncovky -í (jarní, moderní). Měkká mají stejný tvar ve všech rodech!",
        "explanation_cs": "Tvrdá: nový → nový (muž.), nová (žen.), nové (stř.). Měkká: moderní → moderní (muž.), moderní (žen.), moderní (stř.) — vždy stejné!",
        "examples": json.dumps([
            {"correct": "nový dům, nová škola, nové auto", "incorrect": "", "note_cs": "Tvrdé — mění koncovku podle rodu."},
            {"correct": "moderní dům, moderní škola, moderní auto", "incorrect": "", "note_cs": "Měkké — stejná koncovka -í."},
            {"correct": "jarní počasí", "incorrect": "jarný počasí", "note_cs": "Jarní je měkké → -í."}
        ]),
        "mnemonic": "Tvrdé = -ý/-á/-é (mění se). Měkké = -í (nemění se).",
        "common_mistakes": json.dumps([
            {"wrong": "jarný", "right": "jarní", "why_cs": "Jarní je měkké přídavné jméno → -í."},
            {"wrong": "moderný", "right": "moderní", "why_cs": "Moderní je měkké přídavné jméno → -í."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "Je 'jarní' tvrdé nebo měkké?", "answer": "měkké", "options": ["tvrdé", "měkké"]},
            {"type": "choose", "question": "Je 'nový' tvrdé nebo měkké?", "answer": "tvrdé", "options": ["tvrdé", "měkké"]},
            {"type": "fill_gap", "question": "nov___ dům (mužský rod)", "answer": "ý"},
            {"type": "fill_gap", "question": "modern___ škola (ženský rod)", "answer": "í"}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 60,
    },
    {
        "code": "pridavna_stupnovani",
        "category": "tvaroslovi_pridavna",
        "subcategory": "stupňování",
        "level": "A2",
        "title_cs": "Stupňování přídavných jmen",
        "rule_cs": "1. stupeň: malý. 2. stupeň (komparativ): menší (-ší/-ější/-ejší). 3. stupeň (superlativ): nejmenší (nej- + 2. stupeň).",
        "explanation_cs": "Pravidelné: chytrý → chytřejší → nejchytřejší. Krátké: malý → menší → nejmenší, velký → větší → největší. Nepravidelné: dobrý → lepší → nejlepší, špatný → horší → nejhorší.",
        "examples": json.dumps([
            {"correct": "velký → větší → největší", "incorrect": "velký → velkejší → nejvělkejší", "note_cs": "Nepravidelné stupňování."},
            {"correct": "dobrý → lepší → nejlepší", "incorrect": "dobrý → dobřejší", "note_cs": "Nepravidelné stupňování."},
            {"correct": "chytrý → chytřejší → nejchytřejší", "incorrect": "", "note_cs": "Pravidelné: -ejší / nej-."}
        ]),
        "mnemonic": "NEJ + 2. stupeň = 3. stupeň. Zapamatuj nepravidelné: dobrý-lepší, špatný-horší, velký-větší, malý-menší!",
        "common_mistakes": json.dumps([
            {"wrong": "dobřejší", "right": "lepší", "why_cs": "Dobrý má nepravidelný 2. stupeň: lepší."},
            {"wrong": "špatnější", "right": "horší", "why_cs": "Špatný má nepravidelný 2. stupeň: horší."}
        ]),
        "exercise_data": json.dumps([
            {"type": "fill_gap", "question": "dobrý → ___ → nejlepší", "answer": "lepší"},
            {"type": "fill_gap", "question": "malý → ___ → nejmenší", "answer": "menší"},
            {"type": "fill_gap", "question": "chytrý → chytřejší → ___", "answer": "nejchytřejší"},
            {"type": "choose", "question": "2. stupeň od 'špatný' je:", "answer": "horší", "options": ["špatnější", "horší", "nejšpatnější"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 61,
    },

    # ───────────────────────────────────────────────────────────────
    #  KATEGORIE: tvaroslovi_zajmena
    # ───────────────────────────────────────────────────────────────
    {
        "code": "zajmena_osobni",
        "category": "tvaroslovi_zajmena",
        "subcategory": "osobní zájmena",
        "level": "A1",
        "title_cs": "Osobní zájmena a jejich tvary",
        "rule_cs": "Osobní zájmena: já, ty, on/ona/ono, my, vy, oni/ony. V češtině se podmětové zájmeno často vynechává: Jsem student (ne: Já jsem student), protože slovesná koncovka ukazuje osobu.",
        "explanation_cs": "Zájmeno v podmětu se používá jen pro důraz: Já to udělám (zdůrazněno). Bez důrazu: Udělám to.",
        "examples": json.dumps([
            {"correct": "Jsem student.", "incorrect": "Já jsem student. (zbytečné)", "note_cs": "Zájmeno není potřeba — koncovka -m ukazuje 1. osobu."},
            {"correct": "JÁ to udělám! (důraz)", "incorrect": "", "note_cs": "S důrazem je zájmeno v pořádku."},
            {"correct": "Mluvíš česky?", "incorrect": "Ty mluvíš česky? (zbytečné)", "note_cs": "Koncovka -š ukazuje 2. osobu."}
        ]),
        "mnemonic": "Česká slovesa ukazují osobu koncovkou → zájmeno jen pro důraz!",
        "common_mistakes": json.dumps([
            {"wrong": "Já jsem, ty jsi, on je... (vždy)", "right": "Jsem, jsi, je... (běžně)", "why_cs": "V češtině podmětové zájmeno obvykle vynecháváme."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "Která věta je přirozenější?", "answer": "Jsem z Prahy.", "options": ["Já jsem z Prahy.", "Jsem z Prahy."]},
            {"type": "choose", "question": "Kdy použijeme 'já'?", "answer": "pro důraz", "options": ["vždy", "pro důraz", "nikdy"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 70,
    },
    {
        "code": "zajmena_mi_me_mne",
        "category": "tvaroslovi_zajmena",
        "subcategory": "krátké tvary",
        "level": "A2",
        "title_cs": "Krátké tvary zájmen: mi, mě, mně, ti, tě",
        "rule_cs": "Krátké tvary se píšou bez přízvuku a dávají se na 2. místo ve větě: Řekl mi to. Vidí mě. Dlouhé tvary pro důraz: Mně to řekl! Mě viděl!",
        "explanation_cs": "Krátké: mi (3. p.), mě (2./4. p.), ti (3. p.), tě (2./4. p.). Dlouhé: mně (3. p.), mě/mne (2./4. p.), tobě (3. p.), tebe (2./4. p.).",
        "examples": json.dumps([
            {"correct": "Řekl mi to. (krátké, běžné)", "incorrect": "", "note_cs": "Mi na 2. místě."},
            {"correct": "Mně to řekl! (důraz)", "incorrect": "", "note_cs": "Dlouhý tvar pro zdůraznění."},
            {"correct": "Vidí mě. (4. pád)", "incorrect": "Vidí mi.", "note_cs": "Mi = 3. pád, mě = 4. pád."}
        ]),
        "mnemonic": "MI = komu (3. pád). MĚ = koho (4. pád). Krátké tvary na 2. místo!",
        "common_mistakes": json.dumps([
            {"wrong": "Vidí mi.", "right": "Vidí mě.", "why_cs": "Vidět + 4. pád → mě (koho?), ne mi (komu?)."},
            {"wrong": "Mi řekl to.", "right": "Řekl mi to.", "why_cs": "Krátký tvar 'mi' musí být na 2. místě ve větě."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "Vidí ___. (koho?)", "answer": "mě", "options": ["mi", "mě"]},
            {"type": "choose", "question": "Řekl ___ to. (komu?)", "answer": "mi", "options": ["mi", "mě"]},
            {"type": "choose", "question": "Pomozte ___! (komu?)", "answer": "mi", "options": ["mi", "mě"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 71,
    },

    # ───────────────────────────────────────────────────────────────
    #  KATEGORIE: tvaroslovi_slovesa
    # ───────────────────────────────────────────────────────────────
    {
        "code": "slovesa_cas_pritomny",
        "category": "tvaroslovi_slovesa",
        "subcategory": "přítomný čas",
        "level": "A1",
        "title_cs": "Přítomný čas – časování sloves",
        "rule_cs": "Přítomný čas: já dělám, ty děláš, on/ona dělá, my děláme, vy děláte, oni dělají. Koncovky: -m/-ám, -š/-áš, -Ø/-á, -me/-áme, -te/-áte, -jí/-ají.",
        "explanation_cs": "Česká slovesa se dělí do tříd podle koncovek. Nejčastější vzory: dělat (dělám), prosit (prosím), nést (nesu), číst (čtu).",
        "examples": json.dumps([
            {"correct": "Dělám, děláš, dělá, děláme, děláte, dělají.", "incorrect": "", "note_cs": "Vzor dělat (-ám, -áš, -á...)."},
            {"correct": "Prosím, prosíš, prosí, prosíme, prosíte, prosí.", "incorrect": "", "note_cs": "Vzor prosit (-ím, -íš, -í...)."},
            {"correct": "Mluvím česky.", "incorrect": "Já mluvím česky.", "note_cs": "Bez zájmena — koncovka -m = já."}
        ]),
        "mnemonic": "-M = já, -Š = ty, (nic) = on/ona, -ME = my, -TE = vy, -JÍ/-Í = oni.",
        "common_mistakes": json.dumps([
            {"wrong": "Oni dělá.", "right": "Oni dělají.", "why_cs": "3. os. mn. č. = dělají (-jí/-ají), ne dělá."}
        ]),
        "exercise_data": json.dumps([
            {"type": "fill_gap", "question": "Já ___ česky. (mluvit)", "answer": "mluvím"},
            {"type": "fill_gap", "question": "Ty ___ pivo. (pít)", "answer": "piješ"},
            {"type": "fill_gap", "question": "Oni ___ do školy. (chodit)", "answer": "chodí"},
            {"type": "fill_gap", "question": "My ___ v Praze. (bydlet)", "answer": "bydlíme"}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 80,
    },
    {
        "code": "slovesa_cas_minuly",
        "category": "tvaroslovi_slovesa",
        "subcategory": "minulý čas",
        "level": "A1",
        "title_cs": "Minulý čas",
        "rule_cs": "Minulý čas = příčestí minulé (l-ové) + pomocné sloveso být: dělal jsem, dělal jsi, dělal, dělali jsme, dělali jste, dělali. Ve 3. osobě se 'být' vynechává!",
        "explanation_cs": "Příčestí se mění podle rodu: dělal (muž.), dělala (žen.), dělalo (stř.), dělali (mn.č. muž.), dělaly (mn.č. žen./stř.). Pomocné sloveso 'být' se vynechává ve 3. osobě.",
        "examples": json.dumps([
            {"correct": "Dělal jsem. (muž., já)", "incorrect": "", "note_cs": "Jsem = pomocné sloveso pro 1. os."},
            {"correct": "Dělala jsi. (žen., ty)", "incorrect": "Dělal jsi. (pokud je to žena)", "note_cs": "Rod příčestí musí souhlasit s podmětem."},
            {"correct": "On dělal. (bez 'být'!)", "incorrect": "On dělal je.", "note_cs": "Ve 3. osobě se pomocné sloveso nepíše."}
        ]),
        "mnemonic": "L-ové příčestí + jsem/jsi/jsme/jste. Ve 3. osobě BEZ pomocného slovesa!",
        "common_mistakes": json.dumps([
            {"wrong": "Já dělal.", "right": "Dělal jsem.", "why_cs": "V 1. a 2. osobě musí být pomocné sloveso 'být'."},
            {"wrong": "On dělal je.", "right": "On dělal.", "why_cs": "Ve 3. osobě pomocné sloveso NEPÍŠEME."}
        ]),
        "exercise_data": json.dumps([
            {"type": "fill_gap", "question": "Včera ___ ___ v kině. (já, být)", "answer": "jsem byl|jsem byla"},
            {"type": "fill_gap", "question": "Co ___ ___? (ty, dělat)", "answer": "jsi dělal|jsi dělala"},
            {"type": "choose", "question": "On včera ___. (pracovat)", "answer": "pracoval", "options": ["pracoval jsem", "pracoval", "pracoval je"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 81,
    },
    {
        "code": "slovesa_vid",
        "category": "tvaroslovi_slovesa",
        "subcategory": "vid",
        "level": "A2",
        "title_cs": "Vid sloves: dokonavý a nedokonavý",
        "rule_cs": "Nedokonavý vid = děj probíhá, opakuje se: dělat, psát, číst. Dokonavý vid = děj je dokončený, jednorázový: udělat, napsat, přečíst.",
        "explanation_cs": "Dokonavá slovesa NEMOHOU tvořit přítomný čas (napíšu = budoucnost!). Nedokonavá mohou: píšu (teď). Budoucí čas: budu psát (nedok.) × napíšu (dok.).",
        "examples": json.dumps([
            {"correct": "Píšu dopis. (teď, nedok.)", "incorrect": "", "note_cs": "Nedokonavé → přítomný čas."},
            {"correct": "Napíšu dopis. (zítra, dok.)", "incorrect": "Napíšu dopis teď.", "note_cs": "Dokonavé → automaticky budoucí čas."},
            {"correct": "Budu psát dopis. (nedok. budoucí)", "incorrect": "Budu napsat dopis.", "note_cs": "Nedokonavé + budu = budoucí."}
        ]),
        "mnemonic": "Nedokonavé = probíhá (teď). Dokonavé = hotovo (budoucnost). Napíšu ≠ píšu!",
        "common_mistakes": json.dumps([
            {"wrong": "Napíšu to teď (přítomnost).", "right": "Píšu to teď.", "why_cs": "Dokonavé 'napíšu' je budoucí čas, ne přítomný!"},
            {"wrong": "Budu napsat", "right": "Napíšu / Budu psát", "why_cs": "S 'budu' jen nedokonavé: budu psát. Nebo dokončené: napíšu."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "'psát' je vid:", "answer": "nedokonavý", "options": ["dokonavý", "nedokonavý"]},
            {"type": "choose", "question": "'napsat' je vid:", "answer": "dokonavý", "options": ["dokonavý", "nedokonavý"]},
            {"type": "choose", "question": "'Napíšu dopis' je čas:", "answer": "budoucí", "options": ["přítomný", "budoucí"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 82,
    },
    {
        "code": "slovesa_podminovaci_zpusob",
        "category": "tvaroslovi_slovesa",
        "subcategory": "kondicionál",
        "level": "B1",
        "title_cs": "Podmiňovací způsob (kondicionál)",
        "rule_cs": "Podmiňovací způsob = by + l-ové příčestí: dělal bych, dělal bys, dělal by, dělali bychom, dělali byste, dělali by. Pozor: bych/bys/bychom/byste (NE by jsem!).",
        "explanation_cs": "Tvary: bych (já), bys (ty), by (on/ona), bychom (my), byste (vy), by (oni). Chyba: 'bysme' je nespisovné, správně: bychom.",
        "examples": json.dumps([
            {"correct": "Chtěl bych pivo.", "incorrect": "Chtěl by jsem pivo.", "note_cs": "Bych (NE by jsem)."},
            {"correct": "Mohl bys mi pomoct?", "incorrect": "Mohl by jsi mi pomoct?", "note_cs": "Bys (NE by jsi)."},
            {"correct": "Mohli bychom jít?", "incorrect": "Mohli bysme jít?", "note_cs": "Bychom (NE bysme)."}
        ]),
        "mnemonic": "BYCH-BYS-BY-BYCHOM-BYSTE-BY. Nikdy 'by jsem' ani 'bysme'!",
        "common_mistakes": json.dumps([
            {"wrong": "by jsem", "right": "bych", "why_cs": "1. os. j.č. = bych, ne 'by jsem'."},
            {"wrong": "by jsi", "right": "bys", "why_cs": "2. os. j.č. = bys, ne 'by jsi'."},
            {"wrong": "bysme", "right": "bychom", "why_cs": "1. os. mn.č. = bychom, 'bysme' je nespisovné."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "Chtěl ___ pivo. (já)", "answer": "bych", "options": ["by jsem", "bych", "bysem"]},
            {"type": "choose", "question": "Mohl ___ mi říct? (ty)", "answer": "bys", "options": ["by jsi", "bys", "bysi"]},
            {"type": "choose", "question": "Mohli ___ jít? (my)", "answer": "bychom", "options": ["bysme", "bychom", "by jsme"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 83,
    },
    {
        "code": "slovesa_rozkazovaci_zpusob",
        "category": "tvaroslovi_slovesa",
        "subcategory": "imperativ",
        "level": "A2",
        "title_cs": "Rozkazovací způsob (imperativ)",
        "rule_cs": "Rozkazovací způsob: 2. os. j.č. dělej!, 1. os. mn.č. dělejme!, 2. os. mn.č. dělejte! Tvoří se od 3. os. mn.č. přítomného času: dělají → dělej, píšou → piš.",
        "explanation_cs": "Jednoslab. slovesa: piš! čti! jdi! Víceslab.: dělej! mluvte! pomozte! Některá mají zvláštní tvary: buď!, měj!, jez!",
        "examples": json.dumps([
            {"correct": "Dělej! Dělejte! Dělejme!", "incorrect": "", "note_cs": "Pravidelný imperativ od 'dělat'."},
            {"correct": "Piš! Pište!", "incorrect": "Pišeš!", "note_cs": "Imperativ ≠ přítomný čas."},
            {"correct": "Pojď! Pojďte! Pojďme!", "incorrect": "Pojdi!", "note_cs": "Zvláštní tvar od 'jít' (pojď)."}
        ]),
        "mnemonic": "3. os. mn.č. → odeber koncovku → přidej Ø/-i/-ej pro ty, -me pro my, -te pro vy.",
        "common_mistakes": json.dumps([
            {"wrong": "Pojdi!", "right": "Pojď!", "why_cs": "Imperativ od 'jít' je 'pojď', ne 'pojdi'."},
            {"wrong": "Jez!", "right": "Jez! je správně (od jíst)", "why_cs": "Imperativ od jíst = jez (nepravidelné)."}
        ]),
        "exercise_data": json.dumps([
            {"type": "fill_gap", "question": "___! (dělat, ty)", "answer": "Dělej"},
            {"type": "fill_gap", "question": "___! (jít, ty — pojít/pojď)", "answer": "Pojď"},
            {"type": "fill_gap", "question": "___! (mluvit, vy)", "answer": "Mluvte"}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 84,
    },
    {
        "code": "slovesa_byt",
        "category": "tvaroslovi_slovesa",
        "subcategory": "být",
        "level": "A1",
        "title_cs": "Časování slovesa 'být'",
        "rule_cs": "Přítomný čas: jsem, jsi, je, jsme, jste, jsou. Minulý: byl jsem, byl jsi, byl, byli jsme, byli jste, byli. Kondicionál: byl bych, byl bys, byl by...",
        "explanation_cs": "Být je nejdůležitější nepravidelné sloveso. Záporné tvary: nejsem, nejsi, není, nejsme, nejste, nejsou. Pozor: 'jsou' (ne 'sou' — to je nespisovné).",
        "examples": json.dumps([
            {"correct": "Jsem z České republiky.", "incorrect": "Já jsem z České republiky. (zbytečné já)", "note_cs": "Bez zájmena v podmětu."},
            {"correct": "Jsou doma.", "incorrect": "Sou doma.", "note_cs": "Jsou — ne 'sou' (nespisovné)."},
            {"correct": "Nebyl jsem tam.", "incorrect": "Jsem nebyl tam.", "note_cs": "Zápor: ne- + byl + jsem."}
        ]),
        "mnemonic": "JSEM-JSI-JE-JSME-JSTE-JSOU. Zápor: NE + být.",
        "common_mistakes": json.dumps([
            {"wrong": "sou", "right": "jsou", "why_cs": "'Sou' je nespisovné, správně: jsou."},
            {"wrong": "seš", "right": "jsi", "why_cs": "'Seš' je nespisovné, správně: jsi."}
        ]),
        "exercise_data": json.dumps([
            {"type": "fill_gap", "question": "Já ___ student.", "answer": "jsem"},
            {"type": "fill_gap", "question": "Oni ___ doma.", "answer": "jsou"},
            {"type": "fill_gap", "question": "My ___ z Prahy.", "answer": "jsme"},
            {"type": "choose", "question": "Spisovná forma 'seš' je:", "answer": "jsi", "options": ["jsi", "jseš", "seš"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 85,
    },

    # ───────────────────────────────────────────────────────────────
    #  KATEGORIE: tvaroslovi_cislovky
    # ───────────────────────────────────────────────────────────────
    {
        "code": "cislovky_zakladni",
        "category": "tvaroslovi_cislovky",
        "subcategory": "základní číslovky",
        "level": "A1",
        "title_cs": "Základní číslovky a jejich tvary",
        "rule_cs": "Číslovky 1–4 se skloňují a rodově mění: jeden/jedna/jedno, dva/dvě, tři, čtyři. Od 5 výš se číslovky pojí s 2. pádem mn.č.: pět studentů.",
        "explanation_cs": "1–4 se chovají jako přídavná jména: jednoho studenta (2. p.), dvou studentů, tří studentů, čtyř studentů. Od 5: pět studentů, šest studentů → vždy 2. pád mn. č.",
        "examples": json.dumps([
            {"correct": "jeden student, jedna studentka, jedno dítě", "incorrect": "jeden studentka", "note_cs": "Číslovka 'jeden' se mění podle rodu."},
            {"correct": "dva studenti, dvě studentky", "incorrect": "dva studentky", "note_cs": "Dva (muž.) × dvě (žen./stř.)."},
            {"correct": "pět studentů", "incorrect": "pět studenti", "note_cs": "Od 5 → 2. pád mn. č."}
        ]),
        "mnemonic": "1–4 = skloňujeme (mění rod). 5+ = 2. pád množ. čísla.",
        "common_mistakes": json.dumps([
            {"wrong": "dva studentky", "right": "dvě studentky", "why_cs": "Ženský rod: dvě (ne dva)."},
            {"wrong": "pět studenti", "right": "pět studentů", "why_cs": "Od 5 výše → 2. pád mn. č."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "___ studentky (2)", "answer": "dvě", "options": ["dva", "dvě", "dvou"]},
            {"type": "fill_gap", "question": "Mám ___ bratrů. (5)", "answer": "pět"},
            {"type": "choose", "question": "Pět ___ (student)", "answer": "studentů", "options": ["studenti", "studentů", "student"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 90,
    },

    # ───────────────────────────────────────────────────────────────
    #  KATEGORIE: skladba (Skladba)
    # ───────────────────────────────────────────────────────────────
    {
        "code": "slovosled_zakladni",
        "category": "skladba",
        "subcategory": "slovosled",
        "level": "B1",
        "title_cs": "Základy českého slovosledu",
        "rule_cs": "Český slovosled je relativně volný (díky pádům), ale existují pravidla: 1) Příklonky (se, si, jsem, bych, mi, mu...) na 2. místo. 2) Nová informace na konec věty. 3) Přívlastek před jménem.",
        "explanation_cs": "Příklonky (slova bez vlastního přízvuku) stojí na 2. pozici ve větě. Věta 'Koupil jsem si auto.' — 'jsem si' na 2. místě. Nová/důležitá informace stojí na konci: Koupil jsem NOVÉ AUTO (důraz na auto).",
        "examples": json.dumps([
            {"correct": "Koupil jsem si auto.", "incorrect": "Jsem si koupil auto.", "note_cs": "Příklonky jsem/si na 2. místě."},
            {"correct": "Včera jsem byl v kině.", "incorrect": "Včera byl jsem v kině.", "note_cs": "'Jsem' na 2. místě (za 'včera')."},
            {"correct": "Dám ti to zítra.", "incorrect": "Ti to dám zítra.", "note_cs": "'Ti' je příklonka → na 2. místo."}
        ]),
        "mnemonic": "Příklonky (se, si, jsem, bych, mi, ti...) → VŽDY na 2. místo ve větě!",
        "common_mistakes": json.dumps([
            {"wrong": "Jsem koupil auto.", "right": "Koupil jsem auto.", "why_cs": "'Jsem' na 2. místě, ne na 1."},
            {"wrong": "Včera já jsem šel domů.", "right": "Včera jsem šel domů.", "why_cs": "Zájmeno 'já' je zbytečné + 'jsem' na 2. místo."}
        ]),
        "exercise_data": json.dumps([
            {"type": "order", "question": "jsem / Včera / v kině / byl", "answer": "Včera jsem byl v kině."},
            {"type": "order", "question": "auto / Koupil / si / jsem", "answer": "Koupil jsem si auto."},
            {"type": "order", "question": "česky / se / Učím", "answer": "Učím se česky."}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Skladba",
        "sort_order": 100,
    },
    {
        "code": "shoda_prisudku",
        "category": "skladba",
        "subcategory": "shoda",
        "level": "B1",
        "title_cs": "Shoda přísudku s podmětem",
        "rule_cs": "Přísudek se shoduje s podmětem v osobě, čísle a (v min. č.) v rodě: Studenti přišli (muž. mn.č.). Studentky přišly (žen. mn.č.). Děti přišly (stř. mn.č.).",
        "explanation_cs": "V minulém čase přísudek rozlišuje rod: on přišel (muž.), ona přišla (žen.), ono přišlo (stř.), oni přišli (muž. mn.), ony přišly (žen./stř. mn.).",
        "examples": json.dumps([
            {"correct": "Chlapci běželi. (muž. živ. mn.)", "incorrect": "Chlapci běžely.", "note_cs": "Muž. životný mn. č. → -i."},
            {"correct": "Dívky běžely. (žen. mn.)", "incorrect": "Dívky běželi.", "note_cs": "Ženský mn. č. → -y."},
            {"correct": "Auta stála. (stř. mn.)", "incorrect": "Auta stály.", "note_cs": "Střední mn. č. → -a."}
        ]),
        "mnemonic": "Muž. mn. → -i (dělali). Žen. mn. → -y (dělaly). Stř. mn. → -a (dělala).",
        "common_mistakes": json.dumps([
            {"wrong": "Děti přišli.", "right": "Děti přišly.", "why_cs": "Děti je ženský/střední rod → přišly (-y)."},
            {"wrong": "Ženy odešli.", "right": "Ženy odešly.", "why_cs": "Ženy (žen. rod mn. č.) → odešly (-y)."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "Chlapci ___. (přijít, min. č.)", "answer": "přišli", "options": ["přišli", "přišly", "přišla"]},
            {"type": "choose", "question": "Dívky ___. (odejít, min. č.)", "answer": "odešly", "options": ["odešli", "odešly", "odešla"]},
            {"type": "choose", "question": "Auta ___. (stát, min. č.)", "answer": "stála", "options": ["stáli", "stály", "stála"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Skladba",
        "sort_order": 101,
    },

    # ───────────────────────────────────────────────────────────────
    #  KATEGORIE: stylistika
    # ───────────────────────────────────────────────────────────────
    {
        "code": "spisovna_obecna",
        "category": "stylistika",
        "subcategory": "registr",
        "level": "B1",
        "title_cs": "Spisovná × obecná čeština",
        "rule_cs": "Spisovná čeština = oficiální jazyk (škola, úřad, média). Obecná čeština = hovorový jazyk (kamarádi, rodina). Příklady: jsou × sou, jsi × seš, krásný × krásnéj, mlíko × mléko.",
        "explanation_cs": "Obecná čeština: -ej místo -ý (malej, velkej), protetické v- (von, vokno), -eme → -em (půjdem), zkrácení (seš, vem, řek). Pro cizince: rozumět obojímu, ale mluvit/psát spisovně.",
        "examples": json.dumps([
            {"correct": "jsou (spisov.)", "incorrect": "sou (obecná č.)", "note_cs": "V písmu a formální řeči: jsou."},
            {"correct": "jsi (spisov.)", "incorrect": "seš (obecná č.)", "note_cs": "Spisovně: jsi."},
            {"correct": "mléko (spisov.)", "incorrect": "mlíko (obecná č.)", "note_cs": "Spisovně: mléko (é, ne í)."},
            {"correct": "okno (spisov.)", "incorrect": "vokno (obecná č.)", "note_cs": "Protetické v- je nespisovné."}
        ]),
        "mnemonic": "Rozumět obecné (lidé tak mluví) — ale psát/mluvit spisovně!",
        "common_mistakes": json.dumps([
            {"wrong": "Sou doma. (písemně)", "right": "Jsou doma.", "why_cs": "'Sou' je nespisovné, v textu píšeme 'jsou'."},
            {"wrong": "vokno (v textu)", "right": "okno", "why_cs": "Protetické v- nepatří do spisovné češtiny."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "Která forma je spisovná?", "answer": "jsou", "options": ["jsou", "sou"]},
            {"type": "choose", "question": "Která forma je spisovná?", "answer": "okno", "options": ["okno", "vokno"]},
            {"type": "choose", "question": "Která forma je spisovná?", "answer": "mléko", "options": ["mléko", "mlíko"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Stylistika",
        "sort_order": 110,
    },
    {
        "code": "formalni_neformalni",
        "category": "stylistika",
        "subcategory": "registr",
        "level": "B1",
        "title_cs": "Formální × neformální komunikace",
        "rule_cs": "Vykání (vy) = formální, s neznámými, staršími, v práci. Tykání (ty) = neformální, s přáteli, rodinou, dětmi. Přechod z vykání na tykání nabízí starší nebo nadřízený.",
        "explanation_cs": "Formální: Dobrý den, jak se máte? Neformální: Ahoj, jak se máš? V českém prostředí je přechod na tykání důležitý — čekejte, až vám nabídnou tykání.",
        "examples": json.dumps([
            {"correct": "Dobrý den, jak se máte? (vykání)", "incorrect": "", "note_cs": "S neznámými a staršími."},
            {"correct": "Ahoj, jak se máš? (tykání)", "incorrect": "", "note_cs": "S přáteli a rodinou."},
            {"correct": "Mohl byste mi pomoct? (vykání)", "incorrect": "", "note_cs": "Formální žádost."},
            {"correct": "Můžeš mi pomoct? (tykání)", "incorrect": "", "note_cs": "Neformální žádost."}
        ]),
        "mnemonic": "Vy = formální, úcta. Ty = neformální, blízkost. Čekej na nabídku tykání!",
        "common_mistakes": json.dumps([
            {"wrong": "Tykat šéfovi bez nabídku", "right": "Čekat na nabídku tykání", "why_cs": "V češtině je neslušné tykat bez dovolení — vždy vykat a čekat."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "S novým kolegou na schůzce:", "answer": "Dobrý den, jak se máte?", "options": ["Ahoj, jak se máš?", "Dobrý den, jak se máte?"]},
            {"type": "choose", "question": "Komu tykáme?", "answer": "přátelům a rodině", "options": ["všem", "přátelům a rodině", "nikomu"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Stylistika",
        "sort_order": 111,
    },

    # ───────────────────────────────────────────────────────────────
    #  EXTRA: Common tricky rules
    # ───────────────────────────────────────────────────────────────
    {
        "code": "pravopis_i_y_po_tvrdych",
        "category": "pravopis_hlasky",
        "subcategory": "i/y po souhláskách",
        "level": "A1",
        "title_cs": "I/Y po tvrdých a měkkých souhláskách",
        "rule_cs": "Po tvrdých souhláskách (h, ch, k, r, d, t, n) píšeme Y: chyba, krýt, ryba. Po měkkých souhláskách (ž, š, č, ř, c, j, ď, ť, ň) píšeme I: číslo, říkat, život.",
        "explanation_cs": "Po obojetných (b, f, l, m, p, s, v, z) záleží na slově — buď vyjmenované (y) nebo ostatní (i). Po tvrdých VŽDY y, po měkkých VŽDY i.",
        "examples": json.dumps([
            {"correct": "chyba, ryba, hobby", "incorrect": "chiba, riba", "note_cs": "Po tvrdých (ch, r) → Y."},
            {"correct": "číslo, život, řídit", "incorrect": "čýslo, žyvot", "note_cs": "Po měkkých (č, ž, ř) → I."},
            {"correct": "bylo (po obojet. b — vyjmen.)", "incorrect": "bilo (jiný význam!)", "note_cs": "Po obojetných záleží na slově."}
        ]),
        "mnemonic": "TVRDÉ (h,ch,k,r,d,t,n) → Y. MĚKKÉ (ž,š,č,ř,c,j,ď,ť,ň) → I. Obojetné → záleží!",
        "common_mistakes": json.dumps([
            {"wrong": "chiba", "right": "chyba", "why_cs": "Ch je tvrdá souhláska → vždy y."},
            {"wrong": "čýslo", "right": "číslo", "why_cs": "Č je měkká souhláska → vždy i."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "ch_ba — i nebo y?", "answer": "y", "options": ["i", "y"]},
            {"type": "choose", "question": "č_slo — i nebo y?", "answer": "í", "options": ["í", "ý"]},
            {"type": "choose", "question": "r_ba — i nebo y?", "answer": "y", "options": ["i", "y"]},
            {"type": "choose", "question": "ř_kat — i nebo y?", "answer": "í", "options": ["í", "ý"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Pravopis",
        "sort_order": 1,
    },
    {
        "code": "pravopis_pary_souhlasky",
        "category": "pravopis_hlasky",
        "subcategory": "párové souhlásky",
        "level": "A2",
        "title_cs": "Psaní párových souhlásek (b/p, d/t, z/s...)",
        "rule_cs": "Párové souhlásky na konci slova: píšeme podle tvaru s samohláskou. Had → hada (d). Led → ledu (d). Les → lesa (s). Dub → dubu (b).",
        "explanation_cs": "Na konci slova se znělé souhlásky vyslovují neznělé (had = [hat]), ale píšeme podle příbuzného slova s samohláskou: had → hada → píšeme d.",
        "examples": json.dumps([
            {"correct": "had (hada → d)", "incorrect": "hat", "note_cs": "Hada → d na konci."},
            {"correct": "led (ledu → d)", "incorrect": "let", "note_cs": "Ledu → d na konci."},
            {"correct": "les (lesa → s)", "incorrect": "lez", "note_cs": "Lesa → s na konci."},
            {"correct": "dub (dubu → b)", "incorrect": "dup", "note_cs": "Dubu → b na konci."}
        ]),
        "mnemonic": "Nevíš d/t, b/p, z/s? Změň tvar → přidej samohlásku: had → hada → d!",
        "common_mistakes": json.dumps([
            {"wrong": "hat", "right": "had", "why_cs": "Hada → d. Píšeme 'had', i když vyslovujeme [hat]."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "ha_ (ha-a) — d nebo t?", "answer": "d", "options": ["d", "t"]},
            {"type": "choose", "question": "le_ (le-u) — d nebo t?", "answer": "d", "options": ["d", "t"]},
            {"type": "choose", "question": "le_ (le-a) — s nebo z?", "answer": "s", "options": ["s", "z"]},
            {"type": "choose", "question": "du_ (du-u) — b nebo p?", "answer": "b", "options": ["b", "p"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Pravopis",
        "sort_order": 2,
    },
    {
        "code": "predlozky_s_z",
        "category": "pravopis_hlasky",
        "subcategory": "předložky",
        "level": "B1",
        "title_cs": "Předložky s × z",
        "rule_cs": "S + 7. pád (s kým? s čím?): s kamarádem, s mlíkem. Z + 2. pád (z čeho? odkud?): z Prahy, z domu. Pozor na chybné zaměňování!",
        "explanation_cs": "S = společnost, doprovod (s kým jdeš?). Z = směr odněkud, materiál (z čeho je?). Na povrch: ze stolu (z + 2. p.), ale se stolem (s + 7. p.).",
        "examples": json.dumps([
            {"correct": "Jdu s kamarádem. (s + 7. p.)", "incorrect": "Jdu z kamarádem.", "note_cs": "S = doprovod."},
            {"correct": "Jsem z Prahy. (z + 2. p.)", "incorrect": "Jsem s Prahy.", "note_cs": "Z = odkud."},
            {"correct": "Spadl ze stromu. (z + 2. p.)", "incorrect": "Spadl se stromu.", "note_cs": "Z = směr dolů odkud."}
        ]),
        "mnemonic": "S + 7. pád = S KÝM. Z + 2. pád = ODKUD/Z ČEHO.",
        "common_mistakes": json.dumps([
            {"wrong": "Jsem s Prahy.", "right": "Jsem z Prahy.", "why_cs": "Odkud? → z + 2. pád."},
            {"wrong": "Jdu z kamarádem.", "right": "Jdu s kamarádem.", "why_cs": "S kým? → s + 7. pád."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "Jsem ___ Prahy.", "answer": "z", "options": ["s", "z"]},
            {"type": "choose", "question": "Jdu ___ kamarádem.", "answer": "s", "options": ["s", "z"]},
            {"type": "choose", "question": "Káva ___ mlíkem.", "answer": "s", "options": ["s", "z"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Pravopis",
        "sort_order": 23,
    },
    {
        "code": "carka_pristavek",
        "category": "pravopis_interpunkce",
        "subcategory": "čárka",
        "level": "B2",
        "title_cs": "Čárka u přístavku",
        "rule_cs": "Přístavek (bližší vysvětlení) oddělujeme čárkamі z obou stran: Praha, hlavní město Česka, má milion obyvatel. Honzík, můj učitel, je trpělivý.",
        "explanation_cs": "Přístavek vysvětluje nebo upřesňuje slovo před ním. Vždy se odděluje čárkami z obou stran (nebo čárkou a tečkou na konci věty).",
        "examples": json.dumps([
            {"correct": "Praha, hlavní město Česka, je krásná.", "incorrect": "Praha hlavní město Česka je krásná.", "note_cs": "Přístavek z obou stran čárkami."},
            {"correct": "Můj bratr, lékař, pracuje v nemocnici.", "incorrect": "Můj bratr lékař pracuje v nemocnici.", "note_cs": "Přístavek 'lékař' oddělený čárkami."}
        ]),
        "mnemonic": "Přístavek = vsuvka (vysvětlení). Vždy čárky z OBOU stran!",
        "common_mistakes": json.dumps([
            {"wrong": "Praha hlavní město Česka je krásná.", "right": "Praha, hlavní město Česka, je krásná.", "why_cs": "Přístavek musí být oddělený čárkami."}
        ]),
        "exercise_data": json.dumps([
            {"type": "transform", "question": "Praha hlavní město Česka je krásná.", "answer": "Praha, hlavní město Česka, je krásná."},
            {"type": "transform", "question": "Můj bratr lékař pracuje v nemocnici.", "answer": "Můj bratr, lékař, pracuje v nemocnici."}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Interpunkce",
        "sort_order": 32,
    },
    {
        "code": "carka_osloveni",
        "category": "pravopis_interpunkce",
        "subcategory": "čárka",
        "level": "A2",
        "title_cs": "Čárka u oslovení",
        "rule_cs": "Oslovení oddělujeme čárkou: Honzíku, pojď sem! Dobrý den, paní Nováková. Paní učitelko, mohu se zeptat?",
        "explanation_cs": "Oslovenou osobu (5. pád) vždy oddělujeme čárkou od zbytku věty.",
        "examples": json.dumps([
            {"correct": "Honzíku, jak se máš?", "incorrect": "Honzíku jak se máš?", "note_cs": "Čárka za oslovením."},
            {"correct": "Pane profesore, mám otázku.", "incorrect": "Pane profesore mám otázku.", "note_cs": "Čárka za oslovením."},
            {"correct": "To je pravda, Petře.", "incorrect": "To je pravda Petře.", "note_cs": "Čárka před oslovením na konci."}
        ]),
        "mnemonic": "Oslovení (5. pád) = vždy odděleno čárkou!",
        "common_mistakes": json.dumps([
            {"wrong": "Honzíku jak se máš?", "right": "Honzíku, jak se máš?", "why_cs": "Oslovení se odděluje čárkou."}
        ]),
        "exercise_data": json.dumps([
            {"type": "transform", "question": "Honzíku jak se máš?", "answer": "Honzíku, jak se máš?"},
            {"type": "transform", "question": "Pane profesore mám otázku.", "answer": "Pane profesore, mám otázku."},
            {"type": "transform", "question": "To je pravda Petře.", "answer": "To je pravda, Petře."}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Interpunkce",
        "sort_order": 33,
    },
    {
        "code": "podstatna_vzor_hrad",
        "category": "tvaroslovi_podstatna",
        "subcategory": "skloňování",
        "level": "A1",
        "title_cs": "Vzor 'hrad' (mužský neživotný)",
        "rule_cs": "Podstatná jména mužského rodu neživotná na tvrdou souhlásku se skloňují podle vzoru 'hrad': hrad → hradu (2. p.), hradu (3. p.), hrad (4. p. = 1. p.).",
        "explanation_cs": "Vzor hrad: 1.p. hrad, 2.p. hradu, 3.p. hradu, 4.p. hrad, 5.p. hrade!, 6.p. o hradu/hradě, 7.p. hradem. U neživotných: 4. p. = 1. p. (vidím hrad, ne hradu).",
        "examples": json.dumps([
            {"correct": "Vidím hrad. (4. p. = 1. p.)", "incorrect": "Vidím hradu.", "note_cs": "Neživotný: 4. p = 1. p."},
            {"correct": "Bydlím u hradu. (2. p.)", "incorrect": "Bydlím u hrad.", "note_cs": "2. pád: -u."},
            {"correct": "Jedu do obchodu. (2. p.)", "incorrect": "Jedu do obchod.", "note_cs": "Vzor hrad → obchod: obchodu."}
        ]),
        "mnemonic": "Vzor HRAD: neživotný → 4. pád = 1. pád (vidím hrad). 2. pád: -u.",
        "common_mistakes": json.dumps([
            {"wrong": "Vidím hradu.", "right": "Vidím hrad.", "why_cs": "Neživotné: 4. pád = 1. pád."}
        ]),
        "exercise_data": json.dumps([
            {"type": "fill_gap", "question": "Jedu do ___. (obchod, 2. p.)", "answer": "obchodu"},
            {"type": "fill_gap", "question": "Vidím ___. (hrad, 4. p.)", "answer": "hrad"},
            {"type": "choose", "question": "U neživotných jmen: 4. pád je:", "answer": "stejný jako 1. pád", "options": ["stejný jako 1. pád", "stejný jako 2. pád"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 55,
    },
    {
        "code": "slovesa_budouci_cas",
        "category": "tvaroslovi_slovesa",
        "subcategory": "budoucí čas",
        "level": "A2",
        "title_cs": "Budoucí čas",
        "rule_cs": "Budoucí čas — dva způsoby: 1) Nedokonavá: budu + infinitiv (budu dělat, budu psát). 2) Dokonavá: přítomný tvar = budoucí (napíšu, udělám, přečtu).",
        "explanation_cs": "Budu/budeš/bude/budeme/budete/budou + infinitiv pro nedokonavá. Dokonavá slovesa nemají přítomný čas — jejich 'přítomný' tvar je automaticky budoucí.",
        "examples": json.dumps([
            {"correct": "Budu studovat. (nedok.)", "incorrect": "Budu studuju.", "note_cs": "Budu + infinitiv (ne přítomný tvar)."},
            {"correct": "Napíšu ti zítra. (dok. = budoucí)", "incorrect": "Budu napsat.", "note_cs": "Dokonavé → tvar 'napíšu' = budoucí čas."},
            {"correct": "Budeme cestovat. (nedok.)", "incorrect": "Budem cestovat.", "note_cs": "Spisovně: budeme (ne 'budem')."}
        ]),
        "mnemonic": "Nedokonavé: BUDU + infinitiv. Dokonavé: přítomný tvar = budoucí.",
        "common_mistakes": json.dumps([
            {"wrong": "Budu napsat.", "right": "Napíšu.", "why_cs": "Budu + dok. infinitiv je CHYBA. Řekni prostě 'napíšu'."},
            {"wrong": "Budu dělám.", "right": "Budu dělat.", "why_cs": "Budu + infinitiv (dělat), ne přítomný tvar (dělám)."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "Zítra ___ česky. (studovat, nedok.)", "answer": "budu studovat", "options": ["budu studovat", "studuji", "budu studuju"]},
            {"type": "choose", "question": "Zítra ti to ___. (napsat, dok.)", "answer": "napíšu", "options": ["budu napsat", "napíšu", "budu napíšu"]},
            {"type": "fill_gap", "question": "Zítra ___ do školy. (jít, nedok.)", "answer": "budu chodit|půjdu"}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 86,
    },
    {
        "code": "podstatna_pluraly",
        "category": "tvaroslovi_podstatna",
        "subcategory": "množné číslo",
        "level": "A2",
        "title_cs": "Množné číslo podstatných jmen",
        "rule_cs": "Množné číslo závisí na rodu a vzoru. Muž. živ.: student → studenti, muž → muži. Muž. neživ.: hrad → hrady. Žen.: žena → ženy, růže → růže. Stř.: město → města, moře → moře.",
        "explanation_cs": "Pozor na nepravidelnosti: dítě → děti, člověk → lidé, rok → roky i léta, přítel → přátelé. Některá jména existují jen v mn. č.: dveře, nůžky, kalhoty.",
        "examples": json.dumps([
            {"correct": "studenti (muž. živ. mn.)", "incorrect": "studenty", "note_cs": "Muž. životný → -i v 1. pádu mn. č."},
            {"correct": "děti (nepravidelné)", "incorrect": "dítěta", "note_cs": "Dítě → děti (nepravidelné)."},
            {"correct": "lidé (nepravidelné)", "incorrect": "člověky", "note_cs": "Člověk → lidé (supletivní tvar)."},
            {"correct": "města (stř. mn.)", "incorrect": "městy", "note_cs": "Střední rod → -a v mn. č."}
        ]),
        "mnemonic": "Zapamatuj nepravidelné: dítě→děti, člověk→lidé, rok→léta/roky.",
        "common_mistakes": json.dumps([
            {"wrong": "člověky", "right": "lidé / lidi", "why_cs": "Člověk → lidé (1. p. mn.). Neexistuje *člověky."}
        ]),
        "exercise_data": json.dumps([
            {"type": "fill_gap", "question": "Mn. č. od 'student':", "answer": "studenti"},
            {"type": "fill_gap", "question": "Mn. č. od 'dítě':", "answer": "děti"},
            {"type": "fill_gap", "question": "Mn. č. od 'člověk':", "answer": "lidé|lidi"},
            {"type": "fill_gap", "question": "Mn. č. od 'město':", "answer": "města"}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Tvarosloví",
        "sort_order": 56,
    },
    {
        "code": "predlozky_v_na",
        "category": "skladba",
        "subcategory": "předložky",
        "level": "A2",
        "title_cs": "Předložky v × na (místo)",
        "rule_cs": "V = uvnitř uzavřeného prostoru: v domě, v kině, v Praze. Na = na povrchu nebo u konkrétních míst: na stole, na poště, na Moravě, na koncertě.",
        "explanation_cs": "Některá místa tradičně s 'na': na poště, na úřadě, na nádraží, na letišti, na Moravě, na Slovensku. S 'v': v Praze, v Brně, v divadle, v obchodě.",
        "examples": json.dumps([
            {"correct": "v Praze, v kině, v obchodě", "incorrect": "na Praze, na kině", "note_cs": "V = uvnitř města, budovy."},
            {"correct": "na poště, na úřadě, na nádraží", "incorrect": "v poště, v úřadě", "note_cs": "Na = tradičně u těchto míst."},
            {"correct": "na Slovensku, na Moravě", "incorrect": "v Slovensku, v Moravě", "note_cs": "Na = u regionů/zemí (tradice)."}
        ]),
        "mnemonic": "V = uvnitř (v domě). Na = povrch nebo tradice (na poště, na Moravě).",
        "common_mistakes": json.dumps([
            {"wrong": "v poště", "right": "na poště", "why_cs": "Pošta tradičně s 'na'."},
            {"wrong": "v Slovensku", "right": "na Slovensku", "why_cs": "Slovensko tradičně s 'na'."}
        ]),
        "exercise_data": json.dumps([
            {"type": "choose", "question": "___ Praze", "answer": "v", "options": ["v", "na"]},
            {"type": "choose", "question": "___ poště", "answer": "na", "options": ["v", "na"]},
            {"type": "choose", "question": "___ Slovensku", "answer": "na", "options": ["v", "na"]},
            {"type": "choose", "question": "___ kině", "answer": "v", "options": ["v", "na"]}
        ]),
        "source_ref": "prirucka.ujc.cas.cz — Skladba",
        "sort_order": 102,
    },
]


# ═══════════════════════════════════════════════════════════════════


async def seed_grammar_rules():
    """Seed grammar rules into database."""
    print(f"🌱 Seeding {len(GRAMMAR_RULES)} grammar rules...")

    await init_db()

    async with AsyncSessionLocal() as session:
        inserted = 0
        updated = 0

        for rule_data in GRAMMAR_RULES:
            # Check if rule already exists
            from sqlalchemy import select
            result = await session.execute(
                select(GrammarRule).where(GrammarRule.code == rule_data["code"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing rule
                for key, value in rule_data.items():
                    if key != "code":
                        setattr(existing, key, value)
                updated += 1
            else:
                # Insert new rule
                rule = GrammarRule(**rule_data)
                session.add(rule)
                inserted += 1

        await session.commit()

    print(f"✅ Done! Inserted: {inserted}, Updated: {updated}")
    print(f"📊 Total rules in seed: {len(GRAMMAR_RULES)}")

    # Print category breakdown
    categories = {}
    for rule in GRAMMAR_RULES:
        cat = rule["category"]
        categories[cat] = categories.get(cat, 0) + 1

    print("\n📋 Breakdown by category:")
    for cat, count in sorted(categories.items()):
        print(f"   {cat}: {count}")


if __name__ == "__main__":
    asyncio.run(seed_grammar_rules())
