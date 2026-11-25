// Uso: node validar_planejamento.cjs planejamento.json index.html
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');

function readJson(path) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (error) {
    throw new Error(`Não foi possível ler planejamento: ${error.message}`);
  }
}

function slideIds(html) {
  return [...html.matchAll(/\bdata-slide-id\s*=\s*(["'])(.*?)\1/g)].map(match => match[2]);
}

function hasComponent(html, component) {
  if (!component.startsWith('.')) return false;
  const className = component.slice(1).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp(`\\bclass\\s*=\\s*(["'])[^"']*\\b${className}\\b[^"']*\\1`).test(html);
}

function validateSlide(slide, html) {
  assert.equal(typeof slide.id, 'string', 'Toda tela precisa de id textual.');
  assert(slide.id.trim(), 'Toda tela precisa de id não vazio.');
  assert(Array.isArray(slide.sources) && slide.sources.length, `${slide.id}: fonte obrigatória.`);
  for (const source of slide.sources) {
    assert(source && typeof source.document === 'string' && source.document.trim(), `${slide.id}: documento da fonte obrigatório.`);
    assert(source && typeof source.section === 'string' && source.section.trim(), `${slide.id}: seção da fonte obrigatória.`);
  }
  for (const field of ['message', 'composition', 'component', 'verticalUse']) {
    assert(typeof slide[field] === 'string' && slide[field].trim(), `${slide.id}: ${field} obrigatório.`);
  }
  for (const field of ['requiredContent', 'prohibitedContent']) {
    assert(Array.isArray(slide[field]) && slide[field].length, `${slide.id}: ${field} obrigatório.`);
  }
  assert(slide.image && ['específica', 'padrão', 'nenhuma'].includes(slide.image.decision),
    `${slide.id}: decisão de imagem inválida.`);
  assert(typeof slide.image.rationale === 'string' && slide.image.rationale.trim(),
    `${slide.id}: motivo da decisão de imagem obrigatório.`);
  assert(hasComponent(html, slide.component), `${slide.id}: componente ${slide.component} não existe no HTML.`);
}

function validate(plan, html) {
  assert.equal(plan.version, 1, 'Versão de planejamento incompatível.');
  assert(Array.isArray(plan.slides) && plan.slides.length, 'O planejamento precisa conter telas.');
  const ids = slideIds(html);
  assert(ids.length, 'O HTML precisa conter data-slide-id.');
  assert.equal(new Set(ids).size, ids.length, 'data-slide-id precisa ser exclusivo.');
  const planIds = plan.slides.map(slide => slide.id);
  assert.equal(new Set(planIds).size, planIds.length, 'IDs do planejamento precisam ser exclusivos.');
  assert.deepEqual(planIds, ids, 'Ordem e IDs do planejamento precisam corresponder ao HTML.');
  plan.slides.forEach(slide => validateSlide(slide, html));
}

function main() {
  const [planPath, indexPath] = process.argv.slice(2);
  if (!planPath || !indexPath) throw new Error('Informe planejamento.json e index.html.');
  const plan = readJson(resolve(planPath));
  const html = readFileSync(resolve(indexPath), 'utf8');
  validate(plan, html);
  console.log(`${plan.slides.length} telas: planejamento validado.`);
}

try {
  main();
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
