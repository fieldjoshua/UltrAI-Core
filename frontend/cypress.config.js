const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    // This setupNodeEvents function is required for Cypress to run.
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
    // Point Cypress to the correct spec file.
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    baseUrl: 'http://localhost:3000' // Assuming the frontend runs on port 3000
  },
});