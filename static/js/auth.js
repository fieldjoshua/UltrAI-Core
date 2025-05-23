// Authentication Manager

class AuthManager {
    static TOKEN_KEY = 'ultra_auth_token';
    static USER_KEY = 'ultra_user_info';

    /**
     * Set authentication token
     */
    static setToken(token) {
        Utils.storage.set(this.TOKEN_KEY, token);
        this.scheduleTokenRefresh(token);
    }

    /**
     * Get authentication token
     */
    static getToken() {
        return Utils.storage.get(this.TOKEN_KEY);
    }

    /**
     * Clear authentication token and user data
     */
    static clearToken() {
        Utils.storage.remove(this.TOKEN_KEY);
        Utils.storage.remove(this.USER_KEY);
        this.clearTokenRefresh();
    }

    /**
     * Set user information
     */
    static setUser(user) {
        Utils.storage.set(this.USER_KEY, user);
    }

    /**
     * Get user information
     */
    static getUser() {
        return Utils.storage.get(this.USER_KEY);
    }

    /**
     * Check if user is authenticated
     */
    static isAuthenticated() {
        const token = this.getToken();
        if (!token) return false;

        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const currentTime = Date.now() / 1000;
            
            // Check if token is expired (with 5 minute buffer)
            if (payload.exp && payload.exp < currentTime + 300) {
                this.clearToken();
                return false;
            }
            
            return true;
        } catch (error) {
            console.warn('Invalid token format:', error);
            this.clearToken();
            return false;
        }
    }

    /**
     * Get token expiration time
     */
    static getTokenExpiration() {
        const token = this.getToken();
        if (!token) return null;

        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.exp ? new Date(payload.exp * 1000) : null;
        } catch (error) {
            return null;
        }
    }

    /**
     * Schedule automatic token refresh
     */
    static scheduleTokenRefresh(token) {
        this.clearTokenRefresh();
        
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            if (!payload.exp) return;

            const expirationTime = payload.exp * 1000;
            const currentTime = Date.now();
            const refreshTime = expirationTime - currentTime - (10 * 60 * 1000); // 10 minutes before expiry

            if (refreshTime > 0) {
                this.refreshTimeoutId = setTimeout(() => {
                    this.refreshToken();
                }, refreshTime);
            }
        } catch (error) {
            console.warn('Could not schedule token refresh:', error);
        }
    }

    /**
     * Clear token refresh timeout
     */
    static clearTokenRefresh() {
        if (this.refreshTimeoutId) {
            clearTimeout(this.refreshTimeoutId);
            this.refreshTimeoutId = null;
        }
    }

    /**
     * Refresh authentication token
     */
    static async refreshToken() {
        try {
            // Note: This would need to be implemented on the backend
            // For now, we'll just verify the token is still valid
            await api.verifyAuth();
            
            // If verification succeeds, reschedule refresh
            const token = this.getToken();
            if (token) {
                this.scheduleTokenRefresh(token);
            }
        } catch (error) {
            console.warn('Token refresh failed:', error);
            this.logout();
        }
    }

    /**
     * Login user
     */
    static async login(email, password) {
        try {
            LoadingManager.show($('#auth-modal .btn-primary'), 'Logging in...');
            
            const response = await api.login(email, password);
            
            this.setToken(response.access_token);
            
            // Get user info if available in response
            if (response.user) {
                this.setUser(response.user);
            } else {
                // Fetch user info separately
                try {
                    const userInfo = await api.verifyAuth();
                    this.setUser(userInfo);
                } catch (error) {
                    console.warn('Could not fetch user info:', error);
                }
            }

            NotificationManager.show('Login successful!', 'success');
            AppRouter.showDashboard();
            
            return response;
        } catch (error) {
            APIErrorHandler.handle(error, 'Login');
            throw error;
        } finally {
            LoadingManager.hide($('#auth-modal .btn-primary'));
        }
    }

    /**
     * Register user
     */
    static async register(email, username, password) {
        try {
            LoadingManager.show($('#auth-modal .btn-primary'), 'Creating account...');
            
            const response = await api.register(email, username, password);
            
            NotificationManager.show('Registration successful! Please log in.', 'success');
            
            // Switch to login tab
            AuthUI.switchTab('login');
            
            return response;
        } catch (error) {
            APIErrorHandler.handle(error, 'Registration');
            throw error;
        } finally {
            LoadingManager.hide($('#auth-modal .btn-primary'));
        }
    }

    /**
     * Logout user
     */
    static logout() {
        this.clearToken();
        NotificationManager.show('Logged out successfully', 'info');
        AppRouter.showLanding();
    }

    /**
     * Verify current authentication
     */
    static async verifyAuth() {
        if (!this.isAuthenticated()) {
            return false;
        }

        try {
            const userInfo = await api.verifyAuth();
            this.setUser(userInfo);
            return true;
        } catch (error) {
            console.warn('Auth verification failed:', error);
            this.clearToken();
            return false;
        }
    }
}

