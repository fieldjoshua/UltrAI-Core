# AUTO Selection Feature Tests

This directory contains automated tests for the AUTO selection feature in UltrAI.

## What is tested?

1. **AUTO Button Functionality**

   - Tests that clicking the AUTO button selects the recommended models
   - Verifies that the curtain effect is applied to show steps 3-5 have been handled
   - Confirms success message is displayed

2. **RANDOM Button Functionality**

   - Tests that clicking the RANDOM button selects random models
   - Verifies curtain effect and success message

3. **Reset Button Functionality**
   - Tests that clicking "Reset and Choose Manually" clears all AUTO selections
   - Verifies the curtain effect is removed
   - Confirms reset message is displayed

## How to run tests

To run these tests, use one of the following commands:

```bash
# Run all tests
npm test

# Run just the AUTO selection tests
npm run test:auto

# Run tests in watch mode (tests re-run when files change)
npm run test:watch
```

## Notes on the tests

These tests mock various DOM methods and React hooks to isolate the testing of the AUTO selection feature.
The actual API calls are not made during testing, and the UI rendering is simulated using React Testing Library.

### What to do if tests fail

If tests fail, check the following:

1. Has the structure or naming in `UltraWithDocuments.tsx` changed?
2. Have the AUTO/RANDOM button handlers changed?
3. Has the curtain effect implementation changed?

You may need to update the test selectors or expected values to match changes in the implementation.
