const state = { current: 0, currentVisible: false, slides: [] };
const cards = new Map();
const deck = document.querySelector('#deck-title');
const container = document.querySelector('#slides');
const liveJump = document.querySelector('.live-jump');
const sessionId = location.pathname.split('/participar/')[1]?.split('/')[0];
const deckPath = location.pathname.split('/participar/')[0];

let observer;
function scrollCurrent() { cards.get(state.current)?.scrollIntoView({ behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block:'center' }); }
function observeCurrentCard() { observer?.disconnect(); const card = cards.get(state.current); if (!card) return; observer = new IntersectionObserver(([entry]) => { state.currentVisible = entry.isIntersecting && entry.intersectionRatio >= .6; liveJump.hidden = state.currentVisible; }, { threshold: 0.6 }); observer.observe(card); }
function updateCurrent() { cards.forEach((card, index) => card.classList.toggle('is-current', index === state.current)); observeCurrentCard(); }
function applySession(session) { if (!Number.isInteger(session.slideIndex) || session.slideIndex === state.current) return; const follow = state.currentVisible; state.current = session.slideIndex; updateCurrent(); if (follow) scrollCurrent(); }
function renderSlide(slide, index) { const card = document.createElement('article'); card.className = 'slide-card'; card.innerHTML = `<span class="slide-card__number">Tela ${String(slide.number).padStart(2, '0')}</span><h2></h2><p></p>`; card.querySelector('h2').textContent = slide.title; card.querySelector('p').textContent = slide.summary; for (const link of slide.links) { if (!link.url.startsWith('https://')) continue; const anchor = document.createElement('a'); anchor.href = link.url; anchor.target = '_blank'; anchor.rel = 'noopener noreferrer'; anchor.textContent = link.label; card.append(anchor); } cards.set(index, card); return card; }
async function start() { const manifest = await fetch(`${deckPath}/participacao.json`).then((response) => response.json()); deck.textContent = manifest.title; state.slides = manifest.slides; container.replaceChildren(...state.slides.map(renderSlide)); liveJump.addEventListener('click', scrollCurrent); updateCurrent(); if (!sessionId) return; const receive = (session) => { applySession(session); const events = new EventSource(`/api/sessions/${sessionId}/events`); events.onmessage = (event) => receive(JSON.parse(event.data)); events.addEventListener('slide', (event) => receive(JSON.parse(event.data))); }; receive(await fetch(`/api/sessions/${sessionId}`).then((response) => response.json())); }
start().catch(() => { deck.textContent = 'Não foi possível abrir acompanhamento'; });
