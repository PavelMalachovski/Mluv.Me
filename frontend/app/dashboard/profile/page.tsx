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
    queryKey: ["user-stats"],
    queryFn: () => apiClient.get("/api/v1/stats/me"),
    enabled: !!user,
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
    <div className="mx-auto max-w-2xl p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
        <p className="text-sm text-gray-500">Your learning progress and achievements</p>
      </div>

      {/* User Card */}
      <Card className="mb-6 overflow-hidden">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-6">
          <div className="flex items-center gap-4">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-white/20 text-4xl backdrop-blur-sm">
              🇨🇿
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-white">
                {user.first_name} {user.last_name || ""}
              </h2>
              <p className="text-blue-100">@{user.username || "czechlearner"}</p>
              <div className="mt-2 flex items-center gap-3 text-sm text-white">
                <span className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  Joined {new Date(user.created_at || Date.now()).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 divide-x border-t">
          <div className="p-4 text-center">
            <div className="mb-1 text-2xl font-bold text-blue-600">{stats?.streak || 0}</div>
            <div className="text-xs text-gray-500">Day Streak</div>
          </div>
          <div className="p-4 text-center">
            <div className="mb-1 text-2xl font-bold text-yellow-600">{stats?.total_stars || 0}</div>
            <div className="text-xs text-gray-500">Total Stars</div>
          </div>
          <div className="p-4 text-center">
            <div className="mb-1 text-2xl font-bold text-green-600">{stats?.messages_today || 0}</div>
            <div className="text-xs text-gray-500">Messages Today</div>
          </div>
        </div>
      </Card>

      {/* Stats Grid */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2">
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-100">
              <MessageCircle className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {stats?.total_messages || 0}
              </div>
              <div className="text-sm text-gray-500">Total Messages</div>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {stats?.correctness_avg || 0}%
              </div>
              <div className="text-sm text-gray-500">Avg Correctness</div>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-purple-100">
              <Target className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {stats?.words_learned || 0}
              </div>
              <div className="text-sm text-gray-500">Words Learned</div>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-orange-100">
              <Flame className="h-6 w-6 text-orange-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {stats?.max_streak || 0}
              </div>
              <div className="text-sm text-gray-500">Longest Streak</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Level Card */}
      <Card className="mb-6 p-6">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Czech Level</h3>
            <p className="text-sm text-gray-500">Your current proficiency</p>
          </div>
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-yellow-100">
            <Award className="h-6 w-6 text-yellow-600" />
          </div>
        </div>

        <div className="mb-3 flex items-baseline gap-2">
          <span className="text-3xl font-bold text-blue-600">
            {user.level?.toUpperCase() || "A1"}
          </span>
          <span className="text-sm text-gray-500">
            {user.level === "beginner" && "Začátečník"}
            {user.level === "intermediate" && "Středně pokročilý"}
            {user.level === "advanced" && "Pokročilý"}
            {user.level === "native" && "Rodilý"}
          </span>
        </div>

        <div className="h-2 overflow-hidden rounded-full bg-gray-100">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
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
      <Card className="p-6">
        <h3 className="mb-4 text-lg font-semibold text-gray-900">Achievements</h3>
        <div className="grid gap-3 sm:grid-cols-2">
          {stats?.streak && stats.streak >= 7 && (
            <div className="flex items-center gap-3 rounded-lg bg-orange-50 p-3">
              <div className="text-2xl">🔥</div>
              <div>
                <div className="font-medium text-gray-900">Week Warrior</div>
                <div className="text-xs text-gray-500">7 day streak</div>
              </div>
            </div>
          )}

          {stats?.total_messages && stats.total_messages >= 50 && (
            <div className="flex items-center gap-3 rounded-lg bg-blue-50 p-3">
              <div className="text-2xl">💬</div>
              <div>
                <div className="font-medium text-gray-900">Chatty</div>
                <div className="text-xs text-gray-500">50+ messages sent</div>
              </div>
            </div>
          )}

          {stats?.total_stars && stats.total_stars >= 100 && (
            <div className="flex items-center gap-3 rounded-lg bg-yellow-50 p-3">
              <div className="text-2xl">⭐</div>
              <div>
                <div className="font-medium text-gray-900">Star Collector</div>
                <div className="text-xs text-gray-500">100+ stars earned</div>
              </div>
            </div>
          )}

          {stats?.words_learned && stats.words_learned >= 25 && (
            <div className="flex items-center gap-3 rounded-lg bg-purple-50 p-3">
              <div className="text-2xl">📚</div>
              <div>
                <div className="font-medium text-gray-900">Word Master</div>
                <div className="text-xs text-gray-500">25+ words learned</div>
              </div>
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}
