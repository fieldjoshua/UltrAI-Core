// Import jest-dom to extend Jest with DOM matchers
import '@testing-library/jest-dom';

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
class MockIntersectionObserver {
  constructor(callback) {
    this.callback = callback;
  }
  observe = jest.fn();
  unobserve = jest.fn();
  disconnect = jest.fn();
}
window.IntersectionObserver = MockIntersectionObserver;

// CSS animations and transitions
Object.defineProperty(window, 'getComputedStyle', {
  value: () => {
    return {
      animationDuration: '0s',
      transitionDuration: '0s',
      getPropertyValue: prop => {
        return '';
      }
    };
  }
});

// Mock document.createRange
document.createRange = () => {
  const range = new Range();
  range.getBoundingClientRect = jest.fn(() => ({
    x: 0,
    y: 0,
    width: 0,
    height: 0,
    top: 0,
    right: 0,
    bottom: 0,
    left: 0,
  }));
  range.getClientRects = jest.fn(() => []);
  range.selectNodeContents = jest.fn();
  return range;
};

// Console error override to make tests more readable
const originalConsoleError = console.error;
console.error = (...args) => {
  // Suppress specific errors that might come from libraries
  const suppressedErrors = [
    // Add specific error strings you want to suppress
    'Warning: ReactDOM.render is no longer supported',
    'Warning: useLayoutEffect does nothing on the server',
  ];
  
  const errorString = args.join(' ');
  if (!suppressedErrors.some(suppressed => errorString.includes(suppressed))) {
    originalConsoleError(...args);
  }
};

// Setup custom matchers
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