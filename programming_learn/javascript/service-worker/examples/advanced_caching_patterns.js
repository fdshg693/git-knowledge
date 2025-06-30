/**
 * Advanced Service Worker with Multiple Caching Strategies
 * 
 * This example demonstrates sophisticated caching patterns for different
 * types of resources in a real-world web application.
 */

const CACHE_VERSION = 'v2.1.0';
const STATIC_CACHE = `static-${CACHE_VERSION}`;
const DYNAMIC_CACHE = `dynamic-${CACHE_VERSION}`;
const API_CACHE = `api-${CACHE_VERSION}`;
const IMAGE_CACHE = `images-${CACHE_VERSION}`;

// Define cache strategies for different resource types
const CACHE_STRATEGIES = {
    static: 'cacheFirst',
    api: 'networkFirst',
    images: 'staleWhileRevalidate',
    dynamic: 'networkFirst'
};

// Static assets to cache immediately
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/app.js',
    '/styles.css',
    '/manifest.json',
    '/offline.html',
    '/icons/icon-192.png',
    '/icons/icon-512.png'
];

// API endpoints to cache
const API_ENDPOINTS = [
    '/api/user/profile',
    '/api/app/config',
    '/api/content/featured'
];

/**
 * Install Event - Cache Essential Resources
 */
self.addEventListener('install', event => {
    console.log('Service Worker: Installing...');

    event.waitUntil(
        Promise.all([
            // Cache static assets
            caches.open(STATIC_CACHE)
                .then(cache => {
                    console.log('Service Worker: Caching static assets');
                    return cache.addAll(STATIC_ASSETS);
                }),

            // Pre-cache critical API data
            caches.open(API_CACHE)
                .then(cache => {
                    console.log('Service Worker: Pre-caching API data');
                    return Promise.all(
                        API_ENDPOINTS.map(endpoint =>
                            fetch(endpoint)
                                .then(response => {
                                    if (response.ok) {
                                        cache.put(endpoint, response.clone());
                                    }
                                })
                                .catch(err => console.log(`Failed to pre-cache ${endpoint}:`, err))
                        )
                    );
                })
        ]).then(() => {
            console.log('Service Worker: Installation complete');
            return self.skipWaiting();
        })
    );
});

/**
 * Activate Event - Clean Up Old Caches
 */
self.addEventListener('activate', event => {
    console.log('Service Worker: Activating...');

    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    // Delete caches that don't match current version
                    if (!cacheName.includes(CACHE_VERSION)) {
                        console.log('Service Worker: Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('Service Worker: Activation complete');
            return self.clients.claim();
        })
    );
});

/**
 * Fetch Event - Route Requests to Appropriate Strategies
 */
self.addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request));
});

/**
 * Main request handler - determines strategy based on request type
 */
async function handleRequest(request) {
    const url = new URL(request.url);

    try {
        // Route to appropriate strategy based on URL pattern
        if (isStaticAsset(url)) {
            return await cacheFirst(request, STATIC_CACHE);
        } else if (isAPIRequest(url)) {
            return await networkFirst(request, API_CACHE, { timeout: 3000 });
        } else if (isImageRequest(url)) {
            return await staleWhileRevalidate(request, IMAGE_CACHE);
        } else if (isDynamicContent(url)) {
            return await networkFirst(request, DYNAMIC_CACHE, { timeout: 5000 });
        } else {
            // Default to network for unknown requests
            return await fetch(request);
        }
    } catch (error) {
        console.error('Service Worker: Request failed:', error);
        return await handleOfflineFallback(request);
    }
}

/**
 * Cache First Strategy - Serve from cache, fallback to network
 * Best for: Static assets that rarely change
 */
async function cacheFirst(request, cacheName) {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
        console.log('Cache hit:', request.url);
        return cachedResponse;
    }

    console.log('Cache miss, fetching:', request.url);
    const networkResponse = await fetch(request);

    if (networkResponse.ok) {
        cache.put(request, networkResponse.clone());
    }

    return networkResponse;
}

/**
 * Network First Strategy - Try network, fallback to cache
 * Best for: Dynamic content that should be fresh when possible
 */
