"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

/**
 * Saved page now redirects to Learn → Slovíčka tab.
 * Kept as redirect for backward compatibility.
 */
export default function SavedPage() {
  const router = useRouter()

  useEffect(() => {
    router.replace("/dashboard/learn?tab=words")
  }, [router])

  return (
    <div className="flex min-h-screen items-center justify-center cream-bg">
      <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
    </div>
  )
}

