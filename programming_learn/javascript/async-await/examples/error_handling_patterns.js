/**
 * Comprehensive Error Handling Examples for Async/Await
 * Demonstrates various error handling patterns, recovery strategies, and best practices
 */

// =============================================================================
// Custom Error Types for Better Error Handling
// =============================================================================

class NetworkError extends Error {
    constructor(message, code = 'NETWORK_ERROR') {
        super(message);
        this.name = 'NetworkError';
        this.code = code;
        this.retryable = true;
    }
}

class ValidationError extends Error {
    constructor(message, field = null) {
        super(message);
        this.name = 'ValidationError';
        this.field = field;
        this.retryable = false;
    }
}

class AuthenticationError extends Error {
    constructor(message) {
        super(message);
        this.name = 'AuthenticationError';
        this.retryable = false;
    }
}

class RateLimitError extends Error {
    constructor(message, retryAfter = 60) {
        super(message);
        this.name = 'RateLimitError';
        this.retryAfter = retryAfter; // seconds
        this.retryable = true;
    }
}

// =============================================================================
// Error Classification and Recovery Strategies
// =============================================================================

class ErrorHandler {
    static classify(error) {
        // Network-related errors
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            return new NetworkError('Network connection failed', 'CONNECTION_FAILED');
        }

        if (error.name === 'AbortError') {
            return new NetworkError('Request timeout', 'TIMEOUT');
        }

        // HTTP status codes
        if (error.status) {
            switch (Math.floor(error.status / 100)) {
                case 4:
                    if (error.status === 401) {
                        return new AuthenticationError('Authentication required');
                    }
                    if (error.status === 429) {
                        return new RateLimitError('Rate limit exceeded');
                    }
                    return new ValidationError(`Client error: ${error.message}`);

                case 5:
                    return new NetworkError(`Server error: ${error.message}`, 'SERVER_ERROR');

                default:
                    return error;
            }
        }

        return error;
    }

    static async handleWithRetry(operation, options = {}) {
        const {
            maxRetries = 3,
            baseDelay = 1000,
            maxDelay = 10000,
            backoffFactor = 2,
            retryCondition = (error) => error.retryable
        } = options;

        let lastError;

        for (let attempt = 0; attempt <= maxRetries; attempt++) {
            try {
                return await operation();
            } catch (error) {
                const classifiedError = this.classify(error);
                lastError = classifiedError;

                // Don't retry if it's the last attempt or error is not retryable
                if (attempt === maxRetries || !retryCondition(classifiedError)) {
                    throw classifiedError;
                }

                // Calculate delay with exponential backoff
                let delay = Math.min(baseDelay * Math.pow(backoffFactor, attempt), maxDelay);

                // Special handling for rate limit errors
                if (classifiedError instanceof RateLimitError) {
                    delay = classifiedError.retryAfter * 1000;
                }

                console.warn(`Attempt ${attempt + 1} failed, retrying in ${delay}ms:`, classifiedError.message);
                await this.sleep(delay);
            }
        }

        throw lastError;
    }

    static sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// =============================================================================
// Circuit Breaker Pattern for Fault Tolerance
// =============================================================================

class CircuitBreaker {
    constructor(options = {}) {
        this.failureThreshold = options.failureThreshold || 5;
        this.resetTimeout = options.resetTimeout || 30000; // 30 seconds
        this.monitoringPeriod = options.monitoringPeriod || 10000; // 10 seconds

        this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
        this.failureCount = 0;
        this.lastFailureTime = null;
        this.successCount = 0;
    }

    async execute(operation) {
        if (this.state === 'OPEN') {
            if (Date.now() - this.lastFailureTime >= this.resetTimeout) {
                this.state = 'HALF_OPEN';
                this.successCount = 0;
                console.log('Circuit breaker: Transitioning to HALF_OPEN');
            } else {
                throw new Error('Circuit breaker is OPEN - operation not attempted');
            }
        }

        try {
            const result = await operation();
            this.onSuccess();
            return result;
        } catch (error) {
            this.onFailure();
            throw error;
        }
    }

    onSuccess() {
        if (this.state === 'HALF_OPEN') {
            this.successCount++;
            if (this.successCount >= 3) { // Require 3 successes to close
                this.state = 'CLOSED';
                this.failureCount = 0;
                console.log('Circuit breaker: Transitioning to CLOSED');
            }
        } else {
            this.failureCount = Math.max(0, this.failureCount - 1);
        }
    }

