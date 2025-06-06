/// <reference types="cypress" />

describe('Document Management', () => {
    beforeEach(() => {
        // Stub the token to simulate being logged in
        cy.intercept('GET', '/api/user/profile', { fixture: 'user.json' });

        // Stub document list API
        cy.intercept('GET', '/api/documents', { fixture: 'documents.json' }).as('getDocuments');

        // Mock document upload API
        cy.intercept('POST', '/api/documents', (req) => {
            return req.reply({
                statusCode: 201,
                body: {
                    id: 'doc-new',
                    user_id: 'user-1',
                    filename: req.body.get('file').name,
                    content_type: req.body.get('file').type,
                    size_bytes: 12345,
                    created_at: new Date().toISOString(),
                    status: 'processing',
                    word_count: 0,
                    chunk_count: 0
                }
            });
        }).as('uploadDocument');

        // Mock document delete API
        cy.intercept('DELETE', '/api/documents/*', {
            statusCode: 200,
            body: { status: 'deleted' }
        }).as('deleteDocument');

        cy.visit('/documents');
        cy.wait('@getDocuments');
    });

    it('should display the document list', () => {
        cy.get('[data-cy=document-list]').should('be.visible');
        cy.get('[data-cy=document-item]').should('have.length', 3);

        // Check details of the first document
        cy.get('[data-cy=document-item]').first().within(() => {
            cy.get('[data-cy=document-name]').should('contain', 'test-document-1.pdf');
            cy.get('[data-cy=document-size]').should('contain', '125');
            cy.get('[data-cy=document-status]').should('contain', 'processed');
        });
    });

    it('should upload a new document', () => {
        // Create a test file
        cy.fixture('example.pdf', 'base64').then((fileContent) => {
            cy.get('[data-cy=upload-button]').click();

            // Convert the base64 string to a Blob
            const blob = Cypress.Blob.base64StringToBlob(fileContent, 'application/pdf');

            // Create a File object
            const testFile = new File([blob], 'example.pdf', { type: 'application/pdf' });

            // Attach the file
            cy.get('[data-cy=file-input]').attachFile({
                fileContent: blob,
                fileName: 'example.pdf',
                mimeType: 'application/pdf',
            });

            cy.get('[data-cy=submit-upload]').click();
            cy.wait('@uploadDocument');

            // Verify success message
            cy.get('[data-cy=toast]').should('contain', 'Document uploaded successfully');

            // Verify the document list is refreshed
            cy.get('@getDocuments.all').should('have.length', 2);
        });
    });

    it('should delete a document', () => {
        // Delete the first document
        cy.get('[data-cy=document-item]').first().within(() => {
            cy.get('[data-cy=delete-document]').click();
        });

        // Confirm deletion
        cy.get('[data-cy=confirm-delete]').click();
        cy.wait('@deleteDocument');

        // Verify success message
        cy.get('[data-cy=toast]').should('contain', 'Document deleted successfully');

        // Verify the document list is refreshed
        cy.get('@getDocuments.all').should('have.length', 2);
    });

    it('should sort the document list', () => {
        // Sort by name
        cy.get('[data-cy=sort-by-name]').click();
        cy.get('[data-cy=document-item]').first().find('[data-cy=document-name]')
            .should('contain', 'test-document-1.pdf');

        // Sort by name in reverse order
        cy.get('[data-cy=sort-by-name]').click();
        cy.get('[data-cy=document-item]').first().find('[data-cy=document-name]')
            .should('contain', 'test-document-3.docx');

        // Sort by date
        cy.get('[data-cy=sort-by-date]').click();
        cy.get('[data-cy=document-item]').first().find('[data-cy=document-name]')
            .should('contain', 'test-document-1.pdf');
    });

    it('should filter the document list', () => {
        // Filter by file type
        cy.get('[data-cy=filter-input]').type('pdf');
        cy.get('[data-cy=document-item]').should('have.length', 1);
        cy.get('[data-cy=document-item]').first().find('[data-cy=document-name]')
            .should('contain', 'test-document-1.pdf');

        // Clear filter
        cy.get('[data-cy=filter-input]').clear();
        cy.get('[data-cy=document-item]').should('have.length', 3);

        // Filter by status
        cy.get('[data-cy=filter-status]').select('processing');
        cy.get('[data-cy=document-item]').should('have.length', 1);
        cy.get('[data-cy=document-item]').first().find('[data-cy=document-name]')
            .should('contain', 'test-document-3.docx');
    });
});
