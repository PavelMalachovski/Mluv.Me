/**
 * Skeleton loading components for dashboard.
 * Used with Suspense for streaming SSR.
 */

import { cn } from "@/lib/utils"

interface SkeletonProps {
  className?: string
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-md bg-gray-200 dark:bg-gray-700",
        className
      )}
    />
  )
}

export function StatsCardSkeleton() {
  return (
    <div className="illustrated-card p-4 flex items-center gap-3">
      <Skeleton className="w-12 h-12 rounded-full" />
      <div className="space-y-2">
        <Skeleton className="h-7 w-12" />
        <Skeleton className="h-3 w-16" />
      </div>
    </div>
  )
}

export function StatsSkeletons() {
  return (
    <div className="grid grid-cols-2 gap-4 mb-6">
      <StatsCardSkeleton />
      <StatsCardSkeleton />
    </div>
  )
}

export function QuickActionsSkeleton() {
  return (
    <div className="grid grid-cols-2 gap-4 mb-6">
      <Skeleton className="h-24 rounded-xl" />
      <Skeleton className="h-24 rounded-xl" />
    </div>
  )
}

export function ProgressCardSkeleton() {
  return (
    <div className="illustrated-card p-4 mb-6 space-y-3">
      <div className="flex items-center justify-between">
        <Skeleton className="h-5 w-32" />
        <Skeleton className="h-4 w-10" />
      </div>
      <Skeleton className="h-3 w-full rounded-full" />
      <div className="grid grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="text-center space-y-1">
            <Skeleton className="h-5 w-8 mx-auto" />
            <Skeleton className="h-3 w-12 mx-auto" />
          </div>
        ))}
      </div>
    </div>
  )
}

export function AchievementsSkeleton() {
  return (
    <div className="illustrated-card p-4">
      <div className="flex items-center justify-between mb-3">
        <Skeleton className="h-5 w-24" />
        <Skeleton className="h-6 w-16" />
      </div>
      <div className="flex gap-3 overflow-x-auto pb-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex-shrink-0 p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
            <Skeleton className="h-8 w-8 mx-auto mb-1" />
            <Skeleton className="h-3 w-16" />
          </div>
        ))}
      </div>
    </div>
  )
}

export function DashboardSkeleton() {
  return (
    <div className="min-h-screen cream-bg landscape-bg pb-24">
      {/* Header skeleton */}
      <div className="h-16 bg-white/50 dark:bg-gray-900/50" />

      <div className="mx-auto max-w-2xl px-4 pt-6">
        {/* Welcome message */}
        <div className="mb-6 text-center space-y-2">
          <Skeleton className="h-6 w-40 mx-auto" />
          <Skeleton className="h-4 w-52 mx-auto" />
        </div>

        <StatsSkeletons />
        <QuickActionsSkeleton />
        <ProgressCardSkeleton />
        <AchievementsSkeleton />
      </div>
    </div>
  )
}

export function ReviewCardSkeleton() {
  return (
    <div className="p-6 rounded-xl border border-gray-200 dark:border-gray-700 space-y-4">
      <Skeleton className="h-8 w-32 mx-auto" />
      <Skeleton className="h-4 w-48 mx-auto" />
      <div className="flex justify-center gap-2 pt-4">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-10 w-20 rounded-lg" />
        ))}
      </div>
    </div>
  )
}

export function SavedWordsSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex justify-between items-start">
            <div className="space-y-2">
              <Skeleton className="h-5 w-24" />
              <Skeleton className="h-4 w-32" />
            </div>
            <Skeleton className="h-8 w-8 rounded" />
          </div>
        </div>
      ))}
    </div>
  )
}

export function VoiceRecorderSkeleton() {
  return (
    <div className="text-center py-8">
      <Skeleton className="w-20 h-20 rounded-full mx-auto mb-3" />
      <Skeleton className="h-4 w-40 mx-auto" />
    </div>
  )
}

export function ProgressChartSkeleton() {
  return (
    <div className="p-4 rounded-lg border border-gray-200 dark:border-gray-700">
      <Skeleton className="h-5 w-32 mb-4" />
      <Skeleton className="h-48 w-full rounded" />
    </div>
  )
}
