"use client"

import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import { UserStats } from "@/lib/types"
import { Flame, Star } from "lucide-react"
import { StatsSkeletons } from "@/components/ui/skeletons"

interface DashboardStatsProps {
  telegramId: number
}

export function DashboardStats({ telegramId }: DashboardStatsProps) {
  const { data: stats, isLoading } = useQuery<UserStats>({
    queryKey: ["user-stats", telegramId],
    queryFn: () => apiClient.getStats(telegramId),
    staleTime: 30 * 1000, // 30 seconds - stats update often
    gcTime: 5 * 60 * 1000, // 5 minutes
  })

  if (isLoading) {
    return <StatsSkeletons />
  }

  return (
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
  )
}
