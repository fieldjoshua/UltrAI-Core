/// <reference types="cypress" />

describe('Authentication', () => {
    beforeEach(() => {
        // Reset any previous auth state
        cy.clearLocalStorage();
        cy.clearCookies();

        // Stub login API
        cy.intercept('POST', '/api/auth/login', (req) => {
            const { email, password } = req.body;

            if (email === 'test@example.com' && password === 'password') {
                return req.reply({
                    statusCode: 200,
                    body: {
                        token: 'fake-jwt-token',
                        user: {
                            id: 'user-1',
                            email: 'test@example.com',
                            name: 'Test User',
                            role: 'user'
                        }
                    }
                });
            } else {
                return req.reply({
                    statusCode: 401,
                    body: {
                        error: 'Invalid email or password'
                    }
                });
            }
        }).as('loginRequest');

        // Stub signup API
        cy.intercept('POST', '/api/auth/register', (req) => {
            const { email } = req.body;

            if (email === 'existing@example.com') {
                return req.reply({
                    statusCode: 409,
                    body: {
                        error: 'User already exists'
                    }
                });
            } else {
                return req.reply({
                    statusCode: 201,
                    body: {
                        token: 'fake-jwt-token',
                        user: {
                            id: 'new-user',
                            email: req.body.email,
                            name: req.body.name,
                            role: 'user'
                        }
                    }
                });
            }
        }).as('signupRequest');

        // Stub logout API
        cy.intercept('POST', '/api/auth/logout', {
            statusCode: 200,
            body: { success: true }
        }).as('logoutRequest');

        // Stub protected routes
        cy.intercept('GET', '/api/documents', (req) => {
            const authHeader = req.headers.authorization;

            if (authHeader === 'Bearer fake-jwt-token') {
                return req.reply({
                    statusCode: 200,
                    body: []
                });
            } else {
                return req.reply({
                    statusCode: 401,
                    body: {
                        error: 'Unauthorized'
                    }
                });
            }
        }).as('protectedRoute');
    });

    it('should redirect to login when visiting protected route', () => {
        cy.visit('/documents');
        cy.url().should('include', '/login');
        cy.get('[data-cy=login-form]').should('be.visible');
    });

    it('should login successfully with valid credentials', () => {
        cy.visit('/login');

        cy.get('[data-cy=email-input]').type('test@example.com');
        cy.get('[data-cy=password-input]').type('password');
        cy.get('[data-cy=login-button]').click();

        cy.wait('@loginRequest');

        // Should redirect to documents page
        cy.url().should('include', '/documents');

        // Should store auth token
        cy.window().then((window) => {
            expect(window.localStorage.getItem('auth_token')).to.eq('fake-jwt-token');
        });

        // Should be able to access protected route
        cy.wait('@protectedRoute');
    });

    it('should show error with invalid credentials', () => {
        cy.visit('/login');

        cy.get('[data-cy=email-input]').type('test@example.com');
        cy.get('[data-cy=password-input]').type('wrong-password');
        cy.get('[data-cy=login-button]').click();

        cy.wait('@loginRequest');

        // Should show error message
        cy.get('[data-cy=auth-error]').should('be.visible');
        cy.get('[data-cy=auth-error]').should('contain', 'Invalid email or password');

        // Should not redirect
        cy.url().should('include', '/login');
    });

    it('should register a new user successfully', () => {
        cy.visit('/register');

        cy.get('[data-cy=name-input]').type('New User');
        cy.get('[data-cy=email-input]').type('new@example.com');
        cy.get('[data-cy=password-input]').type('password123');
        cy.get('[data-cy=confirm-password-input]').type('password123');
        cy.get('[data-cy=register-button]').click();

        cy.wait('@signupRequest');

        // Should redirect to documents page
        cy.url().should('include', '/documents');

        // Should store auth token
        cy.window().then((window) => {
            expect(window.localStorage.getItem('auth_token')).to.eq('fake-jwt-token');
        });
    });

    it('should show error for existing email during registration', () => {
        cy.visit('/register');

        cy.get('[data-cy=name-input]').type('Existing User');
        cy.get('[data-cy=email-input]').type('existing@example.com');
        cy.get('[data-cy=password-input]').type('password123');
        cy.get('[data-cy=confirm-password-input]').type('password123');
        cy.get('[data-cy=register-button]').click();

        cy.wait('@signupRequest');

        // Should show error message
        cy.get('[data-cy=auth-error]').should('be.visible');
        cy.get('[data-cy=auth-error]').should('contain', 'User already exists');

        // Should not redirect
        cy.url().should('include', '/register');
    });

    it('should validate the registration form', () => {
        cy.visit('/register');

        // Try submitting with empty form
        cy.get('[data-cy=register-button]').click();

        // Should show validation errors
        cy.get('[data-cy=name-error]').should('be.visible');
        cy.get('[data-cy=email-error]').should('be.visible');
        cy.get('[data-cy=password-error]').should('be.visible');

        // Try with mismatched passwords
        cy.get('[data-cy=name-input]').type('Test User');
        cy.get('[data-cy=email-input]').type('test@example.com');
        cy.get('[data-cy=password-input]').type('password123');
        cy.get('[data-cy=confirm-password-input]').type('different-password');
        cy.get('[data-cy=register-button]').click();

        // Should show password match error
        cy.get('[data-cy=password-match-error]').should('be.visible');
    });

    it('should logout successfully', () => {
        // Login first
        cy.window().then((window) => {
            window.localStorage.setItem('auth_token', 'fake-jwt-token');
        });

        cy.visit('/documents');
        cy.wait('@protectedRoute');

        // Click logout button
        cy.get('[data-cy=user-menu]').click();
        cy.get('[data-cy=logout-button]').click();

        cy.wait('@logoutRequest');

        // Should redirect to login page
        cy.url().should('include', '/login');

        // Token should be removed
        cy.window().then((window) => {
            expect(window.localStorage.getItem('auth_token')).to.be.null;
        });
    });
});