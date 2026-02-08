"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import { motion, AnimatePresence } from "framer-motion"
import Image from "next/image"
import {
  Gamepad2, Trophy, Timer, Star, Check, X,
  RotateCcw, ChevronRight, Sparkles, Zap
} from "lucide-react"
import { apiClient } from "@/lib/api-client"

// ===== Types =====

interface MiniGame {
  id: string
  name: string
  description: string
  icon: string
  color: string
  gradient: string
  reward: number
  timeLimit: number
}

interface GameQuestion {
  game_id: string
  game_type: string
  name_cs: string
  question: {
    type: string
    prompt: string
    options?: string[]
    hint?: string
    word?: string
    sentence?: string
    words?: string[]
  }
  time_limit_seconds: number
  reward_stars: number
}

interface GameResult {
  is_correct: boolean
  correct_answer: string
  user_answer: string
  stars_earned: number
  base_stars: number
  bonus_stars: number
  time_seconds: number
  time_bonus_percent: number
}

interface ProfileMiniGamesProps {
  userId: number
  telegramId: number
  level?: string
}

// ===== Local Vocabulary Bank (mirrors backend) =====

interface WordEntry {
  word: string
  hint: string
  category: string
}

interface SentenceEntry {
  sentence: string
  translation: string
}

interface QuickEntry {
  question: string
  answer: string
  options: string[]
}

