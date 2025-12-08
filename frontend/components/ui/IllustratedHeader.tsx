"use client"

import Image from "next/image"

interface IllustratedHeaderProps {
    title: string
    mascot?: boolean
}

export function IllustratedHeader({ title, mascot = false }: IllustratedHeaderProps) {
    return (
        <div className="illustrated-header">
            <h1 className="illustrated-header-title">{title}</h1>
            {mascot && (
                <div className="absolute -bottom-10 left-1/2 -translate-x-1/2">
                    <Image
                        src="/images/mascot/honzik-waving.png"
                        alt="Honzík"
                        width={80}
                        height={80}
                        className="drop-shadow-lg"
                    />
                </div>
            )}
        </div>
    )
}
