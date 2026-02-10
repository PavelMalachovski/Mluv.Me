"use client"

import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    AreaChart, Area, PieChart, Pie, Cell
} from "recharts"
import { TrendingUp, Target, Flame, Star, MessageCircle, BookOpen, Trophy } from "lucide-react"

// Helper to format date
function formatDayName(dateStr: string): string {
    const date = new Date(dateStr)
    return date.toLocaleDateString("cs-CZ", { weekday: "short" })
}

function transformDailyData(data: any[]) {
    return data.map((d) => ({
        date: formatDayName(d.date),
        messages: d.messages_count,
        accuracy: d.correct_percent,
    }))
}

interface StatsTabProps {
    telegramId: number
}

export function StatsTab({ telegramId }: StatsTabProps) {
    const { data: stats, isLoading } = useQuery({
        queryKey: ["user-stats", telegramId],
        queryFn: () => apiClient.getStats(telegramId),
        enabled: !!telegramId,
        staleTime: 30 * 1000,
    })

    const { data: dailyData } = useQuery({
        queryKey: ["daily-stats", telegramId],
        queryFn: () => apiClient.getDailyRange(telegramId, 7),
        enabled: !!telegramId,
    })

    const { data: reviewStats } = useQuery({
        queryKey: ["review-stats", telegramId],
        queryFn: () => apiClient.getReviewStats(telegramId),
        enabled: !!telegramId,
    })

    const chartData = dailyData ? transformDailyData(dailyData) : []

    if (isLoading) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard icon={<Flame className="h-5 w-5 text-orange-500" />} label="Aktuální série" value={stats?.streak || 0} suffix=" dní" />
                <StatCard icon={<Star className="h-5 w-5 text-yellow-500" />} label="Celkem hvězd" value={stats?.stars || 0} />
                <StatCard icon={<MessageCircle className="h-5 w-5 text-blue-500" />} label="Zpráv" value={stats?.messages_count || 0} />
                <StatCard icon={<Target className="h-5 w-5 text-green-500" />} label="Přesnost" value={stats?.correct_percent || 0} suffix="%" />
            </div>

            {/* Activity Chart */}
            {chartData.length > 0 && (
                <div className="illustrated-card p-4">
                    <h3 className="font-semibold mb-4 flex items-center gap-2">
                        <TrendingUp className="h-5 w-5 text-primary" />
                        Týdenní aktivita
                    </h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                                <XAxis dataKey="date" fontSize={12} />
                                <YAxis fontSize={12} />
                                <Tooltip contentStyle={{ backgroundColor: "white", border: "1px solid #e5e7eb", borderRadius: "8px" }} />
                                <Bar dataKey="messages" fill="#8B5CF6" radius={[4, 4, 0, 0]} name="Zpráv" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}

            {/* Accuracy Trend */}
            {chartData.length > 0 && (
                <div className="illustrated-card p-4">
                    <h3 className="font-semibold mb-4 flex items-center gap-2">
                        <Target className="h-5 w-5 text-green-500" />
                        Trend přesnosti
                    </h3>
                    <div className="h-48">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={chartData}>
                                <defs>
                                    <linearGradient id="colorAccuracy" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10B981" stopOpacity={0.8} />
                                        <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                                <XAxis dataKey="date" fontSize={12} />
                                <YAxis fontSize={12} domain={[0, 100]} />
                                <Tooltip />
                                <Area type="monotone" dataKey="accuracy" stroke="#10B981" fillOpacity={1} fill="url(#colorAccuracy)" name="Přesnost %" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}

            {/* Vocabulary Mastery Distribution */}
            {reviewStats && (
                <div className="illustrated-card p-4">
                    <h3 className="font-semibold mb-4 flex items-center gap-2">
                        <BookOpen className="h-5 w-5 text-blue-500" />
                        Ovládání slovíček
                    </h3>
                    <div className="flex flex-col md:flex-row items-center gap-6">
                        <div className="h-48 w-48">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={[
                                            { name: "Nové", value: reviewStats.mastery_breakdown?.new || 0, color: "#9CA3AF" },
                                            { name: "Učím se", value: reviewStats.mastery_breakdown?.learning || 0, color: "#F59E0B" },
                                            { name: "Známé", value: reviewStats.mastery_breakdown?.familiar || 0, color: "#3B82F6" },
                                            { name: "Osvojené", value: reviewStats.mastery_breakdown?.known || 0, color: "#10B981" },
                                            { name: "Mistr", value: reviewStats.mastery_breakdown?.mastered || 0, color: "#8B5CF6" },
                                        ]}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={40}
                                        outerRadius={70}
                                        paddingAngle={2}
                                        dataKey="value"
                                    >
                                        {[
                                            { color: "#9CA3AF" },
                                            { color: "#F59E0B" },
                                            { color: "#3B82F6" },
                                            { color: "#10B981" },
                                            { color: "#8B5CF6" },
                                        ].map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="flex-1 grid grid-cols-2 gap-2">
                            {[
                                { name: "Nové", color: "#9CA3AF", value: reviewStats.mastery_breakdown?.new || 0 },
                                { name: "Učím se", color: "#F59E0B", value: reviewStats.mastery_breakdown?.learning || 0 },
                                { name: "Známé", color: "#3B82F6", value: reviewStats.mastery_breakdown?.familiar || 0 },
                                { name: "Osvojené", color: "#10B981", value: reviewStats.mastery_breakdown?.known || 0 },
                                { name: "Mistr", color: "#8B5CF6", value: reviewStats.mastery_breakdown?.mastered || 0 },
                            ].map((item) => (
                                <div key={item.name} className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                                    <span className="text-sm text-gray-600 dark:text-gray-400">{item.name}: {item.value}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div className="mt-4 text-center">
                        <span className="text-2xl font-bold text-gray-800 dark:text-gray-200">{reviewStats.total_words || 0}</span>
                        <span className="text-sm text-gray-500 ml-2">celkem slov</span>
                    </div>
                </div>
            )}

            {/* Study Recommendations */}
            <div className="illustrated-card p-4">
                <h3 className="font-semibold mb-3">📈 Doporučení</h3>
                <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                    {stats?.streak === 0 && (
                        <li className="flex items-start gap-2">
                            <span className="text-orange-500">🔥</span>
                            Začni sérii! Procvičuj každý den.
                        </li>
                    )}
                    {(reviewStats?.due_today || 0) > 0 && (
                        <li className="flex items-start gap-2">
                            <span className="text-blue-500">📚</span>
                            Dnes máš {reviewStats?.due_today} slov k opakování.
                        </li>
                    )}
                    {(stats?.correct_percent || 0) < 70 && (
                        <li className="flex items-start gap-2">
                            <span className="text-green-500">🎯</span>
                            Zaměř se na přesnost - zkus kratší, pečlivější zprávy.
                        </li>
                    )}
                    {(stats?.messages_count || 0) < 50 && (
                        <li className="flex items-start gap-2">
                            <span className="text-purple-500">💬</span>
                            Procvičuj více! Čím víc píšeš, tím rychleji se učíš.
                        </li>
                    )}
                </ul>
            </div>

            {/* Achievements Section */}
            <div className="illustrated-card p-4">
                <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <Trophy className="h-5 w-5 text-yellow-500" />
                    Úspěchy
                </h3>
                <div className="grid gap-3 grid-cols-2">
                    {stats?.streak && stats.streak >= 7 && (
                        <AchievementBadge
                            emoji="🔥"
                            name="Week Warrior"
                            description="7 dní v řadě"
                            bgClass="bg-orange-50 dark:bg-orange-900/20"
                        />
                    )}
                    {stats?.messages_count && stats.messages_count >= 50 && (
                        <AchievementBadge
                            emoji="💬"
                            name="Chatty"
                            description="50+ zpráv"
                            bgClass="bg-purple-50 dark:bg-purple-900/20"
                        />
                    )}
                    {stats?.stars && stats.stars >= 100 && (
                        <AchievementBadge
                            emoji="⭐"
                            name="Star Collector"
                            description="100+ hvězd"
                            bgClass="bg-yellow-50 dark:bg-yellow-900/20"
                        />
                    )}
                    {stats?.words_said && stats.words_said >= 100 && (
                        <AchievementBadge
                            emoji="📚"
                            name="Word Master"
                            description="100+ slov"
                            bgClass="bg-blue-50 dark:bg-blue-900/20"
                        />
                    )}
                </div>
                {/* Empty achievements message */}
                {(!stats?.streak || stats.streak < 7) &&
                    (!stats?.messages_count || stats.messages_count < 50) &&
                    (!stats?.stars || stats.stars < 100) &&
                    (!stats?.words_said || stats.words_said < 100) && (
                        <div className="text-center py-6">
                            <div className="text-4xl mb-2">🎯</div>
                            <p className="text-sm text-muted-foreground">Pokračuj ve cvičení a odemkni úspěchy!</p>
                        </div>
                    )}
            </div>
        </div>
    )
}

interface StatCardProps {
    icon: React.ReactNode
    label: string
    value: number
    suffix?: string
}

function StatCard({ icon, label, value, suffix = "" }: StatCardProps) {
    return (
        <div className="illustrated-card p-4 text-center">
            <div className="flex justify-center mb-2">{icon}</div>
            <div className="text-2xl font-bold text-gray-800 dark:text-gray-200">{value}{suffix}</div>
            <div className="text-xs text-gray-500">{label}</div>
        </div>
    )
}

interface AchievementBadgeProps {
    emoji: string
    name: string
    description: string
    bgClass: string
}

function AchievementBadge({ emoji, name, description, bgClass }: AchievementBadgeProps) {
    return (
        <div className={`flex items-center gap-3 rounded-lg ${bgClass} p-3`}>
            <div className="text-2xl">{emoji}</div>
            <div>
                <div className="font-medium text-foreground">{name}</div>
                <div className="text-xs text-muted-foreground">{description}</div>
            </div>
        </div>
    )
}
