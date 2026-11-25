import { startPresenter } from './apresentador.mjs';

async function loadManifest(path) {
  const response = await fetch(path, { cache: 'no-store' });
  if (!response.ok) throw new Error('Manifesto de participação indisponível.');
  return response.json();
}

export async function connectParticipation({ manifestUrl = './participacao.json' } = {}) {
  const stage = document.querySelector('.presentation-stage');
  const panel = document.querySelector('[data-entrada]');
  if (!stage || !panel) throw new Error('Palco ou entrada de participação ausente.');
  const slides = [...stage.querySelectorAll(':scope > [data-slide-id]')];
  const containers = slides.map(slide => slide.querySelector('[data-interacao]'));
  let currentIndex = Math.max(0, slides.findIndex(slide => !slide.hidden));
  const presenter = await startPresenter({ manifest: await loadManifest(manifestUrl), containers, panel,
    currentIndex: () => currentIndex, publishInitial: false });
  if (presenter.restoredSession && Number.isInteger(presenter.session.slideIndex)) {
    currentIndex = presenter.session.slideIndex;
    stage.dispatchEvent(new CustomEvent('presentationgoto', { detail: { index: currentIndex } }));
  }
  stage.addEventListener('slidechange', event => {
    currentIndex = event.detail.index;
    void presenter.publish(currentIndex);
  });
  await presenter.publish(currentIndex);
  return presenter;
}
