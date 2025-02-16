// logger.js
const LOG_LEVELS = {
    INFO: 'INFO',
    ERROR: 'ERROR',
    DEBUG: 'DEBUG',
    WARN: 'WARN'
};

class Logger {
    constructor() {
        this.metadata = {
            userAgent: navigator.userAgent,
            url: window.location.href,
            timestamp: new Date().toISOString()
        };
    }

    formatLogEntry(level, component, action, details = {}) {
        return {
            timestamp: new Date().toISOString(),
            level,
            component,
            action,
            details: {
                ...details,
                url: window.location.href
            },
            metadata: this.metadata
        };
    }

    info(component, action, details = {}) {
        const logEntry = this.formatLogEntry(LOG_LEVELS.INFO, component, action, details);
        console.info(`[${logEntry.timestamp}] ${component} - ${action}:`, details);
        this.sendToServer(logEntry);
    }

    error(component, action, error, details = {}) {
        const logEntry = this.formatLogEntry(LOG_LEVELS.ERROR, component, action, {
            ...details,
            error: {
                message: error.message,
                stack: error.stack,
                name: error.name
            }
        });
        console.error(`[${logEntry.timestamp}] ${component} - ${action}:`, error, details);
        this.sendToServer(logEntry);
    }

    debug(component, action, details = {}) {
        const logEntry = this.formatLogEntry(LOG_LEVELS.DEBUG, component, action, details);
        console.debug(`[${logEntry.timestamp}] ${component} - ${action}:`, details);
        this.sendToServer(logEntry);
    }

    warn(component, action, details = {}) {
        const logEntry = this.formatLogEntry(LOG_LEVELS.WARN, component, action, details);
        console.warn(`[${logEntry.timestamp}] ${component} - ${action}:`, details);
        this.sendToServer(logEntry);
    }

    // Performance logging
    logPerformance(component, action, startTime, details = {}) {
        const duration = performance.now() - startTime;
        this.info(component, action, {
            ...details,
            duration_ms: duration
        });
    }

    // API call logging
    logApiCall(component, endpoint, method, startTime, status, details = {}) {
        const duration = performance.now() - startTime;
        this.info(component, 'API_CALL', {
            endpoint,
            method,
            status,
            duration_ms: duration,
            ...details
        });
    }

    // User interaction logging
    logUserInteraction(component, action, details = {}) {
        this.info(component, action, {
            ...details,
            timestamp: new Date().toISOString()
        });
    }

    // Optional: Send logs to backend
    async sendToServer(logEntry) {
        // In development, we'll just console log
        if (process.env.NODE_ENV === 'development') {
            return;
        }

        // In production, you could send logs to your backend
        try {
            await fetch('http://localhost:8000/logs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(logEntry)
            });
        } catch (error) {
            console.error('Failed to send log to server:', error);
        }
    }
}

// Create a singleton instance
const logger = new Logger();

export default logger;
