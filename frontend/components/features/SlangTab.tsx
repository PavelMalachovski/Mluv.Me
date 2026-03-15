"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ChevronDown, ChevronUp, Search } from "lucide-react"

// ===== Data =====

interface SlangItem {
  phrase: string
  meaning: string
  example: string
}

interface SlangCategory {
  id: string
  title: string
  emoji: string
  items: SlangItem[]
}

const SLANG_CATEGORIES: SlangCategory[] = [
  {
    id: "people",
    title: "Lidé a povaha",
    emoji: "👥",
    items: [
      {
        phrase: "Být mimo mísu",
        meaning: "Být zmatený, nechápat situaci.",
        example: "Zase je úplně mimo mísu, vůbec neví, o čem se bavíme.",
      },
      {
        phrase: "Mít pod čepicí",
        meaning: "Být chytrý, mazaný.",
        example: "Ten kluk má pod čepicí, všechno hned pochopí.",
      },
      {
        phrase: "Dělat z komára velblouda",
        meaning: "Zveličovat problém.",
        example: "Zase děláš z komára velblouda, nic hrozného se nestalo.",
      },
      {
        phrase: "Mít hroší kůži",
        meaning: "Být necitlivý vůči kritice, nestydět se.",
        example: "Politici musí mít hroší kůži.",
      },
      {
        phrase: "Házet flintu do žita",
        meaning: "Vzdat se, ztratit naději.",
        example: "Nevzdávej to, neházej flintu do žita!",
      },
      {
        phrase: "Kápo",
        meaning: "Šéf, vedoucí (slang).",
        example: "Zeptej se kápa, jestli můžeme odejít dřív.",
      },
      {
        phrase: "Hustej",
        meaning: "Skvělý, úžasný, nebo naopak drsný (slang).",
        example: "To je hustej film!",
      },
      {
        phrase: "Být na plech",
        meaning: "Být velmi opilý.",
        example: "Včera na té oslavě byl úplně na plech.",
      },
      {
        phrase: "Kecat",
        meaning: "Lhát nebo mluvit o ničem.",
        example: "Nekecej, to ti nevěřím!",
      },
      {
        phrase: "Buchta",
        meaning: "Atraktivní dívka (slang).",
        example: "Podívej na tu buchtu u baru.",
      },
    ],
  },
  {
    id: "work-money",
    title: "Práce a peníze",
    emoji: "💰",
    items: [
      {
        phrase: "Mít hluboko do kapsy",
        meaning: "Mít málo peněz.",
        example: "Před výplatou mám vždycky hluboko do kapsy.",
      },
      {
        phrase: "Zlaté české ručičky",
        meaning: "Ocenění zručnosti a šikovnosti.",
        example: "Opravil to úplně sám, zkrátka zlaté české ručičky.",
      },
      {
        phrase: "Zadarmo ani kuře nehrabe",
        meaning: "Nic není zadarmo.",
        example: "Musíš mu za tu pomoc zaplatit, zadarmo ani kuře nehrabe.",
      },
      {
        phrase: "Makáč",
        meaning: "Člověk, který hodně a tvrdě pracuje.",
        example: "Pavel je neskutečný makáč, dělá i o víkendech.",
      },
      {
        phrase: "Prachy / Kačky",
        meaning: "Peníze (slang).",
        example: "Máš u sebe nějaký prachy?",
      },
      {
        phrase: "Meloun",
        meaning: "Milion korun (slang).",
        example: "To auto stojí přes meloun.",
      },
      {
        phrase: "Kilo",
        meaning: "Sto korun (slang).",
        example: "Půjčíš mi kilo do zítřka?",
      },
      {
        phrase: "Litr",
        meaning: "Tisíc korun (slang).",
        example: "Ta bunda stála dva litry.",
      },
      {
        phrase: "Flákat se",
        meaning: "Nic nedělat, vyhýbat se práci.",
        example: "Přestaň se flákat a pojď mi pomoct.",
      },
      {
        phrase: "Dřít jako kůň",
        meaning: "Velmi tvrdě pracovat.",
        example: "Dřu jako kůň, a stejně nemám peníze.",
      },
    ],
  },
  {
    id: "emotions",
    title: "Emoce a stavy",
    emoji: "😤",
    items: [
      {
        phrase: "Mít nervy nadranc",
        meaning: "Být velmi nervózní, vyčerpaný.",
        example: "Z těch zkoušek mám už nervy nadranc.",
      },
      {
        phrase: "Být v sedmém nebi",
        meaning: "Být extrémně šťastný.",
        example: "Když dostala ten dárek, byla v sedmém nebi.",
      },
      {
        phrase: "Mít knedlík v krku",
        meaning: "Nemoci mluvit dojetím nebo smutkem.",
        example: "Když se loučili na letišti, měl knedlík v krku.",
      },
      {
        phrase: "Sypat si popel na hlavu",
        meaning: "Přiznat svou chybu a litovat jí.",
        example: "Uvědomil si, co udělal, a teď si sype popel na hlavu.",
      },
      {
        phrase: "Vyletět z kůže",
        meaning: "Velmi se rozzlobit.",
        example: "Když viděl ten nepořádek, myslel, že vyletí z kůže.",
      },
      {
        phrase: "Depka",
        meaning: "Deprese, špatná nálada (slang).",
        example: "Dneska mám nějakou depku, venku prší.",
      },
      {
        phrase: "Vytočit někoho",
        meaning: "Naštvat někoho.",
        example: "Jeho arogance mě dokáže vždycky spolehlivě vytočit.",
      },
      {
        phrase: "Být v háji / v prčicích",
        meaning: "Být ve špatné situaci (slušnější forma).",
        example: "Ujel mi poslední vlak, jsem v háji.",
      },
      {
        phrase: "Mít okno",
        meaning: "Nic si nepamatovat (např. po opilosti nebo u zkoušky).",
        example: "Když se mě učitel zeptal, měl jsem úplné okno.",
      },
      {
        phrase: "Spadnout kámen ze srdce",
        meaning: "Pocítit obrovskou úlevu.",
        example: "Když mi zavolali, že je v pořádku, spadl mi kámen ze srdce.",
      },
    ],
  },
  {
    id: "daily",
    title: "Činnosti a každodenní situace",
    emoji: "🏠",
    items: [
      {
        phrase: "Tahání za nos",
        meaning: "Klamat někoho, lhát mu.",
        example: "Už mě nebaví, jak mě taháš za nos.",
      },
      {
        phrase: "Koupit zajíce v pytli",
        meaning: "Koupit něco, aniž by to člověk předem viděl.",
        example: "To auto jsem si měl raději prohlédnout, koupil jsem zajíce v pytli.",
      },
      {
        phrase: "Mazat někomu med kolem huby",
        meaning: "Lichotit někomu s neupřímnými úmysly.",
        example: "Nemaž mi med kolem huby a řekni pravdu.",
      },
      {
        phrase: "Hodit něco za hlavu",
        meaning: "Přestat se něčím trápit, ignorovat to.",
        example: "Ty pomluvy musíš prostě hodit za hlavu.",
      },
      {
        phrase: "Píchat do vosího hnízda",
        meaning: "Otevírat nepříjemné téma.",
        example: "Neměl ses ho na tu výpověď ptát, zbytečně pícháš do vosího hnízda.",
      },
      {
        phrase: "Chcípl tam pes",
        meaning: "O místě, kde je nuda a nic se tam neděje.",
        example: "V té vesnici fakt chcípl pes, není tam ani hospoda.",
      },
      {
        phrase: "Jít na jedno",
        meaning: "Jít na pivo (často to nezůstane u jednoho).",
        example: "Pojďme večer do hospody na jedno.",
      },
      {
        phrase: "Dát si do nosu",
        meaning: "Dobře a hodně se najíst.",
        example: "Na té oslavě jsme si teda pořádně dali do nosu.",
      },
      {
        phrase: "Vykašlat se na něco",
        meaning: "Ignorovat něco, nedělat to.",
        example: "Já se na ten úklid asi vykašlu.",
      },
      {
        phrase: "Tlačit na pilu",
        meaning: "Příliš se snažit, naléhat na někoho.",
        example: "Netlač na pilu, on se rozhodne sám.",
      },
    ],
  },
  {
    id: "common-slang",
    title: "Běžný slang a zkráceniny",
    emoji: "💬",
    items: [
      {
        phrase: "Pohoda / V pohodě",
        meaning: "Všechno je v pořádku, bez problému.",
        example: "Zítra přijdu o trochu později. – V pohodě.",
      },
      {
        phrase: "Trapas",
        meaning: "Trapná situace.",
        example: "To byl ale trapas, když jsem zapomněl její jméno!",
      },
      {
        phrase: "Kámoš / Kámo",
        meaning: "Kamarád.",
        example: "Tohle je můj nejlepší kámoš z dětství.",
      },
      {
        phrase: "Srandy kopec",
        meaning: "Velká legrace.",
        example: "S ním je vždycky srandy kopec.",
      },
      {
        phrase: "Pecka",
        meaning: "Něco vynikajícího, skvělého.",
        example: "Ten nový telefon je fakt pecka.",
      },
      {
        phrase: "Mrtě",
        meaning: "Hodně, velké množství.",
        example: "Na koncertě bylo mrtě lidí.",
      },
      {
        phrase: "Socka",
        meaning: "Městská hromadná doprava (slang), nebo nadávka.",
        example: "Dneska jedu sockou, auto je v servisu.",
      },
      {
        phrase: "Cígo",
        meaning: "Cigareta.",
        example: "Jdu ven na cígo.",
      },
      {
        phrase: "Komp",
        meaning: "Počítač.",
        example: "Zase se mi sekl komp.",
      },
      {
        phrase: "No jo",
        meaning: "Univerzální fráze pro souhlas, rezignaci nebo zamyšlení.",
        example: "No jo, co se dá dělat.",
      },
    ],
  },
  {
    id: "animals",
    title: "Zvířecí idiomy",
    emoji: "🐾",
    items: [
      {
        phrase: "Zabít dvě mouchy jednou ranou",
        meaning: "Vyřešit dva problémy jedním činem.",
        example: "Když půjdeš pro chleba, vyhoď i odpadky, zabiješ dvě mouchy jednou ranou.",
      },
      {
        phrase: "Koukat jako sůva z nudlí",
        meaning: "Dívat se vyjeveně, překvapeně.",
        example: "Nekoukej na mě jako sůva z nudlí a řekni něco.",
      },
      {
        phrase: "Mlčeti zlato",
        meaning: "Někdy je lepší nic neříkat.",
        example: "Měl jsem mu to oplatit, ale řekl jsem si: Mluviti stříbro, mlčeti zlato.",
      },
      {
        phrase: "Lije jako z konve",
        meaning: "Velmi silně prší.",
        example: "Zůstaneme doma, venku lije jako z konve.",
      },
      {
        phrase: "Je zima jako v psírně",
        meaning: "Je obrovská zima.",
        example: "Zavři to okno, je tu zima jako v psírně.",
      },
      {
        phrase: "Mít vlčí mhu",
        meaning: "Nevidět něco, co je zjevné.",
        example: "Já ty klíče fakt nevidím, mám asi vlčí mhu.",
      },
      {
        phrase: "Hladový jako vlk",
        meaning: "Mít obrovský hlad.",
        example: "Dej mi něco k jídlu, jsem hladový jako vlk.",
      },
      {
        phrase: "Spát jako dudek",
        meaning: "Spát tvrdě a klidně.",
        example: "Po tom výletě jsem spal jako dudek.",
      },
      {
        phrase: "Chodit spát se slepicemi",
        meaning: "Chodit spát velmi brzy.",
        example: "Můj děda chodí spát se slepicemi.",
      },
      {
        phrase: "Jako slon v porcelánu",
        meaning: "Chovat se neobratně.",
        example: "Pohybuje se tam jako slon v porcelánu, všechno shodí.",
      },
    ],
  },
  {
    id: "modern",
    title: "Moderní hovorová čeština",
    emoji: "🗣️",
    items: [
      {
        phrase: "Fízl",
        meaning: "Policista (hanlivě).",
        example: "Bacha, jedou fízlové.",
      },
      {
        phrase: "Vole",
        meaning: "Původně nadávka, dnes univerzální vycpávkové slovo (jako 'člověče').",
        example: "To je fakt síla, vole.",
      },
      {
        phrase: "Ty jo / Ty kráso",
        meaning: "Výraz překvapení nebo údivu.",
        example: "Ty jo, to jsem vůbec nečekal!",
      },
      {
        phrase: "Dostat kopačky",
        meaning: "Být opuštěn partnerem.",
        example: "Karel včera dostal od Jany kopačky.",
      },
      {
        phrase: "Mít rande",
        meaning: "Mít schůzku (romantickou).",
        example: "Dneska večer mám rande s Tomášem.",
      },
      {
        phrase: "Baštit",
        meaning: "Jíst s chutí, nebo věřit lži (baštit někomu něco).",
        example: "Dítě krásně baštilo. / Ty mu ty lži fakt baštíš?",
      },
      {
        phrase: "Brnknout",
        meaning: "Zatelefonovat.",
        example: "Zítra ti brnknu a domluvíme se.",
      },
      {
        phrase: "Šprt",
        meaning: "Žák, který se pořád jen učí (hanlivě).",
        example: "Pavel je hrozný šprt, má samé jedničky.",
      },
      {
        phrase: "Zdrhnout",
        meaning: "Utéct.",
        example: "Musíme odsud rychle zdrhnout.",
      },
      {
        phrase: "Šluknout si",
        meaning: "Potáhnout z cigarety.",
        example: "Dáš mi šluknout?",
      },
    ],
  },
  {
    id: "relationships",
    title: "Vztahy a charakter",
    emoji: "❤️",
    items: [
      {
        phrase: "Mít srdce na pravém místě",
        meaning: "Být hodný a laskavý.",
        example: "Je sice trochu drsný, ale má srdce na pravém místě.",
      },
      {
        phrase: "Být páté kolo u vozu",
        meaning: "Být někde navíc, nechtěný.",
        example: "Šli do kina jako pár a já tam byl jen jako páté kolo u vozu.",
      },
      {
        phrase: "Padnout si do oka",
        meaning: "Zalíbit se jeden druhému hned na začátku.",
        example: "Hned na prvním rande si padli do oka.",
      },
      {
        phrase: "Lézt někomu na nervy",
        meaning: "Rozčilovat někoho.",
        example: "Už mi s tím tvým stěžováním lezeš na nervy.",
      },
      {
        phrase: "Držet palce",
        meaning: "Přát někomu štěstí.",
        example: "Zítra máš zkoušku? Budu ti držet palce!",
      },
      {
        phrase: "Pustit k vodě",
        meaning: "Rozejít se s někým, ukončit vztah.",
        example: "Po měsíci ho pustila k vodě.",
      },
      {
        phrase: "Zabouchnout se (do někoho)",
        meaning: "Zamilovat se (slang).",
        example: "Úplně se do ní zabouchnul.",
      },
      {
        phrase: "Mít někoho plné zuby",
        meaning: "Být z někoho otrávený, mít někoho dost.",
        example: "Mám toho tvého chování už plné zuby.",
      },
      {
        phrase: "Házet klacky pod nohy",
        meaning: "Dělat někomu úmyslně problémy.",
        example: "Místo aby mi pomohli, jen mi hází klacky pod nohy.",
      },
      {
        phrase: "Jít přes mrtvoly",
        meaning: "Být bezohledný při dosahování svého cíle.",
        example: "V byznysu jde tvrdě přes mrtvoly.",
      },
    ],
  },
  {
    id: "proverbs",
    title: "Česká přísloví a rčení",
    emoji: "📜",
    items: [
      {
        phrase: "Ráno moudřejší večera",
        meaning: "Je lepší nechat rozhodnutí na další den.",
        example: "Jdi spát, ráno moudřejší večera.",
      },
      {
        phrase: "Kdo se ptá, moc se dozví",
        meaning: "Někdy je lepší se na určité věci neptat.",
        example: "Radši do toho nerýpej, kdo se ptá, moc se dozví.",
      },
      {
        phrase: "Tichá voda břehy mele",
        meaning: "Tichý člověk může překvapit (v dobrém i zlém).",
        example: "Vypadá nenápadně, ale tichá voda břehy mele.",
      },
      {
        phrase: "Bez práce nejsou koláče",
        meaning: "Abys něčeho dosáhl, musíš se snažit.",
        example: "Musíš se víc učit, bez práce nejsou koláče.",
      },
      {
        phrase: "Komu není rady, tomu není pomoci",
        meaning: "Kdo nechce poslouchat dobré rady, ponese následky.",
        example: "Když mě nechceš poslouchat, tvoje chyba. Komu není rady, tomu není pomoci.",
      },
      {
        phrase: "Všude dobře, doma nejlíp",
        meaning: "Doma je to nejlepší.",
        example: "Dovolená byla super, ale všude dobře, doma nejlíp.",
      },
      {
        phrase: "Jablko nepadá daleko od stromu",
        meaning: "Děti se chovají podobně jako rodiče.",
        example: "Je stejně tvrdohlavý jako jeho otec, jablko nepadá daleko od stromu.",
      },
      {
        phrase: "Dvakrát měř, jednou řež",
        meaning: "Dobře si vše rozmysli, než začneš jednat.",
        example: "Než tu smlouvu podepíšeš, dvakrát měř, jednou řež.",
      },
      {
        phrase: "Kdo dřív přijde, ten dřív mele",
        meaning: "Kdo je rychlejší, získá výhodu.",
        example: "Lístky na koncert už nejsou, kdo dřív přijde, ten dřív mele.",
      },
      {
        phrase: "Darovanému koni na zuby nekoukej",
        meaning: "Dary by se neměly kritizovat.",
        example: "Možná se ti to tričko nelíbí, ale darovanému koni na zuby nekoukej.",
      },
    ],
  },
  {
    id: "misc-slang",
    title: "Různé slangové výrazy",
    emoji: "🔥",
    items: [
      {
        phrase: "Mám to na háku",
        meaning: "Je mi to jedno.",
        example: "Zítřejší písemku mám úplně na háku.",
      },
      {
        phrase: "Hrotit to",
        meaning: "Přehánět něco, příliš něco prožívat.",
        example: "Nehroť to tolik, vždyť o nic nejde.",
      },
      {
        phrase: "Vychytávka",
        meaning: "Chytrý detail, zlepšovák.",
        example: "Tahle aplikace má super vychytávky.",
      },
      {
        phrase: "Haluz",
        meaning: "Štěstí, nebo něco velmi zvláštního/divného.",
        example: "To byla úplná haluz, že jsem tu zkoušku udělal.",
      },
      {
        phrase: "Mazec",
        meaning: "Něco intenzivního, šíleného (pozitivně i negativně).",
        example: "Ten včerejší zápas, to byl fakt mazec!",
      },
      {
        phrase: "To nedáš",
        meaning: "To nezvládneš.",
        example: "Tenhle kopec na kole nedáš.",
      },
      {
        phrase: "Rozsekat někoho",
        meaning: "Zničit (v argumentaci) nebo rozesmát k slzám.",
        example: "Ten jeho vtip mě úplně rozsekal.",
      },
      {
        phrase: "Být za vodou",
        meaning: "Mít vyděláno, být finančně zajištěný nebo mít po starostech.",
        example: "Pokud vyhraju v loterii, jsem do konce života za vodou.",
      },
      {
        phrase: "Bordel",
        meaning: "Nepořádek, nebo zmatek.",
        example: "Uklid si ten bordel v pokoji!",
      },
      {
        phrase: "Mít z pekla štěstí",
        meaning: "Mít obrovské štěstí v nebezpečné nebo těžké situaci.",
        example: "Měl z pekla štěstí, že to auto stihlo zabrzdit.",
      },
    ],
  },
  {
    id: "physical",
    title: "Fyzické stavy a tělo",
    emoji: "💪",
    items: [
      {
        phrase: "Dát si dvacet",
        meaning: "Krátce se vyspat, zdřímnout si.",
        example: "Jsem unavený, jdu si po obědě dát dvacet.",
      },
      {
        phrase: "Chytat lelky",
        meaning: "Nudit se, nic nedělat, koukat do blba.",
        example: "Přestaň chytat lelky a začni se učit!",
      },
      {
        phrase: "Mít obě ruce levé",
        meaning: "Být velmi nešikovný.",
        example: "Na opravu auta ho nevolej, má obě ruce levé.",
      },
      {
        phrase: "Padat na hubu",
        meaning: "Být extrémně vyčerpaný.",
        example: "Po té dvanáctihodinové směně úplně padám na hubu.",
      },
      {
        phrase: "Mít husí kůži",
        meaning: "Bát se, nebo mít z něčeho silný (i pozitivní) zážitek.",
        example: "Když začala zpívat, měl jsem úplně husí kůži.",
      },
      {
        phrase: "Být kost a kůže",
        meaning: "Být velmi hubený.",
        example: "Po té nemoci je úplně kost a kůže.",
      },
      {
        phrase: "Vyplivnout duši",
        meaning: "Velmi se fyzicky unavit (např. při sportu).",
        example: "Běželi jsme do takového kopce, že jsem myslel, že vyplivnu duši.",
      },
      {
        phrase: "Mít jazyk na vestě",
        meaning: "Být uhnaný, zadýchaný a unavený.",
        example: "Doběhl na tramvaj na poslední chvíli a měl jazyk na vestě.",
      },
      {
        phrase: "Mít roupy",
        meaning: "Být neposedný, vymýšlet hlouposti (často o dětech).",
        example: "Ty děti dneska mají zase roupy.",
      },
      {
        phrase: "Mátoha",
        meaning: "Unavený člověk bez energie, který se vleče.",
        example: "Ráno před kávou jsem úplná mátoha.",
      },
    ],
  },
  {
    id: "communication",
    title: "Komunikace a mluvení",
    emoji: "🗨️",
    items: [
      {
        phrase: "Plácat játra",
        meaning: "Mluvit nesmysly, říkat hlouposti.",
        example: "Už neplácej játra a řekni mi, jak to doopravdy bylo.",
      },
      {
        phrase: "Chodit kolem horké kaše",
        meaning: "Vyhýbat se přímé odpovědi nebo hlavnímu tématu.",
        example: "Nechoď kolem horké kaše a řekni mi rovnou, co chceš.",
      },
      {
        phrase: "Mít prořízlou pusu",
        meaning: "Být velmi výřečný, často až drze.",
        example: "Ta tvoje sestra má docela prořízlou pusu.",
      },
      {
        phrase: "Zdrbávat někoho",
        meaning: "Pomlouvat někoho za jeho zády.",
        example: "Holky se sešly na kávu a celou dobu jen někoho zdrbávaly.",
      },
      {
        phrase: "Vykecat se z něčeho",
        meaning: "Najít si dobrou výmluvu.",
        example: "Přišel pozdě, ale zase se z toho mistrně vykecal.",
      },
      {
        phrase: "Házet hrách na zeď / Mluvit do zdi",
        meaning: "Zbytečně někomu něco vysvětlovat.",
        example: "Říkám mu to stokrát, ale je to jako házet hrách na zeď.",
      },
      {
        phrase: "Držet jazyk za zuby",
        meaning: "Mlčet, neprozradit tajemství.",
        example: "Slib mi, že o tom budeš držet jazyk za zuby.",
      },
      {
        phrase: "Mít kecy",
        meaning: "Zbytečně a nevhodně komentovat situaci, stěžovat si.",
        example: "Udělej to, co jsem ti řekl, a neměj furt kecy.",
      },
      {
        phrase: "Žvanit",
        meaning: "Hodně a zbytečně mluvit.",
        example: "Ten chlap pořád jenom žvaní a skutek utek.",
      },
      {
        phrase: "Vyslepičit něco",
        meaning: "Vyzradit tajemství (jako slepice).",
        example: "Hned jak to zjistila, běžela to všem vyslepičit.",
      },
    ],
  },
  {
    id: "mistakes",
    title: "Zklamání, chyby a problémy",
    emoji: "⚠️",
    items: [
      {
        phrase: "Šlápnout vedle",
        meaning: "Udělat chybu v rozhodnutí.",
        example: "S touhle investicí jsme docela šlápli vedle.",
      },
      {
        phrase: "Zvorat něco",
        meaning: "Úplně něco zkazit (slang).",
        example: "Tuhle zkoušku jsem fakt zvorala.",
      },
      {
        phrase: "Dostat kartáč / čočku",
        meaning: "Dostat od někoho silně vynadáno.",
        example: "Když jsem přišel pozdě do práce, dostal jsem od šéfa pořádný kartáč.",
      },
      {
        phrase: "Průšvih",
        meaning: "Velký problém, malér.",
        example: "Ztratil jsem firemní notebook, to je obrovský průšvih.",
      },
      {
        phrase: "Nalítnout někomu",
        meaning: "Nechat se hloupě oklamat.",
        example: "Nalítnul podvodníkům na internetu a poslal jim peníze.",
      },
      {
        phrase: "Být namydlený",
        meaning: "Být v bezvýchodné situaci.",
        example: "Jestli ten vlak zruší, jsme úplně namydlení.",
      },
      {
        phrase: "Zpívat jinou písničku",
        meaning: "Najednou změnit názor (většinou pod tlakem).",
        example: "Až zjistí, kolik to stojí, bude zpívat jinou písničku.",
      },
      {
        phrase: "Dostat po čumáku",
        meaning: "Utrpět porážku, neuspět a poučit se.",
        example: "Byl moc sebevědomý, ale u zkoušek dostal pěkně po čumáku.",
      },
      {
        phrase: "Zabalit to",
        meaning: "Vzdat se, ukončit činnost.",
        example: "Už mě ta práce nebaví, asi to tady zabalím.",
      },
      {
        phrase: "Jít ke dnu",
        meaning: "Krachovat, upadat.",
        example: "Jeho firma pomalu ale jistě jde ke dnu.",
      },
    ],
  },
  {
    id: "time-speed",
    title: "Čas a rychlost",
    emoji: "⏰",
    items: [
      {
        phrase: "Dát si na čas",
        meaning: "Nespěchat, úmyslně něco dělat pomalu.",
        example: "S tím úkolem si teda dal docela na čas.",
      },
      {
        phrase: "Za pět minut dvanáct",
        meaning: "Na úplně poslední chvíli.",
        example: "Odevzdal tu práci za pět minut dvanáct.",
      },
      {
        phrase: "Být v presu",
        meaning: "Být pod časovým tlakem.",
        example: "Nezavolala jsem ti, protože jsem byla celý den hrozně v presu.",
      },
      {
        phrase: "Zabít čas",
        meaning: "Dělat něco jen proto, aby čas uběhl.",
        example: "Čekám na vlak a hraju hry na mobilu, abych zabil čas.",
      },
      {
        phrase: "Nestíhat",
        meaning: "Mít zpoždění, nemít na něco čas.",
        example: "Promiň, ale tu schůzku dneska vůbec nestíhám.",
      },
      {
        phrase: "Trvat celou věčnost",
        meaning: "Trvat extrémně dlouho.",
        example: "Než se ta tvoje sestra obleče, trvá to celou věčnost.",
      },
      {
        phrase: "Co nevidět",
        meaning: "Brzy, zanedlouho.",
        example: "Autobus už tu musí být co nevidět.",
      },
      {
        phrase: "Jednou za uherský rok",
        meaning: "Velmi zřídka, téměř nikdy.",
        example: "Do divadla chodíme jen jednou za uherský rok.",
      },
      {
        phrase: "Zmeškat vlak",
        meaning: "Propásnout důležitou životní příležitost.",
        example: "S touhle nabídkou jsi už zmeškal vlak.",
      },
      {
        phrase: "Hoří to / Nehoří to",
        meaning: "Je to velmi naléhavé / Nespěchá to.",
        example: "Klidně si ten e-mail přečti až zítra, nehoří to.",
      },
    ],
  },
  {
    id: "money2",
    title: "Peníze a majetek 2",
    emoji: "💸",
    items: [
      {
        phrase: "Být ve vatě",
        meaning: "Být velmi bohatý, zabezpečený.",
        example: "Její rodina je docela ve vatě, peníze řešit nemusí.",
      },
      {
        phrase: "Nekoupit ani za zlaté prase",
        meaning: "V žádném případě něco nekoupit, vůbec to nechtít.",
        example: "Tyhle ošklivé boty bych si nekoupil ani za zlaté prase.",
      },
      {
        phrase: "Pustit chlup",
        meaning: "Utratit peníze, neochotně zaplatit.",
        example: "Budeme muset na tu opravu pustit chlup.",
      },
      {
        phrase: "Stát za starou bačkoru",
        meaning: "Být k ničemu, mít mizernou kvalitu.",
        example: "Ten film stál za starou bačkoru.",
      },
      {
        phrase: "Vyhodit peníze oknem",
        meaning: "Zbytečně utratit peníze za hloupost.",
        example: "Koupit takhle drahé auto je jako vyhodit peníze oknem.",
      },
      {
        phrase: "Mít z něčeho rito",
        meaning: "Mít z něčeho dobrý zisk.",
        example: "Na tomhle obchodu udělal slušné rito.",
      },
      {
        phrase: "Prodělat kalhoty",
        meaning: "Utrpět velkou finanční ztrátu.",
        example: "Na burze letos hodně lidí prodělalo kalhoty.",
      },
      {
        phrase: "Dřít z někoho kůži",
        meaning: "Zneužívat někoho finančně nebo ho nutit moc pracovat.",
        example: "Ten nový šéf z nás doslova dře kůži.",
      },
      {
        phrase: "Být na mizině",
        meaning: "Zbankrotovat, nemít vůbec žádné peníze.",
        example: "Po tom rozvodu zůstal úplně na mizině.",
      },
      {
        phrase: "Žít na vysoké noze",
        meaning: "Žít luxusně, utrácet spoustu peněz.",
        example: "I když nemá velký plat, pořád si žije na vysoké noze.",
      },
    ],
  },
  {
    id: "party",
    title: "Zábava a alkohol",
    emoji: "🍻",
    items: [
      {
        phrase: "Být pod obraz",
        meaning: "Být extrémně opilý.",
        example: "Po oslavě narozenin dorazil domů úplně pod obraz.",
      },
      {
        phrase: "Dát si do trumpety",
        meaning: "Pořádně se opít.",
        example: "Včera jsme si s klukama v hospodě pěkně dali do trumpety.",
      },
      {
        phrase: "Mít opici",
        meaning: "Mít kocovinu.",
        example: "Dneska radši nevstávám, mám šílenou opici.",
      },
      {
        phrase: "Pařba",
        meaning: "Velký večírek, párty.",
        example: "To byla o víkendu neskutečná pařba!",
      },
      {
        phrase: "Sosat",
        meaning: "Pomalinku pít alkohol, vychutnávat si ho.",
        example: "Celý večer sosal jen jednu skleničku vína.",
      },
      {
        phrase: "Vyrazit si z kopýtka",
        meaning: "Jít se pořádně bavit, užít si večer.",
        example: "Po zkouškách si konečně vyrazíme z kopýtka.",
      },
      {
        phrase: "Být namol",
        meaning: "Být totálně opilý.",
        example: "Včera jsme tě viděli, byl jsi namol!",
      },
      {
        phrase: "Exnout něco",
        meaning: "Vypít nápoj (často alkoholický) na ex, tedy naráz.",
        example: "Když to exneš, koupím ti další.",
      },
      {
        phrase: "Hospodský povaleč",
        meaning: "Člověk, který tráví většinu času v hospodě (často pije pivo).",
        example: "Nechci skončit jako nějaký hospodský povaleč.",
      },
      {
        phrase: "Jít na tah",
        meaning: "Jít se bavit do města na celou noc (z hospody do hospody).",
        example: "S kolegy jdeme v pátek na tah.",
      },
    ],
  },
  {
    id: "school",
    title: "Učení, škola a pozornost",
    emoji: "🎓",
    items: [
      {
        phrase: "Mít v hlavě vymeteno",
        meaning: "Nic nevědět, být hloupý nebo zrovna neschopný myslet.",
        example: "Po té zkoušce mám v hlavě úplně vymeteno.",
      },
      {
        phrase: "Tahák",
        meaning: "Podvodný lístek (špargalka) při písemce.",
        example: "Učitel mi našel tahák a dostal jsem pětku.",
      },
      {
        phrase: "Být mimo",
        meaning: "Nesoustředit se, nedávat pozor (nebo nechápat).",
        example: "Dneska jsem na té přednášce byl úplně mimo.",
      },
      {
        phrase: "Šprtat se / Brtit se",
        meaning: "Intenzivně se učit, biflovat.",
        example: "Musím se celou noc šprtat na test z matiky.",
      },
      {
        phrase: "Projít s odřenýma ušima",
        meaning: "Uspět jen tak tak, s nejhorší možnou známkou.",
        example: "Maturoval jsem s odřenýma ušima.",
      },
      {
        phrase: "Rupnout (u zkoušky)",
        meaning: "Neudělat zkoušku, propadnout.",
        example: "Zase jsem rupnul z angličtiny.",
      },
      {
        phrase: "Zatáhnout školu / Jít za školu",
        meaning: "Nepřijít na vyučování bez omluvy.",
        example: "Včera jsme zatáhli fyziku a šli do kina.",
      },
      {
        phrase: "Výtlem",
        meaning: "Nekontrolovatelný záchvat smíchu (slang).",
        example: "Když učitel zakopl, chytili jsme všichni hrozný výtlem.",
      },
      {
        phrase: "Dávat bacha",
        meaning: "Dávat pozor (jak ve škole, tak na nebezpečí).",
        example: "Dávej bacha, ať to nerozbiješ!",
      },
      {
        phrase: "Být za hvězdu",
        meaning: "Být středem pozornosti za skvělý výkon, excelovat.",
        example: "Odpověděl na všechno a byl před třídou za hvězdu.",
      },
    ],
  },
  {
    id: "love2",
    title: "Láska a vztahy 2",
    emoji: "💕",
    items: [
      {
        phrase: "Být pod pantoflem",
        meaning: "Být zcela ovládán svou partnerkou.",
        example: "Jirka nikam s námi nechodí, je hrozně pod pantoflem.",
      },
      {
        phrase: "Uhánět někoho",
        meaning: "Snažit se někoho získat, nadbíhat mu (romanticky).",
        example: "Už měsíc ji uhání, ale ona ho nechce.",
      },
      {
        phrase: "Namotat si někoho",
        meaning: "Svésť někoho, okouzlit ho.",
        example: "Namotala si ho na první pohled.",
      },
      {
        phrase: "Žehlit průšvih",
        meaning: "Snažit se udobřit partnera po tom, co jsme udělali chybu.",
        example: "Zapomněl na výročí a teď to musí žehlit kytkou.",
      },
      {
        phrase: "Lepit se na někoho",
        meaning: "Být příliš dotěrný, nedat někomu prostor.",
        example: "Na večírku se na mě lepil nějaký divný chlap.",
      },
      {
        phrase: "Zlatokopka",
        meaning: "Žena, která hledá partnera pouze pro jeho peníze.",
        example: "Každý ví, že je to zlatokopka, miluje jen jeho kreditku.",
      },
      {
        phrase: "Vylít si srdíčko",
        meaning: "Svěřit se někomu se svými problémy a trápením.",
        example: "Přišla ke mně na víno, aby si mohla vylít srdíčko.",
      },
      {
        phrase: "Mít bokovku",
        meaning: "Mít milenecký poměr vedle stálého vztahu.",
        example: "Zjistila, že její manžel má už rok bokovku.",
      },
      {
        phrase: "Skákat, jak někdo píská",
        meaning: "Bezmezně někoho poslouchat.",
        example: "On skáče přesně tak, jak ona píská.",
      },
      {
        phrase: "Hrdličky",
        meaning: "Čerstvě nebo silně zamilovaný pár.",
        example: "Koukej na ně, to jsou ale hrdličky.",
      },
    ],
  },
  {
    id: "proverbs2",
    title: "Další populární přísloví a rčení",
    emoji: "📖",
    items: [
      {
        phrase: "Kdo jinému jámu kopá, sám do ní padá",
        meaning: "Kdo se snaží uškodit jinému, doplatí na to sám.",
        example: "Chtěl mě nechat vyhodit, ale nakonec dostal výpověď on. Kdo jinému jámu kopá...",
      },
      {
        phrase: "Láska prochází žaludkem",
        meaning: "Dobré jídlo je klíčem k srdci (hlavně mužů).",
        example: "Uvař mu jeho oblíbené jídlo, víš přece, že láska prochází žaludkem.",
      },
      {
        phrase: "Nechval dne před večerem",
        meaning: "Neraduj se předčasně z úspěchu, dokud není vše hotovo.",
        example: "Zatím to jde dobře, ale nechval dne před večerem.",
      },
      {
        phrase: "Co na srdci, to na jazyku",
        meaning: "O upřímném člověku, který řekne přímo to, co si myslí.",
        example: "S ní se jedná narovinu, má co na srdci, to na jazyku.",
      },
      {
        phrase: "Pes, který štěká, nekouše",
        meaning: "Lidé, kteří hodně vyhrožují a křičí, většinou nic neudělají.",
        example: "Neboj se ho, pes, který štěká, nekouše.",
      },
      {
        phrase: "Práce kvapná, málo platná",
        meaning: "Rychle a narychlo udělaná práce bývá často nekvalitní.",
        example: "Měl jsi mi to dát zkontrolovat, pamatuješ? Práce kvapná, málo platná.",
      },
      {
        phrase: "Trpělivost růže přináší",
        meaning: "Kdo umí počkat, dočká se úspěchu.",
        example: "Nevzdávej to po prvním týdnu. Trpělivost růže přináší.",
      },
      {
        phrase: "Vrána k vráně sedá",
        meaning: "Lidé se stejnou povahou nebo zájmy si k sobě vždycky najdou cestu.",
        example: "Oba jsou strašně líní, není divu, že jsou spolu. Vrána k vráně sedá.",
      },
      {
        phrase: "Bližší košile nežli kabát",
        meaning: "Vlastní zájmy a rodina jsou nám přednější než cizí lidé.",
        example: "Rád bych jim pomohl, ale musím se postarat o své děti. Bližší košile nežli kabát.",
      },
      {
        phrase: "S poctivostí nejdál dojdeš",
        meaning: "Být upřímný a čestný se dlouhodobě vyplatí nejvíce.",
        example: "Nezapírej to, raději přiznej chybu. S poctivostí nejdál dojdeš.",
      },
    ],
  },
  {
    id: "internet",
    title: "Moderní výrazy a internetový slang",
    emoji: "📱",
    items: [
      {
        phrase: "Vygooglit",
        meaning: "Najít něco na internetu pomocí vyhledávače Google.",
        example: "Nevím, kdy ten vlak jede, musím to vygooglit.",
      },
      {
        phrase: "Fejk",
        meaning: "Padělek, falešná věc nebo zpráva (z anglického 'fake').",
        example: "Ty značkové boty z tržnice jsou určitě fejk.",
      },
      {
        phrase: "Hejtr",
        meaning: "Člověk, který jen kritizuje a píše nenávistné komentáře na internetu.",
        example: "Nečti ty komentáře, jsou tam jenom samí hejtři.",
      },
      {
        phrase: "Stajlovat se",
        meaning: "Upravovat se, dlouho se oblékat a česat před zrcadlem.",
        example: "Už se stajluje hodinu, asi přijdeme pozdě.",
      },
      {
        phrase: "Spamovat",
        meaning: "Posílat nevyžádané nebo opakující se zprávy.",
        example: "Nespamuj mi ten chat pořád dokola!",
      },
      {
        phrase: "Zčeknout něco",
        meaning: "Zkontrolovat, prohlédnout si (z anglického 'check').",
        example: "Musím zčeknout, jestli už mi přišla výplata.",
      },
      {
        phrase: "Ujetý",
        meaning: "Velmi divný, bláznivý nebo nevkusný.",
        example: "Ten jeho nový sestřih je fakt ujetý.",
      },
      {
        phrase: "Mega",
        meaning: "Univerzální předpona pro něco obrovského, skvělého nebo zkrátka 'velmi'.",
        example: "Byla to mega dobrá pizza.",
      },
      {
        phrase: "Chill / Chillovat",
        meaning: "Odpočívat, relaxovat, nic nedělat.",
        example: "Dneska večer budu jenom chillovat u Netflixu.",
      },
      {
        phrase: "Hype",
        meaning: "Velký (často přehnaný) rozruch, nadšení nebo reklama kolem nějaké novinky.",
        example: "Nechápu ten hype kolem toho nového iPhonu.",
      },
    ],
  },
]

