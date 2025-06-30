/**
 * Advanced Async/Await Examples for Web Development
 * Demonstrates real-world patterns for API calls, data processing, and error handling
 */

// =============================================================================
// API Client with Advanced Error Handling and Retry Logic
// =============================================================================

class AdvancedApiClient {
    constructor(baseUrl, options = {}) {
        this.baseUrl = baseUrl;
        this.timeout = options.timeout || 10000;
        this.retryAttempts = options.retryAttempts || 3;
        this.retryDelay = options.retryDelay || 1000;
        this.headers = options.headers || {};
    }

    /**
     * Enhanced fetch with timeout, retry logic, and comprehensive error handling
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        let lastError;

        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                console.log(`Attempt ${attempt}/${this.retryAttempts} for ${url}`);

                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.timeout);

                const response = await fetch(url, {
                    ...options,
                    headers: {
                        'Content-Type': 'application/json',
                        ...this.headers,
                        ...options.headers,
                    },
                    signal: controller.signal,
                });

                clearTimeout(timeoutId);

                // Handle different HTTP status codes
                if (!response.ok) {
                    const errorData = await this.safeJsonParse(response);
                    throw new ApiError(
                        `HTTP ${response.status}: ${response.statusText}`,
                        response.status,
                        errorData
                    );
                }

                return await response.json();

            } catch (error) {
                lastError = error;

                // Don't retry on certain errors
                if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
                    throw error; // Client errors shouldn't be retried
                }

                if (error.name === 'AbortError') {
                    throw new ApiError('Request timeout', 408);
                }

                // Wait before retrying (exponential backoff)
                if (attempt < this.retryAttempts) {
                    const delay = this.retryDelay * Math.pow(2, attempt - 1);
                    console.log(`Retrying in ${delay}ms...`);
                    await this.sleep(delay);
                }
            }
        }

        throw new ApiError(`Request failed after ${this.retryAttempts} attempts`, 0, lastError);
    }

    async safeJsonParse(response) {
        try {
            return await response.json();
        } catch {
            return { message: 'Invalid JSON response' };
        }
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // HTTP Methods
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET' });
    }

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

// Custom Error Class
class ApiError extends Error {
    constructor(message, status, data = null) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.data = data;
    }
}

// =============================================================================
// Batch Processing with Rate Limiting
// =============================================================================

class BatchProcessor {
    constructor(options = {}) {
        this.concurrencyLimit = options.concurrencyLimit || 5;
        this.batchSize = options.batchSize || 10;
        this.rateLimitDelay = options.rateLimitDelay || 100;
    }

    /**
     * Process items in batches with concurrency control
     */
    async processBatch(items, processingFunction) {
        const results = [];

        // Split items into batches
        for (let i = 0; i < items.length; i += this.batchSize) {
            const batch = items.slice(i, i + this.batchSize);
            console.log(`Processing batch ${Math.floor(i / this.batchSize) + 1}/${Math.ceil(items.length / this.batchSize)}`);

            // Process batch with concurrency limit
            const batchResults = await this.processWithConcurrencyLimit(
                batch,
                processingFunction
            );

            results.push(...batchResults);

            // Rate limiting between batches
            if (i + this.batchSize < items.length) {
                await this.sleep(this.rateLimitDelay);
            }
        }

        return results;
    }

