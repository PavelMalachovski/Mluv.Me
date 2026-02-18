"use client"

import { Suspense, useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { Gamepad2, BookOpen, Target, Trophy, Star, BookmarkCheck } from "lucide-react"
import { useAuthStore } from "@/lib/auth-store"
import { ProfileMiniGames } from "@/components/features/ProfileMiniGames"
import { ProfileGrammar } from "@/components/features/ProfileGrammar"
import { SavedWordsTab } from "@/components/features/SavedWordsTab"
import { apiClient } from "@/lib/api-client"
import { ChallengeList } from "@/components/features/ChallengeCard"

// ===== Types =====

interface Challenge {
  id: number
  code: string
  type: "daily" | "weekly"
  title: string
  description: string
  goal_type: string
  goal_value: number
  reward_stars: number
  progress: number
  completed: boolean
  reward_claimed: boolean
  expires_at?: string
  week_start?: string
}

// ===== Tab definitions =====

type LearnTab = "games" | "grammar" | "challenges" | "words"

const TABS: { id: LearnTab; label: string; icon: React.ElementType; emoji: string }[] = [
  { id: "words", label: "Slovíčka", icon: BookmarkCheck, emoji: "📚" },
  { id: "grammar", label: "Gramatika", icon: BookOpen, emoji: "📖" },
  { id: "games", label: "Mini hry", icon: Gamepad2, emoji: "🎮" },
  { id: "challenges", label: "Výzvy", icon: Target, emoji: "🏆" },
]

// ===== Challenges Section =====

function ChallengesSection({ telegramId }: { telegramId: number }) {
  const [dailyChallenge, setDailyChallenge] = useState<Challenge | null>(null)
  const [weeklyChallenges, setWeeklyChallenges] = useState<Challenge[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadChallenges()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [telegramId])

  const loadChallenges = async () => {
    setLoading(true)
    try {
      const result = await apiClient.getAllChallenges(telegramId)
      setDailyChallenge(result?.daily_challenge || null)
      setWeeklyChallenges(result?.weekly_challenges || [])
    } catch (error) {
      console.error("Failed to load challenges:", error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-32 bg-gray-100 dark:bg-gray-700 rounded-2xl animate-pulse" />
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Daily challenge */}
      {dailyChallenge && (
        <div>
          <h3 className="text-sm font-bold text-foreground mb-3 flex items-center gap-2">
            <span className="text-lg">📅</span>
            Denní výzva
          </h3>
          <ChallengeList
            challenges={[dailyChallenge]}
            onRewardClaimed={loadChallenges}
          />
        </div>
      )}

      {/* Weekly challenges */}
      {weeklyChallenges.length > 0 && (
        <div>
          <h3 className="text-sm font-bold text-foreground mb-3 flex items-center gap-2">
            <span className="text-lg">📆</span>
            Týdenní výzvy
          </h3>
          <ChallengeList
            challenges={weeklyChallenges}
            onRewardClaimed={loadChallenges}
          />
        </div>
      )}

      {!dailyChallenge && weeklyChallenges.length === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          <Target className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p className="text-sm">Žádné aktivní výzvy</p>
          <p className="text-xs mt-1">Nové výzvy se objeví brzy!</p>
        </div>
      )}
    </div>
  )
}

// ===== Main Page =====

function LearnContent() {
  const searchParams = useSearchParams()
  const user = useAuthStore((state) => state.user)
  const initialTab = (searchParams.get("tab") as LearnTab) || "words"
  const [activeTab, setActiveTab] = useState<LearnTab>(
    ["games", "grammar", "words", "challenges"].includes(initialTab) ? initialTab : "words"
  )

  if (!user) return null

  return (
    <div className="min-h-screen cream-bg landscape-bg pb-24">
      {/* Header */}
      <div className="illustrated-header relative pb-6">
        <h1 className="illustrated-header-title">Procvičování</h1>
        <p className="text-center text-sm text-white/80 mt-1">Hry, gramatika a výzvy</p>
      </div>

      <div className="mx-auto max-w-2xl px-4 pt-4">
        {/* Tab Switcher */}
        <div className="flex gap-1 p-1 bg-gray-100 dark:bg-gray-800 rounded-2xl mb-6">
          {TABS.map((tab) => {
            const isActive = activeTab === tab.id
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? "bg-white dark:bg-gray-700 text-purple-600 dark:text-purple-400 shadow-sm"
                    : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          {activeTab === "games" && (
            <motion.div
              key="games"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              <ProfileMiniGames
                userId={user.id}
                telegramId={user.telegram_id}
                level={user.level}
              />
            </motion.div>
          )}

          {activeTab === "grammar" && (
            <motion.div
              key="grammar"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              <ProfileGrammar
                userId={user.id}
                telegramId={user.telegram_id}
                level={user.level}
              />
            </motion.div>
          )}

          {activeTab === "challenges" && (
            <motion.div
              key="challenges"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              <ChallengesSection telegramId={user.telegram_id} />
            </motion.div>
          )}

          {activeTab === "words" && (
            <motion.div
              key="words"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              <SavedWordsTab telegramId={user.telegram_id} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

export default function LearnPage() {
  const router = useRouter()
  const user = useAuthStore((state) => state.user)

  useEffect(() => {
    if (!user) {
      router.push("/login")
    }
  }, [user, router])

  if (!user) return null

  return (
    <Suspense fallback={
      <div className="flex min-h-screen items-center justify-center cream-bg">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    }>
      <LearnContent />
    </Suspense>
  )
}