const VOCABULARY: Record<string, { words: WordEntry[]; sentences: SentenceEntry[]; quick: QuickEntry[] }> = {
  beginner: {
    words: [
      { word: "pivo", hint: "Oblíbený český nápoj 🍺", category: "drink" },
      { word: "chleba", hint: "Jíme ho každý den 🍞", category: "food" },
      { word: "voda", hint: "Tekutina, kterou pijeme 💧", category: "drink" },
      { word: "dům", hint: "Kde bydlíme 🏠", category: "place" },
      { word: "auto", hint: "Dopravní prostředek se 4 koly 🚗", category: "transport" },
      { word: "kniha", hint: "Čteme ji 📚", category: "object" },
      { word: "pes", hint: "Domácí mazlíček, štěká 🐕", category: "animal" },
      { word: "kočka", hint: "Domácí mazlíček, mňouká 🐱", category: "animal" },
      { word: "škola", hint: "Místo, kde se učíme 🏫", category: "place" },
      { word: "Praha", hint: "Hlavní město Česka 🏰", category: "place" },
      { word: "mlíko", hint: "Bílý nápoj od krávy 🥛", category: "drink" },
      { word: "vlak", hint: "Jezdí po kolejích 🚂", category: "transport" },
    ],
    sentences: [
      { sentence: "Jak se máš?", translation: "Как дела?" },
      { sentence: "Mám se dobře.", translation: "У меня всё хорошо." },
      { sentence: "Děkuji moc.", translation: "Большое спасибо." },
      { sentence: "Jedno pivo, prosím.", translation: "Одно пиво, пожалуйста." },
      { sentence: "Kde je zastávka?", translation: "Где остановка?" },
      { sentence: "Jak se jmenuješ?", translation: "Как тебя зовут?" },
      { sentence: "Dobrý den!", translation: "Добрый день!" },
    ],
    quick: [
      { question: "Jak se řekne 'hello' česky?", answer: "ahoj", options: ["ahoj", "sbohem", "prosím", "děkuji"] },
      { question: "Jaké je hlavní město Česka?", answer: "Praha", options: ["Praha", "Brno", "Ostrava", "Plzeň"] },
      { question: "Co pijeme v hospodě? 🍺", answer: "pivo", options: ["pivo", "mléko", "čaj", "kávu"] },
      { question: "Jak se řekne 'thank you' česky?", answer: "děkuji", options: ["prosím", "ahoj", "děkuji", "pardon"] },
      { question: "Jak se řekne 'goodbye' česky?", answer: "na shledanou", options: ["ahoj", "na shledanou", "prosím", "ano"] },
      { question: "Co je 'pes'? 🐕", answer: "dog", options: ["cat", "dog", "bird", "fish"] },
      { question: "Jakou barvu má nebe? ☀️", answer: "modrá", options: ["červená", "zelená", "modrá", "žlutá"] },
      { question: "Kolik dní má týden?", answer: "sedm", options: ["pět", "šest", "sedm", "deset"] },
    ],
  },
  intermediate: {
    words: [
      { word: "hospoda", hint: "Typické české místo pro pivo 🍺", category: "place" },
      { word: "knedlík", hint: "Příloha k svíčkové", category: "food" },
      { word: "krásný", hint: "Velmi hezký ✨", category: "adjective" },
      { word: "důležitý", hint: "Velmi významný ❗", category: "adjective" },
      { word: "cestovat", hint: "Jezdit do různých míst ✈️", category: "verb" },
      { word: "překvapení", hint: "Něco nečekaného 🎁", category: "noun" },
      { word: "nádraží", hint: "Místo odkud jezdí vlaky 🚉", category: "place" },
      { word: "počasí", hint: "Jaké je venku? ☁️", category: "noun" },
    ],
    sentences: [
      { sentence: "Rád bych si objednal svíčkovou.", translation: "Я бы хотел заказать свичкову." },
      { sentence: "Můžete mi prosím pomoct?", translation: "Вы можете мне помочь?" },
      { sentence: "Jak dlouho trvá cesta?", translation: "Сколько времени занимает дорога?" },
      { sentence: "Máte nějakou slevu?", translation: "У вас есть скидка?" },
      { sentence: "Kde je nejbližší lékárna?", translation: "Где ближайшая аптека?" },
    ],
    quick: [
      { question: "Co je 'svíčková'?", answer: "tradiční české jídlo", options: ["tradiční české jídlo", "druh piva", "typ svíčky", "název města"] },
      { question: "Jak se řekne 'I don't understand'?", answer: "nerozumím", options: ["nerozumím", "nevím", "nemůžu", "nechci"] },
      { question: "Co znamená 'hospoda'?", answer: "pub", options: ["hospital", "pub", "hotel", "house"] },
      { question: "Jaká je česká měna?", answer: "koruna", options: ["euro", "koruna", "zlotý", "dolar"] },
      { question: "Co je 'tramvaj'? 🚊", answer: "tram", options: ["tram", "bus", "train", "taxi"] },
      { question: "Jaký je nejznámější český hrad?", answer: "Karlštejn", options: ["Karlštejn", "Křivoklát", "Bouzov", "Loket"] },
    ],
  },
  advanced: {
    words: [
      { word: "zodpovědnost", hint: "Odpovědnost za něco", category: "noun" },
      { word: "překážka", hint: "Něco, co brání v cestě 🚧", category: "noun" },
      { word: "přehodnotit", hint: "Znovu promyslet 🤔", category: "verb" },
      { word: "záležitost", hint: "Věc nebo problém", category: "noun" },
      { word: "spravedlnost", hint: "Férovost a rovnost ⚖️", category: "noun" },
    ],
    sentences: [
      { sentence: "Bylo by možné přeložit schůzku na příští týden?", translation: "Можно ли перенести встречу на следующую неделю?" },
      { sentence: "Rád bych vás upozornil na důležitý detail.", translation: "Хотел бы обратить ваше внимание на важную деталь." },
      { sentence: "To záleží na okolnostech.", translation: "Это зависит от обстоятельств." },
    ],
    quick: [
      { question: "Co znamená 'nicméně'?", answer: "nevertheless", options: ["never", "nevertheless", "nothing", "nowhere"] },
      { question: "Jaký je rozdíl mezi 'být' a 'mít'?", answer: "to be vs to have", options: ["to be vs to have", "to go vs to come", "to say vs to tell", "to do vs to make"] },
      { question: "Co je 'soudce'?", answer: "judge", options: ["lawyer", "judge", "police", "doctor"] },
      { question: "Jaký pád používáme po 'bez'?", answer: "genitiv", options: ["nominativ", "akuzativ", "genitiv", "dativ"] },
    ],
  },
}

// Helper: pick random element from array
function pickRandom<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)]
}

// Helper: shuffle array (Fisher-Yates)
function shuffle<T>(arr: T[]): T[] {
  const result = [...arr]
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]]
  }
  return result
}

