"use client"

import { useState, useEffect } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/auth-store"
import { apiClient } from "@/lib/api-client"
import { Button } from "@/components/ui/button"
import { ReviewCard } from "@/components/features/ReviewCard"
import { IllustratedHeader } from "@/components/ui/IllustratedHeader"
import { IllustratedEmptyState } from "@/components/ui/IllustratedEmptyState"
import { ReviewSession, ReviewWord, ReviewQuality, ReviewStats } from "@/lib/types"
import { ArrowLeft, Clock, BookOpen, Trophy } from "lucide-react"

export default function ReviewPage() {
    const router = useRouter()
    const queryClient = useQueryClient()
    const user = useAuthStore((state) => state.user)

    const [currentIndex, setCurrentIndex] = useState(0)
    const [sessionStats, setSessionStats] = useState({
        again: 0,
        hard: 0,
        good: 0,
        easy: 0,
    })
    const [isComplete, setIsComplete] = useState(false)

    // Fetch words for review
    const { data: reviewData, isLoading } = useQuery<ReviewSession>({
        queryKey: ["review-words", user?.telegram_id],
        queryFn: () => apiClient.getWordsForReview(user!.telegram_id, 20),
        enabled: !!user?.telegram_id,
    })

    // Fetch review stats
    const { data: stats } = useQuery<ReviewStats>({
        queryKey: ["review-stats", user?.telegram_id],
        queryFn: () => apiClient.getReviewStats(user!.telegram_id),
        enabled: !!user?.telegram_id,
    })

    // Submit answer mutation
    const submitAnswer = useMutation({
        mutationFn: ({ wordId, quality }: { wordId: number; quality: ReviewQuality }) =>
            apiClient.submitReviewAnswer(wordId, quality),
        onSuccess: (_, variables) => {
            // Update session stats
            const qualityNames: Record<ReviewQuality, keyof typeof sessionStats> = {
                0: "again",
                1: "hard",
                2: "good",
                3: "easy",
            }
            setSessionStats((prev) => ({
                ...prev,
                [qualityNames[variables.quality]]: prev[qualityNames[variables.quality]] + 1,
            }))

            // Move to next word or complete
            if (reviewData && currentIndex < reviewData.words.length - 1) {
                setCurrentIndex((prev) => prev + 1)
            } else {
                setIsComplete(true)
                // Invalidate queries to refresh data
                queryClient.invalidateQueries({ queryKey: ["review-words"] })
                queryClient.invalidateQueries({ queryKey: ["review-stats"] })
                queryClient.invalidateQueries({ queryKey: ["saved-words"] })
            }
        },
    })

    if (!user) {
        router.push("/login")
        return null
    }

    const handleAnswer = (quality: ReviewQuality) => {
        if (reviewData && reviewData.words[currentIndex]) {
            submitAnswer.mutate({
                wordId: reviewData.words[currentIndex].id,
                quality,
            })
        }
    }

    const handleRestart = () => {
        setCurrentIndex(0)
        setSessionStats({ again: 0, hard: 0, good: 0, easy: 0 })
        setIsComplete(false)
        queryClient.invalidateQueries({ queryKey: ["review-words"] })
    }

    const totalReviewed = sessionStats.again + sessionStats.hard + sessionStats.good + sessionStats.easy
    const correctCount = sessionStats.good + sessionStats.easy
    const accuracy = totalReviewed > 0 ? Math.round((correctCount / totalReviewed) * 100) : 0

    return (
        <div className="min-h-screen cream-bg landscape-bg pb-20">
            <IllustratedHeader title="Opakování slov" />

            <div className="mx-auto max-w-2xl px-4 pt-6">
                {/* Back button */}
                <Button
                    variant="ghost"
                    onClick={() => router.push("/dashboard")}
                    className="mb-4"
                >
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Zpět
                </Button>

                {isLoading ? (
                    <div className="flex items-center justify-center py-12">
                        <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                    </div>
                ) : isComplete ? (
                    /* Completion Screen */
                    <div className="illustrated-card p-8 text-center">
                        <div className="text-6xl mb-4">🎉</div>
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                            Relace dokončena!
                        </h2>
                        <p className="text-gray-600 dark:text-gray-400 mb-6">
                            Zopakoval/a jsi {totalReviewed} slov s {accuracy}% přesností
                        </p>

                        {/* Stats breakdown */}
                        <div className="grid grid-cols-4 gap-3 mb-6">
                            <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/20">
                                <div className="text-2xl font-bold text-red-600">{sessionStats.again}</div>
                                <div className="text-xs text-red-600">Znovu</div>
                            </div>
                            <div className="p-3 rounded-lg bg-orange-50 dark:bg-orange-900/20">
                                <div className="text-2xl font-bold text-orange-600">{sessionStats.hard}</div>
                                <div className="text-xs text-orange-600">Těžké</div>
                            </div>
                            <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20">
                                <div className="text-2xl font-bold text-blue-600">{sessionStats.good}</div>
                                <div className="text-xs text-blue-600">Dobře</div>
                            </div>
                            <div className="p-3 rounded-lg bg-green-50 dark:bg-green-900/20">
                                <div className="text-2xl font-bold text-green-600">{sessionStats.easy}</div>
                                <div className="text-xs text-green-600">Lehké</div>
                            </div>
                        </div>

                        {/* Stars earned */}
                        {accuracy >= 50 && (
                            <div className="flex items-center justify-center gap-2 mb-6 text-yellow-500">
                                <Trophy className="h-6 w-6" />
                                <span className="text-lg font-medium">
                                    +{accuracy >= 90 ? 5 : accuracy >= 75 ? 3 : accuracy >= 50 ? 2 : 1} hvězd získáno!
                                </span>
                            </div>
                        )}

                        <div className="flex gap-3 justify-center">
                            <Button variant="outline" onClick={() => router.push("/dashboard/saved")}>
                                Zobrazit všechna slova
                            </Button>
                            <Button onClick={handleRestart}>
                                Opakovat více
                            </Button>
                        </div>
                    </div>
                ) : reviewData && reviewData.words.length > 0 ? (
                    /* Review Session */
                    <div>
                        {/* Progress bar */}
                        <div className="mb-6">
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-sm text-gray-600 dark:text-gray-400">
                                    {currentIndex + 1} z {reviewData.words.length}
                                </span>
                                <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1">
                                    <Clock className="h-4 w-4" />
                                    ~{reviewData.estimated_minutes} min
                                </span>
                            </div>
                            <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-primary transition-all duration-300"
                                    style={{ width: `${((currentIndex + 1) / reviewData.words.length) * 100}%` }}
                                />
                            </div>
                        </div>

                        {/* Current card */}
                        <ReviewCard
                            word={reviewData.words[currentIndex]}
                            onAnswer={handleAnswer}
                            isSubmitting={submitAnswer.isPending}
                        />
                    </div>
                ) : (
                    /* Empty state */
                    <IllustratedEmptyState
                        title="Žádná slova k opakování"
                        description="Skvělé! Máš vše zopakováno. Ulož více slov během procvičování pro pozdější opakování."
                        buttonText="Začít procvičovat"
                        buttonHref="/dashboard/practice"
                    />
                )}

                {/* Stats section */}
                {stats && !isComplete && (
                    <div className="mt-8 illustrated-card p-4">
                        <h3 className="font-semibold mb-3 flex items-center gap-2">
                            <BookOpen className="h-5 w-5 text-primary" />
                            Tvůj pokrok
                        </h3>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                                <span className="text-gray-500">Celkem slov:</span>
                                <span className="float-right font-medium">{stats.total_words}</span>
                            </div>
                            <div>
                                <span className="text-gray-500">Dnes k opakování:</span>
                                <span className="float-right font-medium text-orange-500">{stats.due_today}</span>
                            </div>
                            <div className="col-span-2">
                                <div className="text-gray-500 mb-2">Úrovně znalosti:</div>
                                <div className="flex gap-1">
                                    {Object.entries(stats.mastery_breakdown).map(([level, count]) => (
                                        <div
                                            key={level}
                                            className="flex-1 text-center py-1 rounded text-xs"
                                            style={{
                                                backgroundColor:
                                                    level === "new" ? "#f3f4f6" :
                                                        level === "learning" ? "#fef3c7" :
                                                            level === "familiar" ? "#dbeafe" :
                                                                level === "known" ? "#d1fae5" :
                                                                    "#e9d5ff",
                                            }}
                                        >
                                            {count}
                                        </div>
                                    ))}
                                </div>
                                <div className="flex text-[10px] text-gray-400 mt-1">
                                    <div className="flex-1 text-center">Nové</div>
                                    <div className="flex-1 text-center">Učím se</div>
                                    <div className="flex-1 text-center">Známé</div>
                                    <div className="flex-1 text-center">Osvojené</div>
                                    <div className="flex-1 text-center">Mistr</div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
