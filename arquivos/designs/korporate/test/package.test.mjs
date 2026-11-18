import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

test('tokens expose usable presentation roles and motion controls', async () => {
  const css = await readFile(new URL('../tokens.css', import.meta.url), 'utf8');

  for (const token of [
    '--kp-fg',
    '--kp-bg',
    '--kp-brand',
    '--kp-data-positive',
    '--kp-data-alert',
    '--kp-motion-base',
  ]) {
    assert.match(css, new RegExp(`${token}:`));
  }
});

test('asset provenance identifies official Korporate source', async () => {
  const provenance = await readFile(
    new URL('../assets/README.md', import.meta.url),
    'utf8',
  );

  assert.match(provenance, /drive\.google\.com/);
  assert.match(provenance, /Manual de Marca - Korporate/i);
});

test('component layer exposes reusable presentation primitives', async () => {
  const css = await readFile(new URL('../components.css', import.meta.url), 'utf8');

  for (const component of [
    '.kp-slide',
    '.kp-card',
    '.kp-kicker',
    '.kp-metric',
    '.kp-status',
    '.kp-flow',
    '.kp-code',
  ]) {
    assert.match(css, new RegExp(`\\${component}`));
  }
});

test('rationale records safe visual use and accessibility', async () => {
  const rationale = await readFile(
    new URL('../design-rationale.md', import.meta.url),
    'utf8',
  );

  for (const heading of [
    'Papéis de cor',
    'Hierarquia tipográfica',
    'Uso da marca',
    'Faça',
    'Não faça',
    'Acessibilidade',
  ]) {
    assert.match(rationale, new RegExp(heading, 'i'));
  }
});