/**
 * Generate a local question + correct answer for a given game type.
 * This mirrors the backend's game_service._generate_question logic.
 */
function generateLocalQuestion(
  gameId: string,
  level: string,
  gameName: string,
  timeLimit: number,
  reward: number,
): { question: GameQuestion; correctAnswer: string } {
  const vocab = VOCABULARY[level] || VOCABULARY.beginner

  if (gameId === "slovni_hadanka") {
    const entry = pickRandom(vocab.words)
    return {
      question: {
        game_id: gameId,
        game_type: gameId,
        name_cs: gameName,
        question: {
          type: "guess_word",
          prompt: `Uhádni slovo (${entry.word.length} písmen):`,
          hint: entry.hint,
        },
        time_limit_seconds: timeLimit,
        reward_stars: reward,
      },
      correctAnswer: entry.word,
    }
  }

  if (gameId === "dopln_pismeno") {
    const entry = pickRandom(vocab.words)
    const word = entry.word
    const idx = Math.floor(Math.random() * word.length)
    const display = word.slice(0, idx) + "_" + word.slice(idx + 1)
    return {
      question: {
        game_id: gameId,
        game_type: gameId,
        name_cs: gameName,
        question: {
          type: "fill_letter",
          prompt: `Doplň chybějící písmeno:`,
          word: display,
          hint: entry.hint,
        },
        time_limit_seconds: timeLimit,
        reward_stars: reward,
      },
      correctAnswer: word[idx],
    }
  }

  if (gameId === "rychla_odpoved") {
    const entry = pickRandom(vocab.quick)
    return {
      question: {
        game_id: gameId,
        game_type: gameId,
        name_cs: gameName,
        question: {
          type: "quick_answer",
          prompt: entry.question,
          options: shuffle(entry.options),
        },
        time_limit_seconds: timeLimit,
        reward_stars: reward,
      },
      correctAnswer: entry.answer,
    }
  }

  if (gameId === "sestav_vetu") {
    const entry = pickRandom(vocab.sentences)
    const words = entry.sentence
      .replace(/\?/g, " ?")
      .replace(/\./g, " .")
      .replace(/,/g, " ,")
      .split(/\s+/)
      .filter(Boolean)
    return {
      question: {
        game_id: gameId,
        game_type: gameId,
        name_cs: gameName,
        question: {
          type: "build_sentence",
          prompt: `Sestav větu (${entry.translation}):`,
          words: shuffle(words),
        },
        time_limit_seconds: timeLimit,
        reward_stars: reward,
      },
      correctAnswer: entry.sentence,
    }
  }

  if (gameId === "co_slyses") {
    const entry = pickRandom(vocab.words)
    return {
      question: {
        game_id: gameId,
        game_type: gameId,
        name_cs: gameName,
        question: {
          type: "listen_write",
          prompt: `Napiš slovo, které vidíš:`,
          hint: `${entry.hint} (${entry.category})`,
          word: entry.word.split("").join(" · "), // show as spaced letters as hint
        },
        time_limit_seconds: timeLimit,
        reward_stars: reward,
      },
      correctAnswer: entry.word,
    }
  }

  // Fallback — should not happen
  const entry = pickRandom(vocab.quick)
  return {
    question: {
      game_id: gameId,
      game_type: gameId,
      name_cs: gameName,
      question: {
        type: "quick_answer",
        prompt: entry.question,
        options: shuffle(entry.options),
      },
      time_limit_seconds: timeLimit,
      reward_stars: reward,
    },
    correctAnswer: entry.answer,
  }
}

/**
 * Locally check if user answer matches the correct answer.
 */
function checkLocalAnswer(userAnswer: string, correctAnswer: string, gameType: string): boolean {
  const uNorm = userAnswer.trim().toLowerCase()
  const cNorm = correctAnswer.trim().toLowerCase()

  if (gameType === "sestav_vetu") {
    const uClean = uNorm.replace(/ \?/g, "?").replace(/ \./g, ".").replace(/ ,/g, ",")
    const cClean = cNorm.replace(/ \?/g, "?").replace(/ \./g, ".").replace(/ ,/g, ",")
    return uClean === cClean
  }

  return uNorm === cNorm
}

// ===== Game Definitions =====

