"use client"

import { useState, useRef, useEffect } from "react"
import { Send, Mic, X, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"

interface MobileInputProps {
    value: string
    onChange: (value: string) => void
    onSubmit: () => void
    onVoiceClick?: () => void
    placeholder?: string
    isLoading?: boolean
    disabled?: boolean
    showVoice?: boolean
    className?: string
}

export function MobileInput({
    value,
    onChange,
    onSubmit,
    onVoiceClick,
    placeholder = "Type a message...",
    isLoading = false,
    disabled = false,
    showVoice = true,
    className = "",
}: MobileInputProps) {
    const textareaRef = useRef<HTMLTextAreaElement>(null)
    const [isFocused, setIsFocused] = useState(false)

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto'
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`
        }
    }, [value])

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        // Submit on Enter (without Shift)
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            if (value.trim() && !isLoading && !disabled) {
                onSubmit()
            }
        }
    }

    const handleClear = () => {
        onChange('')
        textareaRef.current?.focus()
    }

    return (
        <div
            className={`
        fixed bottom-0 left-0 right-0 z-40
        bg-white dark:bg-gray-900
        border-t border-gray-200 dark:border-gray-800
        pb-safe
        ${className}
      `}
        >
            <div className="flex items-end gap-2 p-3">
                {/* Voice button */}
                {showVoice && onVoiceClick && (
                    <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={onVoiceClick}
                        disabled={disabled || isLoading}
                        className="flex-shrink-0 h-10 w-10 rounded-full"
                    >
                        <Mic className="h-5 w-5" />
                    </Button>
                )}

                {/* Input container */}
                <div
                    className={`
            flex-1 relative flex items-end
            bg-gray-100 dark:bg-gray-800 rounded-2xl
            transition-all
            ${isFocused ? 'ring-2 ring-primary' : ''}
          `}
                >
                    <textarea
                        ref={textareaRef}
                        value={value}
                        onChange={(e) => onChange(e.target.value)}
                        onKeyDown={handleKeyDown}
                        onFocus={() => setIsFocused(true)}
                        onBlur={() => setIsFocused(false)}
                        placeholder={placeholder}
                        disabled={disabled || isLoading}
                        rows={1}
                        className={`
              flex-1 bg-transparent resize-none
              px-4 py-2.5
              text-gray-900 dark:text-gray-100
              placeholder:text-gray-500 dark:placeholder:text-gray-400
              focus:outline-none
              max-h-[120px]
            `}
                        style={{ minHeight: '44px' }}
                    />

                    {/* Clear button */}
                    {value && (
                        <button
                            type="button"
                            onClick={handleClear}
                            className="absolute right-2 bottom-2 p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700"
                        >
                            <X className="h-4 w-4 text-gray-400" />
                        </button>
                    )}
                </div>

                {/* Send button */}
                <Button
                    type="button"
                    size="icon"
                    onClick={onSubmit}
                    disabled={!value.trim() || disabled || isLoading}
                    className={`
            flex-shrink-0 h-10 w-10 rounded-full
            ${value.trim() ? 'bg-primary' : 'bg-gray-300 dark:bg-gray-700'}
          `}
                >
                    {isLoading ? (
                        <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                        <Send className="h-5 w-5" />
                    )}
                </Button>
            </div>

            {/* Safe area padding for iOS */}
            <style jsx>{`
        .pb-safe {
          padding-bottom: env(safe-area-inset-bottom, 0);
        }
      `}</style>
        </div>
    )
}

// Floating action button for mobile
interface FloatingActionButtonProps {
    icon: React.ReactNode
    onClick: () => void
    label?: string
    className?: string
    variant?: 'primary' | 'secondary'
}

export function FloatingActionButton({
    icon,
    onClick,
    label,
    className = "",
    variant = 'primary',
}: FloatingActionButtonProps) {
    return (
        <button
            onClick={onClick}
            className={`
        fixed bottom-24 right-4 z-40
        flex items-center justify-center gap-2
        ${label ? 'px-5 py-3 rounded-full' : 'w-14 h-14 rounded-full'}
        shadow-lg
        transition-all hover:scale-105 active:scale-95
        ${variant === 'primary'
                    ? 'bg-primary text-white'
                    : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-700'
                }
        ${className}
      `}
        >
            {icon}
            {label && <span className="font-medium">{label}</span>}
        </button>
    )
}

// Pull to refresh component
interface PullToRefreshProps {
    onRefresh: () => Promise<void>
    children: React.ReactNode
    className?: string
}

export function PullToRefresh({ onRefresh, children, className = "" }: PullToRefreshProps) {
    const [isPulling, setIsPulling] = useState(false)
    const [isRefreshing, setIsRefreshing] = useState(false)
    const [pullDistance, setPullDistance] = useState(0)
    const containerRef = useRef<HTMLDivElement>(null)
    const startY = useRef(0)

    const THRESHOLD = 80

    const handleTouchStart = (e: React.TouchEvent) => {
        if (containerRef.current?.scrollTop === 0) {
            startY.current = e.touches[0].clientY
            setIsPulling(true)
        }
    }

    const handleTouchMove = (e: React.TouchEvent) => {
        if (!isPulling) return

        const currentY = e.touches[0].clientY
        const diff = Math.max(0, currentY - startY.current)

        // Apply resistance
        const distance = Math.min(150, diff * 0.5)
        setPullDistance(distance)
    }

    const handleTouchEnd = async () => {
        if (pullDistance > THRESHOLD && !isRefreshing) {
            setIsRefreshing(true)
            await onRefresh()
            setIsRefreshing(false)
        }

        setIsPulling(false)
        setPullDistance(0)
    }

    return (
        <div
            ref={containerRef}
            className={`relative ${className}`}
            onTouchStart={handleTouchStart}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleTouchEnd}
        >
            {/* Pull indicator */}
            <div
                className="absolute top-0 left-1/2 -translate-x-1/2 z-50"
                style={{
                    transform: `translate(-50%, ${pullDistance - 40}px)`,
                    opacity: Math.min(1, pullDistance / THRESHOLD),
                }}
            >
                <div className={`
          w-8 h-8 rounded-full bg-white dark:bg-gray-800 shadow-md
          flex items-center justify-center
          ${isRefreshing ? 'animate-spin' : ''}
        `}>
                    <Loader2 className={`h-4 w-4 ${isRefreshing ? '' : 'rotate-180'}`} />
                </div>
            </div>

            {/* Content */}
            <div style={{ transform: `translateY(${pullDistance}px)` }}>
                {children}
            </div>
        </div>
    )
}
