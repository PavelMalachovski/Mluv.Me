"use client"

import { useState } from "react"
import { Lightbulb, ChevronDown, ChevronUp } from "lucide-react"
import { Button } from "@/components/ui/button"

interface Hint {
    type: "vocabulary" | "grammar" | "phrase" | "suggestion"
    czech: string
    translation: string
    usage?: string
}

interface HintChipsProps {
    hints: Hint[]
    onHintClick?: (hint: Hint) => void
    className?: string
}

const HINT_TYPE_STYLES: Record<string, { bg: string; text: string; label: string }> = {
    vocabulary: {
        bg: "bg-blue-100 dark:bg-blue-900/30 hover:bg-blue-200 dark:hover:bg-blue-900/50",
        text: "text-blue-700 dark:text-blue-300",
        label: "📚"
    },
    grammar: {
        bg: "bg-purple-100 dark:bg-purple-900/30 hover:bg-purple-200 dark:hover:bg-purple-900/50",
        text: "text-purple-700 dark:text-purple-300",
        label: "📝"
    },
    phrase: {
        bg: "bg-green-100 dark:bg-green-900/30 hover:bg-green-200 dark:hover:bg-green-900/50",
        text: "text-green-700 dark:text-green-300",
        label: "💬"
    },
    suggestion: {
        bg: "bg-amber-100 dark:bg-amber-900/30 hover:bg-amber-200 dark:hover:bg-amber-900/50",
        text: "text-amber-700 dark:text-amber-300",
        label: "💡"
    },
}

export function HintChips({ hints, onHintClick, className = "" }: HintChipsProps) {
    const [isExpanded, setIsExpanded] = useState(false)
    const [selectedHint, setSelectedHint] = useState<Hint | null>(null)

    if (!hints || hints.length === 0) return null

    const visibleHints = isExpanded ? hints : hints.slice(0, 3)
    const hiddenCount = hints.length - 3

    const handleHintClick = (hint: Hint) => {
        setSelectedHint(selectedHint?.czech === hint.czech ? null : hint)
        onHintClick?.(hint)
    }

    return (
        <div className={`space-y-2 ${className}`}>
            {/* Header */}
            <div className="flex items-center gap-2 text-sm text-gray-500">
                <Lightbulb className="h-4 w-4 text-yellow-500" />
                <span>Need help? Try these:</span>
            </div>

            {/* Chips */}
            <div className="flex flex-wrap gap-2">
                {visibleHints.map((hint, index) => {
                    const style = HINT_TYPE_STYLES[hint.type] || HINT_TYPE_STYLES.suggestion
                    const isSelected = selectedHint?.czech === hint.czech

                    return (
                        <button
                            key={index}
                            onClick={() => handleHintClick(hint)}
                            className={`
                inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm
                transition-all duration-200 cursor-pointer
                ${style.bg} ${style.text}
                ${isSelected ? "ring-2 ring-offset-1 ring-primary" : ""}
              `}
                        >
                            <span>{style.label}</span>
                            <span className="font-medium">{hint.czech}</span>
                        </button>
                    )
                })}

                {/* Expand button */}
                {hiddenCount > 0 && (
                    <button
                        onClick={() => setIsExpanded(!isExpanded)}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-sm
              bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400
              hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                    >
                        {isExpanded ? (
                            <>
                                <ChevronUp className="h-3 w-3" />
                                Less
                            </>
                        ) : (
                            <>
                                +{hiddenCount} more
                                <ChevronDown className="h-3 w-3" />
                            </>
                        )}
                    </button>
                )}
            </div>

            {/* Selected hint details */}
            {selectedHint && (
                <div className="mt-2 p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 animate-fade-in">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="font-semibold text-gray-800 dark:text-gray-200">
                                {selectedHint.czech}
                            </p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                = {selectedHint.translation}
                            </p>
                            {selectedHint.usage && (
                                <p className="mt-1 text-xs text-gray-500 italic">
                                    Usage: &ldquo;{selectedHint.usage}&rdquo;
                                </p>
                            )}
                        </div>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setSelectedHint(null)}
                            className="text-xs"
                        >
                            ✕
                        </Button>
                    </div>
                </div>
            )}
        </div>
    )
}

