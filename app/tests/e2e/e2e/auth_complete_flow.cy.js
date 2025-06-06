/// <reference types="cypress" />

describe('Authentication Flow', () => {
  // Generate a unique email for testing to avoid conflicts
  const uniqueId = Math.floor(Math.random() * 1000000);
  const testUser = {
    email: `test_user_${uniqueId}@example.com`,
    password: 'SecurePassword123!',
    name: 'Test User',
  };

  beforeEach(() => {
    // Intercept API calls to monitor auth requests
    cy.intercept('POST', '/api/auth/register').as('registerRequest');
    cy.intercept('POST', '/api/auth/login').as('loginRequest');
    cy.intercept('POST', '/api/auth/logout').as('logoutRequest');
    cy.intercept('POST', '/api/auth/refresh').as('refreshRequest');
    cy.intercept('GET', '/api/user/profile').as('profileRequest');

    // Clear cookies and localStorage before tests
    cy.clearCookies();
    cy.clearLocalStorage();

    // Visit the login page
    cy.visit('/login');
  });

  it('should register a new user', () => {
    // Click on register link
    cy.get('[data-cy=register-link]').click();

    // Verify we're on the register page
    cy.url().should('include', '/register');

    // Fill out registration form
    cy.get('[data-cy=register-name]').type(testUser.name);
    cy.get('[data-cy=register-email]').type(testUser.email);
    cy.get('[data-cy=register-password]').type(testUser.password);
    cy.get('[data-cy=register-confirm-password]').type(testUser.password);

    // Submit the form
    cy.get('[data-cy=register-submit]').click();

    // Wait for registration request to complete
    cy.wait('@registerRequest').its('response.statusCode').should('eq', 201);

    // User should be redirected to the dashboard or welcome page
    cy.url().should('include', '/dashboard');

    // User should be logged in (profile menu should be visible)
    cy.get('[data-cy=user-profile-menu]').should('be.visible');
  });

  it('should handle registration errors', () => {
    // Click on register link
    cy.get('[data-cy=register-link]').click();

    // Try to register with invalid data

    // 1. Test email validation
    cy.get('[data-cy=register-name]').type('Test User');
    cy.get('[data-cy=register-email]').type('invalid-email');
    cy.get('[data-cy=register-password]').type('password123');
    cy.get('[data-cy=register-confirm-password]').type('password123');
    cy.get('[data-cy=register-submit]').click();

    // Should show email validation error
    cy.get('[data-cy=register-email-error]').should('be.visible');

    // 2. Test password validation
    cy.get('[data-cy=register-email]').clear().type('valid@example.com');
    cy.get('[data-cy=register-password]').clear().type('weak');
    cy.get('[data-cy=register-confirm-password]').clear().type('weak');
    cy.get('[data-cy=register-submit]').click();

    // Should show password validation error
    cy.get('[data-cy=register-password-error]').should('be.visible');

    // 3. Test password confirmation
    cy.get('[data-cy=register-password]').clear().type('StrongPassword123!');
    cy.get('[data-cy=register-confirm-password]')
      .clear()
      .type('DifferentPassword123!');
    cy.get('[data-cy=register-submit]').click();

    // Should show password mismatch error
    cy.get('[data-cy=register-confirm-password-error]').should('be.visible');
  });

  it('should login with valid credentials', () => {
    // First register the user if not already registered
    cy.request({
      method: 'POST',
      url: '/api/auth/register',
      body: testUser,
      failOnStatusCode: false,
    }).then((response) => {
      // Either user was created or already exists

      // Fill in login form
      cy.get('[data-cy=login-email]').type(testUser.email);
      cy.get('[data-cy=login-password]').type(testUser.password);

      // Submit the form
      cy.get('[data-cy=login-submit]').click();

      // Wait for login request to complete
      cy.wait('@loginRequest').its('response.statusCode').should('eq', 200);

      // User should be redirected to the dashboard
      cy.url().should('include', '/dashboard');

      // User should be logged in
      cy.get('[data-cy=user-profile-menu]').should('be.visible');

      // Local storage should contain auth token
      cy.window().then((window) => {
        const authToken = window.localStorage.getItem('auth_token');
        expect(authToken).to.not.be.null;
      });
    });
  });

  it('should handle invalid login credentials', () => {
    // Try to login with wrong password
    cy.get('[data-cy=login-email]').type(testUser.email);
    cy.get('[data-cy=login-password]').type('WrongPassword123!');
    cy.get('[data-cy=login-submit]').click();

    // Wait for login request to complete
    cy.wait('@loginRequest').its('response.statusCode').should('eq', 401);

    // Should show error message
    cy.get('[data-cy=login-error]').should('be.visible');

    // User should still be on login page
    cy.url().should('include', '/login');
  });

  it('should access protected resources when authenticated', () => {
    // Login the user
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: {
        email: testUser.email,
        password: testUser.password,
      },
    }).then((response) => {
      // Set the auth token in localStorage
      const token = response.body.access_token;
      window.localStorage.setItem('auth_token', token);

      // Visit a protected page
      cy.visit('/dashboard');

      // Wait for profile request to complete
      cy.wait('@profileRequest').its('response.statusCode').should('eq', 200);

      // User should see their profile info
      cy.get('[data-cy=user-greeting]').should('contain', testUser.name);

      // User should be able to access other protected resources
      cy.get('[data-cy=documents-link]').click();
      cy.url().should('include', '/documents');
    });
  });

  it('should logout successfully', () => {
    // Login the user
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: {
        email: testUser.email,
        password: testUser.password,
      },
    }).then((response) => {
      // Set the auth token in localStorage
      const token = response.body.access_token;
      window.localStorage.setItem('auth_token', token);

      // Visit the dashboard
      cy.visit('/dashboard');

      // Click logout button
      cy.get('[data-cy=user-profile-menu]').click();
      cy.get('[data-cy=logout-button]').click();

      // Wait for logout request to complete
      cy.wait('@logoutRequest').its('response.statusCode').should('eq', 200);

      // User should be redirected to login page
      cy.url().should('include', '/login');

      // Auth token should be removed from localStorage
      cy.window().then((window) => {
        const authToken = window.localStorage.getItem('auth_token');
        expect(authToken).to.be.null;
      });
    });
  });

  it('should handle token refresh when expired', () => {
    // Login the user
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: {
        email: testUser.email,
        password: testUser.password,
      },
    }).then((response) => {
      // Set an expired token in localStorage
      window.localStorage.setItem('auth_token', 'expired.token');
      window.localStorage.setItem('refresh_token', response.body.refresh_token);

      // Mock token validation failure followed by successful refresh
      cy.intercept('GET', '/api/user/profile', (req) => {
        // Check if the request has the expired token
        if (req.headers.authorization?.includes('expired.token')) {
          req.reply({
            statusCode: 401,
            body: { error: 'Token expired' },
          });
        } else {
          // For refreshed token, allow the request to proceed
          req.reply({
            statusCode: 200,
            body: {
              id: 'user-123',
              name: testUser.name,
              email: testUser.email,
            },
          });
        }
      }).as('profileRequestWithExpiredToken');

      // Mock token refresh response
      cy.intercept('POST', '/api/auth/refresh', {
        statusCode: 200,
        body: {
          access_token: 'new.valid.token',
          refresh_token: 'new.refresh.token',
        },
      }).as('tokenRefresh');

      // Visit dashboard which should trigger a refresh due to 401
      cy.visit('/dashboard');

      // Should attempt to refresh the token
      cy.wait('@tokenRefresh');

      // Should update the token in localStorage
      cy.window().then((window) => {
        const authToken = window.localStorage.getItem('auth_token');
        expect(authToken).to.equal('new.valid.token');
      });

      // Should successfully load the dashboard after refresh
      cy.url().should('include', '/dashboard');
      cy.get('[data-cy=user-profile-menu]').should('be.visible');
    });
  });

  it('should maintain login state across page refreshes', () => {
    // Login the user
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: {
        email: testUser.email,
        password: testUser.password,
      },
    }).then((response) => {
      // Set the auth token in localStorage
      const token = response.body.access_token;
      window.localStorage.setItem('auth_token', token);

      // Visit dashboard
      cy.visit('/dashboard');

      // User should be logged in
      cy.get('[data-cy=user-profile-menu]').should('be.visible');

      // Refresh the page
      cy.reload();

      // User should still be logged in
      cy.get('[data-cy=user-profile-menu]').should('be.visible');

      // User should still have access to protected resources
      cy.get('[data-cy=documents-link]').click();
      cy.url().should('include', '/documents');
    });
  });

  it('should redirect to login when accessing protected routes without auth', () => {
    // Clear any tokens from localStorage
    cy.clearLocalStorage();

    // Try to access dashboard without being logged in
    cy.visit('/dashboard');

    // Should be redirected to login page
    cy.url().should('include', '/login');

    // Should show an error or info message
    cy.get('[data-cy=auth-required-message]').should('be.visible');
  });
});
