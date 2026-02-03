"use client"

import { useRouter } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import { ReviewStats } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { Mic, BookOpen, Trophy } from "lucide-react"

interface QuickActionsProps {
  telegramId: number
}

export function QuickActions({ telegramId }: QuickActionsProps) {
  const router = useRouter()

  const { data: reviewStats } = useQuery<ReviewStats>({
    queryKey: ["review-stats", telegramId],
    queryFn: () => apiClient.getReviewStats(telegramId),
    staleTime: 60 * 1000,
  })

  return (
    <div className="grid grid-cols-3 gap-3 mb-6">
      <Button
        onClick={() => router.push("/dashboard/practice")}
        className="h-24 flex flex-col items-center justify-center gap-2 bg-gradient-to-br from-primary to-purple-600 hover:from-primary/90 hover:to-purple-600/90 text-white rounded-xl shadow-lg transition-transform hover:scale-[1.02] active:scale-[0.98]"
      >
        <Mic className="h-7 w-7" />
        <span className="text-sm font-semibold">Procvičovat</span>
      </Button>

      <Button
        onClick={() => router.push("/dashboard/review")}
        variant="outline"
        className="h-24 relative flex flex-col items-center justify-center gap-2 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-xl shadow-lg border-2 transition-transform hover:scale-[1.02] active:scale-[0.98]"
      >
        <BookOpen className="h-7 w-7 text-green-600" />
        <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">Opakovat</span>
        {reviewStats && reviewStats.due_today > 0 && (
          <span className="absolute top-2 right-2 bg-red-500 text-white text-xs px-2 py-0.5 rounded-full animate-pulse">
            {reviewStats.due_today}
          </span>
        )}
      </Button>

      <Button
        onClick={() => router.push("/dashboard/challenges")}
        variant="outline"
        className="h-24 flex flex-col items-center justify-center gap-2 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-xl shadow-lg border-2 transition-transform hover:scale-[1.02] active:scale-[0.98]"
      >
        <Trophy className="h-7 w-7 text-yellow-500" />
        <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">Výzvy</span>
      </Button>
    </div>
  )
}
