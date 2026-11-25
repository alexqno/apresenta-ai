import { mountInteraction, sessionDefinitions } from './interacoes.mjs';
import qrcode from '../participar/qrcode.mjs';

async function json(path, body) {
  const options = body === undefined ? { cache: 'no-store' } : {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
  };
  const response = await fetch(path, options);
  if (!response.ok) throw new Error('Participação indisponível (' + response.status + ')');
  return response.json();
}

// Cada posição de containers corresponde ao mesmo índice do manifesto.
export async function startPresenter({ manifest, containers, panel, currentIndex, publishInitial = true }) {
  const update = manifest.slides.flatMap((slide, index) => containers[index] ? [mountInteraction(containers[index], slide)] : []);
  const definitions = sessionDefinitions(manifest.slides);
  const storageKey = 'apresenta:session:' + location.pathname;
  const fingerprint = JSON.stringify(definitions);
  let session;
  let restoredSession = false;
  try {
    const stored = JSON.parse(sessionStorage.getItem(storageKey));
    if (stored?.fingerprint === fingerprint) {
      session = { ...await json('/api/sessions/' + stored.sessionId), presenterToken: stored.presenterToken };
      restoredSession = true;
    }
  } catch { /* Uma sessão efêmera pode ter expirado. */ }
  const deck = new URL('.', location.href).pathname.replace(/^\/+|\/+$/g, '');
  session ||= await json('/api/sessions', { deck, ...definitions });
  const { sessionId, presenterToken, participationUrl } = session;
  sessionStorage.setItem(storageKey, JSON.stringify({ sessionId, presenterToken, fingerprint }));
  const qr = qrcode(0, 'M');
  qr.addData(participationUrl);
  qr.make();
  const qrMarkup = () => qr.createSvgTag({ cellSize: 3, margin: 2, scalable: true });
  const hasInteraction = slide => Boolean(slide.poll || slide.diagnostic || slide.triage || slide.postits);
  const reset = document.createElement('button');
  reset.type = 'button';
  reset.setAttribute('aria-label', 'Nova sessão de participação');
  reset.title = 'Nova sessão';
  reset.innerHTML = qrMarkup();
  reset.onclick = () => { sessionStorage.removeItem(storageKey); location.reload(); };
  panel.classList.add('ai-entry-qr');
  panel.replaceChildren(reset);
  function link(label, href) {
    const anchor = document.createElement('a');
    anchor.textContent = label;
    anchor.href = href;
    anchor.target = '_blank';
    anchor.rel = 'noopener noreferrer';
    panel.append(anchor);
  }
  link('Acompanhe pelo celular', participationUrl);
  if (Object.keys(definitions.postits).length) link('Abrir moderação', participationUrl.replace('/participar/', '/moderador/') + '#' + presenterToken);
  manifest.slides.forEach((slide, index) => {
    const container = containers[index];
    if (!container || !hasInteraction(slide)) return;
    const host = container.closest('[data-slide], .slide') || container.parentElement;
    if (!host) return;
    host.classList.add('ai-interaction-host');
    host.querySelector('.ai-interaction-qr')?.remove();
    const interactionQr = document.createElement('aside');
    interactionQr.className = 'ai-interaction-qr';
    interactionQr.setAttribute('aria-label', 'QR code para acompanhar pelo celular');
    interactionQr.innerHTML = qrMarkup();
    host.append(interactionQr);
  });
  const url = '/api/sessions/' + sessionId;
  const render = snapshot => update.forEach(callback => callback(snapshot));
  render(session);
  const events = new EventSource(url + '/events');
  events.addEventListener('slide', event => render(JSON.parse(event.data)));
  let refresh;
  events.onerror = () => {
    refresh ??= setInterval(() => json(url).then(snapshot => {
      if (events.readyState !== EventSource.OPEN) render(snapshot);
    }).catch(() => {}), 1500);
  };
  events.onopen = () => { clearInterval(refresh); refresh = undefined; };
  const stop = () => { clearInterval(refresh); events.close(); };
  events.addEventListener('session-ended', stop);
  window.addEventListener('pagehide', stop, { once: true });
  let queued = Promise.resolve();
  function publish(slideIndex) {
    queued = queued.then(() => json(url + '/slide', { presenterToken, slideIndex })).catch(() => {
      panel.title = 'Sincronização indisponível. Navegação local ativa.';
    });
    return queued;
  }
  if (publishInitial) await publish(currentIndex());
  return { publish, stop, session, restoredSession };
}
