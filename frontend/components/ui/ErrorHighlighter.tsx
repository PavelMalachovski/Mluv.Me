"use client"

import { useState } from "react"

interface ErrorMatch {
    original: string
    corrected: string
    explanation?: string
    severity?: "critical" | "important" | "style"
}

interface ErrorHighlighterProps {
    text: string
    errors: ErrorMatch[]
    className?: string
}

export function ErrorHighlighter({ text, errors, className = "" }: ErrorHighlighterProps) {
    const [activeTooltip, setActiveTooltip] = useState<number | null>(null)

    if (!errors || errors.length === 0) {
        return <span className={className}>{text}</span>
    }

    // Create a map of error positions
    const errorMap = new Map<string, ErrorMatch>()
    errors.forEach((error) => {
        errorMap.set(error.original.toLowerCase(), error)
    })

    // Split text into words while preserving spaces and punctuation
    const tokens = text.split(/(\s+|[.,!?;:]+)/)

    return (
        <span className={className}>
            {tokens.map((token, index) => {
                const error = errorMap.get(token.toLowerCase())

                if (!error) {
                    return <span key={index}>{token}</span>
                }

                const severityColors = {
                    critical: "bg-red-200 dark:bg-red-900/50 text-red-900 dark:text-red-200 border-b-2 border-red-500",
                    important: "bg-yellow-200 dark:bg-yellow-900/50 text-yellow-900 dark:text-yellow-200 border-b-2 border-yellow-500",
                    style: "bg-green-200 dark:bg-green-900/50 text-green-900 dark:text-green-200 border-b-2 border-green-500",
                }

                const severity = error.severity || "important"
                const isActive = activeTooltip === index

                return (
                    <span
                        key={index}
                        className="relative inline-block"
                        onMouseEnter={() => setActiveTooltip(index)}
                        onMouseLeave={() => setActiveTooltip(null)}
                        onClick={() => setActiveTooltip(isActive ? null : index)}
                    >
                        <mark className={`cursor-pointer rounded px-0.5 ${severityColors[severity]}`}>
                            {token}
                        </mark>

                        {/* Tooltip */}
                        {isActive && (
                            <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 z-50 animate-fade-in">
                                <div className="bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 px-3 py-2 rounded-lg shadow-lg text-sm min-w-[150px] max-w-[250px]">
                                    {/* Corrected version */}
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="text-red-400 dark:text-red-600 line-through">{error.original}</span>
                                        <span className="text-gray-400">→</span>
                                        <span className="text-green-400 dark:text-green-600 font-medium">{error.corrected}</span>
                                    </div>

                                    {/* Explanation */}
                                    {error.explanation && (
                                        <p className="text-xs text-gray-300 dark:text-gray-600 mt-1">
                                            {error.explanation}
                                        </p>
                                    )}

                                    {/* Severity indicator */}
                                    <div className="flex items-center gap-1 mt-2 text-xs">
                                        <span
                                            className={`w-2 h-2 rounded-full ${severity === "critical" ? "bg-red-500" :
                                                    severity === "important" ? "bg-yellow-500" :
                                                        "bg-green-500"
                                                }`}
                                        />
                                        <span className="capitalize text-gray-400 dark:text-gray-500">
                                            {severity === "critical" ? "Changes meaning" :
                                                severity === "important" ? "Grammar error" :
                                                    "Style suggestion"}
                                        </span>
                                    </div>
                                </div>

                                {/* Arrow */}
                                <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0
                  border-l-8 border-r-8 border-t-8
                  border-l-transparent border-r-transparent border-t-gray-900 dark:border-t-gray-100"
                                />
                            </div>
                        )}
                    </span>
                )
            })}
        </span>
    )
}

/**
 * Parse backend mistakes into ErrorMatch format
 */
export function parseBackendMistakes(mistakes: string[]): ErrorMatch[] {
    return mistakes.map((mistake) => {
        // Try to parse patterns like "word -> correction: explanation"
        const arrowMatch = mistake.match(/^(.+?)\s*(?:→|->)\s*(.+?)(?::\s*(.+))?$/)
        if (arrowMatch) {
            return {
                original: arrowMatch[1].trim(),
                corrected: arrowMatch[2].trim(),
                explanation: arrowMatch[3]?.trim(),
                severity: "important" as const,
            }
        }

        // Try to parse "word (should be: correction)"
        const parenMatch = mistake.match(/^(.+?)\s*\((?:should be|správně):\s*(.+?)\)/)
        if (parenMatch) {
            return {
                original: parenMatch[1].trim(),
                corrected: parenMatch[2].trim(),
                severity: "important" as const,
            }
        }

        // Fallback - just highlight the first word
        const words = mistake.split(/\s+/)
        return {
            original: words[0] || mistake,
            corrected: "?",
            explanation: mistake,
            severity: "style" as const,
        }
    })
}
