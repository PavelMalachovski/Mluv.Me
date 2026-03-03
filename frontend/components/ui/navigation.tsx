"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { User, Settings, GraduationCap, MessageCircle } from "lucide-react"
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
    href: "/dashboard/practice",
    label: "Chat",
    icon: MessageCircle,
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
 * - Active state indication with purple accent
 * - Bigger tap targets for mobile
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
      aria-label="Hlavní navigace"
      className={cn(
        "fixed bottom-0 left-0 right-0 z-50 border-t bg-white dark:bg-gray-900 dark:border-gray-800 shadow-lg md:left-auto md:top-0 md:h-screen md:w-24 md:border-r md:border-t-0",
        className
      )}
    >
      <div className="flex h-[72px] items-center justify-around md:h-full md:flex-col md:py-8" role="list">
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
              role="listitem"
              aria-current={isActive ? "page" : undefined}
              aria-label={item.label}
              className={cn(
                "flex flex-col items-center justify-center gap-1.5 rounded-xl px-4 py-2.5 transition-all md:w-full md:gap-2 md:py-4",
                "hover:scale-105 active:scale-95 transition-transform duration-150",
                isActive
                  ? "text-[#7d3bed] font-semibold"
                  : "text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              )}
            >
              <Icon
                className={cn(
                  "h-7 w-7 transition-colors",
                  isActive ? "text-[#7d3bed]" : "text-gray-400"
                )}
                strokeWidth={isActive ? 2.5 : 1.8}
              />
              <span className="text-[11px] leading-tight font-medium">{item.label}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
