"use client"

import { useState, useEffect } from "react"
import { X } from "lucide-react"

interface Achievement {
    id: number
    code: string
    name: string
    description: string
    icon: string
    category: string
    stars_reward: number
}

interface AchievementToastProps {
    achievement: Achievement
    onClose: () => void
    duration?: number
}

export function AchievementToast({
    achievement,
    onClose,
    duration = 5000
}: AchievementToastProps) {
    const [isExiting, setIsExiting] = useState(false)

    useEffect(() => {
        const timer = setTimeout(() => {
            setIsExiting(true)
            setTimeout(onClose, 300)
        }, duration)

        return () => clearTimeout(timer)
    }, [duration, onClose])

    const handleClose = () => {
        setIsExiting(true)
        setTimeout(onClose, 300)
    }

    return (
        <div
            className={`fixed top-4 right-4 z-[100] max-w-sm transition-all duration-300 ${isExiting ? "opacity-0 translate-x-4" : "opacity-100 translate-x-0"
                }`}
        >
            <div className="bg-gradient-to-r from-yellow-400 to-amber-500 rounded-xl shadow-2xl overflow-hidden">
                {/* Confetti effect */}
                <div className="absolute inset-0 pointer-events-none overflow-hidden">
                    {[...Array(10)].map((_, i) => (
                        <div
                            key={i}
                            className="absolute w-2 h-2 rounded-full animate-confetti"
                            style={{
                                left: `${Math.random() * 100}%`,
                                backgroundColor: ['#ff0', '#f0f', '#0ff', '#f00', '#0f0'][i % 5],
                                animationDelay: `${Math.random() * 0.5}s`,
                            }}
                        />
                    ))}
                </div>

                <div className="relative p-4">
                    {/* Close button */}
                    <button
                        onClick={handleClose}
                        className="absolute top-2 right-2 p-1 rounded-full hover:bg-white/20 transition-colors"
                    >
                        <X className="h-4 w-4 text-white" />
                    </button>

                    {/* Header */}
                    <div className="text-center mb-2">
                        <span className="text-xs uppercase tracking-wider text-yellow-100 font-medium">
                            🎉 Achievement Unlocked!
                        </span>
                    </div>

                    {/* Achievement */}
                    <div className="flex items-center gap-4">
                        {/* Icon */}
                        <div className="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center text-4xl animate-bounce">
                            {achievement.icon}
                        </div>

                        {/* Info */}
                        <div className="flex-1">
                            <h3 className="text-lg font-bold text-white">
                                {achievement.name}
                            </h3>
                            <p className="text-sm text-yellow-100">
                                {achievement.description}
                            </p>

                            {/* Stars reward */}
                            {achievement.stars_reward > 0 && (
                                <div className="mt-1 flex items-center gap-1 text-white">
                                    <span className="text-lg">⭐</span>
                                    <span className="font-bold">+{achievement.stars_reward}</span>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Progress bar (fading out) */}
                <div className="h-1 bg-white/20">
                    <div
                        className="h-full bg-white transition-all ease-linear"
                        style={{
                            width: "100%",
                            animation: `shrink ${duration}ms linear forwards`
                        }}
                    />
                </div>
            </div>

            <style jsx>{`
        @keyframes shrink {
          from { width: 100%; }
          to { width: 0%; }
        }
        @keyframes confetti {
          0% { transform: translateY(0) rotate(0deg); opacity: 1; }
          100% { transform: translateY(80px) rotate(720deg); opacity: 0; }
        }
        .animate-confetti {
          animation: confetti 2s ease-out forwards;
        }
      `}</style>
        </div>
    )
}

interface AchievementToastContainerProps {
    achievements: Achievement[]
    onClear: () => void
}

export function AchievementToastContainer({
    achievements,
    onClear
}: AchievementToastContainerProps) {
    const [queue, setQueue] = useState<Achievement[]>(achievements)

    useEffect(() => {
        if (achievements.length > 0) {
            setQueue(achievements)
        }
    }, [achievements])

    const handleRemove = (id: number) => {
        setQueue((prev) => {
            const next = prev.filter((a) => a.id !== id)
            if (next.length === 0) {
                onClear()
            }
            return next
        })
    }

    if (queue.length === 0) return null

    // Show only the first achievement
    const current = queue[0]

    return (
        <AchievementToast
            key={current.id}
            achievement={current}
            onClose={() => handleRemove(current.id)}
        />
    )
}