async function networkFirst(request, cacheName, options = {}) {
    const { timeout = 5000 } = options;
    const cache = await caches.open(cacheName);

    try {
        // Create timeout promise
        const timeoutPromise = new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Network timeout')), timeout)
        );

        // Race between fetch and timeout
        const networkResponse = await Promise.race([
            fetch(request),
            timeoutPromise
        ]);

        if (networkResponse.ok) {
            console.log('Network success:', request.url);
            cache.put(request, networkResponse.clone());
            return networkResponse;
        }
    } catch (error) {
        console.log('Network failed, trying cache:', request.url);
    }

    // Fallback to cache
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
        console.log('Cache fallback:', request.url);
        return cachedResponse;
    }

    throw new Error('No cache fallback available');
}

/**
 * Stale While Revalidate Strategy - Serve from cache, update in background
 * Best for: Resources where freshness isn't critical
 */
async function staleWhileRevalidate(request, cacheName) {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);

    // Start background fetch to update cache
    const fetchPromise = fetch(request).then(response => {
        if (response.ok) {
            cache.put(request, response.clone());
        }
        return response;
    }).catch(error => {
        console.log('Background fetch failed:', error);
    });

    // Return cached version immediately if available
    if (cachedResponse) {
        console.log('Stale cache hit:', request.url);
        return cachedResponse;
    }

    // If no cache, wait for network
    console.log('No cache, waiting for network:', request.url);
    return fetchPromise;
}

/**
 * Handle offline fallbacks for different request types
 */
async function handleOfflineFallback(request) {
    if (request.destination === 'document') {
        // Return offline page for navigation requests
        return caches.match('/offline.html');
    }

    if (request.destination === 'image') {
        // Return placeholder image
        return new Response(
            '<svg>...</svg>', // Simple SVG placeholder
            { headers: { 'Content-Type': 'image/svg+xml' } }
        );
    }

    // Generic offline response
    return new Response('Offline', {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'text/plain' }
    });
}

/**
 * URL pattern matching functions
 */
function isStaticAsset(url) {
    const staticExtensions = ['.css', '.js', '.html', '.json', '.ico'];
    return staticExtensions.some(ext => url.pathname.endsWith(ext)) ||
        url.pathname === '/' ||
        url.pathname.startsWith('/icons/');
}

function isAPIRequest(url) {
    return url.pathname.startsWith('/api/');
}

function isImageRequest(url) {
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'];
    return imageExtensions.some(ext => url.pathname.endsWith(ext));
}

function isDynamicContent(url) {
    return url.pathname.startsWith('/user/') ||
        url.pathname.startsWith('/dashboard/') ||
        url.pathname.startsWith('/content/');
}

/**
 * Background Sync for failed requests (if supported)
 */
if ('sync' in self.registration) {
    self.addEventListener('sync', event => {
        if (event.tag === 'background-sync') {
            event.waitUntil(handleBackgroundSync());
        }
    });
}

async function handleBackgroundSync() {
    console.log('Service Worker: Background sync triggered');

    // Retry failed API requests
    const cache = await caches.open('failed-requests');
    const requests = await cache.keys();

    for (const request of requests) {
        try {
            const response = await fetch(request);
            if (response.ok) {
                await cache.delete(request);
                console.log('Background sync: Request succeeded', request.url);
            }
        } catch (error) {
            console.log('Background sync: Request still failing', request.url);
        }
    }
}

/**
 * Cache Management - Prevent cache from growing too large
 */
async function limitCacheSize(cacheName, maxItems) {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();

    if (keys.length > maxItems) {
        // Remove oldest entries
        const keysToDelete = keys.slice(0, keys.length - maxItems);
        await Promise.all(keysToDelete.map(key => cache.delete(key)));
        console.log(`Cache ${cacheName}: Cleaned ${keysToDelete.length} old entries`);
    }
}

// Periodic cache cleanup
setInterval(() => {
    limitCacheSize(DYNAMIC_CACHE, 50);
    limitCacheSize(IMAGE_CACHE, 100);
    limitCacheSize(API_CACHE, 30);
}, 60000); // Run every minute

/**
 * Message handler for communication with main thread
 */
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }

    if (event.data && event.data.type === 'GET_CACHE_STATS') {
        getCacheStats().then(stats => {
            event.ports[0].postMessage(stats);
        });
    }
});

/**
 * Get cache statistics for debugging/monitoring
 */
async function getCacheStats() {
    const cacheNames = await caches.keys();
    const stats = {};

    for (const cacheName of cacheNames) {
        const cache = await caches.open(cacheName);
        const keys = await cache.keys();
        stats[cacheName] = keys.length;
    }

    return stats;
}
