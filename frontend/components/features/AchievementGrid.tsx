"use client"

import { Lock } from "lucide-react"

interface Achievement {
    id: number
    code: string
    name: string
    description: string
    icon: string
    category: string
    threshold: number
    stars_reward: number
    is_unlocked: boolean
    unlocked_at: string | null
    progress: number
}

interface AchievementGridProps {
    achievements: Achievement[]
    className?: string
}

const CATEGORY_COLORS: Record<string, string> = {
    streak: "from-orange-400 to-red-500",
    messages: "from-blue-400 to-indigo-500",
    vocabulary: "from-green-400 to-emerald-500",
    accuracy: "from-purple-400 to-pink-500",
    stars: "from-yellow-400 to-amber-500",
    review: "from-teal-400 to-cyan-500",
    thematic: "from-pink-400 to-rose-500",
    time: "from-indigo-400 to-violet-500",
    quality: "from-emerald-400 to-green-500",
    challenge: "from-amber-400 to-orange-500",
}

const CATEGORY_LABELS: Record<string, string> = {
    streak: "🔥 Série",
    messages: "💬 Zprávy",
    vocabulary: "📚 Slovíčka",
    accuracy: "🎯 Přesnost",
    stars: "⭐ Hvězdy",
    review: "🧠 Opakování",
    thematic: "🎭 Tematické",
    time: "⏰ Časové",
    quality: "✨ Kvalita",
    challenge: "🏆 Výzvy",
}

export function AchievementGrid({ achievements, className = "" }: AchievementGridProps) {
    // Group by category
    const grouped = achievements.reduce((acc, achievement) => {
        if (!acc[achievement.category]) {
            acc[achievement.category] = []
        }
        acc[achievement.category].push(achievement)
        return acc
    }, {} as Record<string, Achievement[]>)

    return (
        <div className={`space-y-6 ${className}`}>
            {Object.entries(grouped).map(([category, categoryAchievements]) => (
                <div key={category}>
                    {/* Category header */}
                    <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-3">
                        {CATEGORY_LABELS[category] || category}
                    </h3>

                    {/* Achievement cards */}
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                        {categoryAchievements.map((achievement) => (
                            <AchievementCard key={achievement.id} achievement={achievement} />
                        ))}
                    </div>
                </div>
            ))}
        </div>
    )
}

interface AchievementCardProps {
    achievement: Achievement
}

function AchievementCard({ achievement }: AchievementCardProps) {
    const colorClass = CATEGORY_COLORS[achievement.category] || "from-gray-400 to-gray-500"

    return (
        <div
            className={`relative rounded-xl overflow-hidden transition-all duration-300 ${achievement.is_unlocked
                    ? "transform hover:scale-105 shadow-lg"
                    : "opacity-60 grayscale"
                }`}
        >
            {/* Background gradient */}
            <div className={`absolute inset-0 bg-gradient-to-br ${colorClass} opacity-20`} />

            <div className="relative p-4 text-center">
                {/* Lock overlay for locked achievements */}
                {!achievement.is_unlocked && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/10">
                        <Lock className="h-6 w-6 text-gray-400" />
                    </div>
                )}

                {/* Icon */}
                <div className={`text-4xl mb-2 ${!achievement.is_unlocked && "blur-sm"}`}>
                    {achievement.icon}
                </div>

                {/* Name */}
                <h4 className="font-semibold text-sm text-gray-800 dark:text-gray-200 truncate">
                    {achievement.name}
                </h4>

                {/* Description */}
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                    {achievement.description}
                </p>

                {/* Stars reward */}
                {achievement.stars_reward > 0 && (
                    <div className={`mt-2 text-xs font-medium ${achievement.is_unlocked ? "text-yellow-600" : "text-gray-400"
                        }`}>
                        ⭐ {achievement.stars_reward}
                    </div>
                )}

                {/* Unlocked date */}
                {achievement.is_unlocked && achievement.unlocked_at && (
                    <div className="mt-1 text-[10px] text-gray-400">
                        {new Date(achievement.unlocked_at).toLocaleDateString()}
                    </div>
                )}
            </div>
        </div>
    )
}

interface AchievementProgressProps {
    total: number
    unlocked: number
    percent: number
}

export function AchievementProgress({ total, unlocked, percent }: AchievementProgressProps) {
    return (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm">
            <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Achievements
                </span>
                <span className="text-sm text-gray-500">
                    {unlocked} / {total}
                </span>
            </div>

            {/* Progress bar */}
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                    className="h-full bg-gradient-to-r from-yellow-400 to-amber-500 transition-all duration-500"
                    style={{ width: `${percent}%` }}
                />
            </div>

            <p className="text-xs text-gray-500 mt-2 text-center">
                {percent}% complete
            </p>
        </div>
    )
}
