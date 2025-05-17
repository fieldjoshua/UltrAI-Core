// Basic test using Node's assert module
const assert = require('assert');

// Simple test runner
function test(name, fn) {
  try {
    fn();
    console.log(`✓ ${name}`);
  } catch (error) {
    console.error(`✗ ${name}`);
    console.error(error);
    process.exitCode = 1;
  }
}

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