    onFailure() {
        this.failureCount++;
        this.lastFailureTime = Date.now();

        if (this.state === 'HALF_OPEN' || this.failureCount >= this.failureThreshold) {
            this.state = 'OPEN';
            console.log('Circuit breaker: Transitioning to OPEN');
        }
    }

    getState() {
        return {
            state: this.state,
            failureCount: this.failureCount,
            lastFailureTime: this.lastFailureTime
        };
    }
}

// =============================================================================
// Graceful Degradation Examples
// =============================================================================

class DataService {
    constructor() {
        this.circuitBreaker = new CircuitBreaker({
            failureThreshold: 3,
            resetTimeout: 20000
        });
        this.cache = new Map();
    }

    /**
     * Fetch data with multiple fallback strategies
     */
    async fetchUserData(userId) {
        const strategies = [
            () => this.fetchFromPrimaryAPI(userId),
            () => this.fetchFromSecondaryAPI(userId),
            () => this.fetchFromCache(userId),
            () => this.getDefaultUserData(userId)
        ];

        const errors = [];

        for (const [index, strategy] of strategies.entries()) {
            try {
                console.log(`Trying strategy ${index + 1}...`);
                const result = await strategy();

                if (result) {
                    // Cache successful results
                    this.cache.set(`user_${userId}`, {
                        data: result,
                        timestamp: Date.now()
                    });
                    return result;
                }
            } catch (error) {
                console.warn(`Strategy ${index + 1} failed:`, error.message);
                errors.push(error);
            }
        }

        // All strategies failed
        throw new Error(`All strategies failed: ${errors.map(e => e.message).join(', ')}`);
    }

    async fetchFromPrimaryAPI(userId) {
        return this.circuitBreaker.execute(async () => {
            const response = await fetch(`https://api.primary.com/users/${userId}`);

            if (!response.ok) {
                throw new Error(`Primary API failed: ${response.status}`);
            }

            return response.json();
        });
    }

    async fetchFromSecondaryAPI(userId) {
        const response = await fetch(`https://api.secondary.com/users/${userId}`);

        if (!response.ok) {
            throw new Error(`Secondary API failed: ${response.status}`);
        }

        return response.json();
    }

    fetchFromCache(userId) {
        const cached = this.cache.get(`user_${userId}`);

        if (cached && Date.now() - cached.timestamp < 300000) { // 5 minutes
            console.log('Returning cached data');
            return cached.data;
        }

        throw new Error('No valid cached data');
    }

    getDefaultUserData(userId) {
        console.log('Returning default user data');
        return {
            id: userId,
            name: 'Unknown User',
            email: null,
            avatar: '/default-avatar.png',
            fromCache: false,
            isDefault: true
        };
    }

    /**
     * Batch operation with partial failure handling
     */
    async batchFetchUsers(userIds) {
        const results = [];
        const errors = [];

        // Process in chunks to avoid overwhelming the system
        const chunkSize = 5;
        for (let i = 0; i < userIds.length; i += chunkSize) {
            const chunk = userIds.slice(i, i + chunkSize);

            const chunkPromises = chunk.map(async (userId) => {
                try {
                    const userData = await this.fetchUserData(userId);
                    return { success: true, userId, data: userData };
                } catch (error) {
                    console.error(`Failed to fetch user ${userId}:`, error.message);
                    return { success: false, userId, error: error.message };
                }
            });

            const chunkResults = await Promise.allSettled(chunkPromises);

            chunkResults.forEach((result, index) => {
                if (result.status === 'fulfilled') {
                    results.push(result.value);
                } else {
                    errors.push({
                        userId: chunk[index],
                        error: result.reason.message
                    });
                }
            });

            // Small delay between chunks
            if (i + chunkSize < userIds.length) {
                await new Promise(resolve => setTimeout(resolve, 100));
            }
        }

        return {
            results,
            errors,
            totalRequested: userIds.length,
            successCount: results.filter(r => r.success).length,
            errorCount: results.filter(r => !r.success).length + errors.length
        };
    }
}

// =============================================================================
// Timeout and Cancellation Patterns
// =============================================================================

class TaskManager {
    constructor() {
        this.activeTasks = new Map();
        this.taskId = 0;
    }

