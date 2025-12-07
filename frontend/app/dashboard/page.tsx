"use client"

import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/auth-store"
import { apiClient } from "@/lib/api-client"
import { ProgressChart } from "@/components/features/ProgressChart"
import { StatsCard } from "@/components/features/StatsCard"
import { RecentLessons } from "@/components/features/RecentLessons"
import { Button } from "@/components/ui/button"
import { UserStats, Message } from "@/lib/types"

export default function DashboardPage() {
  const router = useRouter()
  const user = useAuthStore((state) => state.user)

  const { data: stats, isLoading: statsLoading } = useQuery<UserStats>({
    queryKey: ["user-stats"],
    queryFn: () => apiClient.get("/api/v1/stats/me"),
    enabled: !!user,
  })

  const { data: lessonsData } = useQuery<{ messages: Message[] }>({
    queryKey: ["recent-lessons"],
    queryFn: () =>
      apiClient.get("/api/v1/web/lessons/history", {
        params: { user_id: user?.id, limit: 5 },
      }),
    enabled: !!user,
  })

  if (!user) {
    router.push("/login")
    return null
  }

  if (statsLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">
              Nazdar, {user.first_name}! 🇨🇿
            </h1>
            <p className="text-muted-foreground">
              Welcome to your Czech learning dashboard
            </p>
          </div>
          <Button
            onClick={() => router.push("/dashboard/practice")}
            size="lg"
          >
            Start Practicing
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-4">
          <StatsCard
            title="Current Streak"
            value={stats?.streak || 0}
            icon="flame"
            trend={stats?.streak ? `${stats.streak} days in a row! 🔥` : undefined}
          />
          <StatsCard
            title="Total Stars"
            value={stats?.total_stars || 0}
            icon="star"
          />
          <StatsCard
            title="Czech Level"
            value={stats?.czech_level || "A1"}
            icon="award"
          />
          <StatsCard
            title="Messages Today"
            value={stats?.messages_today || 0}
            icon="message-circle"
          />
        </div>

        {/* Progress Chart */}
        <div className="rounded-lg border bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-semibold">Progress Over Time</h2>
          <ProgressChart data={stats?.progress_data} />
        </div>

        {/* Recent Lessons */}
        <div className="rounded-lg border bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Recent Lessons</h2>
            <Button
              variant="outline"
              onClick={() => router.push("/dashboard/lessons")}
            >
              View All
            </Button>
          </div>
          <RecentLessons lessons={lessonsData?.messages} />
        </div>
      </div>
    </div>
  )
}
