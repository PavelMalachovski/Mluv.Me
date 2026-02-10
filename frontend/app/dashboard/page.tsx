"use client"

import { Suspense, useEffect, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useAuthStore } from "@/lib/auth-store"
import { DashboardStats } from "@/components/features/DashboardStats"
import { DashboardProgress } from "@/components/features/DashboardProgress"
import { DashboardAchievements } from "@/components/features/DashboardAchievements"
import { QuickActions } from "@/components/features/QuickActions"
import { StatsTab } from "@/components/features/StatsTab"
import {
  HonzikVideoAvatar,
  hasSeenWelcomeVideo,
  preloadVideoImages,
} from "@/components/features/HonzikVideoAvatar"
import {
  StatsSkeletons,
  QuickActionsSkeleton,
  ProgressCardSkeleton,
  AchievementsSkeleton,
} from "@/components/ui/skeletons"
import { BarChart2, Home } from "lucide-react"

/**
 * Get user initials for avatar
 */
function getUserInitials(firstName: string, lastName?: string): string {
  const first = firstName?.charAt(0)?.toUpperCase() || ""
  const last = lastName?.charAt(0)?.toUpperCase() || ""
  return first + last || first || "?"
}

/**
 * Get avatar background color based on user name
 */
function getAvatarColor(name: string): string {
  const colors = [
    "from-violet-500 to-purple-600",
    "from-blue-500 to-cyan-600",
    "from-emerald-500 to-teal-600",
    "from-orange-500 to-amber-600",
    "from-pink-500 to-rose-600",
    "from-indigo-500 to-blue-600",
  ]
  const index = name.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length
  return colors[index]
}

/**
 * Dashboard Page - Optimized with Suspense boundaries
 *
 * Each section loads independently with its own loading state,
 * reducing Time to First Contentful Paint (FCP) and improving UX.
 *
 * Data is fetched in parallel by isolated client components.
 */
export default function DashboardPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const user = useAuthStore((state) => state.user)
  const [showWelcomeVideo, setShowWelcomeVideo] = useState(false)
  const initialProfileTab = searchParams.get("tab") === "stats" ? "stats" : "overview"
  const [profileTab, setProfileTab] = useState<"overview" | "stats">(initialProfileTab as "overview" | "stats")

  // Check if this is first visit — show welcome video
  useEffect(() => {
    if (user && !hasSeenWelcomeVideo()) {
      preloadVideoImages("welcome")
      // Small delay to let dashboard render first
      const timer = setTimeout(() => setShowWelcomeVideo(true), 500)
      return () => clearTimeout(timer)
    }
  }, [user])

  // Auth check - use useEffect to avoid SSR issues
  useEffect(() => {
    if (!user) {
      router.push("/login")
    }
  }, [user, router])

  // Auth check - redirect if not logged in
  if (!user) {
    return null
  }

  const initials = getUserInitials(user.first_name, user.last_name)
  const avatarColor = getAvatarColor(user.first_name)

  return (
    <div className="min-h-screen cream-bg landscape-bg pb-24">
      {/* Honzík Welcome Video — shows on first visit */}
      {showWelcomeVideo && (
        <HonzikVideoAvatar
          type="welcome"
          language={user.native_language === "ru" ? "ru" : "cs"}
          onComplete={() => setShowWelcomeVideo(false)}
          onDismiss={() => setShowWelcomeVideo(false)}
        />
      )}

      {/* Custom Header with Avatar */}
      <div className="illustrated-header relative pb-8">
        <h1 className="illustrated-header-title">Přehled</h1>
        {/* User Avatar */}
        <div className="absolute -bottom-10 left-1/2 -translate-x-1/2">
          <div className={`w-20 h-20 rounded-full bg-gradient-to-br ${avatarColor} flex items-center justify-center shadow-lg ring-4 ring-white dark:ring-gray-800`}>
            <span className="text-2xl font-bold text-white">{initials}</span>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-2xl px-4 pt-14">

        {/* Profile Tab Switcher */}
        <div className="flex gap-1 p-1 bg-gray-100 dark:bg-gray-800 rounded-2xl mb-6">
          <button
            onClick={() => setProfileTab("overview")}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
              profileTab === "overview"
                ? "bg-white dark:bg-gray-700 text-purple-600 dark:text-purple-400 shadow-sm"
                : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
            }`}
          >
            <Home className="w-4 h-4" />
            <span>Přehled</span>
          </button>
          <button
            onClick={() => setProfileTab("stats")}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
              profileTab === "stats"
                ? "bg-white dark:bg-gray-700 text-purple-600 dark:text-purple-400 shadow-sm"
                : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
            }`}
          >
            <BarChart2 className="w-4 h-4" />
            <span>Statistiky</span>
          </button>
        </div>

        {profileTab === "overview" ? (
          <>
            {/* Stats Section */}
            <Suspense fallback={<StatsSkeletons />}>
              <DashboardStats telegramId={user.telegram_id} />
            </Suspense>

            {/* Quick Actions */}
            <Suspense fallback={<QuickActionsSkeleton />}>
              <QuickActions />
            </Suspense>

            {/* Progress Section */}
            <Suspense fallback={<ProgressCardSkeleton />}>
              <DashboardProgress telegramId={user.telegram_id} />
            </Suspense>

            {/* Achievements Section */}
            <Suspense fallback={<AchievementsSkeleton />}>
              <DashboardAchievements telegramId={user.telegram_id} />
            </Suspense>
          </>
        ) : (
          <StatsTab telegramId={user.telegram_id} />
        )}


      </div>
    </div>
  )
}
