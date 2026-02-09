"use client"

import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Gamepad2, Trophy } from "lucide-react"

export function QuickActions() {
  const router = useRouter()

  return (
    <div className="grid grid-cols-2 gap-3 mb-6">
      <Button
        onClick={() => {
          // Scroll to mini games section
          document.getElementById('mini-games-section')?.scrollIntoView({ behavior: 'smooth' })
        }}
        className="h-24 flex flex-col items-center justify-center gap-2 bg-gradient-to-br from-primary to-purple-600 hover:from-primary/90 hover:to-purple-600/90 text-white rounded-xl shadow-lg transition-transform hover:scale-[1.02] active:scale-[0.98]"
      >
        <Gamepad2 className="h-7 w-7" />
        <span className="text-sm font-semibold">Mini hry</span>
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
