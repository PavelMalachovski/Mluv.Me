"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Star, Clock, Check, Gift, Loader2 } from "lucide-react"
import { apiClient } from "@/lib/api-client"
import { useAuthStore } from "@/lib/auth-store"

interface Challenge {
  id: number
  code: string
  type: "daily" | "weekly"
  title: string
  description: string
  goal_type: string
  goal_value: number
  reward_stars: number
  progress: number
  completed: boolean
  reward_claimed: boolean
  expires_at?: string
  week_start?: string
}

interface ChallengeCardProps {
  challenge: Challenge
  onRewardClaimed?: () => void
  className?: string
}

export function ChallengeCard({ challenge, onRewardClaimed, className = "" }: ChallengeCardProps) {
  const [claiming, setClaiming] = useState(false)
  const [claimed, setClaimed] = useState(challenge.reward_claimed)
  const user = useAuthStore((state) => state.user)

  const progress = Math.min(100, (challenge.progress / challenge.goal_value) * 100)
  const canClaim = challenge.completed && !claimed

  const handleClaimReward = async () => {
    if (!user?.telegram_id || !canClaim) return
    setClaiming(true)
    try {
      const challengeDate = challenge.type === "weekly"
        ? challenge.week_start
        : new Date().toISOString().split('T')[0]

      const result = await apiClient.claimChallengeReward(
        user.telegram_id,
        challenge.id,
        challengeDate || new Date().toISOString().split('T')[0]
      )

      if (result.success) {
        setClaimed(true)
        onRewardClaimed?.()
      }
    } catch (error) {
      console.error("Failed to claim reward:", error)
    } finally {
      setClaiming(false)
    }
  }

  // Calculate time remaining
  const getTimeRemaining = () => {
    if (!challenge.expires_at) return null
    const expires = new Date(challenge.expires_at)
    const now = new Date()
    const diff = expires.getTime() - now.getTime()

    if (diff <= 0) return "Vypršelo"

    const hours = Math.floor(diff / (1000 * 60 * 60))
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

    if (hours > 24) {
      const days = Math.floor(hours / 24)
      return `${days}d ${hours % 24}h`
    }
    return `${hours}h ${minutes}m`
  }

  const typeColors = {
    daily: "from-blue-500 to-indigo-600",
    weekly: "from-purple-500 to-pink-600",
  }

  const typeBadgeColors = {
    daily: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
    weekly: "bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300",
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`relative bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden ${className}`}
    >
      {/* Header gradient */}
      <div className={`h-2 bg-gradient-to-r ${typeColors[challenge.type]}`} />

      <div className="p-4">
        {/* Type badge and timer */}
        <div className="flex items-center justify-between mb-3">
          <span className={`text-xs font-medium px-2 py-1 rounded-full ${typeBadgeColors[challenge.type]}`}>
            {challenge.type === "daily" ? "📅 Denní" : "📆 Týdenní"}
          </span>

          {challenge.expires_at && (
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <Clock className="h-3 w-3" />
              {getTimeRemaining()}
            </div>
          )}
        </div>

        {/* Title and description */}
        <h3 className="font-bold text-lg text-gray-800 dark:text-gray-200 mb-1">
          {challenge.title}
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          {challenge.description}
        </p>

        {/* Progress bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-sm mb-1">
            <span className="text-gray-600 dark:text-gray-400">
              Pokrok
            </span>
            <span className={`font-medium ${challenge.completed ? 'text-green-600' : 'text-gray-700 dark:text-gray-300'}`}>
              {challenge.progress} / {challenge.goal_value}
            </span>
          </div>
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
              className={`h-full rounded-full ${
                challenge.completed
                  ? 'bg-gradient-to-r from-green-400 to-emerald-500'
                  : `bg-gradient-to-r ${typeColors[challenge.type]}`
              }`}
            />
          </div>
        </div>

        {/* Reward section */}
        <div className="flex items-center justify-between">
          {/* Reward info */}
          <div className="flex items-center gap-2">
            <div className={`flex items-center gap-1 ${claimed ? 'text-gray-400' : 'text-yellow-600'}`}>
              <Star className="h-5 w-5" fill={claimed ? 'none' : 'currentColor'} />
              <span className="font-bold">+{challenge.reward_stars}</span>
            </div>
          </div>

          {/* Claim button */}
          {canClaim ? (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleClaimReward}
              disabled={claiming}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-yellow-400 to-amber-500 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-shadow disabled:opacity-50"
            >
              {claiming ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Gift className="h-4 w-4" />
              )}
              Převzít
            </motion.button>
          ) : claimed ? (
            <div className="flex items-center gap-2 px-4 py-2 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 font-medium rounded-xl">
              <Check className="h-4 w-4" />
              Převzato
            </div>
          ) : (
            <div className="text-sm text-gray-400">
              {challenge.completed ? "Dokončeno" : `${challenge.goal_value - challenge.progress} zbývá`}
            </div>
          )}
        </div>
      </div>

      {/* Completed overlay */}
      {claimed && (
        <div className="absolute inset-0 bg-gradient-to-t from-green-500/10 to-transparent pointer-events-none" />
      )}
    </motion.div>
  )
}

interface ChallengeListProps {
  challenges: Challenge[]
  title?: string
  onRewardClaimed?: () => void
  className?: string
}

export function ChallengeList({ challenges, title, onRewardClaimed, className = "" }: ChallengeListProps) {
  if (challenges.length === 0) {
    return (
      <div className={`text-center py-8 text-gray-500 ${className}`}>
        <p>Žádné výzvy k zobrazení</p>
      </div>
    )
  }

  return (
    <div className={className}>
      {title && (
        <h2 className="text-lg font-bold text-gray-800 dark:text-gray-200 mb-4">
          {title}
        </h2>
      )}
      <div className="space-y-4">
        {challenges.map((challenge) => (
          <ChallengeCard
            key={`${challenge.type}-${challenge.id}`}
            challenge={challenge}
            onRewardClaimed={onRewardClaimed}
          />
        ))}
      </div>
    </div>
  )
}