// ===== Components =====

function SlangCard({ item }: { item: SlangItem }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <motion.div
      layout
      className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 overflow-hidden shadow-sm hover:shadow-md transition-shadow"
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left px-4 py-3 flex items-center justify-between gap-3"
      >
        <span className="font-semibold text-sm text-foreground">{item.phrase}</span>
        {expanded ? (
          <ChevronUp className="w-4 h-4 text-gray-400 flex-shrink-0" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-400 flex-shrink-0" />
        )}
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-3 space-y-2 border-t border-gray-100 dark:border-gray-700 pt-2">
              <p className="text-xs text-muted-foreground">
                <span className="font-medium text-purple-600 dark:text-purple-400">Význam:</span>{" "}
                {item.meaning}
              </p>
              <div className="bg-purple-50 dark:bg-purple-900/20 rounded-xl px-3 py-2">
                <p className="text-xs text-purple-800 dark:text-purple-300 italic">
                  <span className="font-medium not-italic">Příklad:</span> {item.example}
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

function CategorySection({ category }: { category: SlangCategory }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="mb-4">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/30 dark:to-indigo-900/30 rounded-2xl px-4 py-3 hover:from-purple-100 hover:to-indigo-100 dark:hover:from-purple-900/40 dark:hover:to-indigo-900/40 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-xl">{category.emoji}</span>
          <span className="font-bold text-sm text-foreground">{category.title}</span>
          <span className="text-xs bg-purple-100 dark:bg-purple-800 text-purple-600 dark:text-purple-300 px-2 py-0.5 rounded-full">
            {category.items.length}
          </span>
        </div>
        {isOpen ? (
          <ChevronUp className="w-5 h-5 text-purple-500" />
        ) : (
          <ChevronDown className="w-5 h-5 text-purple-500" />
        )}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="space-y-2 pt-3 pl-2">
              {category.items.map((item, idx) => (
                <SlangCard key={idx} item={item} />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// ===== Main Export =====

export function SlangTab() {
  const [searchQuery, setSearchQuery] = useState("")

  const filteredCategories = searchQuery.trim()
    ? SLANG_CATEGORIES.map((cat) => ({
        ...cat,
        items: cat.items.filter(
          (item) =>
            item.phrase.toLowerCase().includes(searchQuery.toLowerCase()) ||
            item.meaning.toLowerCase().includes(searchQuery.toLowerCase()) ||
            item.example.toLowerCase().includes(searchQuery.toLowerCase())
        ),
      })).filter((cat) => cat.items.length > 0)
    : SLANG_CATEGORIES

  const totalCount = SLANG_CATEGORIES.reduce((sum, cat) => sum + cat.items.length, 0)
  const filteredCount = filteredCategories.reduce((sum, cat) => sum + cat.items.length, 0)

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="text-center mb-2">
        <p className="text-xs text-muted-foreground">
          {totalCount} idiomů a slangových výrazů v {SLANG_CATEGORIES.length} kategoriích
        </p>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Hledat idiom nebo výraz..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        />
        {searchQuery && (
          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
            {filteredCount} výsledků
          </span>
        )}
      </div>

      {/* Categories */}
      <div>
        {filteredCategories.length > 0 ? (
          filteredCategories.map((category) => (
            <CategorySection key={category.id} category={category} />
          ))
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            <p className="text-sm">Nic nenalezeno</p>
            <p className="text-xs mt-1">Zkuste jiný hledaný výraz</p>
          </div>
        )}
      </div>
    </div>
  )
}
