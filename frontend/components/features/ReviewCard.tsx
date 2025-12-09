"use client"

import { useState } from "react"
import { Volume2, RotateCcw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ReviewWord, ReviewQuality } from "@/lib/types"

interface ReviewCardProps {
    word: ReviewWord
    onAnswer: (quality: ReviewQuality) => void
    isSubmitting: boolean
}

export function ReviewCard({ word, onAnswer, isSubmitting }: ReviewCardProps) {
    const [isFlipped, setIsFlipped] = useState(false)

    const handleSpeak = () => {
        if (typeof window !== "undefined" && window.speechSynthesis) {
            const utterance = new SpeechSynthesisUtterance(word.word_czech)
            utterance.lang = "cs-CZ"
            utterance.rate = 0.8
            window.speechSynthesis.speak(utterance)
        }
    }

    const masteryColors: Record<string, string> = {
        new: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
        learning: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
        familiar: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
        known: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
        mastered: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
    }

    return (
        <div className="w-full max-w-md mx-auto">
            {/* Card */}
            <div
                onClick={() => !isFlipped && setIsFlipped(true)}
                className={`relative min-h-[300px] rounded-2xl shadow-lg cursor-pointer transition-all duration-500 transform-gpu ${isFlipped ? "bg-white dark:bg-gray-800" : "bg-gradient-to-br from-primary/90 to-primary text-white"
                    }`}
                style={{
                    perspective: "1000px",
                }}
            >
                {/* Front - Czech word */}
                {!isFlipped && (
                    <div className="absolute inset-0 flex flex-col items-center justify-center p-8">
                        {/* Mastery badge */}
                        <span className={`absolute top-4 right-4 px-3 py-1 rounded-full text-xs font-medium ${masteryColors[word.mastery_level]}`}>
                            {word.mastery_level}
                        </span>

                        {/* Word */}
                        <h2 className="text-4xl font-bold mb-4 text-center">
                            {word.word_czech}
                        </h2>

                        {/* Phonetics */}
                        {word.phonetics && (
                            <p className="text-lg opacity-75 mb-4">[{word.phonetics}]</p>
                        )}

                        {/* Audio button */}
                        <Button
                            variant="secondary"
                            size="icon"
                            onClick={(e) => {
                                e.stopPropagation()
                                handleSpeak()
                            }}
                            className="mt-4"
                        >
                            <Volume2 className="h-5 w-5" />
                        </Button>

                        {/* Hint */}
                        <p className="absolute bottom-6 text-sm opacity-60">
                            Tap to reveal translation
                        </p>
                    </div>
                )}

                {/* Back - Translation */}
                {isFlipped && (
                    <div className="absolute inset-0 flex flex-col items-center justify-center p-8">
                        {/* Reset button */}
                        <button
                            onClick={(e) => {
                                e.stopPropagation()
                                setIsFlipped(false)
                            }}
                            className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        >
                            <RotateCcw className="h-4 w-4 text-gray-500" />
                        </button>

                        {/* Czech word (smaller) */}
                        <p className="text-xl text-gray-500 dark:text-gray-400 mb-2">
                            {word.word_czech}
                        </p>

                        {/* Translation */}
                        <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4 text-center">
                            {word.translation}
                        </h2>

                        {/* Context sentence */}
                        {word.context_sentence && (
                            <p className="text-sm text-gray-600 dark:text-gray-400 italic text-center max-w-[280px]">
                                &ldquo;{word.context_sentence}&rdquo;
                            </p>
                        )}

                        {/* Review count */}
                        <p className="absolute bottom-6 text-xs text-gray-400">
                            Reviewed {word.sr_review_count} times
                        </p>
                    </div>
                )}
            </div>

            {/* Answer buttons - only show when flipped */}
            {isFlipped && (
                <div className="mt-6 grid grid-cols-4 gap-2">
                    <Button
                        variant="outline"
                        onClick={() => onAnswer(0)}
                        disabled={isSubmitting}
                        className="flex flex-col py-4 h-auto border-red-300 hover:bg-red-50 hover:border-red-400 dark:border-red-800 dark:hover:bg-red-900/20"
                    >
                        <span className="text-2xl mb-1">😔</span>
                        <span className="text-xs font-medium text-red-600 dark:text-red-400">Again</span>
                    </Button>

                    <Button
                        variant="outline"
                        onClick={() => onAnswer(1)}
                        disabled={isSubmitting}
                        className="flex flex-col py-4 h-auto border-orange-300 hover:bg-orange-50 hover:border-orange-400 dark:border-orange-800 dark:hover:bg-orange-900/20"
                    >
                        <span className="text-2xl mb-1">🤔</span>
                        <span className="text-xs font-medium text-orange-600 dark:text-orange-400">Hard</span>
                    </Button>

                    <Button
                        variant="outline"
                        onClick={() => onAnswer(2)}
                        disabled={isSubmitting}
                        className="flex flex-col py-4 h-auto border-blue-300 hover:bg-blue-50 hover:border-blue-400 dark:border-blue-800 dark:hover:bg-blue-900/20"
                    >
                        <span className="text-2xl mb-1">😊</span>
                        <span className="text-xs font-medium text-blue-600 dark:text-blue-400">Good</span>
                    </Button>

                    <Button
                        variant="outline"
                        onClick={() => onAnswer(3)}
                        disabled={isSubmitting}
                        className="flex flex-col py-4 h-auto border-green-300 hover:bg-green-50 hover:border-green-400 dark:border-green-800 dark:hover:bg-green-900/20"
                    >
                        <span className="text-2xl mb-1">🌟</span>
                        <span className="text-xs font-medium text-green-600 dark:text-green-400">Easy</span>
                    </Button>
                </div>
            )}
        </div>
    )
}
