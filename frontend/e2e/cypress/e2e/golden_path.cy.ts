/// <reference types="cypress" />

describe('Golden Path E2E Test', () => {
  beforeEach(() => {
    // For this test, we will assume a logged-in state.
    // A robust login flow would be in its own test.
    // We can use a session cookie or token to simulate this.
    cy.visit('/'); // Visit the root of the application
  });

  it('successfully completes a full analysis from the Wizard', () => {
    // Phase 1: Setup and Query Input
    cy.get('button').contains('START ULTRAI!', { matchCase: false }).click();
    
    // It's better to use data-cy attributes for selectors, but we'll use classes/ids for now.
    cy.get('textarea[placeholder*="your query"]').should('be.visible').type('Analyze the impact of AI on the future of software development.');
    cy.get('button').contains('Next', { matchCase: false }).click();

    // Phase 2: Model Selection
    // Wait for models to be available and select one from each of the Big 3.
    // Note: These selectors are based on the likely structure and may need adjustment.
    cy.contains('gpt-4o', { timeout: 10000 }).should('be.visible').click();
    cy.contains('claude-3-5-sonnet-20241022', { timeout: 10000 }).should('be.visible').click();
    cy.contains('gemini-1.5-pro', { timeout: 10000 }).should('be.visible').click();
    cy.get('button').contains('Next', { matchCase: false }).click();
    
    // Phase 3: Approval and Status Monitoring
    // Approve the final cost/summary screen
    cy.get('button').contains('Approve & Run', { matchCase: false }).click();

    // Now we should be on the status screen.
    // Verify that the status updater component is visible.
    cy.contains('Initializing Analysis', { timeout: 15000 }).should('be.visible');

    // Verify key stages of the SSE stream appear in the UI.
    // This confirms the frontend is receiving and displaying stream events.
    cy.contains('Generating Initial Responses', { timeout: 20000 }).should('be.visible');
    cy.contains('Peer Review & Revision', { timeout: 30000 }).should('be.visible');
    cy.contains('Ultra Synthesis', { timeout: 45000 }).should('be.visible');

    // Phase 4: Final Result Verification
    // Wait for the "View Full Results" button to appear, indicating completion.
    cy.contains('button', 'View Full Results', { timeout: 60000 }).should('be.visible').click();

    // Verify that we are now on the results page and that a synthesis is displayed.
    // A more robust check would look for specific content or structure.
    cy.get('.synthesis-output-container').should('not.be.empty');
    cy.contains('Analysis Complete').should('be.visible');
  });
});