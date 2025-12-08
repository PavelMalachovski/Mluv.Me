"use client"

import Image from "next/image"
import { useRouter } from "next/navigation"

interface IllustratedEmptyStateProps {
    title: string
    description: string
    buttonText?: string
    buttonHref?: string
    mascotImage?: string
    showLandscape?: boolean
}

export function IllustratedEmptyState({
    title,
    description,
    buttonText = "Start Practicing",
    buttonHref = "/dashboard/practice",
    mascotImage = "/images/mascot/honzik-waving.png",
    showLandscape = true,
}: IllustratedEmptyStateProps) {
    const router = useRouter()

    return (
        <div className={`illustrated-empty-state ${showLandscape ? "landscape-bg" : "cream-bg"}`}>
            {/* Mascot */}
            <Image
                src={mascotImage}
                alt="Honzík"
                width={150}
                height={150}
                className="mascot drop-shadow-xl"
            />

            {/* Message */}
            <div className="message bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm rounded-xl p-4">
                <h3>{title}</h3>
                <p>{description}</p>

                {/* Wooden Button */}
                <button
                    onClick={() => router.push(buttonHref)}
                    className="wooden-button"
                >
                    {buttonText}
                </button>
            </div>
        </div>
    )
}
