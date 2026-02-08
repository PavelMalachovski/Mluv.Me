"use client"

import Image from "next/image"

interface IllustratedHeaderProps {
    title: string
    subtitle?: string
    mascot?: boolean
}

export function IllustratedHeader({ title, subtitle, mascot = false }: IllustratedHeaderProps) {
    return (
        <div className="illustrated-header">
            <h1 className="illustrated-header-title">{title}</h1>
            {subtitle && (
                <p className="text-sm text-white/80 mt-1 text-center">
                    {subtitle}
                </p>
            )}
            {mascot && (
                <div className="absolute -bottom-10 left-1/2 -translate-x-1/2">
                    <Image
                        src="/images/mascot/honzik-waving.png"
                        alt="Honzík"
                        width={80}
                        height={80}
                        className="drop-shadow-lg mix-blend-multiply"
                    />
                </div>
            )}
        </div>
    )
}