// Sample hints for different topics
export const TOPIC_HINTS: Record<string, Hint[]> = {
    hospoda: [
        { type: "phrase", czech: "Jedno pivo, prosím", translation: "One beer, please", usage: "Jedno pivo, prosím!" },
        { type: "vocabulary", czech: "účet", translation: "bill/check", usage: "Můžu dostat účet?" },
        { type: "phrase", czech: "Na zdraví!", translation: "Cheers!", usage: "Na zdraví!" },
        { type: "vocabulary", czech: "točené", translation: "draft (beer)", usage: "Dáte si točené?" },
        { type: "grammar", czech: "Dáte si...?", translation: "Will you have...?", usage: "Dáte si ještě jedno?" },
    ],
    nadrazi: [
        { type: "phrase", czech: "Kdy jede vlak do...", translation: "When does the train leave for...", usage: "Kdy jede vlak do Prahy?" },
        { type: "vocabulary", czech: "nástupiště", translation: "platform", usage: "Které nástupiště?" },
        { type: "vocabulary", czech: "jízdenka", translation: "ticket", usage: "Jednu jízdenku do Brna" },
        { type: "phrase", czech: "zpáteční", translation: "return (ticket)", usage: "Jednu zpáteční, prosím" },
        { type: "vocabulary", czech: "zpoždění", translation: "delay", usage: "Vlak má zpoždění" },
    ],
    obchod: [
        { type: "phrase", czech: "Kolik to stojí?", translation: "How much does it cost?", usage: "Kolik to stojí?" },
        { type: "vocabulary", czech: "sleva", translation: "discount", usage: "Je tam sleva?" },
        { type: "phrase", czech: "Můžu platit kartou?", translation: "Can I pay by card?", usage: "Můžu platit kartou?" },
        { type: "vocabulary", czech: "pokladna", translation: "checkout/cashier", usage: "Kde je pokladna?" },
        { type: "grammar", czech: "Hledám...", translation: "I'm looking for...", usage: "Hledám mléko" },
    ],
    restaurace: [
        { type: "phrase", czech: "Máte volný stůl?", translation: "Do you have a free table?", usage: "Dobrý den, máte volný stůl?" },
        { type: "vocabulary", czech: "jídelní lístek", translation: "menu", usage: "Můžu prosím jídelní lístek?" },
        { type: "phrase", czech: "Dám si...", translation: "I'll have...", usage: "Dám si svíčkovou" },
        { type: "vocabulary", czech: "dezert", translation: "dessert", usage: "Máte nějaký dezert?" },
        { type: "phrase", czech: "Zaplatím, prosím", translation: "I'll pay, please", usage: "Zaplatím, prosím" },
    ],
    lekar: [
        { type: "phrase", czech: "Bolí mě...", translation: "My ... hurts", usage: "Bolí mě hlava" },
        { type: "vocabulary", czech: "recept", translation: "prescription", usage: "Potřebuji recept" },
        { type: "vocabulary", czech: "lékárna", translation: "pharmacy", usage: "Kde je nejbližší lékárna?" },
        { type: "phrase", czech: "Jsem nemocný/á", translation: "I'm sick", usage: "Jsem nemocný" },
        { type: "vocabulary", czech: "horečka", translation: "fever", usage: "Mám horečku" },
    ],
    free: [
        { type: "phrase", czech: "Jak se máš?", translation: "How are you?", usage: "Ahoj, jak se máš?" },
        { type: "phrase", czech: "Co děláš?", translation: "What are you doing?", usage: "Co děláš dnes večer?" },
        { type: "vocabulary", czech: "rád/a", translation: "I like", usage: "Mám rád české pivo" },
        { type: "phrase", czech: "Odkud jsi?", translation: "Where are you from?", usage: "Odkud jsi?" },
        { type: "grammar", czech: "Myslím, že...", translation: "I think that...", usage: "Myslím, že Praha je krásná" },
    ],
}

export type { Hint }
