export function clampIndex(index, count) {
  return Math.max(0, Math.min(index, count - 1));
}

function isEditable(target) {
  return target?.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(target?.tagName);
}

export function keyToAction(event) {
  if (isEditable(event.target)) return null;
  if (event.key === 'ArrowRight' || event.key === ' ') return 'next';
  if (event.key === 'ArrowLeft') return 'previous';
  if (event.key === 'Home') return 'first';
  if (event.key === 'End') return 'last';
  if (event.key.toLowerCase() === 'f') return 'fullscreen';
  return null;
}

export function createGalleryController({ slides, counter, status, root = document }) {
  let activeIndex = 0;
  const render = () => {
    slides.forEach((slide, index) => {
      const active = index === activeIndex;
      slide.hidden = !active;
      slide.setAttribute('aria-hidden', String(!active));
    });
    if (counter) counter.textContent = `${activeIndex + 1} / ${slides.length}`;
    status.textContent = `Padrão ${activeIndex + 1} de ${slides.length}`;
  };
  const move = (action) => {
    if (action === 'next') activeIndex = clampIndex(activeIndex + 1, slides.length);
    if (action === 'previous') activeIndex = clampIndex(activeIndex - 1, slides.length);
    if (action === 'first') activeIndex = 0;
    if (action === 'last') activeIndex = slides.length - 1;
    render();
  };
  const fullscreen = async () => {
    if (root.fullscreenElement) await root.exitFullscreen();
    else await root.documentElement.requestFullscreen();
  };
  return { move, fullscreen, render };
}

if (typeof document !== 'undefined') {
  const slides = [...document.querySelectorAll('[data-slide]')];
  const controller = createGalleryController({
    slides,
    counter: document.querySelector('#slide-counter'),
    status: document.querySelector('#gallery-status'),
  });
  document.addEventListener('keydown', (event) => {
    const action = keyToAction(event);
    if (!action) return;
    event.preventDefault();
    if (action === 'fullscreen') controller.fullscreen(); else controller.move(action);
  });
  controller.render();
}
