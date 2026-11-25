// Uso: node montar_comparacao_visual.cjs referencia candidata comparacao.html
const { readFileSync, writeFileSync } = require('node:fs');
const { resolve, join, relative, dirname } = require('node:path');

function readManifest(directory) {
  return JSON.parse(readFileSync(join(resolve(directory), 'manifest.json'), 'utf8'));
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
}

function imagePath(reportPath, directory, file) {
  return relative(dirname(reportPath), join(resolve(directory), file)).split('\\').join('/');
}

function byViewport(manifest) {
  return new Map(manifest.captures.map(capture => [`${capture.width}x${capture.height}`, capture]));
}

function main() {
  const [referenceDirectory, candidateDirectory, reportPath] = process.argv.slice(2);
  if (!referenceDirectory || !candidateDirectory || !reportPath) {
    throw new Error('Informe pasta de referência, pasta candidata e arquivo HTML de saída.');
  }
  const output = resolve(reportPath);
  const reference = readManifest(referenceDirectory);
  const candidate = readManifest(candidateDirectory);
  const referenceViewports = byViewport(reference);
  const candidateViewports = byViewport(candidate);
  const viewportKeys = [...new Set([...referenceViewports.keys(), ...candidateViewports.keys()])];
  const blocks = viewportKeys.map(key => {
    const left = referenceViewports.get(key);
    const right = candidateViewports.get(key);
    const leftSlides = new Map((left?.slides || []).map(slide => [slide.id, slide]));
    const rightSlides = new Map((right?.slides || []).map(slide => [slide.id, slide]));
    const ids = [...new Set([...leftSlides.keys(), ...rightSlides.keys()])];
    const pairs = ids.map(id => {
      const before = leftSlides.get(id);
      const after = rightSlides.get(id);
      const image = (entry, directory, label) => entry
        ? `<figure><figcaption>${label}</figcaption><img src="${escapeHtml(imagePath(output, directory, entry.file))}" alt="${escapeHtml(label)} — ${escapeHtml(id)}"></figure>`
        : `<figure class="missing"><figcaption>${label}</figcaption><p>Captura ausente.</p></figure>`;
      return `<article><h3>${escapeHtml(id)}</h3><div class="pair">${image(before, referenceDirectory, 'Referência aprovada')}${image(after, candidateDirectory, 'Nova versão')}</div></article>`;
    }).join('\n');
    return `<section><h2>${escapeHtml(key.replace('x', '×'))}</h2>${pairs || '<p>Sem telas capturadas.</p>'}</section>`;
  }).join('\n');
  const html = `<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Comparação visual</title><style>
    :root { color-scheme: light; font-family: system-ui, sans-serif; color: #202124; background: #f5f5f5; }
    body { margin: 0 auto; max-width: 1500px; padding: 2rem; } section { margin-block: 3rem; } article { background: white; border: 1px solid #ddd; border-radius: 1rem; margin-block: 1.5rem; overflow: hidden; } h3 { margin: 0; padding: .8rem 1rem; } .pair { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; padding: 1rem; } figure { margin: 0; min-width: 0; } figcaption { font-weight: 700; margin-bottom: .5rem; } img { display: block; width: 100%; height: auto; border: 1px solid #ddd; } .missing { display: grid; place-items: center; min-height: 12rem; background: #fff4e5; } @media (max-width: 700px) { .pair { grid-template-columns: 1fr; } }
  </style><body><h1>Comparação visual</h1><p>Compare composição, escala, distribuição e legibilidade. Diferença visual exige revisão humana; este relatório não aprova conteúdo automaticamente.</p>${blocks}</body></html>`;
  writeFileSync(output, html);
  console.log(`Relatório salvo em ${output}.`);
}

try {
  main();
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
