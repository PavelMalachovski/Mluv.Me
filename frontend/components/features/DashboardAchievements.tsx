"use client"

import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { apiClient } from "@/lib/api-client"
import { UserStats } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { Trophy } from "lucide-react"
import { AchievementsSkeleton } from "@/components/ui/skeletons"

interface DashboardAchievementsProps {
  telegramId: number
}

export function DashboardAchievements({ telegramId }: DashboardAchievementsProps) {
  const router = useRouter()

  const { data: stats, isLoading } = useQuery<UserStats>({
    queryKey: ["user-stats", telegramId],
    queryFn: () => apiClient.getStats(telegramId),
    staleTime: 60 * 1000, // 1 minute
  })

  if (isLoading) {
    return <AchievementsSkeleton />
  }

  // Achievement badges based on stats
  const achievements = []

  if (stats?.streak && stats.streak >= 7) {
    achievements.push({
      emoji: "🔥",
      name: "Week Warrior",
      bgClass: "bg-orange-50 dark:bg-orange-900/20",
      textClass: "text-orange-700 dark:text-orange-400",
    })
  }

  if (stats?.messages_count && stats.messages_count >= 50) {
    achievements.push({
      emoji: "💬",
      name: "Chatty",
      bgClass: "bg-purple-50 dark:bg-purple-900/20",
      textClass: "text-purple-700 dark:text-purple-400",
    })
  }

  if (stats?.stars && stats.stars >= 100) {
    achievements.push({
      emoji: "⭐",
      name: "Star Collector",
      bgClass: "bg-yellow-50 dark:bg-yellow-900/20",
      textClass: "text-yellow-700 dark:text-yellow-400",
    })
  }

  return (
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
        {achievements.map((achievement, index) => (
          <div
            key={index}
            className={`flex-shrink-0 flex flex-col items-center p-3 rounded-lg ${achievement.bgClass}`}
          >
            <span className="text-3xl mb-1">{achievement.emoji}</span>
            <span className={`text-xs font-medium ${achievement.textClass}`}>
              {achievement.name}
            </span>
          </div>
        ))}

        {/* Placeholder for locked achievements */}
        <div className="flex-shrink-0 flex flex-col items-center p-3 rounded-lg bg-gray-100 dark:bg-gray-800 opacity-50">
          <span className="text-3xl mb-1">🔒</span>
          <span className="text-xs font-medium text-gray-500">Keep going!</span>
        </div>
      </div>
    </div>
  )
}
