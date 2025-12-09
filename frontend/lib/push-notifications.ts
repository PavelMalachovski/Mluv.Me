/**
 * Push notification utilities for PWA
 */

// Convert VAPID key to Uint8Array for subscription
export function urlBase64ToUint8Array(base64String: string): Uint8Array {
    const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding)
        .replace(/-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Check if push notifications are supported
export function isPushSupported(): boolean {
    return (
        typeof window !== 'undefined' &&
        'serviceWorker' in navigator &&
        'PushManager' in window &&
        'Notification' in window
    );
}

// Get current notification permission
export function getNotificationPermission(): NotificationPermission | 'unsupported' {
    if (!isPushSupported()) {
        return 'unsupported';
    }
    return Notification.permission;
}

// Request notification permission
export async function requestNotificationPermission(): Promise<NotificationPermission | 'unsupported'> {
    if (!isPushSupported()) {
        return 'unsupported';
    }

    try {
        const permission = await Notification.requestPermission();
        return permission;
    } catch (error) {
        console.error('Error requesting notification permission:', error);
        return 'denied';
    }
}

// Register service worker
export async function registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
    if (!('serviceWorker' in navigator)) {
        console.warn('Service workers not supported');
        return null;
    }

    try {
        const registration = await navigator.serviceWorker.register('/sw.js', {
            scope: '/',
        });
        console.log('Service worker registered:', registration.scope);
        return registration;
    } catch (error) {
        console.error('Service worker registration failed:', error);
        return null;
    }
}

// Subscribe to push notifications
export async function subscribeToPush(): Promise<PushSubscription | null> {
    if (!isPushSupported()) {
        console.warn('Push notifications not supported');
        return null;
    }

    try {
        const registration = await navigator.serviceWorker.ready;

        // Check for existing subscription
        let subscription = await registration.pushManager.getSubscription();

        if (subscription) {
            console.log('Already subscribed to push');
            return subscription;
        }

        // Get VAPID public key
        const vapidKey = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY;

        if (!vapidKey) {
            console.warn('VAPID public key not configured');
            return null;
        }

        // Subscribe
        subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: vapidKey,
        });

        console.log('Push subscription created:', subscription.endpoint);

        // Send subscription to backend
        await saveSubscriptionToServer(subscription);

        return subscription;
    } catch (error) {
        console.error('Failed to subscribe to push:', error);
        return null;
    }
}

// Unsubscribe from push notifications
export async function unsubscribeFromPush(): Promise<boolean> {
    if (!isPushSupported()) {
        return false;
    }

    try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();

        if (!subscription) {
            console.log('No push subscription to unsubscribe');
            return true;
        }

        // Unsubscribe locally
        const success = await subscription.unsubscribe();

        if (success) {
            // Remove from server
            await removeSubscriptionFromServer(subscription);
            console.log('Unsubscribed from push');
        }

        return success;
    } catch (error) {
        console.error('Failed to unsubscribe from push:', error);
        return false;
    }
}

// Check current subscription status
export async function getSubscriptionStatus(): Promise<{
    isSubscribed: boolean;
    subscription: PushSubscription | null;
}> {
    if (!isPushSupported()) {
        return { isSubscribed: false, subscription: null };
    }

    try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        return {
            isSubscribed: !!subscription,
            subscription,
        };
    } catch (error) {
        console.error('Failed to get subscription status:', error);
        return { isSubscribed: false, subscription: null };
    }
}

// Save subscription to server
async function saveSubscriptionToServer(subscription: PushSubscription): Promise<void> {
    try {
        const response = await fetch('/api/v1/notifications/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                subscription: subscription.toJSON(),
            }),
        });

        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}`);
        }

        console.log('Subscription saved to server');
    } catch (error) {
        console.error('Failed to save subscription to server:', error);
        throw error;
    }
}

// Remove subscription from server
async function removeSubscriptionFromServer(subscription: PushSubscription): Promise<void> {
    try {
        const response = await fetch('/api/v1/notifications/unsubscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                endpoint: subscription.endpoint,
            }),
        });

        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}`);
        }

        console.log('Subscription removed from server');
    } catch (error) {
        console.error('Failed to remove subscription from server:', error);
        // Don't throw - local unsubscribe succeeded
    }
}

// Show local notification (for testing without backend)
export async function showLocalNotification(
    title: string,
    options?: NotificationOptions
): Promise<void> {
    if (!isPushSupported()) {
        console.warn('Notifications not supported');
        return;
    }

    const permission = await requestNotificationPermission();

    if (permission !== 'granted') {
        console.warn('Notification permission not granted');
        return;
    }

    const registration = await navigator.serviceWorker.ready;

    await registration.showNotification(title, {
        icon: '/images/mascot/honzik-waving.png',
        badge: '/images/icons/badge-72x72.png',
        ...options,
    });
}
