// Utility Functions

/**
 * DOM Helper Functions
 */
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

const createElement = (tag, attributes = {}, textContent = '') => {
    const element = document.createElement(tag);
    Object.assign(element, attributes);
    if (textContent) element.textContent = textContent;
    return element;
};

const addClass = (element, className) => element.classList.add(className);
const removeClass = (element, className) => element.classList.remove(className);
const toggleClass = (element, className) => element.classList.toggle(className);
const hasClass = (element, className) => element.classList.contains(className);

/**
 * Event Helper Functions
 */
const on = (element, event, handler) => element.addEventListener(event, handler);
const off = (element, event, handler) => element.removeEventListener(event, handler);
const emit = (element, event, data = {}) => {
    element.dispatchEvent(new CustomEvent(event, { detail: data }));
};

/**
 * Validation Functions
 */
const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

const isValidPassword = (password) => {
    return password.length >= 6;
};

const sanitizeHtml = (str) => {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
};

/**
 * Format Functions
 */
const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatDate = (date) => {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
};

const truncateText = (text, maxLength = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
};

/**
 * Debounce Function
 */
const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

/**
 * Throttle Function
 */
const throttle = (func, limit) => {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
};

/**
 * Deep Clone Function
 */
const deepClone = (obj) => {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj.getTime());
    if (obj instanceof Array) return obj.map(item => deepClone(item));
    if (typeof obj === 'object') {
        const clonedObj = {};
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                clonedObj[key] = deepClone(obj[key]);
            }
        }
        return clonedObj;
    }
};

/**
 * Local Storage Helpers
 */
const storage = {
    get: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.warn('Error reading from localStorage:', error);
            return defaultValue;
        }
    },
    
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.warn('Error writing to localStorage:', error);
            return false;
        }
    },
    
    remove: (key) => {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.warn('Error removing from localStorage:', error);
            return false;
        }
    },
    
    clear: () => {
        try {
            localStorage.clear();
            return true;
        } catch (error) {
            console.warn('Error clearing localStorage:', error);
            return false;
        }
    }
};

/**
 * URL Helpers
 */
const url = {
    getParams: () => {
        const params = new URLSearchParams(window.location.search);
        const result = {};
        for (const [key, value] of params) {
            result[key] = value;
        }
        return result;
    },
    
    setParam: (key, value) => {
        const url = new URL(window.location);
        url.searchParams.set(key, value);
        window.history.replaceState({}, '', url);
    },
    
    removeParam: (key) => {
        const url = new URL(window.location);
        url.searchParams.delete(key);
        window.history.replaceState({}, '', url);
    }
};

/**
 * Animation Helpers
 */
const animate = {
    fadeIn: (element, duration = 300) => {
        element.style.opacity = '0';
        element.style.display = 'block';
        
        let start = null;
        const step = (timestamp) => {
            if (!start) start = timestamp;
            const progress = Math.min((timestamp - start) / duration, 1);
            element.style.opacity = progress;
            
            if (progress < 1) {
                requestAnimationFrame(step);
            }
        };
        requestAnimationFrame(step);
    },
    
    fadeOut: (element, duration = 300) => {
        let start = null;
        const step = (timestamp) => {
            if (!start) start = timestamp;
            const progress = Math.min((timestamp - start) / duration, 1);
            element.style.opacity = 1 - progress;
            
            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                element.style.display = 'none';
            }
        };
        requestAnimationFrame(step);
    },
    
    slideDown: (element, duration = 300) => {
        element.style.display = 'block';
        const height = element.scrollHeight;
        element.style.height = '0px';
        element.style.overflow = 'hidden';
        
        let start = null;
        const step = (timestamp) => {
            if (!start) start = timestamp;
            const progress = Math.min((timestamp - start) / duration, 1);
            element.style.height = (height * progress) + 'px';
            
            if (progress >= 1) {
                element.style.height = '';
                element.style.overflow = '';
            } else {
                requestAnimationFrame(step);
            }
        };
        requestAnimationFrame(step);
    }
};

/**
 * Error Handling
 */
const handleError = (error, context = 'Unknown') => {
    console.error(`Error in ${context}:`, error);
    
    // Send to error reporting service in production
    if (window.location.hostname !== 'localhost') {
        // Add error reporting logic here
    }
    
    return {
        message: error.message || 'An unexpected error occurred',
        context,
        timestamp: new Date().toISOString()
    };
};

/**
 * Feature Detection
 */
const features = {
    supportsFileAPI: () => {
        return window.File && window.FileReader && window.FileList && window.Blob;
    },
    
    supportsDragDrop: () => {
        const div = document.createElement('div');
        return ('draggable' in div) || ('ondragstart' in div && 'ondrop' in div);
    },
    
    supportsLocalStorage: () => {
        try {
            const test = 'test';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch(e) {
            return false;
        }
    }
};

// Export utilities for use in other modules
window.Utils = {
    $, $$, createElement, addClass, removeClass, toggleClass, hasClass,
    on, off, emit,
    isValidEmail, isValidPassword, sanitizeHtml,
    formatFileSize, formatDate, truncateText,
    debounce, throttle, deepClone,
    storage, url, animate, handleError, features
};