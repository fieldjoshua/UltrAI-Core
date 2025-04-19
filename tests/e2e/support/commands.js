// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

import '@testing-library/cypress/add-commands';
import 'cypress-file-upload';

// Login command to simplify authentication in tests
Cypress.Commands.add('login', (email = 'test@example.com', password = 'password') => {
    cy.session([email, password], () => {
        cy.visit('/login');
        cy.get('[data-cy=email-input]').type(email);
        cy.get('[data-cy=password-input]').type(password);
        cy.get('[data-cy=login-button]').click();

        // Wait for redirect or check for successful login state
        cy.url().should('not.include', '/login');
    });
});

// Upload a document
Cypress.Commands.add('uploadDocument', (filePath, fileName) => {
    cy.get('[data-cy=document-upload-input]').attachFile({
        filePath: filePath,
        fileName: fileName,
    });
});

// Check for toast notification
Cypress.Commands.add('checkToast', (message) => {
    cy.get('[data-cy=toast]').should('be.visible').and('contain', message);
});

// Run analysis on a document
Cypress.Commands.add('runAnalysis', (documentId, pattern, prompt) => {
    cy.visit(`/documents/${documentId}`);
    cy.get('[data-cy=pattern-select]').select(pattern);
    cy.get('[data-cy=prompt-input]').type(prompt);
    cy.get('[data-cy=run-analysis-button]').click();
});