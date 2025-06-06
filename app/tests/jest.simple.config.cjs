// Simple Jest configuration without complex setup
module.exports = {
  testEnvironment: 'node',
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
  },
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '^@/(.*)$': '<rootDir>/src/$1',
    '^api$': '<rootDir>/api.js',
  },
  transformIgnorePatterns: [
    '/node_modules/(?!.*\\.(js|jsx|ts|tsx|mjs)$)'
  ],
  testPathIgnorePatterns: ['/node_modules/', '/dist/', '/archive/'],
  testMatch: ['**/src/tests/auto/simple.test.js'],
  moduleFileExtensions: ['js', 'jsx', 'cjs'],
};
