"use client"

import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import { UserStats, ReviewStats } from "@/lib/types"
import { TrendingUp, MessageCircle, BookOpen, Trophy } from "lucide-react"
import { ProgressCardSkeleton } from "@/components/ui/skeletons"

interface DashboardProgressProps {
  telegramId: number
}

export function DashboardProgress({ telegramId }: DashboardProgressProps) {
  const { data: stats, isLoading: statsLoading } = useQuery<UserStats>({
    queryKey: ["user-stats", telegramId],
    queryFn: () => apiClient.getStats(telegramId),
    staleTime: 30 * 1000,
  })

  const { data: reviewStats, isLoading: reviewLoading } = useQuery<ReviewStats>({
    queryKey: ["review-stats", telegramId],
    queryFn: () => apiClient.getReviewStats(telegramId),
    staleTime: 60 * 1000, // 1 minute
  })

  if (statsLoading || reviewLoading) {
    return <ProgressCardSkeleton />
  }

  // Calculate today's progress (goal is 10 messages)
  const dailyGoal = 10
  const todayMessages = stats?.messages_count || 0
  const progress = Math.min(100, (todayMessages / dailyGoal) * 100)

  return (
    <div className="illustrated-card p-4 mb-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-gray-800 dark:text-gray-100 flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-primary" />
          Dnešní pokrok
        </h3>
        <span className="text-sm text-gray-500">{Math.round(progress)}%</span>
      </div>

      {/* Progress bar with animation */}
      <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden mb-3">
        <div
          className="h-full bg-gradient-to-r from-green-400 to-green-500 transition-all duration-700 ease-out"
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
          <div className="text-xs text-gray-500">Zpráv</div>
        </div>
        <div>
          <div className="flex items-center justify-center gap-1 text-lg font-semibold text-gray-800 dark:text-gray-100">
            <BookOpen className="h-4 w-4 text-green-500" />
            {reviewStats?.due_today || 0}
          </div>
          <div className="text-xs text-gray-500">K opakování</div>
        </div>
        <div>
          <div className="flex items-center justify-center gap-1 text-lg font-semibold text-gray-800 dark:text-gray-100">
            <Trophy className="h-4 w-4 text-yellow-500" />
            {stats?.correct_percent || 0}%
          </div>
          <div className="text-xs text-gray-500">Přesnost</div>
        </div>
      </div>
    </div>
  )
}
