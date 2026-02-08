"use client";

/**
 * AnimatedProgress - Animated progress bar component with smooth transitions
 *
 * Features:
 * - Smooth fill animation on value change
 * - Gradient colors based on progress
 * - Pulse effect when value increases
 * - Support for daily goals and achievement progress
 */

import { useEffect, useState, useRef } from "react";
import { cn } from "@/lib/utils";

interface AnimatedProgressProps {
    /** Current value (0-100) */
    value: number;
    /** Maximum value (default: 100) */
    max?: number;
    /** Height of the progress bar */
    height?: "sm" | "md" | "lg";
    /** Show percentage label */
    showLabel?: boolean;
    /** Custom gradient colors */
    gradient?: string;
    /** Label text (replaces percentage) */
    label?: string;
    /** Animate on mount */
    animateOnMount?: boolean;
    /** Additional class names */
    className?: string;
}

const HEIGHT_CLASSES = {
    sm: "h-2",
    md: "h-3",
    lg: "h-4",
};

const DEFAULT_GRADIENT = "from-green-400 to-green-500";

// Gradient based on progress level
function getProgressGradient(percent: number): string {
    if (percent >= 100) return "from-yellow-400 to-amber-500"; // Complete!
    if (percent >= 75) return "from-green-400 to-emerald-500"; // Almost there
    if (percent >= 50) return "from-blue-400 to-cyan-500"; // Halfway
    if (percent >= 25) return "from-indigo-400 to-purple-500"; // Getting started
    return "from-gray-400 to-gray-500"; // Just beginning
}

export function AnimatedProgress({
    value,
    max = 100,
    height = "md",
    showLabel = false,
    gradient,
    label,
    animateOnMount = true,
    className,
}: AnimatedProgressProps) {
    const [displayValue, setDisplayValue] = useState(animateOnMount ? 0 : value);
    const [isPulsing, setIsPulsing] = useState(false);
    const prevValueRef = useRef(value);

    const percent = Math.min(100, Math.max(0, (value / max) * 100));
    const progressGradient = gradient || getProgressGradient(percent);

    // Animate value changes
    useEffect(() => {
        const prevValue = prevValueRef.current;
        prevValueRef.current = value;

        // Check if value increased (trigger pulse)
        if (value > prevValue) {
            setIsPulsing(true);
            const timer = setTimeout(() => setIsPulsing(false), 600);
            return () => clearTimeout(timer);
        }
    }, [value]);

    // Smooth animation on mount and value change
    useEffect(() => {
        if (animateOnMount) {
            // Delayed animation for mount
            const timer = setTimeout(() => {
                setDisplayValue(percent);
            }, 100);
            return () => clearTimeout(timer);
        } else {
            setDisplayValue(percent);
        }
    }, [percent, animateOnMount]);

    return (
        <div className={cn("relative", className)}>
            {/* Background track */}
            <div
                className={cn(
                    "bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden",
                    HEIGHT_CLASSES[height]
                )}
            >
                {/* Animated fill */}
                <div
                    className={cn(
                        "h-full rounded-full bg-gradient-to-r transition-all duration-700 ease-out",
                        progressGradient,
                        isPulsing && "animate-pulse"
                    )}
                    style={{ width: `${displayValue}%` }}
                >
                    {/* Shimmer effect for 100% */}
                    {percent >= 100 && (
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
                    )}
                </div>
            </div>

            {/* Label */}
            {showLabel && (
                <span className="absolute right-0 top-1/2 -translate-y-1/2 text-xs font-medium text-gray-600 dark:text-gray-400 -mr-10">
                    {label || `${Math.round(percent)}%`}
                </span>
            )}
        </div>
    );
}

/**
 * DailyProgressBar - Specialized progress bar for daily goals
 */
interface DailyProgressBarProps {
    current: number;
    goal: number;
    className?: string;
}

export function DailyProgressBar({
    current,
    goal,
    className,
}: DailyProgressBarProps) {
    const percent = Math.min(100, (current / goal) * 100);
    const isComplete = current >= goal;

    return (
        <div className={cn("space-y-2", className)}>
            <div className="flex items-center justify-between text-sm">
                <span className="font-medium text-gray-700 dark:text-gray-300">
                    Dnešní pokrok
                </span>
                <span className={cn(
                    "font-semibold",
                    isComplete ? "text-green-600" : "text-gray-600 dark:text-gray-400"
                )}>
                    {current} / {goal}
                    {isComplete && " 🎉"}
                </span>
            </div>
            <AnimatedProgress
                value={current}
                max={goal}
                height="md"
                animateOnMount
            />
        </div>
    );
}

/**
 * StreakProgressBar - Progress bar for streak achievements
 */
interface StreakProgressBarProps {
    currentStreak: number;
    targetStreak: number;
    className?: string;
}

export function StreakProgressBar({
    currentStreak,
    targetStreak,
    className,
}: StreakProgressBarProps) {
    const percent = Math.min(100, (currentStreak / targetStreak) * 100);

    return (
        <div className={cn("space-y-2", className)}>
            <div className="flex items-center justify-between text-sm">
                <span className="font-medium text-gray-700 dark:text-gray-300 flex items-center gap-1">
                    🔥 Série dnů
                </span>
                <span className="font-semibold text-orange-600">
                    {currentStreak} / {targetStreak}
                </span>
            </div>
            <AnimatedProgress
                value={currentStreak}
                max={targetStreak}
                height="md"
                gradient="from-orange-400 to-red-500"
                animateOnMount
            />
        </div>
    );
}

export default AnimatedProgress;
