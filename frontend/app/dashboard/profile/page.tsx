"use client"

import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import Image from "next/image"
import { useAuthStore } from "@/lib/auth-store"
import { apiClient } from "@/lib/api-client"
import { UserStats } from "@/lib/types"
import { Calendar } from "lucide-react"
import { IllustratedHeader } from "@/components/ui/IllustratedHeader"
import { IllustratedStatCard } from "@/components/ui/IllustratedStatCard"

export default function ProfilePage() {
  const router = useRouter()
  const user = useAuthStore((state) => state.user)

  const { data: stats, isLoading } = useQuery<UserStats>({
    queryKey: ["user-stats", user?.telegram_id],
    queryFn: () => apiClient.getStats(user!.telegram_id),
    enabled: !!user?.telegram_id,
  })

  if (!user) {
    router.push("/login")
    return null
  }

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center cream-bg">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="min-h-screen cream-bg landscape-bg pb-20">
      {/* Purple Header with Profile Label */}
      <IllustratedHeader title="Profile" />

      <div className="mx-auto max-w-2xl px-4 pt-6">
        {/* Parchment Profile Card */}
        <div className="parchment-header mb-6 relative">
          {/* Avatar Circle */}
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-amber-100 to-amber-200 border-4 border-amber-400 flex items-center justify-center text-4xl mb-2 shadow-lg">
            🇨🇿
          </div>

          {/* User Info */}
          <h2 className="text-xl font-bold text-gray-800">
            {user.first_name} {user.last_name || ""}
          </h2>
          <p className="text-sm text-gray-600">@{user.username || "czechlearner"}</p>
          <div className="flex items-center gap-1 text-xs text-gray-500 mt-1">
            <Calendar className="h-3 w-3" />
            <span>Joined {new Date(user.created_at || Date.now()).toLocaleDateString()}</span>
          </div>
        </div>

        {/* Stats Grid - 2x3 */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <IllustratedStatCard
            label="Day Streak"
            value={stats?.streak || 0}
            mascotImage="/images/mascot/honzik-running.png"
            showNumber={true}
          />
          <IllustratedStatCard
            label="Total Stars"
            value={stats?.stars || 0}
            mascotImage="/images/mascot/honzik-stars.png"
            showNumber={true}
          />
          <IllustratedStatCard
            label="Total Messages"
            value={stats?.messages_count || 0}
            mascotImage="/images/mascot/honzik-waving.png"
            showNumber={true}
          />
          <IllustratedStatCard
            label="Words Said"
            value={stats?.words_said || 0}
            mascotImage="/images/mascot/honzik-reading.png"
            showNumber={true}
          />
          <IllustratedStatCard
            label="Avg Correctness"
            value={`${stats?.correct_percent || 0}%`}
          />
        </div>

        {/* Czech Level Section - Single Level Display */}
        <div className="illustrated-card p-4 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xl">💬</span>
            <h3 className="font-semibold text-foreground">Czech Level</h3>
          </div>

          {(() => {
            const levels: Record<string, { label: string; image: string }> = {
              beginner: { label: "Začátečník", image: "/images/mascot/honzik-waving.png" },
              intermediate: { label: "Středně pokročilý", image: "/images/mascot/honzik-running.png" },
              advanced: { label: "Pokročilý", image: "/images/mascot/honzik-reading.png" },
              native: { label: "Rodilý", image: "/images/mascot/honzik-stars.png" },
            };
            const currentLevel = levels[user.level] || levels.beginner;

            return (
              <div className="level-card active mx-auto w-fit px-8">
                <Image
                  src={currentLevel.image}
                  alt={currentLevel.label}
                  width={80}
                  height={80}
                  className="mx-auto mb-2"
                />
                <span className="level-name">{currentLevel.label}</span>
              </div>
            );
          })()}
        </div>

        {/* Achievements Section */}
        <div className="illustrated-card p-4">
          <h3 className="mb-4 text-lg font-semibold text-foreground">Achievements</h3>
          <div className="grid gap-3 grid-cols-2">
            {stats?.streak && stats.streak >= 7 && (
              <div className="flex items-center gap-3 rounded-lg bg-orange-50 dark:bg-orange-900/20 p-3">
                <div className="text-2xl">🔥</div>
                <div>
                  <div className="font-medium text-foreground">Week Warrior</div>
                  <div className="text-xs text-muted-foreground">7 day streak</div>
                </div>
              </div>
            )}

            {stats?.messages_count && stats.messages_count >= 50 && (
              <div className="flex items-center gap-3 rounded-lg bg-purple-50 dark:bg-purple-900/20 p-3">
                <div className="text-2xl">💬</div>
                <div>
                  <div className="font-medium text-foreground">Chatty</div>
                  <div className="text-xs text-muted-foreground">50+ messages</div>
                </div>
              </div>
            )}

            {stats?.stars && stats.stars >= 100 && (
              <div className="flex items-center gap-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 p-3">
                <div className="text-2xl">⭐</div>
                <div>
                  <div className="font-medium text-foreground">Star Collector</div>
                  <div className="text-xs text-muted-foreground">100+ stars</div>
                </div>
              </div>
            )}

            {stats?.words_said && stats.words_said >= 100 && (
              <div className="flex items-center gap-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 p-3">
                <div className="text-2xl">📚</div>
                <div>
                  <div className="font-medium text-foreground">Word Master</div>
                  <div className="text-xs text-muted-foreground">100+ words</div>
                </div>
              </div>
            )}
          </div>

          {/* Empty achievements message */}
          {(!stats?.streak || stats.streak < 7) &&
            (!stats?.messages_count || stats.messages_count < 50) &&
            (!stats?.stars || stats.stars < 100) &&
            (!stats?.words_said || stats.words_said < 100) && (
              <div className="text-center py-8">
                <div className="text-4xl mb-2">🎯</div>
                <p className="text-sm text-muted-foreground">Keep practicing to unlock achievements!</p>
              </div>
            )}
        </div>
      </div>
    </div>
  )
}
