"use client"

import { Suspense } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/auth-store"
import { IllustratedHeader } from "@/components/ui/IllustratedHeader"
import { DashboardStats } from "@/components/features/DashboardStats"
import { DashboardProgress } from "@/components/features/DashboardProgress"
import { DashboardAchievements } from "@/components/features/DashboardAchievements"
import { QuickActions } from "@/components/features/QuickActions"
import { WelcomeMessage } from "@/components/features/WelcomeMessage"
import {
  StatsSkeletons,
  QuickActionsSkeleton,
  ProgressCardSkeleton,
  AchievementsSkeleton,
  Skeleton,
} from "@/components/ui/skeletons"

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

  // Auth check - redirect if not logged in
  if (!user) {
    router.push("/login")
    return null
  }

  return (
    <div className="min-h-screen cream-bg landscape-bg pb-24">
      <IllustratedHeader title="Dashboard" />

      <div className="mx-auto max-w-2xl px-4 pt-6">
        {/* Welcome Message - renders immediately with user name */}
        <div className="mb-6 text-center">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100">
            Ahoj, {user.first_name}! 👋
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Ready to practice Czech today?
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