const MINI_GAMES: MiniGame[] = [
  {
    id: "slovni_hadanka",
    name: "🎯 Slovní hádanka",
    description: "Uhádni slovo podle popisu",
    icon: "🎯",
    color: "text-red-500",
    gradient: "from-red-400 to-orange-400",
    reward: 3,
    timeLimit: 60,
  },
  {
    id: "dopln_pismeno",
    name: "🔤 Doplň písmeno",
    description: "Doplň chybějící písmeno",
    icon: "🔤",
    color: "text-blue-500",
    gradient: "from-blue-400 to-cyan-400",
    reward: 2,
    timeLimit: 30,
  },
  {
    id: "rychla_odpoved",
    name: "⚡ Rychlá odpověď",
    description: "Odpověz za 10 sekund!",
    icon: "⚡",
    color: "text-yellow-500",
    gradient: "from-yellow-400 to-amber-400",
    reward: 5,
    timeLimit: 10,
  },
  {
    id: "sestav_vetu",
    name: "🧩 Sestav větu",
    description: "Sestav větu ze slov",
    icon: "🧩",
    color: "text-green-500",
    gradient: "from-green-400 to-emerald-400",
    reward: 4,
    timeLimit: 45,
  },
  {
    id: "co_slyses",
    name: "👂 Co slyšíš?",
    description: "Napiš co uslyšíš",
    icon: "👂",
    color: "text-purple-500",
    gradient: "from-purple-400 to-violet-400",
    reward: 3,
    timeLimit: 30,
  },
]

// ===== Game State Machine =====

type GameState = "menu" | "loading" | "playing" | "result"

// ===== Sub-Components =====

/** Game Card in the selection menu */
function GameCard({
  game,
  onSelect,
  index,
}: {
  game: MiniGame
  onSelect: () => void
  index: number
}) {
  return (
    <motion.button
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08 }}
      onClick={onSelect}
      className="w-full text-left"
    >
      <div className="illustrated-card p-3 hover:shadow-md transition-all duration-200 active:scale-[0.98] group">
        <div className="flex items-center gap-3">
          {/* Game Icon */}
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${game.gradient} flex items-center justify-center text-2xl shadow-sm`}>
            {game.icon}
          </div>

          {/* Game Info */}
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-sm text-foreground truncate">
              {game.name}
            </h4>
            <p className="text-xs text-muted-foreground truncate">
              {game.description}
            </p>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="flex items-center gap-0.5 text-xs text-amber-500">
                <Star className="w-3 h-3 fill-current" /> {game.reward}
              </span>
              <span className="flex items-center gap-0.5 text-xs text-gray-400">
                <Timer className="w-3 h-3" /> {game.timeLimit}s
              </span>
            </div>
          </div>

          {/* Arrow */}
          <ChevronRight className="w-5 h-5 text-gray-300 group-hover:text-purple-500 transition-colors" />
        </div>
      </div>
    </motion.button>
  )
}

/** Timer bar component */
function TimerBar({
  timeLeft,
  totalTime,
}: {
  timeLeft: number
  totalTime: number
}) {
  const percent = (timeLeft / totalTime) * 100
  const isLow = percent < 25

  return (
    <div className="flex items-center gap-2 mb-4">
      <Timer className={`w-4 h-4 ${isLow ? "text-red-500 animate-pulse" : "text-gray-400"}`} />
      <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <motion.div
          className={`h-full rounded-full ${isLow ? "bg-red-500" : "bg-gradient-to-r from-purple-500 to-amber-500"}`}
          initial={{ width: "100%" }}
          animate={{ width: `${percent}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>
      <span className={`text-sm font-mono font-bold min-w-[2rem] text-right ${isLow ? "text-red-500" : "text-gray-600 dark:text-gray-300"}`}>
        {timeLeft}s
      </span>
    </div>
  )
}

