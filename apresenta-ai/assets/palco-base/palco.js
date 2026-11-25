(() => {
  const stage = document.querySelector('.presentation-stage');
  const slides = [...stage.querySelectorAll(':scope > [data-slide-id]')];
  if (!slides.length) return;
  const pagination = stage.querySelector('[data-pagination]');
  let current = -1;
  let screenWakeLock = null;
  let wakeLockRequest = 0;

  async function releaseScreenWakeLock() {
    wakeLockRequest++;
    const wakeLock = screenWakeLock;
    screenWakeLock = null;
    if (wakeLock) await wakeLock.release();
  }

  async function syncScreenWakeLock() {
    const shouldKeepScreenAwake = Boolean(document.fullscreenElement) && document.visibilityState === 'visible';
    if (!shouldKeepScreenAwake) {
      await releaseScreenWakeLock();
      return;
    }
    if (!navigator.wakeLock?.request || screenWakeLock) return;
    const request = ++wakeLockRequest;
    try {
      const wakeLock = await navigator.wakeLock.request('screen');
      if (request !== wakeLockRequest || !document.fullscreenElement || document.visibilityState !== 'visible') {
        await wakeLock.release();
        return;
      }
      screenWakeLock = wakeLock;
      screenWakeLock.addEventListener('release', () => {
        screenWakeLock = null;
        if (document.fullscreenElement && document.visibilityState === 'visible') void syncScreenWakeLock();
      }, { once: true });
    } catch {
      // Wake Lock pode exigir contexto seguro ou ser bloqueado pelo navegador.
    }
  }

  function show(index) {
    const next = Math.max(0, Math.min(slides.length - 1, index));
    if (next === current) return;
    const previous = current;
    slides.forEach((slide, position) => { slide.hidden = position !== next; });
    if (previous >= 0) slides[next].dataset.entry = next > previous ? 'forward' : 'back';
    current = next;
    if (pagination) pagination.textContent = [current + 1, slides.length]
      .map(number => String(number).padStart(2, '0')).join(' / ');
    stage.dispatchEvent(new CustomEvent('slidechange', {
      bubbles: true,
      detail: { index: current, id: slides[current].dataset.slideId }
    }));
  }

  document.addEventListener('keydown', event => {
    if (event.defaultPrevented || event.isComposing || event.altKey || event.ctrlKey || event.metaKey ||
        event.target.isContentEditable || document.querySelector('dialog[open]') ||
        event.target.closest?.('input,textarea,select,button,a[href],[role="button"]')) return;
    switch (event.key) {
      case 'ArrowRight': case 'PageDown': case ' ': show(current + 1); break;
      case 'ArrowLeft': case 'PageUp': show(current - 1); break;
      case 'Home': show(0); break;
      case 'End': show(slides.length - 1); break;
      case 'f': case 'F':
        if (!event.repeat) {
          const request = document.fullscreenElement
            ? document.exitFullscreen?.()
            : document.documentElement.requestFullscreen?.();
          request?.catch(() => {});
        }
        break;
      default: return;
    }
    event.preventDefault();
  });
  stage.addEventListener('presentationgoto', event => {
    if (Number.isInteger(event.detail?.index)) show(event.detail.index);
  });
  document.addEventListener('fullscreenchange', () => { void syncScreenWakeLock(); });
  document.addEventListener('visibilitychange', () => { void syncScreenWakeLock(); });
  window.addEventListener('pagehide', () => { void releaseScreenWakeLock(); });
  show(0);
})();
