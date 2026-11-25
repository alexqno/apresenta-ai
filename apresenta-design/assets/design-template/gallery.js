(() => {
  const slides = [...document.querySelectorAll('[data-gallery-slide]')];
  const status = document.querySelector('[data-gallery-status]');
  let current = 0;
  const show = index => {
    current = Math.max(0, Math.min(slides.length - 1, index));
    slides.forEach((slide, position) => { slide.hidden = position !== current; });
    const active = slides[current];
    active.querySelector('[data-pagination]')?.replaceChildren(`${String(current + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`);
    if (status) status.textContent = `Exemplo ${current + 1} de ${slides.length}`;
    document.dispatchEvent(new Event('presentation-gallery-change'));
  };
  document.addEventListener('keydown', event => {
    if (event.target.closest('input,textarea,select,button,a[href]')) return;
    const actions = { ArrowRight: 1, PageDown: 1, ' ': 1, ArrowLeft: -1, PageUp: -1 };
    if (event.key in actions) { event.preventDefault(); show(current + actions[event.key]); }
    if (event.key === 'Home') { event.preventDefault(); show(0); }
    if (event.key === 'End') { event.preventDefault(); show(slides.length - 1); }
    if (/^f$/i.test(event.key)) document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen?.();
  });
  show(0);
})();
