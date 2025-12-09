"use client"

import { useState, useEffect } from "react"
import Image from "next/image"

export type MascotEmotion = "happy" | "thinking" | "encouraging" | "waving" | "stars" | "reading" | "running"

interface AnimatedMascotProps {
    emotion: MascotEmotion
    size?: number
    className?: string
    animate?: boolean
}

const EMOTION_IMAGES: Record<MascotEmotion, string> = {
    happy: "/images/mascot/honzik-happy.png",
    thinking: "/images/mascot/honzik-thinking.png",
    encouraging: "/images/mascot/honzik-encouraging.png",
    waving: "/images/mascot/honzik-waving.png",
    stars: "/images/mascot/honzik-stars.png",
    reading: "/images/mascot/honzik-reading.png",
    running: "/images/mascot/honzik-running.png",
}

const EMOTION_MESSAGES: Record<MascotEmotion, string[]> = {
    happy: ["Skvělé! 🎉", "Výborně! ⭐", "Super! 💪"],
    thinking: ["Hmm... 🤔", "Počkej... 💭", "Moment..."],
    encouraging: ["Nevadí! 💪", "Zkus to znovu!", "Pokračuj! 🎯"],
    waving: ["Ahoj! 👋", "Nazdar! 🇨🇿", "Čau!"],
    stars: ["Wow! ⭐⭐⭐", "Perfektní!", "Mistr!"],
    reading: ["Učíme se! 📚", "Studium...", "Čteme..."],
    running: ["Rychle! 🏃", "Běžíme!", "Tempo!"],
}

export function AnimatedMascot({
    emotion,
    size = 100,
    className = "",
    animate = true
}: AnimatedMascotProps) {
    const [currentEmotion, setCurrentEmotion] = useState<MascotEmotion>(emotion)
    const [isTransitioning, setIsTransitioning] = useState(false)
    const [message, setMessage] = useState<string | null>(null)

    // Handle emotion changes with transition
    useEffect(() => {
        if (emotion !== currentEmotion) {
            setIsTransitioning(true)
            const timer = setTimeout(() => {
                setCurrentEmotion(emotion)
                setIsTransitioning(false)

                // Show a random message for the emotion
                const messages = EMOTION_MESSAGES[emotion]
                setMessage(messages[Math.floor(Math.random() * messages.length)])

                // Hide message after 2 seconds
                setTimeout(() => setMessage(null), 2000)
            }, 150)
            return () => clearTimeout(timer)
        }
    }, [emotion, currentEmotion])

    const animationClass = animate ? {
        happy: "animate-bounce",
        thinking: "",
        encouraging: "animate-pulse",
        waving: "animate-bounce",
        stars: "animate-pulse",
        reading: "",
        running: "animate-bounce",
    }[currentEmotion] : ""

    return (
        <div className={`relative inline-block ${className}`}>
            {/* Speech bubble */}
            {message && (
                <div className="absolute -top-8 left-1/2 -translate-x-1/2 whitespace-nowrap">
                    <div className="bg-white dark:bg-gray-800 px-3 py-1 rounded-full shadow-md text-sm font-medium animate-fade-in">
                        {message}
                    </div>
                    {/* Triangle pointer */}
                    <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-white dark:bg-gray-800 rotate-45" />
                </div>
            )}

            {/* Mascot image */}
            <div
                className={`transition-all duration-150 ${isTransitioning ? "scale-95 opacity-70" : "scale-100 opacity-100"
                    } ${animationClass}`}
            >
                <Image
                    src={EMOTION_IMAGES[currentEmotion]}
                    alt={`Honzík - ${currentEmotion}`}
                    width={size}
                    height={size}
                    className="drop-shadow-lg"
                    priority
                />
            </div>
        </div>
    )
}

/**
 * Get appropriate emotion based on correctness score
 */
export function getEmotionFromScore(score: number): MascotEmotion {
    if (score >= 90) return "happy"
    if (score >= 70) return "stars"
    if (score >= 50) return "encouraging"
    return "thinking"
}
