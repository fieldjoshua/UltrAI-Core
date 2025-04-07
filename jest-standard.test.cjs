// Basic test using Jest's test function
const assert = require('assert');

// Using Jest's global test function
test('addition', () => {
  assert.strictEqual(1 + 1, 2);
});

test('subtraction', () => {
  assert.strictEqual(5 - 3, 2);
});

test('multiplication', () => {
  assert.strictEqual(2 * 3, 6);
});

test('division', () => {
  assert.strictEqual(10 / 2, 5);
}); 