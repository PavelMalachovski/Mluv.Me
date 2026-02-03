/**
 * Česká lokalizace pro Mluv.Me frontend.
 *
 * Koncepce: Language Immersion (Ponoření do jazyka)
 * - Celé rozhraní je v češtině
 * - Student se učí i z rozhraní
 * - Vysvětlení chyb jsou na jednoduchém A2 úrovni
 */

export const CS_TEXTS = {
  // Navigace
  nav: {
    dashboard: "Přehled",
    practice: "Procvičování",
    review: "Opakování",
    saved: "Uložená slova",
    profile: "Profil",
    settings: "Nastavení",
    achievements: "Úspěchy",
    logout: "Odhlásit se",
  },

  // Dashboard
  dashboard: {
    greeting: (name: string) => `Ahoj, ${name}! 👋`,
    subtitle: "Připraven/a na dnešní češtinu?",
    streak: "Série dnů",
    streakDays: (count: number) => {
      if (count === 1) return "den";
      if (count >= 2 && count <= 4) return "dny";
      return "dní";
    },
    stars: "Hvězdy",
    level: "Úroveň",
    practiceBtn: "Procvičovat",
    reviewBtn: "Opakovat",
    todaysProgress: "Dnešní pokrok",
    messages: "Zprávy",
    messagesCount: (count: number) => {
      if (count === 1) return "zpráva";
      if (count >= 2 && count <= 4) return "zprávy";
      return "zpráv";
    },
    toReview: "K opakování",
    accuracy: "Přesnost",
    achievements: "Úspěchy",
    viewAll: "Zobrazit vše →",
    keepGoing: "Pokračuj! 💪",
    dailyChallenge: "Denní výzva",
    challengeProgress: (current: number, goal: number) => `${current} / ${goal}`,
    challengeComplete: "Hotovo! 🎉",
    noChallenge: "Žádná výzva",
    weeklyStats: "Statistiky za týden",
    wordsLearned: "Naučená slova",
    averageScore: "Průměrné skóre",
  },

  // Practice (Procvičování)
  practice: {
    title: "Procvičuj češtinu s Honzíkem",
    subtitle: "Napiš nebo nahraj zprávu v češtině",
    topicSelect: "Vyber téma",
    startBtn: "Začít procvičovat",
    topicLabel: "Téma:",
    sendBtn: "Odeslat",
    recording: "Nahrávání...",
    processing: "Zpracovávám...",
    showText: "Zobrazit text",
    hideText: "Skrýt text",
    translateWord: "Přeložit slovo",
    correctionsHeader: "Opravy:",
    noCorrections: "Výborně! Bez chyb! 🎉",
    starsEarned: (n: number) => `+${n} hvězd ⭐`,
    tipsTitle: "Tipy pro procvičování:",
    tips: [
      "✅ Piš celé věty",
      "✅ Neboj se chyb — tak se učíme!",
      "✅ Ptej se Honzíka na českou kulturu",
      "✅ Procvičuj pravidelně",
    ],
    inputPlaceholder: "Napiš zprávu v češtině...",
    voiceHint: "🎤 Klepni pro nahrání (max 60 sekund)",
    voiceRecording: "🔴 Nahrávám... Klepni pro ukončení",
    voiceTooLong: "Zpráva je příliš dlouhá (max 60 sekund)",
    emptyMessage: "Napiš nebo nahraj něco v češtině!",
    honzikThinking: "Honzík přemýšlí...",
    honzikListening: "Honzík poslouchá...",
    topics: {
      general: "🗣️ Obecná konverzace",
      beer: "🍺 Pivo a hospody",
      food: "🍽️ Jídlo a restaurace",
      travel: "✈️ Cestování",
      work: "💼 Práce",
      family: "👨‍👩‍👧‍👦 Rodina",
      hobbies: "🎨 Koníčky",
      weather: "🌤️ Počasí",
      sports: "⚽ Sport",
      culture: "🏛️ Kultura a historie",
    },
  },

  // Review (Opakování - Spaced Repetition)
  review: {
    title: "Opakování slovíček",
    cardsDue: "Slovíček k opakování",
    noCards: "Žádná slovíčka k opakování! 🎉",
    comeBackLater: "Vrať se později pro další opakování",
    showAnswer: "Zobrazit odpověď",
    again: "Znovu",
    hard: "Těžké",
    good: "Dobré",
    easy: "Snadné",
    progress: (current: number, total: number) => `${current} / ${total}`,
    completed: "Dnešní opakování hotovo! 🎉",
    streakBonus: "Bonus za sérii!",
    nextReview: "Další opakování:",
    tomorrow: "zítra",
    inDays: (days: number) => {
      if (days === 1) return "za 1 den";
      if (days >= 2 && days <= 4) return `za ${days} dny`;
      return `za ${days} dní`;
    },
  },

  // Saved words (Uložená slova)
  saved: {
    title: "Uložená slova",
    searchPlaceholder: "Hledat slovo...",
    noWords: "Zatím nemáš žádná uložená slova",
    addWordsHint: "Klepni na slovo v konverzaci pro jeho uložení",
    deleteConfirm: "Opravdu smazat toto slovo?",
    phonetics: "Výslovnost",
    example: "Příklad",
    translation: "Překlad",
    addedOn: "Přidáno",
    reviewCount: "Počet opakování",
    sortBy: "Řadit podle",
    sortNewest: "Nejnovější",
    sortOldest: "Nejstarší",
    sortAlphabetical: "Abecedně",
    exportAnki: "Exportovat do Anki",
  },

  // Profile (Profil)
  profile: {
    title: "Profil",
    level: "Úroveň češtiny",
    memberSince: "Člen od",
    statsTitle: "Statistiky",
    totalMessages: "Celkem zpráv",
    totalWords: "Naučených slov",
    bestStreak: "Nejdelší série",
    avgAccuracy: "Průměrná přesnost",
    totalStars: "Celkem hvězd",
    editProfile: "Upravit profil",
  },

  // Settings (Nastavení)
  settings: {
    title: "Nastavení",
    levelSection: "Úroveň češtiny",
    levelBeginner: "Začátečník (A1-A2)",
    levelIntermediate: "Středně pokročilý (B1-B2)",
    levelAdvanced: "Pokročilý (B2-C1)",
    levelNative: "Rodilý mluvčí (C2)",
    styleSection: "Styl komunikace",
    styleFriendly: "Přátelský",
    styleFriendlyDesc: "Více podpory, méně oprav",
    styleTutor: "Učitel",
    styleTutorDesc: "Detailní vysvětlení chyb",
    styleCasual: "Kamarádský",
    styleCasualDesc: "Neformální konverzace",
    correctionsSection: "Úroveň oprav",
    correctionsMinimal: "Minimální",
    correctionsMinimalDesc: "Pouze kritické chyby",
    correctionsBalanced: "Vyvážená",
    correctionsBalancedDesc: "Doporučeno",
    correctionsDetailed: "Detailní",
    correctionsDetailedDesc: "Všechny chyby s vysvětlením",
    voiceSpeed: "Rychlost hlasu Honzíka",
    voiceVerySlow: "Velmi pomalu",
    voiceSlow: "Pomalu",
    voiceNormal: "Normálně",
    voiceNative: "Rychle (rodilý)",
    nativeLanguage: "Rodný jazyk (pro vysvětlení)",
    nativeRu: "🇷🇺 Ruština",
    nativeUk: "🇺🇦 Ukrajinština",
    nativePl: "🇵🇱 Polština",
    nativeSk: "🇸🇰 Slovenština",
    notifications: "Oznámení",
    notificationsEnabled: "Zapnuto",
    notificationsDisabled: "Vypnuto",
    theme: "Vzhled",
    themeLight: "Světlý",
    themeDark: "Tmavý",
    themeSystem: "Podle systému",
    timezone: "Časové pásmo",
    saveBtn: "Uložit nastavení",
    savedToast: "Nastavení uloženo! ✅",
    subscription: "Předplatné",
    subscriptionFree: "Zdarma",
    subscriptionPremium: "Premium",
    upgradeBtn: "Upgradovat na Premium",
  },

  // Achievements (Úspěchy)
  achievements: {
    title: "Úspěchy",
    locked: "Zamčeno",
    unlocked: "Odemčeno",
    progress: "Pokrok",
    reward: "Odměna",
    starsReward: (n: number) => `+${n} hvězd`,
    unlockedOn: "Odemčeno",
    categories: {
      streak: "🔥 Série",
      messages: "💬 Zprávy",
      vocabulary: "📚 Slovíčka",
      accuracy: "🎯 Přesnost",
      time: "⏰ Čas",
      thematic: "🎭 Tematické",
    },
    names: {
      first_message: "🎉 První krok",
      week_streak: "🔥 Týden v kuse",
      month_streak: "🔥 Měsíc bez pauzy",
      messages_10: "💬 Aktivní student",
      messages_100: "💬 Mluvka",
      words_50: "📚 Začínající slovníkář",
      words_200: "📚 Sběratel slov",
      accuracy_90: "🎯 Přesný střelec",
      early_bird: "🌅 Ranní ptáče",
      night_owl: "🦉 Noční sova",
      beer_master: "🍺 Pivař",
    },
  },

  // Honzík phrases (Fráze Honzíka)
  honzik: {
    greeting: "Ahoj! Jsem Honzík 🇨🇿",
    thinking: "Honzík přemýšlí...",
    listening: "Honzík poslouchá...",
    encouragement: [
      "Výborně! Jde ti to skvěle! 💪",
      "Super práce! Pokračuj! 🎉",
      "Skvělé! Učíš se rychle! ⭐",
      "Prima! To bylo dobré! 👍",
      "Paráda! Jsi šikovný/á! 🌟",
    ],
    mistakes: [
      "Nevadí, zkusíme to znovu!",
      "Učení je proces! Neboj se chyb.",
      "Postupně to půjde líp!",
    ],
  },

  // Onboarding
  onboarding: {
    welcome: {
      title: "Ahoj! 🇨🇿",
      subtitle: "Jsem Honzík — tvůj veselý český kamarád!\nPomohu ti naučit se česky.",
    },
    nativeLanguage: {
      title: "Tvůj rodný jazyk?",
      subtitle: "Pro vysvětlení gramatiky",
    },
    level: {
      title: "Tvoje úroveň češtiny",
      subtitle: "Abych věděl, jak s tebou mluvit",
    },
    style: {
      title: "Jak komunikovat?",
      subtitle: "Můžeš to změnit v nastavení",
    },
    ready: {
      title: "Hotovo! 🎉",
      subtitle: "Pošli mi hlasovou zprávu nebo napiš česky.\nNeboj se chyb — tak se učíme!",
    },
    nextBtn: "Další",
    skipBtn: "Přeskočit",
    startBtn: "Začít procvičovat! 🚀",
  },

  // Common (Obecné)
  common: {
    loading: "Načítání...",
    error: "Něco se pokazilo",
    retry: "Zkusit znovu",
    back: "Zpět",
    next: "Další",
    cancel: "Zrušit",
    confirm: "Potvrdit",
    save: "Uložit",
    delete: "Smazat",
    yes: "Ano",
    no: "Ne",
    close: "Zavřít",
    more: "Více",
    less: "Méně",
    search: "Hledat",
    filter: "Filtrovat",
    sort: "Řadit",
    all: "Vše",
    none: "Nic",
    today: "Dnes",
    yesterday: "Včera",
    thisWeek: "Tento týden",
    thisMonth: "Tento měsíc",
  },

  // Errors (Chyby)
  errors: {
    network: "Problém s připojením. Zkus to znovu.",
    voiceTooLong: "Zpráva je příliš dlouhá (max 60 sekund)",
    processingFailed: "Nepodařilo se zpracovat. Zkus to znovu.",
    serverError: "Server je momentálně nedostupný.",
    unauthorized: "Přihlas se prosím znovu.",
    notFound: "Stránka nenalezena.",
    invalidInput: "Neplatný vstup.",
    sessionExpired: "Relace vypršela. Přihlas se znovu.",
  },

  // Success messages
  success: {
    saved: "Uloženo! ✅",
    deleted: "Smazáno!",
    copied: "Zkopírováno!",
    sent: "Odesláno!",
  },

  // Time
  time: {
    now: "Právě teď",
    minutesAgo: (n: number) => {
      if (n === 1) return "před minutou";
      if (n >= 2 && n <= 4) return `před ${n} minutami`;
      return `před ${n} minutami`;
    },
    hoursAgo: (n: number) => {
      if (n === 1) return "před hodinou";
      if (n >= 2 && n <= 4) return `před ${n} hodinami`;
      return `před ${n} hodinami`;
    },
    daysAgo: (n: number) => {
      if (n === 1) return "včera";
      if (n >= 2 && n <= 4) return `před ${n} dny`;
      return `před ${n} dny`;
    },
  },

  // Correction explanation component
  correction: {
    showTranslation: "Zobrazit překlad",
    hideTranslation: "Skrýt překlad",
    explanationCs: "Vysvětlení:",
    explanationNative: "Překlad:",
  },
};

// Type for the localization object
export type CSTexts = typeof CS_TEXTS;

// Helper function to get text with fallback
export function getText(key: string): string {
  const keys = key.split(".");
  let value: unknown = CS_TEXTS;

  for (const k of keys) {
    if (value && typeof value === "object" && k in value) {
      value = (value as Record<string, unknown>)[k];
    } else {
      console.warn(`Missing translation key: ${key}`);
      return key;
    }
  }

  return typeof value === "string" ? value : key;
}

// Export default
export default CS_TEXTS;
