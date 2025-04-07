// Basic Jest test without any complex dependencies
const assert = require('assert');

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