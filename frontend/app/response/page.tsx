"use client"

import { useState, useEffect } from "react"
import { useSearchParams } from "next/navigation"
import { useMutation } from "@tanstack/react-query"
import { useAuthStore } from "@/lib/auth-store"
import { apiClient } from "@/lib/api-client"
import { ClickableText } from "@/components/ui/ClickableText"
import { TranslationPopup } from "@/components/ui/TranslationPopup"
import { WordTranslation } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { Languages } from "lucide-react"

interface TranslationState {
    word: string
    translation: string | null
    phonetics: string | null
    isLoading: boolean
    position: { top: number; left: number }
}

export default function ResponsePage() {
    const searchParams = useSearchParams()
    const user = useAuthStore((state) => state.user)
    const [text, setText] = useState("")
    const [translateMode, setTranslateMode] = useState(true) // Включен по умолчанию
    const [translationState, setTranslationState] = useState<TranslationState | null>(null)

    useEffect(() => {
        // Получаем текст из URL параметров
        const textParam = searchParams.get("text")
        if (textParam) {
            setText(decodeURIComponent(textParam))
        }
    }, [searchParams])

    const translateWord = useMutation({
        mutationFn: (word: string) =>
            apiClient.translateWord(word, user?.ui_language || "ru"),
        onSuccess: (data: WordTranslation) => {
            setTranslationState((prev) =>
                prev ? {
                    ...prev,
                    translation: data.translation,
                    phonetics: data.phonetics || null,
                    isLoading: false
                } : null
            )
        },
        onError: () => {
            setTranslationState((prev) =>
                prev ? { ...prev, translation: null, isLoading: false } : null
            )
        },
    })

    const saveWord = useMutation({
        mutationFn: (wordData: { word_czech: string; translation: string }) =>
            apiClient.saveWord(user!.id, wordData),
        onSuccess: () => {
            setTranslationState(null)
        },
    })

    const handleWordClick = (word: string, rect: DOMRect) => {
        setTranslationState({
            word,
            translation: null,
            phonetics: null,
            isLoading: true,
            position: { top: rect.bottom + window.scrollY, left: rect.left + rect.width / 2 },
        })
        translateWord.mutate(word)
    }

    const handleSaveWord = () => {
        if (translationState?.translation) {
            saveWord.mutate({
                word_czech: translationState.word,
                translation: translationState.translation,
            })
        }
    }

    if (!text) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center">
                <p className="text-gray-600 dark:text-gray-400">Загрузка...</p>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
            <div className="container mx-auto max-w-4xl p-6">
                {/* Header */}
                <div className="mb-6 flex items-center justify-between">
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                        Ответ Хонзика
                    </h1>
                    <Button
                        variant={translateMode ? "default" : "outline"}
                        size="sm"
                        onClick={() => setTranslateMode(!translateMode)}
                        className={`flex items-center gap-2 ${translateMode
                                ? "bg-yellow-500 hover:bg-yellow-600 text-black"
                                : ""
                            }`}
                    >
                        <Languages className="h-4 w-4" />
                        {translateMode ? "Выключить перевод" : "Translate by word"}
                    </Button>
                </div>

                {/* Text Content */}
                <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-6 shadow-sm">
                    {translateMode ? (
                        <>
                            <ClickableText
                                text={text}
                                onWordClick={handleWordClick}
                                className="text-lg leading-relaxed text-gray-800 dark:text-gray-200"
                            />
                            <div className="mt-4 rounded-md bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 p-3 text-sm text-yellow-800 dark:text-yellow-200">
                                💡 Нажмите на любое слово, чтобы увидеть перевод
                            </div>
                        </>
                    ) : (
                        <p className="text-lg leading-relaxed text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
                            {text}
                        </p>
                    )}
                </div>

                {/* Tips */}
                <div className="mt-6 rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-6 shadow-sm">
                    <h3 className="mb-3 font-semibold text-gray-900 dark:text-gray-100">
                        Как использовать:
                    </h3>
                    <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                        <li>✅ Кликай на слова для перевода</li>
                        <li>✅ Сохраняй новые слова в словарь</li>
                        <li>✅ Изучай чешский язык эффективно</li>
                    </ul>
                </div>
            </div>

            {/* Translation Popup */}
            {translationState && (
                <TranslationPopup
                    word={translationState.word}
                    translation={translationState.translation}
                    isLoading={translationState.isLoading}
                    position={translationState.position}
                    onClose={() => setTranslationState(null)}
                    onSave={handleSaveWord}
                    phonetics={translationState.phonetics}
                />
            )}
        </div>
    )
}
