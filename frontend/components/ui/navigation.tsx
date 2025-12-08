"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { User, BookmarkCheck, Settings, MessageCircle } from "lucide-react"
import { cn } from "@/lib/utils"

interface NavigationProps {
  className?: string
}

const navigationItems = [
  {
    href: "/dashboard",
    label: "Chat",
    icon: MessageCircle,
  },
  {
    href: "/dashboard/profile",
    label: "Profile",
    icon: User,
  },
  {
    href: "/dashboard/saved",
    label: "Saved",
    icon: BookmarkCheck,
  },
  {
    href: "/dashboard/settings",
    label: "Settings",
    icon: Settings,
  },
]

export function Navigation({ className }: NavigationProps) {
  const pathname = usePathname()

  return (
    <nav
      className={cn(
        "fixed bottom-0 left-0 right-0 z-50 border-t bg-white shadow-lg md:left-auto md:top-0 md:h-screen md:w-20 md:border-r md:border-t-0",
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
              className={cn(
                "flex flex-col items-center justify-center gap-1 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-gray-100 md:w-full md:gap-2 md:py-4",
                isActive
                  ? "text-blue-600 font-semibold"
                  : "text-gray-600 hover:text-gray-900"
              )}
            >
              <Icon
                className={cn(
                  "h-6 w-6",
                  isActive ? "text-blue-600" : "text-gray-500"
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