/** Game Result Screen */
function ResultScreen({
  result,
  onPlayAgain,
  onBack,
}: {
  result: GameResult
  onPlayAgain: () => void
  onBack: () => void
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="text-center py-4"
    >
      {/* Result Icon */}
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", damping: 10, delay: 0.2 }}
        className="mb-4"
      >
        {result.is_correct ? (
          <div className="w-20 h-20 mx-auto rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
            <Check className="w-10 h-10 text-green-500" />
          </div>
        ) : (
          <div className="w-20 h-20 mx-auto rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
            <X className="w-10 h-10 text-red-500" />
          </div>
        )}
      </motion.div>

      <h3 className="text-xl font-bold text-foreground mb-1">
        {result.is_correct ? "Správně! 🎉" : "Špatně 😔"}
      </h3>

      {!result.is_correct && (
        <p className="text-sm text-muted-foreground mb-2">
          Správná odpověď: <strong>{result.correct_answer}</strong>
        </p>
      )}

      {/* Stars Earned */}
      {result.stars_earned > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="flex items-center justify-center gap-1 text-amber-500 mb-4"
        >
          <Sparkles className="w-5 h-5" />
          <span className="text-lg font-bold">+{result.stars_earned}</span>
          <Star className="w-5 h-5 fill-current" />
          {result.bonus_stars > 0 && (
            <span className="text-xs bg-amber-100 dark:bg-amber-900/30 px-2 py-0.5 rounded-full ml-1">
              +{result.time_bonus_percent}% time bonus
            </span>
          )}
        </motion.div>
      )}

      {/* Actions */}
      <div className="flex gap-3 justify-center mt-4">
        <button
          onClick={onBack}
          className="px-4 py-2 rounded-xl bg-gray-100 dark:bg-gray-800 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
        >
          ← Zpět
        </button>
        <button
          onClick={onPlayAgain}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-purple-500 to-amber-500 text-sm font-bold text-white hover:opacity-90 transition-opacity flex items-center gap-1.5"
        >
          <RotateCcw className="w-4 h-4" />
          Hrát znovu
        </button>
      </div>
    </motion.div>
  )
}

// ===== Main Component =====

/**
 * Mini-games section for the Profile page.
 *
 * Displays available language learning games and allows
 * playing them inline without navigating away.
 */