    /**
     * Run task with timeout and cancellation support
     */
    async runWithTimeout(operation, timeoutMs = 5000, onProgress = null) {
        const taskId = ++this.taskId;
        const controller = new AbortController();

        // Store task for potential cancellation
        this.activeTasks.set(taskId, {
            controller,
            startTime: Date.now(),
            timeout: timeoutMs
        });

        try {
            // Create timeout promise
            const timeoutPromise = new Promise((_, reject) => {
                const timeoutId = setTimeout(() => {
                    controller.abort();
                    reject(new Error(`Operation timed out after ${timeoutMs}ms`));
                }, timeoutMs);

                // Clear timeout if operation completes
                controller.signal.addEventListener('abort', () => {
                    clearTimeout(timeoutId);
                });
            });

            // Progress tracking
            let progressInterval;
            if (onProgress) {
                progressInterval = setInterval(() => {
                    const elapsed = Date.now() - this.activeTasks.get(taskId).startTime;
                    const progress = Math.min(elapsed / timeoutMs, 0.99);
                    onProgress(progress);
                }, 100);
            }

            // Race between operation and timeout
            const result = await Promise.race([
                operation(controller.signal),
                timeoutPromise
            ]);

            if (progressInterval) {
                clearInterval(progressInterval);
                onProgress(1); // Complete
            }

            return result;

        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error(`Operation was cancelled (task ${taskId})`);
            }
            throw error;
        } finally {
            this.activeTasks.delete(taskId);
        }
    }

    /**
     * Cancel all active tasks
     */
    cancelAllTasks() {
        const taskCount = this.activeTasks.size;

        for (const [taskId, task] of this.activeTasks) {
            task.controller.abort();
        }

        this.activeTasks.clear();
        console.log(`Cancelled ${taskCount} active tasks`);
    }

    /**
     * Get status of active tasks
     */
    getActiveTasksStatus() {
        const now = Date.now();
        return Array.from(this.activeTasks.entries()).map(([taskId, task]) => ({
            taskId,
            elapsed: now - task.startTime,
            timeout: task.timeout,
            progress: Math.min((now - task.startTime) / task.timeout, 1)
        }));
    }
}

// =============================================================================
// Real-World Error Handling Examples
// =============================================================================

/**
 * File upload with comprehensive error handling
 */
async function uploadFileWithErrorHandling(file, options = {}) {
    const {
        maxSize = 10 * 1024 * 1024, // 10MB
        allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'],
        maxRetries = 3,
        chunkSize = 1024 * 1024 // 1MB
    } = options;

    try {
        // Validation
        if (!file) {
            throw new ValidationError('No file provided');
        }

        if (file.size > maxSize) {
            throw new ValidationError(`File too large: ${file.size} bytes (max: ${maxSize})`);
        }

        if (!allowedTypes.includes(file.type)) {
            throw new ValidationError(`Unsupported file type: ${file.type}`);
        }

        // Upload with retry logic
        return await ErrorHandler.handleWithRetry(
            async () => {
                if (file.size <= chunkSize) {
                    return await uploadSingleChunk(file);
                } else {
                    return await uploadInChunks(file, chunkSize);
                }
            },
            { maxRetries }
        );

    } catch (error) {
        // Log error for monitoring
        console.error('File upload failed:', {
            fileName: file?.name,
            fileSize: file?.size,
            error: error.message,
            errorType: error.constructor.name
        });

        // Return user-friendly error message
        if (error instanceof ValidationError) {
            throw new Error(`Upload failed: ${error.message}`);
        } else if (error instanceof NetworkError) {
            throw new Error('Upload failed due to network issues. Please try again.');
        } else {
            throw new Error('Upload failed due to an unexpected error. Please try again later.');
        }
    }
}

async function uploadSingleChunk(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
    }

    return await response.json();
}

