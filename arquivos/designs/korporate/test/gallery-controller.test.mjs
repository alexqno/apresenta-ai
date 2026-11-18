import assert from 'node:assert/strict';
import test from 'node:test';
import { clampIndex, keyToAction } from '../gallery.js';

test('clampIndex keeps navigation inside gallery boundaries', () => {
  assert.equal(clampIndex(-1, 8), 0);
  assert.equal(clampIndex(8, 8), 7);
});

test('keyToAction maps gallery navigation keys', () => {
  assert.equal(keyToAction({ key: 'ArrowRight', target: {} }), 'next');
  assert.equal(keyToAction({ key: ' ', target: {} }), 'next');
  assert.equal(keyToAction({ key: 'ArrowLeft', target: {} }), 'previous');
  assert.equal(keyToAction({ key: 'Home', target: {} }), 'first');
  assert.equal(keyToAction({ key: 'End', target: {} }), 'last');
});

test('keyToAction protects editable controls from slide navigation', () => {
  for (const tagName of ['INPUT', 'TEXTAREA', 'SELECT']) {
    assert.equal(keyToAction({ key: 'ArrowRight', target: { tagName } }), null);
  }
  assert.equal(keyToAction({ key: 'ArrowRight', target: { isContentEditable: true } }), null);
});
