"use client"

import { Suspense, useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/auth-store"
import { DashboardStats } from "@/components/features/DashboardStats"
import { DashboardProgress } from "@/components/features/DashboardProgress"
import { DashboardAchievements } from "@/components/features/DashboardAchievements"
import { QuickActions } from "@/components/features/QuickActions"
import { WelcomeMessage } from "@/components/features/WelcomeMessage"
import {
  HonzikVideoAvatar,
  hasSeenWelcomeVideo,
  preloadVideoImages,
} from "@/components/features/HonzikVideoAvatar"
import { ProfileMiniGames } from "@/components/features/ProfileMiniGames"
import {
  StatsSkeletons,
  QuickActionsSkeleton,
  ProgressCardSkeleton,
  AchievementsSkeleton,
  Skeleton,
} from "@/components/ui/skeletons"

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
  const user = useAuthStore((state) => state.user)
  const [showWelcomeVideo, setShowWelcomeVideo] = useState(false)

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
        {/* Welcome Message - renders immediately with user name */}
        <div className="mb-6 text-center">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100">
            Ahoj, {user.first_name}! 👋
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Jsi připraven/a procvičovat češtinu?
          </p>
        </div>

        {/* Stats Section - loads with own suspense boundary */}
        <Suspense fallback={<StatsSkeletons />}>
          <DashboardStats telegramId={user.telegram_id} />
        </Suspense>

        {/* Quick Actions - loads quickly, uses review stats for badge */}
        <Suspense fallback={<QuickActionsSkeleton />}>
          <QuickActions telegramId={user.telegram_id} />
        </Suspense>

        {/* Progress Section */}
        <Suspense fallback={<ProgressCardSkeleton />}>
          <DashboardProgress telegramId={user.telegram_id} />
        </Suspense>

        {/* Mini Games Section */}
        <ProfileMiniGames
          userId={user.id}
          telegramId={user.telegram_id}
          level={user.level}
        />

        {/* Achievements Section */}
        <Suspense fallback={<AchievementsSkeleton />}>
          <DashboardAchievements telegramId={user.telegram_id} />
        </Suspense>

        {/* Motivational Mascot - with streak message */}
        <Suspense
          fallback={
            <div className="mt-6 text-center">
              <Skeleton className="w-[100px] h-[100px] rounded-full mx-auto mb-2" />
              <Skeleton className="h-4 w-48 mx-auto" />
            </div>
          }
        >
          <WelcomeMessage
            firstName={user.first_name}
            telegramId={user.telegram_id}
          />
        </Suspense>
      </div>
    </div>
  )
}
