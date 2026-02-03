"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Trophy, Target, Calendar, Star, ArrowLeft, RefreshCw } from "lucide-react"
import Link from "next/link"
import { apiClient } from "@/lib/api-client"
import { useAuthStore } from "@/lib/auth-store"
import { IllustratedHeader } from "@/components/ui/IllustratedHeader"
import { ChallengeList } from "@/components/features/ChallengeCard"
import { Leaderboard } from "@/components/features/Leaderboard"

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

interface ChallengesData {
  daily_challenge: Challenge | null
  weekly_challenges: Challenge[]
  stats: {
    daily_completed: number
    weekly_completed: number
    weekly_total: number
  }
  current_date: string
}

export default function ChallengesPage() {
  const [data, setData] = useState<ChallengesData | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [activeTab, setActiveTab] = useState<'challenges' | 'leaderboard'>('challenges')
  const user = useAuthStore((state) => state.user)

  useEffect(() => {
    if (user?.telegram_id) {
      loadChallenges()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.telegram_id])

  const loadChallenges = async () => {
    if (!user?.telegram_id) return
    setLoading(true)
    try {
      const result = await apiClient.getAllChallenges(user.telegram_id)
      setData(result)
    } catch (error) {
      console.error("Failed to load challenges:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await loadChallenges()
    setRefreshing(false)
  }

  const handleRewardClaimed = () => {
    // Reload to update stars
    loadChallenges()
  }

  const totalCompleted = (data?.stats.daily_completed || 0) + (data?.stats.weekly_completed || 0)
  const totalChallenges = 1 + (data?.stats.weekly_total || 0)

  return (
    <div className="min-h-screen pb-24 bg-gradient-to-b from-purple-50 to-white dark:from-gray-900 dark:to-gray-800">
      <IllustratedHeader title="Výzvy a žebříček" subtitle="Plň výzvy a soutěž s ostatními!" />

      {/* Back button */}
      <div className="px-4 pt-4">
        <Link
          href="/dashboard"
          className="inline-flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
        >
          <ArrowLeft className="h-4 w-4" />
          Zpět na přehled
        </Link>
      </div>

      <div className="max-w-2xl mx-auto px-4 pt-4">
        {/* Stats cards */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-2xl p-4 shadow-lg"
          >
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500 to-indigo-600 text-white">
                <Target className="h-6 w-6" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                  {totalCompleted}/{totalChallenges}
                </p>
                <p className="text-sm text-gray-500">Dokončené výzvy</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-2xl p-4 shadow-lg"
          >
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-gradient-to-br from-yellow-400 to-amber-500 text-white">
                <Star className="h-6 w-6" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                  {(data?.daily_challenge?.reward_stars || 0) +
                    (data?.weekly_challenges.reduce((sum, c) => sum + c.reward_stars, 0) || 0)}
                </p>
                <p className="text-sm text-gray-500">Hvězd k získání</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Tab selector */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('challenges')}
            className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-medium transition-all ${
              activeTab === 'challenges'
                ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg'
                : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            <Calendar className="h-5 w-5" />
            Výzvy
          </button>
          <button
            onClick={() => setActiveTab('leaderboard')}
            className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-medium transition-all ${
              activeTab === 'leaderboard'
                ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg'
                : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            <Trophy className="h-5 w-5" />
            Žebříček
          </button>
        </div>

        {/* Content */}
        {activeTab === 'challenges' ? (
          <div className="space-y-6">
            {/* Refresh button */}
            <div className="flex justify-end">
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="flex items-center gap-2 text-sm text-purple-600 hover:text-purple-700 disabled:opacity-50"
              >
                <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
                Aktualizovat
              </button>
            </div>

            {loading ? (
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-48 bg-gray-100 dark:bg-gray-700 rounded-2xl animate-pulse" />
                ))}
              </div>
            ) : (
              <>
                {/* Daily challenge */}
                {data?.daily_challenge && (
                  <div>
                    <h2 className="text-lg font-bold text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
                      <span className="text-2xl">📅</span>
                      Denní výzva
                    </h2>
                    <ChallengeList
                      challenges={[data.daily_challenge]}
                      onRewardClaimed={handleRewardClaimed}
                    />
                  </div>
                )}

                {/* Weekly challenges */}
                {data?.weekly_challenges && data.weekly_challenges.length > 0 && (
                  <div>
                    <h2 className="text-lg font-bold text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
                      <span className="text-2xl">📆</span>
                      Týdenní výzvy
                    </h2>
                    <ChallengeList
                      challenges={data.weekly_challenges}
                      onRewardClaimed={handleRewardClaimed}
                    />
                  </div>
                )}

                {/* Empty state */}
                {!data?.daily_challenge && (!data?.weekly_challenges || data.weekly_challenges.length === 0) && (
                  <div className="text-center py-12 text-gray-500">
                    <Target className="h-16 w-16 mx-auto mb-4 opacity-50" />
                    <p className="text-lg font-medium">Žádné výzvy k dispozici</p>
                    <p className="text-sm">Zkus to znovu později</p>
                  </div>
                )}
              </>
            )}
          </div>
        ) : (
          <Leaderboard />
        )}

        {/* Info card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-8 bg-gradient-to-r from-purple-100 to-indigo-100 dark:from-purple-900/30 dark:to-indigo-900/30 rounded-2xl p-4"
        >
          <h3 className="font-bold text-purple-800 dark:text-purple-200 mb-2">
            💡 Tipy pro výzvy
          </h3>
          <ul className="text-sm text-purple-700 dark:text-purple-300 space-y-1">
            <li>• Denní výzvy se resetují o půlnoci</li>
            <li>• Týdenní výzvy začínají v pondělí</li>
            <li>• Nezapomeň si převzít odměny!</li>
            <li>• Procvičuj pravidelně pro vyšší pozici v žebříčku</li>
          </ul>
        </motion.div>
      </div>
    </div>
  )
}
