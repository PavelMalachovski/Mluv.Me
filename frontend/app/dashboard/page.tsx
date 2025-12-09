"use client"

import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import Image from "next/image"
import { useAuthStore } from "@/lib/auth-store"
import { apiClient } from "@/lib/api-client"
import { UserStats, ReviewStats } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { IllustratedHeader } from "@/components/ui/IllustratedHeader"
import { Mic, BookOpen, Flame, Star, MessageCircle, Trophy, Clock, TrendingUp } from "lucide-react"

export default function DashboardPage() {
  const router = useRouter()
  const user = useAuthStore((state) => state.user)

  const { data: stats, isLoading: statsLoading } = useQuery<UserStats>({
    queryKey: ["user-stats", user?.telegram_id],
    queryFn: () => apiClient.getStats(user!.telegram_id),
    enabled: !!user?.telegram_id,
  })

  const { data: reviewStats } = useQuery<ReviewStats>({
    queryKey: ["review-stats", user?.telegram_id],
    queryFn: () => apiClient.getReviewStats(user!.telegram_id),
    enabled: !!user?.telegram_id,
  })

  if (!user) {
    router.push("/login")
    return null
  }

  if (statsLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center cream-bg">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  // Calculate today's progress (example: goal is 10 messages)
  const dailyGoal = 10
  const todayMessages = stats?.messages_count || 0
  const progress = Math.min(100, (todayMessages / dailyGoal) * 100)

  return (
    <div className="min-h-screen cream-bg landscape-bg pb-24">
      <IllustratedHeader title="Dashboard" />

      <div className="mx-auto max-w-2xl px-4 pt-6">
        {/* Welcome Message */}
        <div className="mb-6 text-center">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100">
            Ahoj, {user.first_name}! 👋
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Ready to practice Czech today?
          </p>
        </div>

        {/* Stats Header */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          {/* Streak Card */}
          <div className="illustrated-card p-4 flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
              <Flame className="h-6 w-6 text-orange-500" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {stats?.streak || 0}
              </div>
              <div className="text-xs text-gray-500">Day Streak</div>
            </div>
          </div>

          {/* Stars Card */}
          <div className="illustrated-card p-4 flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-yellow-100 dark:bg-yellow-900/30 flex items-center justify-center">
              <Star className="h-6 w-6 text-yellow-500" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {stats?.stars || 0}
              </div>
              <div className="text-xs text-gray-500">Total Stars</div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <Button
            onClick={() => router.push("/dashboard/practice")}
            className="h-24 flex flex-col items-center justify-center gap-2 bg-gradient-to-br from-primary to-purple-600 hover:from-primary/90 hover:to-purple-600/90 text-white rounded-xl shadow-lg"
          >
            <Mic className="h-8 w-8" />
            <span className="text-lg font-semibold">Practice</span>
          </Button>

          <Button
            onClick={() => router.push("/dashboard/review")}
            variant="outline"
            className="h-24 flex flex-col items-center justify-center gap-2 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-xl shadow-lg border-2"
          >
            <BookOpen className="h-8 w-8 text-green-600" />
            <span className="text-lg font-semibold text-gray-800 dark:text-gray-200">Review</span>
            {reviewStats && reviewStats.due_today > 0 && (
              <span className="absolute top-2 right-2 bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                {reviewStats.due_today}
              </span>
            )}
          </Button>
        </div>

        {/* Today's Progress */}
        <div className="illustrated-card p-4 mb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-800 dark:text-gray-100 flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              Today&apos;s Progress
            </h3>
            <span className="text-sm text-gray-500">{Math.round(progress)}%</span>
          </div>

          {/* Progress bar */}
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden mb-3">
            <div
              className="h-full bg-gradient-to-r from-green-400 to-green-500 transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Stats row */}
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="flex items-center justify-center gap-1 text-lg font-semibold text-gray-800 dark:text-gray-100">
                <MessageCircle className="h-4 w-4 text-blue-500" />
                {stats?.messages_count || 0}
              </div>
              <div className="text-xs text-gray-500">Messages</div>
            </div>
            <div>
              <div className="flex items-center justify-center gap-1 text-lg font-semibold text-gray-800 dark:text-gray-100">
                <BookOpen className="h-4 w-4 text-green-500" />
                {reviewStats?.due_today || 0}
              </div>
              <div className="text-xs text-gray-500">To Review</div>
            </div>
            <div>
              <div className="flex items-center justify-center gap-1 text-lg font-semibold text-gray-800 dark:text-gray-100">
                <Trophy className="h-4 w-4 text-yellow-500" />
                {stats?.correct_percent || 0}%
              </div>
              <div className="text-xs text-gray-500">Accuracy</div>
            </div>
          </div>
        </div>

        {/* Achievements Preview */}
        <div className="illustrated-card p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-800 dark:text-gray-100 flex items-center gap-2">
              <Trophy className="h-5 w-5 text-yellow-500" />
              Achievements
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push("/dashboard/profile")}
              className="text-xs"
            >
              View all →
            </Button>
          </div>

          <div className="flex gap-3 overflow-x-auto pb-2">
            {stats?.streak && stats.streak >= 7 && (
              <div className="flex-shrink-0 flex flex-col items-center p-3 rounded-lg bg-orange-50 dark:bg-orange-900/20">
                <span className="text-3xl mb-1">🔥</span>
                <span className="text-xs font-medium text-orange-700 dark:text-orange-400">Week Warrior</span>
              </div>
            )}
            {stats?.messages_count && stats.messages_count >= 50 && (
              <div className="flex-shrink-0 flex flex-col items-center p-3 rounded-lg bg-purple-50 dark:bg-purple-900/20">
                <span className="text-3xl mb-1">💬</span>
                <span className="text-xs font-medium text-purple-700 dark:text-purple-400">Chatty</span>
              </div>
            )}
            {stats?.stars && stats.stars >= 100 && (
              <div className="flex-shrink-0 flex flex-col items-center p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20">
                <span className="text-3xl mb-1">⭐</span>
                <span className="text-xs font-medium text-yellow-700 dark:text-yellow-400">Star Collector</span>
              </div>
            )}

            {/* Placeholder for locked achievements */}
            <div className="flex-shrink-0 flex flex-col items-center p-3 rounded-lg bg-gray-100 dark:bg-gray-800 opacity-50">
              <span className="text-3xl mb-1">🔒</span>
              <span className="text-xs font-medium text-gray-500">Keep going!</span>
            </div>
          </div>
        </div>

        {/* Motivational Mascot */}
        <div className="mt-6 text-center">
          <Image
            src="/images/mascot/honzik-waving.png"
            alt="Honzík"
            width={100}
            height={100}
            className="mx-auto mb-2"
          />
          <p className="text-sm text-gray-600 dark:text-gray-400 italic">
            {stats?.streak && stats.streak > 0
              ? `Skvělé! ${stats.streak} day streak! 🎉`
              : "Let's start learning Czech today! 🇨🇿"
            }
          </p>
        </div>
      </div>
    </div>
  )
}
