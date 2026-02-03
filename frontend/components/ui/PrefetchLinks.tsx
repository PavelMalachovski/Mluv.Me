"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

/**
 * PrefetchLinks Component
 *
 * Prefetches popular navigation routes when the component mounts.
 * This improves navigation speed by preloading the JavaScript bundles
 * and data for frequently accessed pages.
 *
 * Uses Next.js router.prefetch() for optimal caching.
 */

const PREFETCH_ROUTES = [
  "/dashboard/practice",
  "/dashboard/review",
  "/dashboard/saved",
  "/dashboard/settings",
  "/dashboard/analytics",
  "/dashboard/profile",
]

export function PrefetchLinks() {
  const router = useRouter()

  useEffect(() => {
    // Delay prefetching to not compete with initial page load
    const timeoutId = setTimeout(() => {
      PREFETCH_ROUTES.forEach((route) => {
        router.prefetch(route)
      })
    }, 1000) // Start prefetching after 1 second

    return () => clearTimeout(timeoutId)
  }, [router])

  // Also add link rel="prefetch" hints for browsers
  return (
    <>
      {PREFETCH_ROUTES.map((route) => (
        <link
          key={route}
          rel="prefetch"
          href={route}
          as="document"
        />
      ))}
    </>
  )
}
