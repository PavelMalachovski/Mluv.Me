"use client"

import { useState, useEffect } from "react"
import Image from "next/image"
import { X, Download, Smartphone } from "lucide-react"
import { Button } from "@/components/ui/button"

interface BeforeInstallPromptEvent extends Event {
    prompt(): Promise<void>
    userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

interface InstallPromptProps {
    className?: string
    onInstall?: () => void
    onDismiss?: () => void
}

export function InstallPrompt({ className = "", onInstall, onDismiss }: InstallPromptProps) {
    const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null)
    const [isVisible, setIsVisible] = useState(false)
    const [isInstalled, setIsInstalled] = useState(false)
    const [isInstalling, setIsInstalling] = useState(false)

    useEffect(() => {
        // Check if already installed
        if (typeof window !== 'undefined') {
            const isStandalone = window.matchMedia('(display-mode: standalone)').matches
            const isInWebAppiOS = (window.navigator as any).standalone === true

            if (isStandalone || isInWebAppiOS) {
                setIsInstalled(true)
                return
            }
        }

        // Check if previously dismissed
        const dismissed = localStorage.getItem('pwa-install-dismissed')
        const dismissedTime = dismissed ? parseInt(dismissed) : 0
        const daysSinceDismissed = (Date.now() - dismissedTime) / (1000 * 60 * 60 * 24)

        // Don't show if dismissed less than 7 days ago
        if (daysSinceDismissed < 7) {
            return
        }

        // Listen for install prompt
        const handleBeforeInstallPrompt = (e: Event) => {
            e.preventDefault()
            setDeferredPrompt(e as BeforeInstallPromptEvent)
            setIsVisible(true)
        }

        window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)

        // Listen for successful install
        window.addEventListener('appinstalled', () => {
            setIsInstalled(true)
            setIsVisible(false)
            onInstall?.()
        })

        return () => {
            window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
        }
    }, [onInstall])

    const handleInstall = async () => {
        if (!deferredPrompt) return

        setIsInstalling(true)

        try {
            await deferredPrompt.prompt()
            const { outcome } = await deferredPrompt.userChoice

            if (outcome === 'accepted') {
                setIsInstalled(true)
                setIsVisible(false)
                onInstall?.()
            }
        } catch (error) {
            console.error('Install prompt error:', error)
        }

        setDeferredPrompt(null)
        setIsInstalling(false)
    }

    const handleDismiss = () => {
        setIsVisible(false)
        localStorage.setItem('pwa-install-dismissed', Date.now().toString())
        onDismiss?.()
    }

    if (!isVisible || isInstalled) {
        return null
    }

    return (
        <div className={`fixed bottom-20 left-4 right-4 z-50 ${className}`}>
            <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden animate-slide-up">
                <div className="p-4">
                    <div className="flex items-start gap-4">
                        {/* App icon */}
                        <div className="flex-shrink-0">
                            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center shadow-lg">
                                <Image
                                    src="/images/mascot/honzik-waving.png"
                                    alt="Mluv.Me"
                                    width={40}
                                    height={40}
                                    className="object-contain"
                                />
                            </div>
                        </div>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                            <h3 className="font-bold text-gray-900 dark:text-gray-100">
                                Install Mluv.Me
                            </h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                Add to home screen for the best experience!
                            </p>

                            <div className="flex items-center gap-2 mt-3">
                                <Button
                                    size="sm"
                                    onClick={handleInstall}
                                    disabled={isInstalling}
                                    className="gap-2"
                                >
                                    <Download className="h-4 w-4" />
                                    Install
                                </Button>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={handleDismiss}
                                    className="text-gray-500"
                                >
                                    Not now
                                </Button>
                            </div>
                        </div>

                        {/* Dismiss button */}
                        <button
                            onClick={handleDismiss}
                            className="flex-shrink-0 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800"
                        >
                            <X className="h-5 w-5 text-gray-400" />
                        </button>
                    </div>
                </div>

                {/* Benefits */}
                <div className="px-4 pb-4 pt-0">
                    <div className="flex items-center justify-around text-xs text-gray-500 border-t border-gray-100 dark:border-gray-800 pt-3">
                        <span className="flex items-center gap-1">
                            ⚡ Faster
                        </span>
                        <span className="flex items-center gap-1">
                            📴 Works Offline
                        </span>
                        <span className="flex items-center gap-1">
                            🔔 Notifications
                        </span>
                    </div>
                </div>
            </div>

            <style jsx>{`
        @keyframes slide-up {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-slide-up {
          animation: slide-up 0.3s ease-out;
        }
      `}</style>
        </div>
    )
}

// iOS Safari specific install instructions
export function IOSInstallInstructions({ className = "" }: { className?: string }) {
    const [isVisible, setIsVisible] = useState(false)

    useEffect(() => {
        // Detect iOS Safari
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent)
        const isInStandalone = (window.navigator as any).standalone === true
        const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent)

        if (isIOS && isSafari && !isInStandalone) {
            // Check if dismissed
            const dismissed = localStorage.getItem('ios-install-dismissed')
            if (!dismissed) {
                setIsVisible(true)
            }
        }
    }, [])

    const handleDismiss = () => {
        setIsVisible(false)
        localStorage.setItem('ios-install-dismissed', 'true')
    }

    if (!isVisible) return null

    return (
        <div className={`fixed bottom-20 left-4 right-4 z-50 ${className}`}>
            <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 p-4">
                <div className="flex items-start gap-3">
                    <Smartphone className="h-8 w-8 text-primary flex-shrink-0" />

                    <div className="flex-1">
                        <h3 className="font-bold text-gray-900 dark:text-gray-100">
                            Add to Home Screen
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            Tap the{' '}
                            <span className="inline-flex items-center bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">
                                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z" />
                                </svg>
                            </span>
                            {' '}share button, then &quot;Add to Home Screen&quot;
                        </p>
                    </div>

                    <button onClick={handleDismiss} className="p-1">
                        <X className="h-5 w-5 text-gray-400" />
                    </button>
                </div>
            </div>
        </div>
    )
}
