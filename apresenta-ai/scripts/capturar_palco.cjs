// Uso: node capturar_palco.cjs caminho/para/index.html pasta-de-saida
const assert = require('node:assert/strict');
const { mkdirSync, writeFileSync } = require('node:fs');
const { resolve, join } = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright');

const VIEWPORTS = [[1366, 768], [1920, 1080]];

function fileName(index, id) {
  const safeId = id.replace(/[^a-z0-9_-]+/gi, '-').replace(/^-+|-+$/g, '') || 'tela';
  return `${String(index + 1).padStart(2, '0')}-${safeId}.png`;
}

async function capture(indexPath, outputPath) {
  const absoluteIndex = resolve(indexPath);
  const absoluteOutput = resolve(outputPath);
  mkdirSync(absoluteOutput, { recursive: true });
  const browser = await chromium.launch(process.env.CHROME_PATH
    ? { executablePath: process.env.CHROME_PATH } : {});
  try {
    const page = await browser.newPage({ reducedMotion: 'reduce' });
    const captures = [];
    for (const [width, height] of VIEWPORTS) {
      await page.setViewportSize({ width, height });
      await page.goto(pathToFileURL(absoluteIndex).href);
      await page.evaluate(() => document.fonts.ready.then(() => true));
      const baseStage = page.locator('.presentation-stage');
      const usesBaseContract = await baseStage.count() === 1;
      const stage = usesBaseContract ? baseStage : page.locator('#presentation');
      await assert.equal(await stage.count(), 1,
        'A apresentação precisa de .presentation-stage ou #presentation.');
      const slides = stage.locator(usesBaseContract ? ':scope > [data-slide-id]' : ':scope > [data-slide]');
      const ids = await slides.evaluateAll(nodes => nodes.map(node => node.dataset.slideId || node.dataset.slide));
      assert(ids.length && ids.every(Boolean), 'O palco precisa de data-slide-id ou data-slide.');
      const directory = `${width}x${height}`;
      mkdirSync(join(absoluteOutput, directory), { recursive: true });
      await page.keyboard.press('Home');
      const files = [];
      for (let index = 0; index < ids.length; index++) {
        const file = join(directory, fileName(index, ids[index]));
        await stage.screenshot({ path: join(absoluteOutput, file) });
        files.push({ id: ids[index], file });
        if (index < ids.length - 1) await page.keyboard.press('ArrowRight');
      }
      captures.push({ width, height, slides: files });
    }
    writeFileSync(join(absoluteOutput, 'manifest.json'), JSON.stringify({
      version: 1,
      source: absoluteIndex,
      captures
    }, null, 2) + '\n');
    console.log(`Capturas salvas em ${absoluteOutput}.`);
  } finally {
    await browser.close();
  }
}

const [indexPath, outputPath] = process.argv.slice(2);
if (!indexPath || !outputPath) {
  console.error('Informe index.html e pasta de saída.');
  process.exitCode = 1;
} else {
  capture(indexPath, outputPath).catch(error => { console.error(error.message); process.exitCode = 1; });
}
