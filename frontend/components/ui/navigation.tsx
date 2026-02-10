"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { User, Settings, GraduationCap } from "lucide-react"
import { cn } from "@/lib/utils"
import { useCallback } from "react"

interface NavigationProps {
  className?: string
}

const navigationItems = [
  {
    href: "/dashboard",
    label: "Profil",
    icon: User,
  },
  {
    href: "/dashboard/learn",
    label: "Procvičování",
    icon: GraduationCap,
  },
  {
    href: "/dashboard/settings",
    label: "Nastavení",
    icon: Settings,
  },
]

/**
 * Navigation Component with Prefetching on Hover
 *
 * Features:
 * - Prefetches routes when user hovers over links
 * - Active state indication
 * - Responsive design (bottom on mobile, sidebar on desktop)
 */
export function Navigation({ className }: NavigationProps) {
  const pathname = usePathname()
  const router = useRouter()

  // Prefetch on hover for faster navigation
  const handleMouseEnter = useCallback((href: string) => {
    router.prefetch(href)
  }, [router])

  return (
    <nav
      className={cn(
        "fixed bottom-0 left-0 right-0 z-50 border-t bg-white dark:bg-gray-900 dark:border-gray-800 shadow-lg md:left-auto md:top-0 md:h-screen md:w-20 md:border-r md:border-t-0",
        className
      )}
    >
      <div className="flex h-16 items-center justify-around md:h-full md:flex-col md:py-8">
        {navigationItems.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon

          return (
            <Link
              key={item.href}
              href={item.href}
              prefetch={true}
              onMouseEnter={() => handleMouseEnter(item.href)}
              onTouchStart={() => handleMouseEnter(item.href)}
              className={cn(
                "flex flex-col items-center justify-center gap-1 rounded-lg px-3 py-2 text-sm transition-all hover:bg-purple-50 dark:hover:bg-purple-900/20 md:w-full md:gap-2 md:py-4",
                "hover:scale-105 active:scale-95 transition-transform duration-150",
                isActive
                  ? "text-purple-600 dark:text-purple-400 font-semibold bg-purple-50 dark:bg-purple-900/30"
                  : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
              )}
            >
              <Icon
                className={cn(
                  "h-6 w-6 transition-colors",
                  isActive ? "text-purple-600 dark:text-purple-400" : "text-gray-500 dark:text-gray-500"
                )}
              />
              <span className="text-xs">{item.label}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