async function uploadInChunks(file, chunkSize) {
    const totalChunks = Math.ceil(file.size / chunkSize);
    const uploadId = `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    console.log(`Uploading ${file.name} in ${totalChunks} chunks...`);

    for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
        const start = chunkIndex * chunkSize;
        const end = Math.min(start + chunkSize, file.size);
        const chunk = file.slice(start, end);

        await ErrorHandler.handleWithRetry(
            async () => {
                const formData = new FormData();
                formData.append('chunk', chunk);
                formData.append('chunkIndex', chunkIndex.toString());
                formData.append('totalChunks', totalChunks.toString());
                formData.append('uploadId', uploadId);
                formData.append('fileName', file.name);

                const response = await fetch('/api/upload/chunk', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`Chunk upload failed: ${response.status}`);
                }

                return await response.json();
            },
            { maxRetries: 2 }
        );

        console.log(`Uploaded chunk ${chunkIndex + 1}/${totalChunks}`);
    }

    // Finalize upload
    const finalizeResponse = await fetch('/api/upload/finalize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ uploadId, fileName: file.name })
    });

    if (!finalizeResponse.ok) {
        throw new Error('Failed to finalize upload');
    }

    return await finalizeResponse.json();
}

/**
 * API pagination with error recovery
 */
async function fetchAllPages(baseUrl, options = {}) {
    const {
        maxPages = 100,
        pageSize = 20,
        maxConcurrentRequests = 3
    } = options;

    const results = [];
    const errors = [];
    let page = 1;
    let hasMorePages = true;

    while (hasMorePages && page <= maxPages) {
        try {
            // Determine how many pages to fetch in parallel
            const remainingPages = Math.min(maxConcurrentRequests, maxPages - page + 1);
            const pagePromises = [];

            for (let i = 0; i < remainingPages; i++) {
                const currentPage = page + i;
                pagePromises.push(
                    fetchPageWithRetry(baseUrl, currentPage, pageSize)
                        .then(data => ({ page: currentPage, success: true, data }))
                        .catch(error => ({ page: currentPage, success: false, error: error.message }))
                );
            }

            const pageResults = await Promise.all(pagePromises);

            for (const result of pageResults) {
                if (result.success) {
                    results.push(...result.data.items);

                    // Check if this was the last page
                    if (result.data.items.length < pageSize) {
                        hasMorePages = false;
                    }
                } else {
                    errors.push(result);
                    console.error(`Failed to fetch page ${result.page}:`, result.error);
                }
            }

            page += remainingPages;

        } catch (error) {
            console.error('Batch page fetch failed:', error);
            errors.push({ page, error: error.message });
            page++;
        }
    }

    return {
        data: results,
        errors,
        totalPages: page - 1,
        hasErrors: errors.length > 0
    };
}

async function fetchPageWithRetry(baseUrl, page, pageSize) {
    return ErrorHandler.handleWithRetry(
        async () => {
            const url = `${baseUrl}?page=${page}&limit=${pageSize}`;
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        },
        { maxRetries: 2 }
    );
}

// =============================================================================
// Demo and Testing Functions
// =============================================================================

/**
 * Comprehensive error handling demo
 */
async function demonstrateErrorHandling() {
    console.log('=== Async/Await Error Handling Demo ===\n');

    const dataService = new DataService();
    const taskManager = new TaskManager();

    // Demo 1: Graceful degradation
    console.log('1. Testing graceful degradation...');
    try {
        const userData = await dataService.fetchUserData(123);
        console.log('✓ User data fetched:', userData.name || 'Default User');
    } catch (error) {
        console.error('✗ All strategies failed:', error.message);
    }

    // Demo 2: Batch operations with partial failures
    console.log('\n2. Testing batch operations...');
    const userIds = [1, 2, 999, 4, 5]; // 999 will likely fail
    const batchResult = await dataService.batchFetchUsers(userIds);
    console.log(`✓ Batch completed: ${batchResult.successCount} success, ${batchResult.errorCount} errors`);

    // Demo 3: Task with timeout
    console.log('\n3. Testing timeout handling...');
    try {
        const result = await taskManager.runWithTimeout(
            async (signal) => {
                // Simulate slow operation
                await new Promise(resolve => setTimeout(resolve, 2000));
                if (signal.aborted) throw new Error('Aborted');
                return 'Operation completed';
            },
            3000, // 3 second timeout
            (progress) => {
                if (progress < 1) {
                    process.stdout.write(`\rProgress: ${(progress * 100).toFixed(1)}%`);
                }
            }
        );
        console.log('\n✓ Task completed:', result);
    } catch (error) {
        console.log('\n✗ Task failed:', error.message);
    }

    // Demo 4: Circuit breaker
    console.log('\n4. Testing circuit breaker...');
    const circuitBreaker = new CircuitBreaker({ failureThreshold: 2 });

    for (let i = 1; i <= 5; i++) {
        try {
            await circuitBreaker.execute(async () => {
                if (Math.random() < 0.7) { // 70% failure rate
                    throw new Error('Random failure');
                }
                return 'Success';
            });
            console.log(`✓ Attempt ${i}: Success`);
        } catch (error) {
            console.log(`✗ Attempt ${i}: ${error.message}`);
        }
    }

    console.log('\nCircuit breaker state:', circuitBreaker.getState());
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        NetworkError,
        ValidationError,
        AuthenticationError,
        RateLimitError,
        ErrorHandler,
        CircuitBreaker,
        DataService,
        TaskManager,
        uploadFileWithErrorHandling,
        fetchAllPages,
        demonstrateErrorHandling
    };
}

// Run demo if this file is executed directly
if (typeof window === 'undefined' && require.main === module) {
    demonstrateErrorHandling().catch(console.error);
}
