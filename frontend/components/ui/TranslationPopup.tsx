"use client"

import React, { useEffect, useRef } from "react"
import { X, Bookmark, Volume2 } from "lucide-react"
import { Button } from "./button"

interface TranslationPopupProps {
    word: string
    translation: string | null
    isLoading: boolean
    position: { top: number; left: number }
    onClose: () => void
    onSave: () => void
    phonetics?: string | null
}

/**
 * Popup component that displays word translation.
 * Appears near the clicked word with translation and save option.
 */
export function TranslationPopup({
    word,
    translation,
    isLoading,
    position,
    onClose,
    onSave,
    phonetics,
}: TranslationPopupProps) {
    const popupRef = useRef<HTMLDivElement>(null)

    // Close on click outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (popupRef.current && !popupRef.current.contains(event.target as Node)) {
                onClose()
            }
        }

        document.addEventListener("mousedown", handleClickOutside)
        return () => document.removeEventListener("mousedown", handleClickOutside)
    }, [onClose])

    // Close on Escape key
    useEffect(() => {
        const handleEscape = (event: KeyboardEvent) => {
            if (event.key === "Escape") {
                onClose()
            }
        }

        document.addEventListener("keydown", handleEscape)
        return () => document.removeEventListener("keydown", handleEscape)
    }, [onClose])

    // Keep popup within viewport bounds
    useEffect(() => {
        if (!popupRef.current) return
        const el = popupRef.current
        const rect = el.getBoundingClientRect()
        const vw = window.innerWidth
        const vh = window.innerHeight
        const pad = 12

        // Clamp left edge so popup doesn't overflow left or right
        if (rect.left < pad) {
            el.style.left = `${pad + rect.width / 2}px`
        } else if (rect.right > vw - pad) {
            el.style.left = `${vw - pad - rect.width / 2}px`
        }

        // If popup goes below viewport, show above the word
        if (rect.bottom > vh - pad) {
            el.style.top = `${position.top - rect.height - 20}px`
        }
    }, [position])

    return (
        <div
            ref={popupRef}
            className="absolute z-50 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl p-4 min-w-[220px] max-w-[300px]"
            style={{
                top: `${position.top + 10}px`,
                left: `clamp(140px, ${position.left}px, calc(100vw - 160px))`,
                transform: "translateX(-50%)",
            }}
        >
            {/* Header with word and close button */}
            <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                        {word}
                    </h3>
                    {phonetics && (
                        <p className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-1">
                            <Volume2 className="h-3 w-3" />
                            {phonetics}
                        </p>
                    )}
                </div>
                <button
                    onClick={onClose}
                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
                >
                    <X className="h-5 w-5" />
                </button>
            </div>

            {/* Translation content */}
            <div className="border-t border-gray-200 dark:border-gray-700 pt-3">
                {isLoading ? (
                    <div className="flex items-center gap-2 text-gray-500">
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-blue-500" />
                        <span>Переводим...</span>
                    </div>
                ) : translation ? (
                    <div className="space-y-2">
                        <p className="text-lg text-gray-800 dark:text-gray-200 font-medium">
                            {translation}
                        </p>
                    </div>
                ) : (
                    <p className="text-gray-500">Перевод не найден</p>
                )}
            </div>

            {/* Save button */}
            {translation && !isLoading && (
                <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
                    <Button
                        onClick={onSave}
                        variant="outline"
                        size="sm"
                        className="w-full flex items-center justify-center gap-2"
                    >
                        <Bookmark className="h-4 w-4" />
                        Сохранить в словарь
                    </Button>
                </div>
            )}
        </div>
    )
}
