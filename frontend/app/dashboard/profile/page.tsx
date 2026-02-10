"use client"

import { useEffect } from "react"
import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import Image from "next/image"
import { useAuthStore } from "@/lib/auth-store"
import { apiClient } from "@/lib/api-client"
import { UserStats } from "@/lib/types"
import { Calendar, BarChart2 } from "lucide-react"
import { IllustratedHeader } from "@/components/ui/IllustratedHeader"
import { IllustratedStatCard } from "@/components/ui/IllustratedStatCard"
import { Button } from "@/components/ui/button"

export default function ProfilePage() {
  const router = useRouter()
  const user = useAuthStore((state) => state.user)

  const { data: stats, isLoading } = useQuery<UserStats>({
    queryKey: ["user-stats", user?.telegram_id],
    queryFn: () => apiClient.getStats(user!.telegram_id),
    enabled: !!user?.telegram_id,
  })

  // Auth check - use useEffect to avoid SSR issues
  useEffect(() => {
    if (!user) {
      router.push("/login")
    }
  }, [user, router])

  if (!user) {
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

        {/* Link to detailed statistics */}
        <div className="illustrated-card p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BarChart2 className="h-5 w-5 text-purple-500" />
              <h3 className="font-semibold text-foreground">Podrobné statistiky</h3>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push("/dashboard?tab=stats")}
              className="text-xs"
            >
              Zobrazit →
            </Button>
          </div>
          <p className="text-sm text-muted-foreground mt-2">
            Grafy aktivity, trend přesnosti, ovládání slovíček a úspěchy
          </p>
        </div>
      </div>
    </div>
  )
}
