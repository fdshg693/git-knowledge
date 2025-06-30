/**
 * Network Request Handling and Offline Management
 * 
 * This example demonstrates advanced network request handling,
 * including request interception, modification, and offline queue management.
 */

// Configuration
const CONFIG = {
    apiBaseUrl: 'https://api.example.com',
    offlineQueueName: 'offline-queue',
    maxRetries: 3,
    retryDelay: 1000,
    cacheTimeout: 5 * 60 * 1000, // 5 minutes
};

// Request queue for offline operations
let offlineQueue = [];
let isOnline = true;

/**
 * Enhanced fetch event handler with request modification and queuing
 */
self.addEventListener('fetch', event => {
    const request = event.request;

    // Only handle GET requests and API calls for this example
    if (request.method === 'GET' || isAPIRequest(request.url)) {
        event.respondWith(handleNetworkRequest(request));
    }
});

/**
 * Main network request handler with comprehensive error handling
 */
async function handleNetworkRequest(request) {
    try {
        // Check if request should be modified
        const modifiedRequest = await modifyRequest(request);

        // Attempt network request with retry logic
        const response = await fetchWithRetry(modifiedRequest);

        // Process successful response
        return await processResponse(request, response);

    } catch (error) {
        console.log('Network request failed:', error);

        // Handle failed request based on method and type
        return await handleFailedRequest(request, error);
    }
}

/**
 * Modify requests before sending (add headers, authentication, etc.)
 */
async function modifyRequest(originalRequest) {
    const url = new URL(originalRequest.url);

    // Don't modify non-API requests
    if (!isAPIRequest(originalRequest.url)) {
        return originalRequest;
    }

    // Create new request with modifications
    const headers = new Headers(originalRequest.headers);

    // Add authentication token if available
    const authToken = await getAuthToken();
    if (authToken) {
        headers.set('Authorization', `Bearer ${authToken}`);
    }

    // Add custom headers
    headers.set('X-Requested-With', 'ServiceWorker');
    headers.set('X-Client-Version', '1.0.0');

    // Add cache control for API requests
    if (originalRequest.method === 'GET') {
        headers.set('Cache-Control', 'max-age=300'); // 5 minutes
    }

    return new Request(originalRequest.url, {
        method: originalRequest.method,
        headers: headers,
        body: originalRequest.body,
        mode: originalRequest.mode,
        credentials: originalRequest.credentials,
        cache: originalRequest.cache,
        redirect: originalRequest.redirect,
        referrer: originalRequest.referrer
    });
}

/**
 * Fetch with automatic retry logic
 */