/**
 * Authentication UI Controller
 */
class AuthUI {
    static init() {
        this.bindEvents();
        this.updateUI();
    }

    static bindEvents() {
        // Auth button click
        Utils.on($('#auth-button'), 'click', () => {
            if (AuthManager.isAuthenticated()) {
                AuthManager.logout();
            } else {
                this.showModal();
            }
        });

        // Modal close
        Utils.on($('#modal-close'), 'click', () => this.hideModal());
        Utils.on($('#auth-modal'), 'click', (e) => {
            if (e.target === $('#auth-modal')) {
                this.hideModal();
            }
        });

        // Tab switching
        $$('#auth-modal .tab-btn').forEach(btn => {
            Utils.on(btn, 'click', () => {
                const tab = btn.dataset.tab;
                this.switchTab(tab);
            });
        });

        // Form submissions
        Utils.on($('#login-form'), 'submit', (e) => this.handleLogin(e));
        Utils.on($('#register-form'), 'submit', (e) => this.handleRegister(e));

        // Get started button
        Utils.on($('#get-started-btn'), 'click', () => this.showModal());
    }

    static showModal() {
        Utils.removeClass($('#auth-modal'), 'hidden');
        document.body.style.overflow = 'hidden';
        $('#login-email').focus();
    }

    static hideModal() {
        Utils.addClass($('#auth-modal'), 'hidden');
        document.body.style.overflow = '';
        this.clearForms();
    }

    static switchTab(tab) {
        // Update tab buttons
        $$('#auth-modal .tab-btn').forEach(btn => {
            Utils.removeClass(btn, 'active');
            if (btn.dataset.tab === tab) {
                Utils.addClass(btn, 'active');
            }
        });

        // Update forms
        if (tab === 'login') {
            Utils.removeClass($('#login-form'), 'hidden');
            Utils.addClass($('#register-form'), 'hidden');
            $('#auth-title').textContent = 'Login';
            $('#login-email').focus();
        } else {
            Utils.addClass($('#login-form'), 'hidden');
            Utils.removeClass($('#register-form'), 'hidden');
            $('#auth-title').textContent = 'Register';
            $('#register-email').focus();
        }
    }

    static async handleLogin(e) {
        e.preventDefault();
        
        const email = $('#login-email').value.trim();
        const password = $('#login-password').value;

        if (!Utils.isValidEmail(email)) {
            NotificationManager.show('Please enter a valid email address', 'error');
            return;
        }

        if (!password) {
            NotificationManager.show('Please enter your password', 'error');
            return;
        }

        try {
            await AuthManager.login(email, password);
            this.hideModal();
        } catch (error) {
            // Error handling is done in AuthManager.login
        }
    }

    static async handleRegister(e) {
        e.preventDefault();
        
        const email = $('#register-email').value.trim();
        const username = $('#register-username').value.trim();
        const password = $('#register-password').value;

        if (!Utils.isValidEmail(email)) {
            NotificationManager.show('Please enter a valid email address', 'error');
            return;
        }

        if (!username) {
            NotificationManager.show('Please enter a username', 'error');
            return;
        }

        if (!Utils.isValidPassword(password)) {
            NotificationManager.show('Password must be at least 6 characters long', 'error');
            return;
        }

        try {
            await AuthManager.register(email, username, password);
        } catch (error) {
            // Error handling is done in AuthManager.register
        }
    }

    static clearForms() {
        $('#login-form').reset();
        $('#register-form').reset();
    }

    static updateUI() {
        const isAuthenticated = AuthManager.isAuthenticated();
        const user = AuthManager.getUser();
        
        if (isAuthenticated && user) {
            $('#user-status').textContent = `Welcome, ${user.username || user.email}`;
            $('#auth-button').textContent = 'Logout';
            Utils.removeClass($('#auth-button'), 'btn-primary');
            Utils.addClass($('#auth-button'), 'btn-secondary');
        } else {
            $('#user-status').textContent = 'Not logged in';
            $('#auth-button').textContent = 'Login';
            Utils.removeClass($('#auth-button'), 'btn-secondary');
            Utils.addClass($('#auth-button'), 'btn-primary');
        }
    }
}

/**
 * Loading Manager for buttons
 */
class LoadingManager {
    static show(element, message = 'Loading...') {
        if (!element) return;
        
        Utils.addClass(element, 'loading');
        element.disabled = true;
        element.originalText = element.textContent;
        element.textContent = message;
    }

    static hide(element) {
        if (!element) return;
        
        Utils.removeClass(element, 'loading');
        element.disabled = false;
        if (element.originalText) {
            element.textContent = element.originalText;
            delete element.originalText;
        }
    }
}

// Make classes available globally
window.AuthManager = AuthManager;
window.AuthUI = AuthUI;
window.LoadingManager = LoadingManager;