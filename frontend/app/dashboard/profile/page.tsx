"use client"

import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/auth-store"
import { apiClient } from "@/lib/api-client"
import { UserStats } from "@/lib/types"
import { Award, Calendar, Flame, MessageCircle, Star, Target, TrendingUp } from "lucide-react"
import { Card } from "@/components/ui/card"

export default function ProfilePage() {
  const router = useRouter()
  const user = useAuthStore((state) => state.user)

  const { data: stats, isLoading } = useQuery<UserStats>({
    queryKey: ["user-stats", user?.id],
    queryFn: () => apiClient.getStats(user!.id),
    enabled: !!user?.id,
  })

  if (!user) {
    router.push("/login")
    return null
  }

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-2xl p-6 animate-fade-in">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Profile</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">Your learning progress and achievements</p>
      </div>

      {/* User Card */}
      <Card className="mb-6 overflow-hidden hover:shadow-lg transition-shadow dark:border-gray-800">
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 dark:from-purple-600 dark:to-purple-700 p-6">
          <div className="flex items-center gap-4">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-white/20 dark:bg-white/10 text-4xl backdrop-blur-sm">
              🇨🇿
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-white">
                {user.first_name} {user.last_name || ""}
              </h2>
              <p className="text-purple-100 dark:text-purple-200">@{user.username || "czechlearner"}</p>
              <div className="mt-2 flex items-center gap-3 text-sm text-white">
                <span className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  Joined {new Date(user.created_at || Date.now()).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 divide-x border-t bg-white dark:bg-gray-900 dark:border-gray-800 dark:divide-gray-800">
          <div className="p-4 text-center hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-colors cursor-pointer">
            <div className="mb-1 text-2xl font-bold text-purple-600 dark:text-purple-400">{stats?.streak || 0}</div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Day Streak</div>
          </div>
          <div className="p-4 text-center hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-colors cursor-pointer">
            <div className="mb-1 text-2xl font-bold text-yellow-600 dark:text-yellow-400">{stats?.total_stars || 0}</div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Total Stars</div>
          </div>
          <div className="p-4 text-center hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-colors cursor-pointer">
            <div className="mb-1 text-2xl font-bold text-green-600 dark:text-green-400">{stats?.messages_today || 0}</div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Today</div>
          </div>
        </div>
      </Card>

      {/* Stats Grid */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2">
        <Card className="p-4 hover:shadow-md transition-shadow cursor-pointer dark:border-gray-800 dark:bg-gray-900">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-purple-100 dark:bg-purple-900/30">
              <MessageCircle className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {stats?.total_messages || 0}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Total Messages</div>
            </div>
          </div>
        </Card>

        <Card className="p-4 hover:shadow-md transition-shadow cursor-pointer dark:border-gray-800 dark:bg-gray-900">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30">
              <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {stats?.correctness_avg || 0}%
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Avg Correctness</div>
            </div>
          </div>
        </Card>

        <Card className="p-4 hover:shadow-md transition-shadow cursor-pointer dark:border-gray-800 dark:bg-gray-900">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900/30">
              <Target className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {stats?.words_learned || 0}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Words Learned</div>
            </div>
          </div>
        </Card>

        <Card className="p-4 hover:shadow-md transition-shadow cursor-pointer dark:border-gray-800 dark:bg-gray-900">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-orange-100 dark:bg-orange-900/30">
              <Flame className="h-6 w-6 text-orange-600 dark:text-orange-400" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {stats?.max_streak || 0}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Longest Streak</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Level Card */}
      <Card className="mb-6 p-6 hover:shadow-md transition-shadow dark:border-gray-800 dark:bg-gray-900">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Czech Level</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">Your current proficiency</p>
          </div>
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-purple-100 dark:bg-purple-900/30">
            <Award className="h-6 w-6 text-purple-600 dark:text-purple-400" />
          </div>
        </div>

        <div className="mb-3 flex items-baseline gap-2">
          <span className="text-3xl font-bold text-purple-600 dark:text-purple-400">
            {user.level?.toUpperCase() || "A1"}
          </span>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            {user.level === "beginner" && "Začátečník"}
            {user.level === "intermediate" && "Středně pokročilý"}
            {user.level === "advanced" && "Pokročilý"}
            {user.level === "native" && "Rodilý"}
          </span>
        </div>

        <div className="h-2 overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
          <div
            className="h-full bg-gradient-to-r from-purple-500 to-purple-600 dark:from-purple-400 dark:to-purple-500 transition-all duration-500"
            style={{
              width: `${
                user.level === "beginner"
                  ? "25%"
                  : user.level === "intermediate"
                  ? "50%"
                  : user.level === "advanced"
                  ? "75%"
                  : "100%"
              }`,
            }}
          />
        </div>
      </Card>

      {/* Achievements */}
      <Card className="p-6 hover:shadow-md transition-shadow dark:border-gray-800 dark:bg-gray-900">
        <h3 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Achievements</h3>
        <div className="grid gap-3 sm:grid-cols-2">
          {stats?.streak && stats.streak >= 7 && (
            <div className="flex items-center gap-3 rounded-lg bg-orange-50 dark:bg-orange-900/20 p-3 hover:bg-orange-100 dark:hover:bg-orange-900/30 transition-colors cursor-pointer">
              <div className="text-2xl">🔥</div>
              <div>
                <div className="font-medium text-gray-900 dark:text-gray-100">Week Warrior</div>
                <div className="text-xs text-gray-500 dark:text-gray-400">7 day streak</div>
              </div>
            </div>
          )}

          {stats?.total_messages && stats.total_messages >= 50 && (
            <div className="flex items-center gap-3 rounded-lg bg-purple-50 dark:bg-purple-900/20 p-3 hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors cursor-pointer">
              <div className="text-2xl">💬</div>
              <div>
                <div className="font-medium text-gray-900 dark:text-gray-100">Chatty</div>
                <div className="text-xs text-gray-500 dark:text-gray-400">50+ messages sent</div>
              </div>
            </div>
          )}

          {stats?.total_stars && stats.total_stars >= 100 && (
            <div className="flex items-center gap-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 p-3 hover:bg-yellow-100 dark:hover:bg-yellow-900/30 transition-colors cursor-pointer">
              <div className="text-2xl">⭐</div>
              <div>
                <div className="font-medium text-gray-900 dark:text-gray-100">Star Collector</div>
                <div className="text-xs text-gray-500 dark:text-gray-400">100+ stars earned</div>
              </div>
            </div>
          )}

          {stats?.words_learned && stats.words_learned >= 25 && (
            <div className="flex items-center gap-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 p-3 hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors cursor-pointer">
              <div className="text-2xl">📚</div>
              <div>
                <div className="font-medium text-gray-900 dark:text-gray-100">Word Master</div>
                <div className="text-xs text-gray-500 dark:text-gray-400">25+ words learned</div>
              </div>
            </div>
          )}
        </div>

        {/* Message if no achievements yet */}
        {(!stats?.streak || stats.streak < 7) &&
         (!stats?.total_messages || stats.total_messages < 50) &&
         (!stats?.total_stars || stats.total_stars < 100) &&
         (!stats?.words_learned || stats.words_learned < 25) && (
          <div className="text-center py-8">
            <div className="text-4xl mb-2">🎯</div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Keep practicing to unlock achievements!</p>
          </div>
        )}
      </Card>
    </div>
  )
}
