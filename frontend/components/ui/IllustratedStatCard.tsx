"use client"

import Image from "next/image"

interface IllustratedStatCardProps {
    label: string
    value: string | number
    mascotImage?: string
    showNumber?: boolean
}

export function IllustratedStatCard({
    label,
    value,
    mascotImage,
    showNumber = false,
}: IllustratedStatCardProps) {
    return (
        <div className="illustrated-card illustrated-stat-card">
            {mascotImage ? (
                <Image
                    src={mascotImage}
                    alt={label}
                    width={64}
                    height={64}
                    className="drop-shadow-md"
                />
            ) : (
                <div className="text-3xl font-bold text-primary">{value}</div>
            )}
            {mascotImage && !showNumber && (
                <span className="stat-label">{label}</span>
            )}
            {mascotImage && showNumber && (
                <>
                    <span className="stat-value">{value}</span>
                    <span className="stat-label">{label}</span>
                </>
            )}
            {!mascotImage && <span className="stat-label">{label}</span>}
        </div>
    )
}
