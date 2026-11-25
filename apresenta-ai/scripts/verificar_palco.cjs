// Uso: node verificar_palco.cjs caminho/para/index.html (Node + Playwright/Chromium).
const assert = require('node:assert/strict');
const { resolve } = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright');

async function verificar(arquivo) {
  const browser = await chromium.launch(process.env.CHROME_PATH
    ? { executablePath: process.env.CHROME_PATH } : {});
  try {
    const page = await browser.newPage({ reducedMotion: 'reduce' });
    const url = pathToFileURL(resolve(arquivo)).href;
    for (const [width, height] of [[1366, 768], [1920, 1080], [1280, 900]]) {
      await page.setViewportSize({ width, height });
      await page.goto(url);
      await page.evaluate(() => document.fonts.ready.then(() => true));
      const slides = page.locator('.presentation-stage > [data-slide-id]');
      const ids = await slides.evaluateAll(nodes => nodes.map(node => node.dataset.slideId));
      assert(ids.length && ids.every(Boolean) && new Set(ids).size === ids.length,
        'O palco precisa de identificadores de tela exclusivos.');
      const ativo = page.locator('.presentation-stage > [data-slide-id]:visible');
      await page.keyboard.press('Home');
      for (let index = 0; index < ids.length; index++) {
        const slide = ids[index];
        const contexto = `${width}×${height}, ${slide}`;
        assert.equal(await ativo.count(), 1, contexto);
        assert.equal(await ativo.getAttribute('data-slide-id'), slide, contexto);
        const metrics = await ativo.evaluate(element => {
          const box = element.parentElement.getBoundingClientRect();
          const rect = element.getBoundingClientRect();
          const footer = element.parentElement.querySelector('.presentation-footer')?.getBoundingClientRect();
          const children = [...element.querySelectorAll('*')].map(node => node.getBoundingClientRect())
            .filter(child => child.width && child.height);
          const readable = [...element.querySelectorAll('h1,h2,h3,h4,p,li,dt,dd,blockquote,[data-footer-content]')]
            .map(node => node.getBoundingClientRect()).filter(child => child.width && child.height);
          return {
            centered: Math.abs(box.x * 2 + box.width - innerWidth) <= 2 &&
              Math.abs(box.y * 2 + box.height - innerHeight) <= 2,
            ratio: box.width / box.height,
            fits: children.every(child => child.left >= rect.left - 1 && child.top >= rect.top - 1 &&
              child.right <= rect.right + 1 && child.bottom <= rect.bottom + 1),
            footerFits: !footer || (footer.left >= box.left && footer.right <= box.right + 1 &&
              footer.top >= box.top && footer.bottom <= box.bottom + 1),
            footerClear: !footer || readable.every(child => child.right <= footer.left || child.left >= footer.right ||
              child.bottom <= footer.top || child.top >= footer.bottom)
          };
        });
        assert(metrics.centered && Math.abs(metrics.ratio - 16 / 9) < .01, 'Palco descentralizado ou fora de 16:9 em ' + contexto);
        assert(metrics.fits && metrics.footerFits && metrics.footerClear,
          'Conteúdo fora do palco ou texto sobreposto ao rodapé em ' + contexto);
        const paginacao = page.locator('[data-pagination]');
        if (await paginacao.count()) {
          const expected = [index + 1, ids.length].map(n => String(n).padStart(2, '0')).join(' / ');
          assert.equal(await paginacao.innerText(), expected, contexto);
        }
        if (index < ids.length - 1) await page.keyboard.press('ArrowRight');
      }
      await page.keyboard.press('Home');
      assert.equal(await ativo.getAttribute('data-slide-id'), ids[0]);
      await page.keyboard.press('End');
      assert.equal(await ativo.getAttribute('data-slide-id'), ids.at(-1));
      await page.keyboard.press('PageUp');
      assert.equal(await ativo.getAttribute('data-slide-id'), ids.at(-2) || ids[0]);
      console.log(`${width}×${height}: ${ids.length} telas verificadas.`);
    }
  } finally {
    await browser.close();
  }
}

if (!process.argv[2]) {
  console.error('Informe o caminho para o index.html da apresentação.');
  process.exitCode = 1;
} else {
  verificar(process.argv[2]).catch(error => { console.error(error.message); process.exitCode = 1; });
}
