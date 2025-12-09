"use client"

import { Navigation } from "@/components/ui/navigation"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen cream-bg landscape-bg">
      {/* Navigation Sidebar/Bottom Bar */}
      <Navigation />

      {/* Main Content */}
      <main className="flex-1 pb-20 md:ml-20 md:pb-0">
        {children}
      </main>
    </div>
  )
}
