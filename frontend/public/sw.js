/**
 * Mluv.Me Service Worker
 * Handles push notifications and offline caching
 */

// Cache name for offline resources
const CACHE_NAME = 'mluv-me-v1';

// Resources to cache for offline use
const OFFLINE_URLS = [
    '/',
    '/dashboard',
    '/dashboard/practice',
    '/dashboard/review',
    '/dashboard/profile',
    '/images/mascot/honzik-waving.png',
    '/images/mascot/honzik-happy.png',
    '/images/mascot/honzik-thinking.png',
];

// Install event - cache offline resources
self.addEventListener('install', (event) => {
    console.log('[SW] Installing service worker...');
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[SW] Caching offline resources');
            return cache.addAll(OFFLINE_URLS);
        })
    );
    // Activate immediately
    self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating service worker...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => name !== CACHE_NAME)
                    .map((name) => {
                        console.log('[SW] Deleting old cache:', name);
                        return caches.delete(name);
                    })
            );
        })
    );
    // Take control immediately
    self.clients.claim();
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
    // Only handle GET requests
    if (event.request.method !== 'GET') return;

    // Skip API requests
    if (event.request.url.includes('/api/')) return;

    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // Clone response for caching
                const responseClone = response.clone();
                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(event.request, responseClone);
                });
                return response;
            })
            .catch(() => {
                // Return from cache if offline
                return caches.match(event.request);
            })
    );
});

// Push notification event
self.addEventListener('push', (event) => {
    console.log('[SW] Push notification received');

    if (!event.data) {
        console.log('[SW] No data in push event');
        return;
    }

    try {
        const data = event.data.json();

        const options = {
            body: data.body || 'Čas na učení! 📚',
            icon: data.icon || '/images/mascot/honzik-waving.png',
            badge: '/images/icons/badge-72x72.png',
            vibrate: [100, 50, 100],
            tag: data.tag || 'mluv-me-notification',
            renotify: true,
            requireInteraction: data.requireInteraction || false,
            data: {
                url: data.url || '/dashboard',
                dateOfArrival: Date.now(),
                type: data.type || 'general',
            },
            actions: data.actions || [
                { action: 'open', title: 'Otevřít' },
                { action: 'dismiss', title: 'Zavřít' },
            ],
        };

        event.waitUntil(
            self.registration.showNotification(data.title || 'Mluv.Me', options)
        );
    } catch (error) {
        console.error('[SW] Error parsing push data:', error);
    }
});

// Notification click event
self.addEventListener('notificationclick', (event) => {
    console.log('[SW] Notification clicked:', event.action);

    event.notification.close();

    if (event.action === 'dismiss') {
        return;
    }

    const urlToOpen = event.notification.data?.url || '/dashboard';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
            // Check if app is already open
            for (const client of clientList) {
                if (client.url.includes(self.location.origin) && 'focus' in client) {
                    client.navigate(urlToOpen);
                    return client.focus();
                }
            }
            // Open new window
            return clients.openWindow(urlToOpen);
        })
    );
});

// Background sync (for offline message sending)
self.addEventListener('sync', (event) => {
    console.log('[SW] Background sync:', event.tag);

    if (event.tag === 'sync-messages') {
        event.waitUntil(syncMessages());
    }
});

async function syncMessages() {
    // Get pending messages from IndexedDB and send them
    console.log('[SW] Syncing pending messages...');
    // Implementation would depend on IndexedDB setup
}

console.log('[SW] Service worker loaded');
