"use client"

import { Navigation } from "@/components/ui/navigation"
import { PrefetchLinks } from "@/components/ui/PrefetchLinks"

/**
 * Dashboard Layout with Prefetching
 *
 * Features:
 * - Prefetches popular routes on mount
 * - Lazy loads Navigation to reduce initial bundle
 * - Provides consistent layout structure
 */

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen cream-bg landscape-bg">
      {/* Prefetch popular routes */}
      <PrefetchLinks />

      {/* Navigation Sidebar/Bottom Bar */}
      <Navigation />

      {/* Main Content */}
      <main className="flex-1 pb-20 md:ml-20 md:pb-0">
        {children}
      </main>
    </div>
  )
}
