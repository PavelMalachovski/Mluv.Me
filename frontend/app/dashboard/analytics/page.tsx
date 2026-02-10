"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

/**
 * Analytics page now redirects to Dashboard → Statistiky tab.
 * Kept as redirect for backward compatibility.
 */
export default function AnalyticsPage() {
    const router = useRouter()

    useEffect(() => {
        router.replace("/dashboard?tab=stats")
    }, [router])

    return (
        <div className="flex min-h-screen items-center justify-center cream-bg">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
    )
}
