"use client"

import { useState, useEffect } from "react"
import { Trophy, Flame, MessageCircle, Star, Target, Crown, Medal, Award, ChevronDown } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { apiClient } from "@/lib/api-client"
import { useAuthStore } from "@/lib/auth-store"

interface LeaderboardEntry {
  rank: number
  telegram_id: number
  first_name: string
  username: string | null
  level: string
  score: number | string
  total_messages: number
  total_stars: number
  max_streak: number
  avg_correctness: number | null
}

interface LeaderboardData {
  metric: string
  period: string
  leaderboard: LeaderboardEntry[]
  user_rank: number | null
  user_score: number | null
}

type MetricType = 'stars' | 'streak' | 'messages' | 'accuracy'

const METRIC_CONFIG: Record<MetricType, { icon: typeof Trophy; label: string; color: string }> = {
  stars: { icon: Star, label: "Hvězdy", color: "text-yellow-500" },
  streak: { icon: Flame, label: "Série", color: "text-orange-500" },
  messages: { icon: MessageCircle, label: "Zprávy", color: "text-blue-500" },
  accuracy: { icon: Target, label: "Přesnost", color: "text-green-500" },
}

const RANK_ICONS = [Crown, Medal, Award]
const RANK_COLORS = ["text-yellow-500", "text-gray-400", "text-amber-600"]

interface LeaderboardProps {
  className?: string
}

export function Leaderboard({ className = "" }: LeaderboardProps) {
  const [metric, setMetric] = useState<MetricType>('stars')
  const [data, setData] = useState<LeaderboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [showMetricSelector, setShowMetricSelector] = useState(false)
  const user = useAuthStore((state) => state.user)

  useEffect(() => {
    if (user?.telegram_id) {
      loadLeaderboard()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [metric, user?.telegram_id])

  const loadLeaderboard = async () => {
    if (!user?.telegram_id) return
    setLoading(true)
    try {
      const result = await apiClient.getLeaderboard(metric, 10, user.telegram_id)
      setData(result)
    } catch (error) {
      console.error("Failed to load leaderboard:", error)
    } finally {
      setLoading(false)
    }
  }

  const MetricIcon = METRIC_CONFIG[metric].icon

  const formatScore = (entry: LeaderboardEntry) => {
    if (metric === 'accuracy') {
      return `${entry.avg_correctness?.toFixed(1) || 0}%`
    }
    return entry.score.toString()
  }

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 p-4 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Trophy className="h-6 w-6" />
            <h2 className="text-lg font-bold">Týdenní žebříček</h2>
          </div>

          {/* Metric Selector */}
          <button
            onClick={() => setShowMetricSelector(!showMetricSelector)}
            className="flex items-center gap-1 bg-white/20 hover:bg-white/30 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors"
          >
            <MetricIcon className="h-4 w-4" />
            {METRIC_CONFIG[metric].label}
            <ChevronDown className={`h-4 w-4 transition-transform ${showMetricSelector ? 'rotate-180' : ''}`} />
          </button>
        </div>

        {/* Metric Dropdown */}
        <AnimatePresence>
          {showMetricSelector && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="mt-3 overflow-hidden"
            >
              <div className="grid grid-cols-2 gap-2">
                {(Object.keys(METRIC_CONFIG) as MetricType[]).map((m) => {
                  const config = METRIC_CONFIG[m]
                  const Icon = config.icon
                  return (
                    <button
                      key={m}
                      onClick={() => {
                        setMetric(m)
                        setShowMetricSelector(false)
                      }}
                      className={`flex items-center gap-2 p-2 rounded-lg text-sm font-medium transition-colors ${
                        metric === m
                          ? 'bg-white text-purple-600'
                          : 'bg-white/10 hover:bg-white/20 text-white'
                      }`}
                    >
                      <Icon className="h-4 w-4" />
                      {config.label}
                    </button>
                  )
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Leaderboard List */}
      <div className="p-4">
        {loading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-14 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : data?.leaderboard.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Trophy className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>Zatím žádní uživatelé</p>
            <p className="text-sm">Začni procvičovat, abys se dostal na žebříček!</p>
          </div>
        ) : (
          <div className="space-y-2">
            {data?.leaderboard.map((entry, index) => {
              const isCurrentUser = entry.telegram_id === user?.telegram_id
              const RankIcon = index < 3 ? RANK_ICONS[index] : null
              const rankColor = index < 3 ? RANK_COLORS[index] : "text-gray-400"

              return (
                <motion.div
                  key={entry.telegram_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`flex items-center gap-3 p-3 rounded-xl transition-colors ${
                    isCurrentUser
                      ? 'bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/30 dark:to-indigo-900/30 ring-2 ring-purple-500'
                      : 'bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  {/* Rank */}
                  <div className={`flex items-center justify-center w-8 h-8 ${rankColor}`}>
                    {RankIcon ? (
                      <RankIcon className="h-6 w-6" />
                    ) : (
                      <span className="font-bold text-lg">{entry.rank}</span>
                    )}
                  </div>

                  {/* User Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={`font-semibold truncate ${isCurrentUser ? 'text-purple-600 dark:text-purple-400' : 'text-gray-800 dark:text-gray-200'}`}>
                        {entry.first_name}
                        {isCurrentUser && " (ty)"}
                      </span>
                      {entry.username && (
                        <span className="text-xs text-gray-400 truncate">
                          @{entry.username}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-gray-500">
                      <span>📊 {entry.level}</span>
                      <span>💬 {entry.total_messages}</span>
                      <span>🔥 {entry.max_streak}</span>
                    </div>
                  </div>

                  {/* Score */}
                  <div className={`flex items-center gap-1 font-bold text-lg ${METRIC_CONFIG[metric].color}`}>
                    <MetricIcon className="h-5 w-5" />
                    {formatScore(entry)}
                  </div>
                </motion.div>
              )
            })}
          </div>
        )}

        {/* User's rank if not in top 10 */}
        {data && data.user_rank && data.user_rank > 10 && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-500 mb-2">Tvoje pozice:</p>
            <div className="flex items-center gap-3 p-3 rounded-xl bg-purple-50 dark:bg-purple-900/30">
              <div className="flex items-center justify-center w-8 h-8 text-purple-600 font-bold">
                #{data.user_rank}
              </div>
              <div className="flex-1">
                <span className="font-semibold text-purple-600 dark:text-purple-400">
                  {user?.first_name} (ty)
                </span>
              </div>
              <div className={`flex items-center gap-1 font-bold text-lg ${METRIC_CONFIG[metric].color}`}>
                <MetricIcon className="h-5 w-5" />
                {data.user_score}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