    /**
     * Process items with concurrency limit using semaphore pattern
     */
    async processWithConcurrencyLimit(items, processingFunction) {
        const semaphore = new Semaphore(this.concurrencyLimit);

        const promises = items.map(async (item, index) => {
            await semaphore.acquire();
            try {
                return await processingFunction(item, index);
            } finally {
                semaphore.release();
            }
        });

        return Promise.all(promises);
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Simple Semaphore implementation
class Semaphore {
    constructor(permits) {
        this.permits = permits;
        this.waiting = [];
    }

    async acquire() {
        if (this.permits > 0) {
            this.permits--;
            return;
        }

        return new Promise(resolve => {
            this.waiting.push(resolve);
        });
    }

    release() {
        if (this.waiting.length > 0) {
            const resolve = this.waiting.shift();
            resolve();
        } else {
            this.permits++;
        }
    }
}

// =============================================================================
// Real-World Usage Examples
// =============================================================================

/**
 * Example: User Data Management System
 */
class UserDataManager {
    constructor(apiClient) {
        this.apiClient = apiClient;
        this.batchProcessor = new BatchProcessor({
            concurrencyLimit: 3,
            batchSize: 5,
            rateLimitDelay: 500
        });
    }

    /**
     * Fetch user with all related data
     */
    async getUserProfile(userId) {
        try {
            // Fetch user basic info first
            const user = await this.apiClient.get(`/users/${userId}`);

            // Fetch related data in parallel
            const [posts, friends, notifications, settings] = await Promise.all([
                this.apiClient.get(`/users/${userId}/posts`, { limit: 10 }),
                this.apiClient.get(`/users/${userId}/friends`),
                this.apiClient.get(`/users/${userId}/notifications`, { unread: true }),
                this.apiClient.get(`/users/${userId}/settings`)
            ]);

            return {
                user,
                posts: posts.data || [],
                friends: friends.data || [],
                notifications: notifications.data || [],
                settings: settings.data || {}
            };

        } catch (error) {
            console.error('Error fetching user profile:', error);

            if (error instanceof ApiError && error.status === 404) {
                throw new Error('User not found');
            }

            throw new Error('Failed to load user profile');
        }
    }

    /**
     * Bulk update users with progress tracking
     */
    async bulkUpdateUsers(userUpdates) {
        const updateUser = async (update, index) => {
            try {
                const result = await this.apiClient.put(`/users/${update.id}`, update.data);
                console.log(`✓ Updated user ${update.id} (${index + 1}/${userUpdates.length})`);
                return { success: true, userId: update.id, data: result };
            } catch (error) {
                console.error(`✗ Failed to update user ${update.id}:`, error.message);
                return { success: false, userId: update.id, error: error.message };
            }
        };

        console.log(`Starting bulk update of ${userUpdates.length} users...`);
        const results = await this.batchProcessor.processBatch(userUpdates, updateUser);

        const successful = results.filter(r => r.success).length;
        const failed = results.filter(r => !r.success).length;

        console.log(`Bulk update completed: ${successful} successful, ${failed} failed`);
        return results;
    }

    /**
     * Search users with pagination and caching
     */
    async searchUsers(query, options = {}) {
        const {
            page = 1,
            limit = 20,
            useCache = true,
            cacheTimeout = 5 * 60 * 1000 // 5 minutes
        } = options;

        const cacheKey = `search_${query}_${page}_${limit}`;

        // Check cache first
        if (useCache) {
            const cached = this.getFromCache(cacheKey);
            if (cached) {
                console.log('Returning cached search results');
                return cached;
            }
        }

        try {
            const response = await this.apiClient.get('/users/search', {
                q: query,
                page,
                limit
            });

            const result = {
                users: response.data || [],
                pagination: {
                    page,
                    limit,
                    total: response.total || 0,
                    totalPages: Math.ceil((response.total || 0) / limit)
                },
                timestamp: Date.now()
            };

            // Cache the result
            if (useCache) {
                this.setCache(cacheKey, result, cacheTimeout);
            }

            return result;

        } catch (error) {
            console.error('Search failed:', error);
            throw new Error('Search operation failed');
        }
    }

    // Simple in-memory cache implementation
    getFromCache(key) {
        const cached = this.cache?.get(key);
        if (cached && cached.expires > Date.now()) {
            return cached.data;
        }
        return null;
    }

    setCache(key, data, timeout) {
        if (!this.cache) {
            this.cache = new Map();
        }
        this.cache.set(key, {
            data,
            expires: Date.now() + timeout
        });
    }
}

// =============================================================================
// File Processing Examples
// =============================================================================

/**
 * Advanced file processing with progress tracking
 */
class FileProcessor {
    constructor(options = {}) {
        this.maxFileSize = options.maxFileSize || 10 * 1024 * 1024; // 10MB
        this.allowedTypes = options.allowedTypes || ['text/plain', 'application/json', 'text/csv'];
        this.chunkSize = options.chunkSize || 1024 * 1024; // 1MB chunks
    }

    /**
     * Process multiple files with validation and progress tracking
     */
    async processFiles(files, onProgress = null) {
        const results = [];

        for (let i = 0; i < files.length; i++) {
            const file = files[i];

            try {
                // Validate file
                this.validateFile(file);

                // Process file
                const result = await this.processFile(file, (progress) => {
                    if (onProgress) {
                        onProgress({
                            fileIndex: i,
                            totalFiles: files.length,
                            fileName: file.name,
                            fileProgress: progress,
                            overallProgress: ((i + progress) / files.length) * 100
                        });
                    }
                });

                results.push({
                    fileName: file.name,
                    success: true,
                    data: result
                });

            } catch (error) {
                console.error(`Error processing ${file.name}:`, error);
                results.push({
                    fileName: file.name,
                    success: false,
                    error: error.message
                });
            }
        }

        return results;
    }

    validateFile(file) {
        if (file.size > this.maxFileSize) {
            throw new Error(`File too large: ${file.size} bytes (max: ${this.maxFileSize})`);
        }

        if (!this.allowedTypes.includes(file.type)) {
            throw new Error(`Unsupported file type: ${file.type}`);
        }
    }

    /**
     * Process a single file with chunked reading for large files
     */
    async processFile(file, onProgress = null) {
        if (file.size <= this.chunkSize) {
            // Small file - read all at once
            const content = await this.readFileAsText(file);
            if (onProgress) onProgress(1);
            return this.analyzeContent(content);
        } else {
            // Large file - read in chunks
            return this.processFileInChunks(file, onProgress);
        }
    }

    async processFileInChunks(file, onProgress = null) {
        const chunks = Math.ceil(file.size / this.chunkSize);
        let processedContent = '';
        let wordCount = 0;
        let lineCount = 0;

        for (let i = 0; i < chunks; i++) {
            const start = i * this.chunkSize;
            const end = Math.min(start + this.chunkSize, file.size);
            const chunk = file.slice(start, end);

            const chunkContent = await this.readFileAsText(chunk);
            processedContent += chunkContent;

            // Analyze chunk
            wordCount += chunkContent.split(/\s+/).filter(word => word.length > 0).length;
            lineCount += chunkContent.split('\n').length;

            // Update progress
            if (onProgress) {
                onProgress((i + 1) / chunks);
            }

            // Small delay to prevent blocking
            await this.sleep(10);
        }

        return {
            size: file.size,
            wordCount,
            lineCount,
            charCount: processedContent.length,
            preview: processedContent.substring(0, 200) + (processedContent.length > 200 ? '...' : '')
        };
    }

    analyzeContent(content) {
        const words = content.split(/\s+/).filter(word => word.length > 0);
        const lines = content.split('\n');

        return {
            wordCount: words.length,
            lineCount: lines.length,
            charCount: content.length,
            preview: content.substring(0, 200) + (content.length > 200 ? '...' : ''),
            wordFrequency: this.getWordFrequency(words.slice(0, 1000)) // Limit for performance
        };
    }

    getWordFrequency(words) {
        const frequency = {};
        words.forEach(word => {
            const cleanWord = word.toLowerCase().replace(/[^\w]/g, '');
            if (cleanWord.length > 2) {
                frequency[cleanWord] = (frequency[cleanWord] || 0) + 1;
            }
        });

        return Object.entries(frequency)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 10)
            .reduce((obj, [word, count]) => ({ ...obj, [word]: count }), {});
    }

    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// =============================================================================
// Usage Examples and Demo Functions
// =============================================================================

/**
 * Demo function showing how to use the advanced patterns
 */
async function demonstrateAsyncPatterns() {
    console.log('=== Async/Await Advanced Patterns Demo ===\n');

    // Initialize API client
    const apiClient = new AdvancedApiClient('https://jsonplaceholder.typicode.com', {
        timeout: 5000,
        retryAttempts: 2,
        retryDelay: 1000
    });

    // Initialize user data manager
    const userManager = new UserDataManager(apiClient);

    try {
        // Example 1: Fetch user profile with error handling
        console.log('1. Fetching user profile...');
        const profile = await userManager.getUserProfile(1);
        console.log('✓ User profile loaded:', profile.user.name);

        // Example 2: Search users with caching
        console.log('\n2. Searching users...');
        const searchResults = await userManager.searchUsers('user', { limit: 5 });
        console.log(`✓ Found ${searchResults.users.length} users`);

        // Example 3: Bulk operations with progress tracking
        console.log('\n3. Bulk updating users...');
        const updates = [
            { id: 1, data: { name: 'Updated User 1' } },
            { id: 2, data: { name: 'Updated User 2' } },
            { id: 3, data: { name: 'Updated User 3' } }
        ];

        const bulkResults = await userManager.bulkUpdateUsers(updates);
        console.log('✓ Bulk update completed');

    } catch (error) {
        console.error('Demo failed:', error.message);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        AdvancedApiClient,
        ApiError,
        BatchProcessor,
        UserDataManager,
        FileProcessor,
        demonstrateAsyncPatterns
    };
}
