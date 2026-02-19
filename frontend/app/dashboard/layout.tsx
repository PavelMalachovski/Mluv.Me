"use client"

import { Navigation } from "@/components/ui/navigation"
import { PrefetchLinks } from "@/components/ui/PrefetchLinks"
import { ErrorBoundary } from "@/components/ui/ErrorBoundary"

/**
 * Dashboard Layout with Error Boundary and Prefetching
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
      <main className="flex-1 pb-20 md:ml-20 md:pb-0" role="main" aria-label="Hlavní obsah">
        <ErrorBoundary>{children}</ErrorBoundary>
      </main>
    </div>
  )
}