async function fetchWithRetry(request, retryCount = 0) {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout

        const response = await fetch(request, {
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        // Check if response indicates we should retry
        if (shouldRetry(response, retryCount)) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return response;

    } catch (error) {
        if (retryCount < CONFIG.maxRetries) {
            console.log(`Retry ${retryCount + 1}/${CONFIG.maxRetries} for:`, request.url);

            // Exponential backoff delay
            const delay = CONFIG.retryDelay * Math.pow(2, retryCount);
            await new Promise(resolve => setTimeout(resolve, delay));

            return fetchWithRetry(request, retryCount + 1);
        }

        throw error;
    }
}

/**
 * Process successful responses (caching, transformation, etc.)
 */
async function processResponse(originalRequest, response) {
    // Clone response for caching (can only read body once)
    const responseClone = response.clone();

    // Cache successful GET responses
    if (originalRequest.method === 'GET' && response.ok) {
        await cacheResponse(originalRequest, responseClone);
    }

    // Transform API responses if needed
    if (isAPIRequest(originalRequest.url) && response.ok) {
        return await transformAPIResponse(response);
    }

    return response;
}

/**
 * Handle failed network requests
 */
async function handleFailedRequest(request, error) {
    console.log(`Request failed: ${request.url}`, error);

    // For GET requests, try to serve from cache
    if (request.method === 'GET') {
        const cachedResponse = await getCachedResponse(request);
        if (cachedResponse) {
            console.log('Serving stale content from cache:', request.url);
            return addStaleHeaders(cachedResponse);
        }
    }

    // For POST/PUT/DELETE requests, queue for later retry
    if (request.method !== 'GET') {
        await queueOfflineRequest(request);
        return createOfflineResponse('Request queued for retry when online');
    }

    // Return appropriate offline response
    return createOfflineResponse('Content unavailable offline');
}

/**
 * Queue failed requests for retry when online
 */
async function queueOfflineRequest(request) {
    try {
        const requestData = {
            url: request.url,
            method: request.method,
            headers: Object.fromEntries(request.headers.entries()),
            body: request.body ? await request.text() : null,
            timestamp: Date.now(),
            retryCount: 0
        };

        // Store in IndexedDB for persistence
        await saveToOfflineQueue(requestData);

        console.log('Request queued for offline retry:', request.url);

        // Notify main thread about queued request
        await notifyClients({
            type: 'REQUEST_QUEUED',
            url: request.url,
            method: request.method
        });

    } catch (error) {
        console.error('Failed to queue offline request:', error);
    }
}

/**
 * Process offline queue when connection is restored
 */
async function processOfflineQueue() {
    const queuedRequests = await getOfflineQueue();

    if (queuedRequests.length === 0) {
        return;
    }

    console.log(`Processing ${queuedRequests.length} queued requests`);

    for (const requestData of queuedRequests) {
        try {
            // Recreate request from stored data
            const request = new Request(requestData.url, {
                method: requestData.method,
                headers: requestData.headers,
                body: requestData.body
            });

            // Attempt to send the request
            const response = await fetch(request);

            if (response.ok) {
                // Remove from queue on success
                await removeFromOfflineQueue(requestData.id);

                console.log('Offline request processed successfully:', requestData.url);

                // Notify main thread
                await notifyClients({
                    type: 'OFFLINE_REQUEST_SUCCESS',
                    url: requestData.url,
                    method: requestData.method
                });

            } else {
                // Update retry count
                requestData.retryCount++;

                if (requestData.retryCount >= CONFIG.maxRetries) {
                    await removeFromOfflineQueue(requestData.id);
                    console.log('Max retries reached, removing from queue:', requestData.url);
                } else {
                    await updateOfflineQueueItem(requestData);
                }
            }

        } catch (error) {
            console.log('Offline request still failing:', requestData.url, error);

            // Update retry count and timestamp
            requestData.retryCount++;
            requestData.timestamp = Date.now();

            if (requestData.retryCount >= CONFIG.maxRetries) {
                await removeFromOfflineQueue(requestData.id);
            } else {
                await updateOfflineQueueItem(requestData);
            }
        }
    }
}

/**
 * Cache management functions
 */
async function cacheResponse(request, response) {
    try {
        const cache = await caches.open('network-responses');
        await cache.put(request, response);

        // Add timestamp for cache expiration
        const metadata = {
            url: request.url,
            timestamp: Date.now(),
            expiresAt: Date.now() + CONFIG.cacheTimeout
        };

        await saveMetadata(metadata);

    } catch (error) {
        console.error('Failed to cache response:', error);
    }
}

async function getCachedResponse(request) {
    try {
        const cache = await caches.open('network-responses');
        const response = await cache.match(request);

        if (!response) {
            return null;
        }

        // Check if cache is expired
        const metadata = await getMetadata(request.url);
        if (metadata && Date.now() > metadata.expiresAt) {
            console.log('Cache expired for:', request.url);
            await cache.delete(request);
            return null;
        }

        return response;

    } catch (error) {
        console.error('Failed to get cached response:', error);
        return null;
    }
}

/**
 * Transform API responses (add custom headers, modify data, etc.)
 */
async function transformAPIResponse(response) {
    try {
        const data = await response.json();

        // Add metadata
        const transformedData = {
            ...data,
            _metadata: {
                cachedAt: Date.now(),
                version: '1.0.0',
                source: 'service-worker'
            }
        };

        return new Response(JSON.stringify(transformedData), {
            status: response.status,
            statusText: response.statusText,
            headers: {
                ...Object.fromEntries(response.headers.entries()),
                'Content-Type': 'application/json',
                'X-Transformed': 'true'
            }
        });

    } catch (error) {
        console.error('Failed to transform API response:', error);
        return response;
    }
}

/**
 * Utility functions
 */
function isAPIRequest(url) {
    return url.includes('/api/') || url.startsWith(CONFIG.apiBaseUrl);
}

function shouldRetry(response, retryCount) {
    // Retry on server errors (5xx) and specific client errors
    const retryStatuses = [408, 429, 500, 502, 503, 504];
    return retryStatuses.includes(response.status) && retryCount < CONFIG.maxRetries;
}

function createOfflineResponse(message) {
    return new Response(JSON.stringify({
        error: 'offline',
        message: message,
        timestamp: Date.now()
    }), {
        status: 503,
        statusText: 'Service Unavailable',
        headers: {
            'Content-Type': 'application/json',
            'X-Offline': 'true'
        }
    });
}

function addStaleHeaders(response) {
    const headers = new Headers(response.headers);
    headers.set('X-Served-From-Cache', 'true');
    headers.set('X-Cache-Date', new Date().toISOString());

    return new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: headers
    });
}

/**
 * Online/offline detection and queue processing
 */
self.addEventListener('online', () => {
    console.log('Connection restored');
    isOnline = true;
    processOfflineQueue();
});

self.addEventListener('offline', () => {
    console.log('Connection lost');
    isOnline = false;
});

/**
 * Communication with main thread
 */
async function notifyClients(message) {
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
        client.postMessage(message);
    });
}

/**
 * Mock IndexedDB operations (implement according to your needs)
 */
async function saveToOfflineQueue(requestData) {
    // Implementation depends on your IndexedDB setup
    // This is a simplified version
    const id = Date.now() + Math.random();
    requestData.id = id;
    offlineQueue.push(requestData);
}

async function getOfflineQueue() {
    // Return copy of offline queue
    return [...offlineQueue];
}

async function removeFromOfflineQueue(id) {
    offlineQueue = offlineQueue.filter(item => item.id !== id);
}

async function updateOfflineQueueItem(requestData) {
    const index = offlineQueue.findIndex(item => item.id === requestData.id);
    if (index !== -1) {
        offlineQueue[index] = requestData;
    }
}

async function getAuthToken() {
    // Mock auth token retrieval
    // In real implementation, get from IndexedDB or secure storage
    return null;
}

async function saveMetadata(metadata) {
    // Save cache metadata to IndexedDB
    console.log('Saving metadata:', metadata);
}

async function getMetadata(url) {
    // Get cache metadata from IndexedDB
    return null;
}

/**
 * Background sync for processing offline queue
 */
if ('sync' in self.registration) {
    self.addEventListener('sync', event => {
        if (event.tag === 'process-offline-queue') {
            event.waitUntil(processOfflineQueue());
        }
    });
}
