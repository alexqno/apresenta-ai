import assert from 'node:assert/strict';
import { access, readFile } from 'node:fs/promises';
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

test('asset package keeps official signature and isolated symbol', async () => {
  await access(new URL('../assets/korporate-signature-dark.png', import.meta.url));
  await access(new URL('../assets/korporate-symbol-orange.png', import.meta.url));
  const provenance = await readFile(new URL('../assets/README.md', import.meta.url), 'utf8');
  assert.match(provenance, /Marca 1\.png/);
  assert.match(provenance, /Marca 6\.png/);
  assert.doesNotMatch(provenance, /korporate-logo\.jpg/);
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

test('gallery demonstrates every required presentation pattern', async () => {
  const html = await readFile(new URL('../gallery.html', import.meta.url), 'utf8');

  for (const pattern of [
    'data-pattern="cover"',
    'data-pattern="chapter"',
    'data-pattern="content"',
    'data-pattern="data"',
    'data-pattern="ai-flow"',
    'data-pattern="closing"',
    'Sucesso',
    'Atenção',
    'name="viewport"',
    'name="description"',
  ]) {
    assert.match(html, new RegExp(pattern));
  }
});

test('gallery preserves understanding when motion is reduced', async () => {
  const css = await readFile(new URL('../gallery.css', import.meta.url), 'utf8');
  assert.match(css, /@media \(prefers-reduced-motion: reduce\)/);
});
