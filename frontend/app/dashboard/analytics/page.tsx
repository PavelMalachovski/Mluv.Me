"use client"

import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/auth-store"
import { apiClient } from "@/lib/api-client"
import { Button } from "@/components/ui/button"
import { IllustratedHeader } from "@/components/ui/IllustratedHeader"
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    LineChart, Line, AreaChart, Area, PieChart, Pie, Cell
} from "recharts"
import { ArrowLeft, TrendingUp, Target, Flame, Star, MessageCircle, BookOpen } from "lucide-react"

// Helper to format date as day name
function formatDayName(dateStr: string): string {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { weekday: 'short' })
}

// Helper to transform API data for charts
function transformDailyData(data: any[]) {
    return data.map(d => ({
        date: formatDayName(d.date),
        messages: d.messages_count,
        accuracy: d.correct_percent,
    }))
}

export default function AnalyticsPage() {
    const router = useRouter()
    const user = useAuthStore((state) => state.user)

    const { data: stats, isLoading } = useQuery({
        queryKey: ["user-stats", user?.telegram_id],
        queryFn: () => apiClient.getStats(user!.telegram_id),
        enabled: !!user?.telegram_id,
    })

    const { data: dailyData } = useQuery({
        queryKey: ["daily-stats", user?.telegram_id],
        queryFn: () => apiClient.getDailyRange(user!.telegram_id, 7),
        enabled: !!user?.telegram_id,
    })

    const { data: reviewStats } = useQuery({
        queryKey: ["review-stats", user?.telegram_id],
        queryFn: () => apiClient.getReviewStats(user!.telegram_id),
        enabled: !!user?.telegram_id,
    })

    // Transform daily data for charts
    const chartData = dailyData ? transformDailyData(dailyData) : []

    if (!user) {
        router.push("/login")
        return null
    }

    return (
        <div className="min-h-screen cream-bg landscape-bg pb-24">
            <IllustratedHeader title="Analytics" />

            <div className="mx-auto max-w-4xl px-4 pt-6">
                {/* Back button */}
                <Button
                    variant="ghost"
                    onClick={() => router.push("/dashboard")}
                    className="mb-4"
                >
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back
                </Button>

                {isLoading ? (
                    <div className="flex items-center justify-center py-12">
                        <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                    </div>
                ) : (
                    <div className="space-y-6">
                        {/* Summary Cards */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <StatCard
                                icon={<Flame className="h-5 w-5 text-orange-500" />}
                                label="Current Streak"
                                value={stats?.streak || 0}
                                suffix=" days"
                            />
                            <StatCard
                                icon={<Star className="h-5 w-5 text-yellow-500" />}
                                label="Total Stars"
                                value={stats?.stars || 0}
                            />
                            <StatCard
                                icon={<MessageCircle className="h-5 w-5 text-blue-500" />}
                                label="Messages"
                                value={stats?.messages_count || 0}
                            />
                            <StatCard
                                icon={<Target className="h-5 w-5 text-green-500" />}
                                label="Accuracy"
                                value={stats?.correct_percent || 0}
                                suffix="%"
                            />
                        </div>

                        {/* Activity Chart */}
                        <div className="illustrated-card p-4">
                            <h3 className="font-semibold mb-4 flex items-center gap-2">
                                <TrendingUp className="h-5 w-5 text-primary" />
                                Weekly Activity
                            </h3>
                            <div className="h-64">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={chartData}>
                                        <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                                        <XAxis dataKey="date" fontSize={12} />
                                        <YAxis fontSize={12} />
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: 'white',
                                                border: '1px solid #e5e7eb',
                                                borderRadius: '8px',
                                            }}
                                        />
                                        <Bar
                                            dataKey="messages"
                                            fill="#8B5CF6"
                                            radius={[4, 4, 0, 0]}
                                            name="Messages"
                                        />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Accuracy Trend */}
                        <div className="illustrated-card p-4">
                            <h3 className="font-semibold mb-4 flex items-center gap-2">
                                <Target className="h-5 w-5 text-green-500" />
                                Accuracy Trend
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
                                        <Area
                                            type="monotone"
                                            dataKey="accuracy"
                                            stroke="#10B981"
                                            fillOpacity={1}
                                            fill="url(#colorAccuracy)"
                                            name="Accuracy %"
                                        />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Vocabulary Mastery Distribution */}
                        {reviewStats && (
                            <div className="illustrated-card p-4">
                                <h3 className="font-semibold mb-4 flex items-center gap-2">
                                    <BookOpen className="h-5 w-5 text-blue-500" />
                                    Vocabulary Mastery
                                </h3>
                                <div className="flex flex-col md:flex-row items-center gap-6">
                                    <div className="h-48 w-48">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <PieChart>
                                                <Pie
                                                    data={[
                                                        { name: "New", value: reviewStats.mastery_breakdown?.new || 0, color: "#9CA3AF" },
                                                        { name: "Learning", value: reviewStats.mastery_breakdown?.learning || 0, color: "#F59E0B" },
                                                        { name: "Familiar", value: reviewStats.mastery_breakdown?.familiar || 0, color: "#3B82F6" },
                                                        { name: "Known", value: reviewStats.mastery_breakdown?.known || 0, color: "#10B981" },
                                                        { name: "Mastered", value: reviewStats.mastery_breakdown?.mastered || 0, color: "#8B5CF6" },
                                                    ]}
                                                    cx="50%"
                                                    cy="50%"
                                                    innerRadius={40}
                                                    outerRadius={70}
                                                    paddingAngle={2}
                                                    dataKey="value"
                                                >
                                                    {[
                                                        { name: "New", color: "#9CA3AF" },
                                                        { name: "Learning", color: "#F59E0B" },
                                                        { name: "Familiar", color: "#3B82F6" },
                                                        { name: "Known", color: "#10B981" },
                                                        { name: "Mastered", color: "#8B5CF6" },
                                                    ].map((entry, index) => (
                                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                                    ))}
                                                </Pie>
                                                <Tooltip />
                                            </PieChart>
                                        </ResponsiveContainer>
                                    </div>

                                    {/* Legend */}
                                    <div className="flex-1 grid grid-cols-2 gap-2">
                                        {[
                                            { name: "New", color: "#9CA3AF", value: reviewStats.mastery_breakdown?.new || 0 },
                                            { name: "Learning", color: "#F59E0B", value: reviewStats.mastery_breakdown?.learning || 0 },
                                            { name: "Familiar", color: "#3B82F6", value: reviewStats.mastery_breakdown?.familiar || 0 },
                                            { name: "Known", color: "#10B981", value: reviewStats.mastery_breakdown?.known || 0 },
                                            { name: "Mastered", color: "#8B5CF6", value: reviewStats.mastery_breakdown?.mastered || 0 },
                                        ].map((item) => (
                                            <div key={item.name} className="flex items-center gap-2">
                                                <div
                                                    className="w-3 h-3 rounded-full"
                                                    style={{ backgroundColor: item.color }}
                                                />
                                                <span className="text-sm text-gray-600 dark:text-gray-400">
                                                    {item.name}: {item.value}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Total */}
                                <div className="mt-4 text-center">
                                    <span className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                                        {reviewStats.total_words || 0}
                                    </span>
                                    <span className="text-sm text-gray-500 ml-2">total words</span>
                                </div>
                            </div>
                        )}

                        {/* Study Recommendations */}
                        <div className="illustrated-card p-4">
                            <h3 className="font-semibold mb-3">📈 Recommendations</h3>
                            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                                {stats?.streak === 0 && (
                                    <li className="flex items-start gap-2">
                                        <span className="text-orange-500">🔥</span>
                                        Start a streak! Practice daily to build consistency.
                                    </li>
                                )}
                                {(reviewStats?.due_today || 0) > 0 && (
                                    <li className="flex items-start gap-2">
                                        <span className="text-blue-500">📚</span>
                                        You have {reviewStats?.due_today} words due for review today.
                                    </li>
                                )}
                                {(stats?.correct_percent || 0) < 70 && (
                                    <li className="flex items-start gap-2">
                                        <span className="text-green-500">🎯</span>
                                        Focus on accuracy - try shorter, more careful messages.
                                    </li>
                                )}
                                {(stats?.messages_count || 0) < 50 && (
                                    <li className="flex items-start gap-2">
                                        <span className="text-purple-500">💬</span>
                                        Practice more! The more you write, the faster you learn.
                                    </li>
                                )}
                            </ul>
                        </div>
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
            <div className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                {value}{suffix}
            </div>
            <div className="text-xs text-gray-500">{label}</div>
        </div>
    )
}
