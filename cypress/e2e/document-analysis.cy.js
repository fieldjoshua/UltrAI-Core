/// <reference types="cypress" />

describe('Document Analysis', () => {
    beforeEach(() => {
        // Stub the token to simulate being logged in
        cy.intercept('GET', '/api/user/profile', { fixture: 'user.json' });

        // Stub document API
        cy.intercept('GET', '/api/documents/doc-1', {
            fixture: 'documents.json',
            body: {
                id: 'doc-1',
                user_id: 'user-1',
                filename: 'test-document-1.pdf',
                content_type: 'application/pdf',
                size_bytes: 125000,
                created_at: '2024-04-12T14:30:00Z',
                status: 'processed',
                word_count: 1250,
                chunk_count: 5,
                embedding_model: 'text-embedding-3-small'
            }
        }).as('getDocument');

        // Stub analyses list API
        cy.intercept('GET', '/api/documents/doc-1/analyses', { fixture: 'analyses.json' }).as('getAnalyses');

        // Mock analysis creation API
        cy.intercept('POST', '/api/analyze', (req) => {
            return req.reply({
                statusCode: 202,
                body: {
                    id: 'analysis-new',
                    user_id: 'user-1',
                    document_id: 'doc-1',
                    pattern: req.body.pattern,
                    prompt: req.body.prompt,
                    models: req.body.models || ['gpt-4-turbo'],
                    status: 'pending',
                    created_at: new Date().toISOString(),
                    completed_at: null,
                    result: null,
                    error: null,
                    options: req.body.options || {}
                }
            });
        }).as('createAnalysis');

        // Mock analysis status polling API
        cy.intercept('GET', '/api/analyses/analysis-new', (req) => {
            return req.reply({
                statusCode: 200,
                body: {
                    id: 'analysis-new',
                    user_id: 'user-1',
                    document_id: 'doc-1',
                    pattern: 'summarize',
                    prompt: 'Summarize this document',
                    models: ['gpt-4-turbo'],
                    status: 'completed',
                    created_at: new Date(Date.now() - 120000).toISOString(),
                    completed_at: new Date().toISOString(),
                    result: {
                        summary: 'This is a test summary generated during the test.'
                    },
                    error: null,
                    options: { max_tokens: 500 }
                }
            });
        }).as('getAnalysisStatus');

        cy.visit('/documents/doc-1');
        cy.wait(['@getDocument', '@getAnalyses']);
    });

    it('should display document details', () => {
        cy.get('[data-cy=document-title]').should('contain', 'test-document-1.pdf');
        cy.get('[data-cy=document-status]').should('contain', 'processed');
        cy.get('[data-cy=document-size]').should('contain', '125');
        cy.get('[data-cy=document-word-count]').should('contain', '1250');
        cy.get('[data-cy=document-chunk-count]').should('contain', '5');
    });

    it('should display previous analyses', () => {
        cy.get('[data-cy=analyses-list]').should('be.visible');
        cy.get('[data-cy=analysis-item]').should('have.length', 2);

        // Check first analysis
        cy.get('[data-cy=analysis-item]').first().within(() => {
            cy.get('[data-cy=analysis-pattern]').should('contain', 'summarize');
            cy.get('[data-cy=analysis-prompt]').should('contain', 'Summarize the key points');
            cy.get('[data-cy=analysis-status]').should('contain', 'completed');
            cy.get('[data-cy=analysis-date]').should('be.visible');
        });
    });

    it('should create a new analysis', () => {
        // Open the analysis form
        cy.get('[data-cy=new-analysis-button]').click();

        // Fill in the form
        cy.get('[data-cy=pattern-select]').select('summarize');
        cy.get('[data-cy=prompt-input]').type('Summarize this document');
        cy.get('[data-cy=model-select]').select('gpt-4-turbo');

        // Submit the form
        cy.get('[data-cy=submit-analysis]').click();
        cy.wait('@createAnalysis');

        // Verify success message
        cy.get('[data-cy=toast]').should('contain', 'Analysis started');

        // Wait for analysis to complete
        cy.wait('@getAnalysisStatus');

        // Check that analysis results are displayed
        cy.get('[data-cy=analysis-result]').should('be.visible');
        cy.get('[data-cy=analysis-summary]').should('contain', 'This is a test summary');
    });

    it('should handle analysis errors', () => {
        // Override the analysis status response to simulate an error
        cy.intercept('GET', '/api/analyses/analysis-new', {
            statusCode: 200,
            body: {
                id: 'analysis-new',
                user_id: 'user-1',
                document_id: 'doc-1',
                pattern: 'summarize',
                prompt: 'Summarize this document',
                models: ['gpt-4-turbo'],
                status: 'failed',
                created_at: new Date(Date.now() - 60000).toISOString(),
                completed_at: new Date().toISOString(),
                result: null,
                error: 'Model service unavailable',
                options: { max_tokens: 500 }
            }
        }).as('getFailedAnalysisStatus');

        // Open the analysis form
        cy.get('[data-cy=new-analysis-button]').click();

        // Fill in the form
        cy.get('[data-cy=pattern-select]').select('summarize');
        cy.get('[data-cy=prompt-input]').type('Summarize this document');

        // Submit the form
        cy.get('[data-cy=submit-analysis]').click();
        cy.wait('@createAnalysis');

        // Wait for failed analysis status
        cy.wait('@getFailedAnalysisStatus');

        // Check that error is displayed
        cy.get('[data-cy=analysis-error]').should('be.visible');
        cy.get('[data-cy=error-message]').should('contain', 'Model service unavailable');

        // Check retry button
        cy.get('[data-cy=retry-analysis]').should('be.visible');
    });

    it('should allow setting advanced options', () => {
        // Open the analysis form
        cy.get('[data-cy=new-analysis-button]').click();

        // Open advanced options
        cy.get('[data-cy=advanced-options-toggle]').click();

        // Set advanced options
        cy.get('[data-cy=max-tokens-input]').clear().type('1000');
        cy.get('[data-cy=temperature-input]').clear().type('0.7');

        // Fill in the main form
        cy.get('[data-cy=pattern-select]').select('summarize');
        cy.get('[data-cy=prompt-input]').type('Summarize this document');

        // Submit the form
        cy.get('[data-cy=submit-analysis]').click();

        // Check that the request includes the advanced options
        cy.get('@createAnalysis.all').then((interceptions) => {
            const request = interceptions[0].request;
            expect(request.body.options).to.have.property('max_tokens', 1000);
            expect(request.body.options).to.have.property('temperature', 0.7);
        });
    });
});