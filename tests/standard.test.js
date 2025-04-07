// Basic test using Node's test module instead of Jest
const assert = require('node:assert');
const test = require('node:test');

test('basic arithmetic operations', async (t) => {
  await t.test('addition', () => {
    assert.strictEqual(1 + 1, 2);
  });
  
  await t.test('subtraction', () => {
    assert.strictEqual(5 - 3, 2);
  });
  
  await t.test('multiplication', () => {
    assert.strictEqual(2 * 3, 6);
  });
  
  await t.test('division', () => {
    assert.strictEqual(10 / 2, 5);
  });
}); 