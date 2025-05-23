// Main Application Controller

/**
 * Notification Manager
 */
class NotificationManager {
    static show(message, type = 'info', duration = 5000) {
        const notification = Utils.createElement('div', {
            className: `notification notification-${type}`
        }, message);

        $('#notifications').appendChild(notification);

        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, duration);

        return notification;
    }

    static clear() {
        $('#notifications').innerHTML = '';
    }
}

/**
 * App Router
 */
class AppRouter {
    static showLanding() {
        Utils.removeClass($('#landing-page'), 'hidden');
        Utils.addClass($('#dashboard'), 'hidden');
        AuthUI.updateUI();
    }

    static showDashboard() {
        Utils.addClass($('#landing-page'), 'hidden');
        Utils.removeClass($('#dashboard'), 'hidden');
        AuthUI.updateUI();
        
        // Initialize dashboard components
        DocumentUploader.loadDocuments();
    }

    static showAuth() {
        AuthUI.showModal();
    }
}

/**
 * Application Class
 */
class UltraApp {
    static async init() {
        console.log('🚀 UltraAI Application Starting...');
        
        try {
            // Check authentication status
            const isAuthenticated = await AuthManager.verifyAuth();
            
            // Initialize UI components
            AuthUI.init();
            DocumentUploader.init();
            AnalysisManager.init();
            
            // Initialize routing
            if (isAuthenticated) {
                AppRouter.showDashboard();
            } else {
                AppRouter.showLanding();
            }
            
            // Check backend health
            this.checkBackendHealth();
            
            console.log('✅ UltraAI Application Ready');
            
        } catch (error) {
            console.error('❌ Application initialization failed:', error);
            NotificationManager.show('Application failed to start. Please refresh the page.', 'error');
        }
    }

    static async checkBackendHealth() {
        try {
            await api.checkHealth();
            console.log('✅ Backend connection healthy');
        } catch (error) {
            console.warn('⚠️ Backend health check failed:', error);
            NotificationManager.show('Backend connection issues detected', 'warning');
        }
    }

    static handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + K: Focus search or prompt
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const promptInput = $('#prompt-input');
            if (promptInput && !Utils.hasClass(promptInput.closest('.dashboard'), 'hidden')) {
                promptInput.focus();
            }
        }

        // Escape: Close modals
        if (e.key === 'Escape') {
            if (!Utils.hasClass($('#auth-modal'), 'hidden')) {
                AuthUI.hideModal();
            }
        }
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => UltraApp.init());
} else {
    UltraApp.init();
}

// Global keyboard shortcuts
document.addEventListener('keydown', UltraApp.handleKeyboardShortcuts);

// Handle window before unload
window.addEventListener('beforeunload', (e) => {
    // Only show warning if there's unsaved work
    const hasUnsavedWork = $('#prompt-input').value.trim() !== '';
    if (hasUnsavedWork) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Handle online/offline status
window.addEventListener('online', () => {
    NotificationManager.show('Connection restored', 'success');
});

window.addEventListener('offline', () => {
    NotificationManager.show('You are offline. Some features may not work.', 'warning');
});

// Error handling
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
    NotificationManager.show('An unexpected error occurred', 'error');
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
    NotificationManager.show('An unexpected error occurred', 'error');
});

// Make classes available globally
window.NotificationManager = NotificationManager;
window.AppRouter = AppRouter;
window.UltraApp = UltraApp;