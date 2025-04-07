// Custom matchers for Jest

// Export a function that will set up custom matchers
function setupCustomMatchers() {
  expect.extend({
    toBeInRange(received, floor, ceiling) {
      const pass = received >= floor && received <= ceiling;
      if (pass) {
        return {
          message: () => `expected ${received} not to be within range ${floor} - ${ceiling}`,
          pass: true,
        };
      } else {
        return {
          message: () => `expected ${received} to be within range ${floor} - ${ceiling}`,
          pass: false,
        };
      }
    },
    toMatchResponse(received, expected) {
      // Basic check if response has expected structure
      const hasExpectedKeys = Object.keys(expected).every(key => 
        received.hasOwnProperty(key)
      );
      
      if (hasExpectedKeys) {
        return {
          message: () => `expected response not to match structure`,
          pass: true,
        };
      } else {
        return {
          message: () => `expected response to match structure, but it did not`,
          pass: false,
        };
      }
    }
  });
}

// Auto-setup when file is included
setupCustomMatchers();

// Export the setup function in case it needs to be called explicitly
export { setupCustomMatchers }; 