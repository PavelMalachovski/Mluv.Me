"use client"

import { useState, useRef } from "react"
import { Volume2, Tag, MessageSquare, Loader2, ChevronDown, ChevronUp, X, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"

interface EnhancedWord {
    id: number
    word_czech: string
    translation: string
    phonetic?: string
    examples?: string[]
    tags?: string[]
    audio_url?: string
    notes?: string
    mastery_level?: 'new' | 'learning' | 'familiar' | 'known' | 'mastered'
}

interface EnhancedWordCardProps {
    word: EnhancedWord
    onPlayAudio?: (word: string) => void
    onAddTag?: (wordId: number, tag: string) => void
    onRemoveTag?: (wordId: number, tag: string) => void
    onDelete?: (wordId: number) => void
    className?: string
}

const MASTERY_COLORS = {
    new: 'bg-gray-100 text-gray-600',
    learning: 'bg-yellow-100 text-yellow-700',
    familiar: 'bg-blue-100 text-blue-700',
    known: 'bg-green-100 text-green-700',
    mastered: 'bg-purple-100 text-purple-700',
}

export function EnhancedWordCard({
    word,
    onPlayAudio,
    onAddTag,
    onRemoveTag,
    onDelete,
    className = "",
}: EnhancedWordCardProps) {
    const [isExpanded, setIsExpanded] = useState(false)
    const [isPlayingAudio, setIsPlayingAudio] = useState(false)
    const [showTagInput, setShowTagInput] = useState(false)
    const [newTag, setNewTag] = useState("")
    const audioRef = useRef<HTMLAudioElement | null>(null)

    const handlePlayAudio = async () => {
        if (isPlayingAudio) return

        setIsPlayingAudio(true)

        try {
            // Try custom audio URL first
            if (word.audio_url) {
                if (!audioRef.current) {
                    audioRef.current = new Audio(word.audio_url)
                }
                await audioRef.current.play()
            } else {
                // Use Web Speech API as fallback
                const utterance = new SpeechSynthesisUtterance(word.word_czech)
                utterance.lang = 'cs-CZ'
                utterance.rate = 0.8
                speechSynthesis.speak(utterance)
            }

            onPlayAudio?.(word.word_czech)
        } catch (error) {
            console.error('Audio playback failed:', error)
        }

        setIsPlayingAudio(false)
    }

    const handleAddTag = () => {
        if (newTag.trim() && onAddTag) {
            onAddTag(word.id, newTag.trim())
            setNewTag("")
            setShowTagInput(false)
        }
    }

    const masteryClass = word.mastery_level
        ? MASTERY_COLORS[word.mastery_level]
        : MASTERY_COLORS.new

    return (
        <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden ${className}`}>
            {/* Main row */}
            <div className="p-4">
                <div className="flex items-start justify-between gap-3">
                    {/* Word info */}
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                            <h3 className="font-bold text-lg text-gray-900 dark:text-gray-100">
                                {word.word_czech}
                            </h3>

                            {/* Audio button */}
                            <button
                                onClick={handlePlayAudio}
                                disabled={isPlayingAudio}
                                className="p-1.5 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                                title="Listen to pronunciation"
                            >
                                {isPlayingAudio ? (
                                    <Loader2 className="h-4 w-4 animate-spin text-primary" />
                                ) : (
                                    <Volume2 className="h-4 w-4 text-gray-500 hover:text-primary" />
                                )}
                            </button>
                        </div>

                        {/* Phonetic */}
                        {word.phonetic && (
                            <p className="text-sm text-gray-400 italic">
                                /{word.phonetic}/
                            </p>
                        )}

                        {/* Translation */}
                        <p className="text-gray-600 dark:text-gray-400 mt-1">
                            {word.translation}
                        </p>
                    </div>

                    {/* Mastery badge */}
                    {word.mastery_level && (
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium capitalize ${masteryClass}`}>
                            {word.mastery_level}
                        </span>
                    )}
                </div>

                {/* Tags */}
                {(word.tags && word.tags.length > 0) || showTagInput ? (
                    <div className="flex flex-wrap gap-1.5 mt-3">
                        {word.tags?.map((tag) => (
                            <span
                                key={tag}
                                className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400"
                            >
                                <Tag className="h-3 w-3" />
                                {tag}
                                {onRemoveTag && (
                                    <button
                                        onClick={() => onRemoveTag(word.id, tag)}
                                        className="hover:text-red-500"
                                    >
                                        <X className="h-3 w-3" />
                                    </button>
                                )}
                            </span>
                        ))}

                        {showTagInput ? (
                            <div className="flex items-center gap-1">
                                <input
                                    type="text"
                                    value={newTag}
                                    onChange={(e) => setNewTag(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleAddTag()}
                                    placeholder="Tag..."
                                    className="w-20 px-2 py-0.5 text-xs rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800"
                                    autoFocus
                                />
                                <button onClick={handleAddTag} className="text-primary">
                                    <Plus className="h-4 w-4" />
                                </button>
                                <button onClick={() => setShowTagInput(false)} className="text-gray-400">
                                    <X className="h-4 w-4" />
                                </button>
                            </div>
                        ) : onAddTag && (
                            <button
                                onClick={() => setShowTagInput(true)}
                                className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-gray-100 dark:bg-gray-700 text-gray-400 hover:text-primary"
                            >
                                <Plus className="h-3 w-3" />
                                Add tag
                            </button>
                        )}
                    </div>
                ) : null}

                {/* Expand toggle */}
                {(word.examples || word.notes) && (
                    <button
                        onClick={() => setIsExpanded(!isExpanded)}
                        className="flex items-center gap-1 mt-3 text-sm text-gray-500 hover:text-primary"
                    >
                        {isExpanded ? (
                            <>
                                <ChevronUp className="h-4 w-4" />
                                Less
                            </>
                        ) : (
                            <>
                                <ChevronDown className="h-4 w-4" />
                                Examples & notes
                            </>
                        )}
                    </button>
                )}
            </div>

            {/* Expanded content */}
            {isExpanded && (
                <div className="px-4 pb-4 pt-0 border-t border-gray-100 dark:border-gray-700">
                    {/* Examples */}
                    {word.examples && word.examples.length > 0 && (
                        <div className="mt-3">
                            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-1.5 mb-2">
                                <MessageSquare className="h-4 w-4" />
                                Examples
                            </h4>
                            <ul className="space-y-2">
                                {word.examples.map((example, index) => (
                                    <li key={index} className="text-sm text-gray-600 dark:text-gray-400 pl-4 border-l-2 border-primary/30">
                                        {example}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* Notes */}
                    {word.notes && (
                        <div className="mt-3">
                            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                Notes
                            </h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900 rounded p-2">
                                {word.notes}
                            </p>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}

// Compact word chip for inline display
interface WordChipProps {
    word: string
    translation?: string
    onClick?: () => void
    onPlayAudio?: () => void
    className?: string
}

export function WordChip({ word, translation, onClick, onPlayAudio, className = "" }: WordChipProps) {
    return (
        <span
            onClick={onClick}
            className={`
        inline-flex items-center gap-1.5 px-2 py-1 rounded-lg
        bg-primary/10 text-primary cursor-pointer
        hover:bg-primary/20 transition-colors
        ${className}
      `}
        >
            <span className="font-medium">{word}</span>
            {translation && (
                <span className="text-xs text-gray-500">({translation})</span>
            )}
            {onPlayAudio && (
                <button
                    onClick={(e) => {
                        e.stopPropagation()
                        onPlayAudio()
                    }}
                    className="p-0.5 hover:text-primary"
                >
                    <Volume2 className="h-3 w-3" />
                </button>
            )}
        </span>
    )
}
