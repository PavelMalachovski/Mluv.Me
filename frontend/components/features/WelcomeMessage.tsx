"use client"

import { useQuery } from "@tanstack/react-query"
import Image from "next/image"
import { apiClient } from "@/lib/api-client"
import { UserStats } from "@/lib/types"

interface WelcomeMessageProps {
  firstName: string
  telegramId: number
}

export function WelcomeMessage({ firstName, telegramId }: WelcomeMessageProps) {
  const { data: stats } = useQuery<UserStats>({
    queryKey: ["user-stats", telegramId],
    queryFn: () => apiClient.getStats(telegramId),
    staleTime: 60 * 1000,
  })

  return (
    <>
      {/* Welcome Header */}
      <div className="mb-6 text-center">
        <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100">
          Ahoj, {firstName}! 👋
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Ready to practice Czech today?
        </p>
      </div>

      {/* Motivational Mascot - at the bottom */}
      <div className="mt-6 text-center">
        <Image
          src="/images/mascot/honzik-waving.png"
          alt="Honzík"
          width={100}
          height={100}
          className="mx-auto mb-2"
          priority={false}
        />
        <p className="text-sm text-gray-600 dark:text-gray-400 italic">
          {stats?.streak && stats.streak > 0
            ? `Skvělé! ${stats.streak} day streak! 🎉`
            : "Let's start learning Czech today! 🇨🇿"
          }
        </p>
      </div>
    </>
  )
}
