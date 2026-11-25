import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { pollShares, sessionDefinitions } from '../assets/palco/interacoes.mjs';

test('maiores restos preservam 100% e resolvem empate por ID', () => {
  assert.deepEqual(pollShares({ c: 1, b: 1, a: 1 }), { a: 34, b: 33, c: 33 });
  assert.deepEqual(pollShares({ a: 0 }), { a: 0 });
});

test('manifesto de demonstração registra as quatro interações por índice', () => {
  const manifest = JSON.parse(readFileSync(new URL('../assets/galeria-interacoes/participacao.json', import.meta.url)));
  const definitions = sessionDefinitions(manifest.slides);
  assert.deepEqual(definitions.polls.prioridade, { slideIndex: 0, options: ['prazo', 'custo', 'qualidade'] });
  assert.deepEqual(definitions.diagnostics.atencao, { slideIndex: 1, items: ['agenda', 'materiais', 'espaco'], maxSelections: 2 });
  assert.deepEqual(definitions.triages.atividades, { slideIndex: 2, items: ['convite', 'registro'], categories: ['antes', 'durante'] });
  assert.deepEqual(definitions.postits.ideias, { slideIndex: 3, maxLength: 180 });
});

test('adaptador replica QR puro nas telas interativas', () => {
  const source = readFileSync(new URL('../assets/palco/apresentador.mjs', import.meta.url), 'utf8');
  assert.match(source, /hasInteraction/);
  assert.match(source, /ai-interaction-qr/);
  assert.match(source, /QR code para acompanhar pelo celular/);
});

test('bootstrap conecta palco-base sem acessar índice privado', () => {
  const source = readFileSync(new URL('../assets/palco/bootstrap.mjs', import.meta.url), 'utf8');
  const stage = readFileSync(new URL('../../apresenta-ai/assets/palco-base/palco.js', import.meta.url), 'utf8');
  assert.match(source, /connectParticipation/);
  assert.match(source, /slidechange/);
  assert.match(source, /presentationgoto/);
  assert.match(source, /currentIndex = presenter\.session\.slideIndex/);
  assert.match(stage, /presentationgoto/);
});

test('circuito monta quando o palco emite troca de tela', () => {
  const source = readFileSync(new URL('../../apresenta-design/assets/design-template/circuit.js', import.meta.url), 'utf8');
  assert.match(source, /document\.addEventListener\('slidechange', enhance\)/);
  assert.doesNotMatch(source, /aria-hidden': 'true'/);
});

test('triagem preserva semáforos e selo após revelar referência', () => {
  const source = readFileSync(new URL('../assets/palco/interacoes.mjs', import.meta.url), 'utf8');
  assert.match(source, /ai-triage-signals/);
  assert.match(source, /Classificação correta/);
  assert.match(source, /Rever classificação/);
});
