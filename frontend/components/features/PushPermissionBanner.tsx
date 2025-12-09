"use client"

import { useState, useEffect } from "react"
import { Bell, BellOff, X, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
    isPushSupported,
    getNotificationPermission,
    requestNotificationPermission,
    subscribeToPush,
    unsubscribeFromPush,
    getSubscriptionStatus,
    registerServiceWorker,
} from "@/lib/push-notifications"

interface PushPermissionBannerProps {
    className?: string
    dismissible?: boolean
    onStatusChange?: (isSubscribed: boolean) => void
}

export function PushPermissionBanner({
    className = "",
    dismissible = true,
    onStatusChange,
}: PushPermissionBannerProps) {
    const [isSupported, setIsSupported] = useState(false)
    const [permission, setPermission] = useState<NotificationPermission | 'unsupported'>('default')
    const [isSubscribed, setIsSubscribed] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const [isDismissed, setIsDismissed] = useState(false)
    const [showSuccess, setShowSuccess] = useState(false)

    // Check support and status on mount
    useEffect(() => {
        const checkStatus = async () => {
            const supported = isPushSupported()
            setIsSupported(supported)

            if (!supported) {
                setPermission('unsupported')
                return
            }

            // Register service worker
            await registerServiceWorker()

            // Check permission
            const perm = getNotificationPermission()
            setPermission(perm)

            // Check subscription status
            const { isSubscribed: subscribed } = await getSubscriptionStatus()
            setIsSubscribed(subscribed)
            onStatusChange?.(subscribed)
        }

        // Check if dismissed in localStorage
        const dismissed = localStorage.getItem('push-banner-dismissed')
        if (dismissed) {
            setIsDismissed(true)
        }

        checkStatus()
    }, [onStatusChange])

    const handleSubscribe = async () => {
        setIsLoading(true)

        try {
            // Request permission if needed
            if (permission !== 'granted') {
                const newPermission = await requestNotificationPermission()
                setPermission(newPermission)

                if (newPermission !== 'granted') {
                    setIsLoading(false)
                    return
                }
            }

            // Subscribe
            const subscription = await subscribeToPush()

            if (subscription) {
                setIsSubscribed(true)
                setShowSuccess(true)
                onStatusChange?.(true)

                // Hide success after 3 seconds
                setTimeout(() => setShowSuccess(false), 3000)
            }
        } catch (error) {
            console.error('Failed to subscribe:', error)
        }

        setIsLoading(false)
    }

    const handleUnsubscribe = async () => {
        setIsLoading(true)

        try {
            const success = await unsubscribeFromPush()

            if (success) {
                setIsSubscribed(false)
                onStatusChange?.(false)
            }
        } catch (error) {
            console.error('Failed to unsubscribe:', error)
        }

        setIsLoading(false)
    }

    const handleDismiss = () => {
        setIsDismissed(true)
        localStorage.setItem('push-banner-dismissed', 'true')
    }

    // Don't show if not supported, already subscribed, denied, or dismissed
    if (!isSupported || permission === 'denied' || (isDismissed && !isSubscribed)) {
        return null
    }

    // Show success message briefly
    if (showSuccess) {
        return (
            <div className={`bg-green-100 dark:bg-green-900/30 rounded-lg p-4 ${className}`}>
                <div className="flex items-center gap-3">
                    <Bell className="h-5 w-5 text-green-600" />
                    <span className="text-sm text-green-800 dark:text-green-200">
                        🎉 Notifications enabled! You&apos;ll receive reminders to practice.
                    </span>
                </div>
            </div>
        )
    }

    // Show unsubscribe option if subscribed
    if (isSubscribed) {
        return (
            <div className={`bg-gray-100 dark:bg-gray-800 rounded-lg p-4 ${className}`}>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Bell className="h-5 w-5 text-primary" />
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                            Notifications are enabled
                        </span>
                    </div>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={handleUnsubscribe}
                        disabled={isLoading}
                        className="text-gray-500"
                    >
                        {isLoading ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                            <>
                                <BellOff className="h-4 w-4 mr-1" />
                                Turn off
                            </>
                        )}
                    </Button>
                </div>
            </div>
        )
    }

    // Show subscribe banner
    return (
        <div className={`bg-gradient-to-r from-primary/10 to-purple-500/10 rounded-lg p-4 ${className}`}>
            <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                    <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                        <Bell className="h-5 w-5 text-primary" />
                    </div>
                </div>

                <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-gray-800 dark:text-gray-200">
                        Get Reminders to Practice
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        Enable notifications for daily streak reminders and new achievements!
                    </p>

                    <div className="flex items-center gap-2 mt-3">
                        <Button
                            size="sm"
                            onClick={handleSubscribe}
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                            ) : (
                                <Bell className="h-4 w-4 mr-2" />
                            )}
                            Enable Notifications
                        </Button>

                        {dismissible && (
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={handleDismiss}
                                className="text-gray-500"
                            >
                                Maybe Later
                            </Button>
                        )}
                    </div>
                </div>

                {dismissible && (
                    <button
                        onClick={handleDismiss}
                        className="flex-shrink-0 p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
                    >
                        <X className="h-4 w-4 text-gray-400" />
                    </button>
                )}
            </div>
        </div>
    )
}

// Settings toggle component for settings page
export function NotificationToggle({ className = "" }: { className?: string }) {
    const [isSubscribed, setIsSubscribed] = useState(false)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        const checkStatus = async () => {
            const { isSubscribed: subscribed } = await getSubscriptionStatus()
            setIsSubscribed(subscribed)
            setIsLoading(false)
        }
        checkStatus()
    }, [])

    const handleToggle = async () => {
        setIsLoading(true)

        if (isSubscribed) {
            const success = await unsubscribeFromPush()
            if (success) setIsSubscribed(false)
        } else {
            const permission = await requestNotificationPermission()
            if (permission === 'granted') {
                const subscription = await subscribeToPush()
                if (subscription) setIsSubscribed(true)
            }
        }

        setIsLoading(false)
    }

    return (
        <div className={`flex items-center justify-between p-4 rounded-lg bg-gray-50 dark:bg-gray-800/50 ${className}`}>
            <div className="flex items-center gap-3">
                <Bell className="h-5 w-5 text-gray-500" />
                <div>
                    <p className="font-medium text-gray-800 dark:text-gray-200">
                        Push Notifications
                    </p>
                    <p className="text-sm text-gray-500">
                        Daily reminders and achievements
                    </p>
                </div>
            </div>

            <button
                onClick={handleToggle}
                disabled={isLoading}
                className={`relative w-12 h-7 rounded-full transition-colors ${isSubscribed
                        ? 'bg-primary'
                        : 'bg-gray-300 dark:bg-gray-600'
                    }`}
            >
                {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin absolute top-1.5 left-4" />
                ) : (
                    <div
                        className={`absolute w-5 h-5 rounded-full bg-white top-1 transition-transform ${isSubscribed ? 'translate-x-6' : 'translate-x-1'
                            }`}
                    />
                )}
            </button>
        </div>
    )
}
