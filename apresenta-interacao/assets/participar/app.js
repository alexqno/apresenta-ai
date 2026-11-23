const state = { current: 0, mode: localStorage.getItem('participation-mode') || 'live', slides: [] };
const cards = new Map();
const deck = document.querySelector('#deck-title');
const container = document.querySelector('#slides');
const now = document.querySelector('.now');
const nowTitle = now.querySelector('strong');
const goCurrent = now.querySelector('button');
const sessionId = location.pathname.split('/participar/')[1]?.split('/')[0];
const deckPath = location.pathname.split('/participar/')[0];

function setMode(mode) { state.mode = mode; localStorage.setItem('participation-mode', mode); document.querySelectorAll('[data-mode]').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.mode === mode))); updateCurrent(false); }
function updateCurrent(scroll = true) { const slide = state.slides[state.current]; if (!slide) return; cards.forEach((card, index) => card.classList.toggle('is-current', index === state.current)); now.hidden = state.mode === 'live'; nowTitle.textContent = `${String(slide.number).padStart(2, '0')} · ${slide.title}`; if (scroll && state.mode === 'live') cards.get(state.current)?.scrollIntoView({ behavior:'smooth', block:'center' }); }
function applySession(session) { if (Number.isInteger(session.slideIndex)) { state.current = session.slideIndex; updateCurrent(); } }
function renderSlide(slide, index) { const card = document.createElement('article'); card.className = 'slide-card'; card.innerHTML = `<span class="slide-card__number">Tela ${String(slide.number).padStart(2, '0')}</span><h2></h2><p></p>`; card.querySelector('h2').textContent = slide.title; card.querySelector('p').textContent = slide.summary; for (const link of slide.links) { if (!link.url.startsWith('https://')) continue; const anchor = document.createElement('a'); anchor.href = link.url; anchor.target = '_blank'; anchor.rel = 'noopener noreferrer'; anchor.textContent = link.label; card.append(anchor); } cards.set(index, card); return card; }
async function start() { const manifest = await fetch(`${deckPath}/participacao.json`).then((response) => response.json()); deck.textContent = manifest.title; state.slides = manifest.slides; container.replaceChildren(...state.slides.map(renderSlide)); document.querySelectorAll('[data-mode]').forEach((button) => button.addEventListener('click', () => setMode(button.dataset.mode))); goCurrent.addEventListener('click', () => { setMode('live'); }); setMode(state.mode); if (!sessionId) return; const receive = (session) => { applySession(session); const events = new EventSource(`/api/sessions/${sessionId}/events`); events.onmessage = (event) => receive(JSON.parse(event.data)); events.addEventListener('slide', (event) => receive(JSON.parse(event.data))); }; receive(await fetch(`/api/sessions/${sessionId}`).then((response) => response.json())); }
start().catch(() => { deck.textContent = 'Não foi possível abrir acompanhamento'; });