export function ProfileMiniGames({
  userId,
  telegramId,
  level = "beginner",
}: ProfileMiniGamesProps) {
  const [gameState, setGameState] = useState<GameState>("menu")
  const [selectedGame, setSelectedGame] = useState<MiniGame | null>(null)
  const [question, setQuestion] = useState<GameQuestion | null>(null)
  const [answer, setAnswer] = useState("")
  const [timeLeft, setTimeLeft] = useState(0)
  const [result, setResult] = useState<GameResult | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [totalStarsWon, setTotalStarsWon] = useState(0)
  const [gamesPlayed, setGamesPlayed] = useState(0)
  const [localCorrectAnswer, setLocalCorrectAnswer] = useState<string>("")
  const [gameStartedAt, setGameStartedAt] = useState<number>(0)
  const [isLocalMode, setIsLocalMode] = useState(false)

  // Load stats from localStorage
  useEffect(() => {
    const saved = localStorage.getItem(`minigames_stats_${telegramId}`)
    if (saved) {
      try {
        const data = JSON.parse(saved)
        setTotalStarsWon(data.totalStars || 0)
        setGamesPlayed(data.gamesPlayed || 0)
      } catch {}
    }
  }, [telegramId])

  // Save stats to localStorage
  const saveStats = useCallback((stars: number, played: number) => {
    localStorage.setItem(`minigames_stats_${telegramId}`, JSON.stringify({
      totalStars: stars,
      gamesPlayed: played,
    }))
  }, [telegramId])

  // Timer countdown
  useEffect(() => {
    if (gameState !== "playing" || timeLeft <= 0) return

    const interval = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          // Time's up — auto submit
          handleSubmit()
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(interval)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gameState, timeLeft])

  // Start a game
  const handleStartGame = useCallback(async (game: MiniGame) => {
    setSelectedGame(game)
    setGameState("loading")
    setAnswer("")
    setResult(null)

    try {
      const response = await apiClient.post(`/api/v1/games/start/${game.id}`, {
        user_id: telegramId,
        level: level,
      })
      setQuestion(response)
      setTimeLeft(response.time_limit_seconds)
      setIsLocalMode(false)
      setGameStartedAt(Date.now())
      setGameState("playing")
    } catch (error) {
      console.error("Failed to start game, using local mode:", error)
      // Generate a proper local question with real vocabulary
      const local = generateLocalQuestion(
        game.id, level, game.name, game.timeLimit, game.reward
      )
      setQuestion(local.question)
      setLocalCorrectAnswer(local.correctAnswer)
      setIsLocalMode(true)
      setGameStartedAt(Date.now())
      setTimeLeft(game.timeLimit)
      setGameState("playing")
    }
  }, [telegramId, level])

  // Submit answer
  const handleSubmit = useCallback(async () => {
    if (isSubmitting || !question) return
    setIsSubmitting(true)

    const elapsed = (Date.now() - gameStartedAt) / 1000

    // If we're in local mode (API was unavailable), evaluate locally
    if (isLocalMode) {
      const isCorrect = checkLocalAnswer(
        answer || "(no answer)",
        localCorrectAnswer,
        question.game_type,
      )
      const timeBonus = Math.max(0, 1 - elapsed / question.time_limit_seconds)
      const baseStars = isCorrect ? question.reward_stars : 0
      const bonusStars = isCorrect ? Math.round(baseStars * timeBonus * 0.5) : 0

      const localResult: GameResult = {
        is_correct: isCorrect,
        correct_answer: localCorrectAnswer,
        user_answer: answer || "(no answer)",
        stars_earned: baseStars + bonusStars,
        base_stars: baseStars,
        bonus_stars: bonusStars,
        time_seconds: Math.round(elapsed * 10) / 10,
        time_bonus_percent: Math.round(timeBonus * 100),
      }
      setResult(localResult)

      const newStars = totalStarsWon + localResult.stars_earned
      const newPlayed = gamesPlayed + 1
      setTotalStarsWon(newStars)
      setGamesPlayed(newPlayed)
      saveStats(newStars, newPlayed)
    } else {
      // Use API
      try {
        const response = await apiClient.post("/api/v1/games/submit", {
          user_id: telegramId,
          answer: answer || "(no answer)",
        })
        setResult(response)

        const newStars = totalStarsWon + (response.stars_earned || 0)
        const newPlayed = gamesPlayed + 1
        setTotalStarsWon(newStars)
        setGamesPlayed(newPlayed)
        saveStats(newStars, newPlayed)
      } catch (error) {
        console.error("Failed to submit answer:", error)
        // Even in API mode, use local correct answer if available
        setResult({
          is_correct: false,
          correct_answer: localCorrectAnswer || "?",
          user_answer: answer || "(no answer)",
          stars_earned: 0,
          base_stars: 0,
          bonus_stars: 0,
          time_seconds: Math.round(elapsed * 10) / 10,
          time_bonus_percent: 0,
        })
      }
    }

    setIsSubmitting(false)
    setGameState("result")
  }, [answer, isSubmitting, question, telegramId, totalStarsWon, gamesPlayed, saveStats, isLocalMode, localCorrectAnswer, gameStartedAt])

  // Reset to menu
  const handleBack = useCallback(() => {
    setGameState("menu")
    setSelectedGame(null)
    setQuestion(null)
    setAnswer("")
    setResult(null)
    // Cancel any active game
    apiClient.delete(`/api/v1/games/cancel/${telegramId}`).catch(() => {})
  }, [telegramId])

  // Play the same game again
  const handlePlayAgain = useCallback(() => {
    if (selectedGame) {
      handleStartGame(selectedGame)
    }
  }, [selectedGame, handleStartGame])

  // Render word arrangement for "sestav_vetu"
  const renderWordChips = useMemo(() => {
    if (!question?.question?.words) return null
    return (
      <div className="flex flex-wrap gap-2 justify-center my-3">
        {question.question.words.map((word, i) => (
          <button
            key={i}
            onClick={() => setAnswer((prev) => prev ? `${prev} ${word}` : word)}
            className="px-3 py-1.5 rounded-lg bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-sm font-medium hover:bg-purple-200 dark:hover:bg-purple-800/40 transition-colors active:scale-95"
          >
            {word}
          </button>
        ))}
      </div>
    )
  }, [question?.question?.words])

  return (
    <div className="illustrated-card p-4 mb-6">
      {/* Section Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Gamepad2 className="w-5 h-5 text-purple-500" />
          <h3 className="font-semibold text-foreground">Mini hry</h3>
        </div>

        {/* Stats Badge */}
        {gamesPlayed > 0 && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className="flex items-center gap-0.5">
              <Trophy className="w-3 h-3 text-amber-500" /> {gamesPlayed}
            </span>
            <span className="flex items-center gap-0.5">
              <Star className="w-3 h-3 text-amber-500 fill-current" /> {totalStarsWon}
            </span>
          </div>
        )}
      </div>

      <AnimatePresence mode="wait">
        {/* ===== MENU STATE ===== */}
        {gameState === "menu" && (
          <motion.div
            key="menu"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-2"
          >
            {MINI_GAMES.map((game, i) => (
              <GameCard
                key={game.id}
                game={game}
                index={i}
                onSelect={() => handleStartGame(game)}
              />
            ))}
          </motion.div>
        )}

        {/* ===== LOADING STATE ===== */}
        {gameState === "loading" && (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="py-12 text-center"
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
              className="w-12 h-12 mx-auto mb-4"
            >
              <Zap className="w-12 h-12 text-purple-500" />
            </motion.div>
            <p className="text-sm text-muted-foreground">Připravuji hru...</p>
          </motion.div>
        )}

        {/* ===== PLAYING STATE ===== */}
        {gameState === "playing" && question && (
          <motion.div
            key="playing"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
          >
            {/* Game Title */}
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-bold text-foreground">{question.name_cs}</h4>
              <button
                onClick={handleBack}
                className="text-xs text-gray-400 hover:text-red-500 transition-colors"
              >
                Zrušit
              </button>
            </div>

            {/* Timer */}
            <TimerBar timeLeft={timeLeft} totalTime={question.time_limit_seconds} />

            {/* Question */}
            <div className="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-4 mb-4">
              <p className="text-center text-foreground font-medium">
                {question.question.prompt}
              </p>
              {question.question.hint && (
                <p className="text-center text-xs text-muted-foreground mt-1">
                  💡 {question.question.hint}
                </p>
              )}
              {question.question.word && (
                <p className="text-center text-2xl font-bold text-purple-600 dark:text-purple-400 mt-2 tracking-wider">
                  {question.question.word}
                </p>
              )}
            </div>

            {/* Word chips for sentence building */}
            {renderWordChips}

            {/* Options or Text Input */}
            {question.question.options ? (
              <div className="grid grid-cols-2 gap-2 mb-4">
                {question.question.options.map((option, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setAnswer(option)
                      // Auto-submit for multiple choice
                      setTimeout(() => {
                        setAnswer(option)
                        handleSubmit()
                      }, 100)
                    }}
                    className={`p-3 rounded-xl text-sm font-medium transition-all ${
                      answer === option
                        ? "bg-purple-500 text-white shadow-md"
                        : "bg-white dark:bg-gray-800 text-foreground border border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-600"
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            ) : (
              <div className="mb-4">
                <input
                  type="text"
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
                  placeholder="Napiš odpověď..."
                  autoFocus
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-foreground placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>
            )}

            {/* Submit Button */}
            {!question.question.options && (
              <button
                onClick={handleSubmit}
                disabled={!answer.trim() || isSubmitting}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-purple-500 to-amber-500 text-white font-bold text-sm disabled:opacity-50 hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
              >
                {isSubmitting ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ repeat: Infinity, duration: 0.8 }}
                  >
                    <RotateCcw className="w-4 h-4" />
                  </motion.div>
                ) : (
                  <>
                    <Check className="w-4 h-4" />
                    Odpovědět
                  </>
                )}
              </button>
            )}

            {/* Reward info */}
            <p className="text-center text-xs text-muted-foreground mt-3">
              <Star className="w-3 h-3 inline text-amber-500 fill-current" /> Až {question.reward_stars} hvězd za správnou odpověď
            </p>
          </motion.div>
        )}

        {/* ===== RESULT STATE ===== */}
        {gameState === "result" && result && (
          <motion.div
            key="result"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <ResultScreen
              result={result}
              onPlayAgain={handlePlayAgain}
              onBack={handleBack}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
