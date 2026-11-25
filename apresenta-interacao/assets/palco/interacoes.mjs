const ids = entries => entries.map(entry => entry.id);

export function sessionDefinitions(slides) {
  const definitions = { polls: {}, diagnostics: {}, triages: {}, postits: {} };
  slides.forEach(({ poll, diagnostic, triage, postits }, slideIndex) => {
    if (poll) definitions.polls[poll.id] = { slideIndex, options: ids(poll.options) };
    if (diagnostic) definitions.diagnostics[diagnostic.id] = { slideIndex, items: ids(diagnostic.items), maxSelections: diagnostic.maxSelections };
    if (triage) definitions.triages[triage.id] = { slideIndex, items: ids(triage.items), categories: ids(triage.categories) };
    if (postits) definitions.postits[postits.id] = { slideIndex, maxLength: postits.maxLength };
  });
  return definitions;
}

export function pollShares(totals) {
  const entries = Object.entries(totals);
  const sum = entries.reduce((total, [, count]) => total + count, 0);
  const result = Object.fromEntries(entries.map(([id, count]) => [id, sum ? Math.floor(count * 100 / sum) : 0]));
  if (sum) {
    const remaining = 100 - Object.values(result).reduce((a, b) => a + b, 0);
    entries.sort(([a, x], [b, y]) => (y * 100 % sum) - (x * 100 % sum) || a.localeCompare(b));
    entries.slice(0, remaining).forEach(([id]) => result[id]++);
  }
  return result;
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function buildPoll(root, poll) {
  const total = element('strong', 'ai-poll-total');
  root.append(total);
  const rows = poll.options.map(({ id, label }) => {
    const row = element('div', 'ai-poll-row');
    const bar = element('i', 'ai-poll-bar');
    const share = element('strong', '');
    row.append(element('span', '', label), bar, share);
    root.append(row);
    return { id, row, bar, share };
  });
  return session => {
    const { totals = {}, totalVotes = 0 } = session.polls?.[poll.id] || {};
    const percentages = pollShares(totals);
    const max = Math.max(0, ...Object.values(totals));
    total.textContent = totalVotes + (totalVotes === 1 ? ' voto' : ' votos');
    rows.forEach(({ id, row, bar, share }) => {
      const count = totals[id] || 0;
      row.classList.toggle('is-leading', max > 0 && count === max);
      bar.style.setProperty('--width', (max ? count / max * 100 : 0) + '%');
      share.textContent = (percentages[id] || 0) + '%';
    });
  };
}

function buildDiagnostic(root, diagnostic) {
  const rows = diagnostic.items.map(({ id, label }) => {
    const row = element('div', 'ai-diagnostic-row');
    const density = element('i', '');
    density.setAttribute('aria-hidden', 'true');
    const count = element('strong', '');
    row.append(element('span', '', label), density, count);
    root.append(row);
    return { id, row, density, count };
  });
  return session => rows.forEach(({ id, row, density, count }) => {
    const value = session.diagnostics?.[diagnostic.id]?.totals?.[id] || 0;
    row.classList.toggle('is-collective', value >= diagnostic.highlightThreshold);
    density.textContent = value ? '●'.repeat(Math.min(8, value)) : '—';
    count.textContent = value;
  });
}

function buildTriage(root, triage) {
  const cards = triage.items.map(item => {
    const card = element('article', 'ai-triage-card');
    const winner = element('strong', '');
    const signals = element('div', '');
    const badge = element('b', 'ai-triage-badge');
    const reference = triage.categories.find(category => category.id === item.referenceCategory);
    signals.className = 'ai-triage-signals';
    badge.hidden = true;
    card.append(element('b', '', item.label), winner, signals, badge,
      element('span', 'ai-reference', 'Referência: ' + reference.label));
    root.append(card);
    return { item, winner, signals, badge };
  });
  function render(session) {
    root.classList.toggle('is-revealed', Boolean(session.triages?.[triage.id]?.referenceRevealed));
    cards.forEach(({ item, winner, signals, badge }) => {
    const totals = session.triages?.[triage.id]?.totals?.[item.id] || {};
    const max = Math.max(0, ...Object.values(totals));
    const leaders = triage.categories.filter(category => max && totals[category.id] === max);
    const winnerId = leaders.length === 1 ? leaders[0].id : null;
    winner.textContent = winnerId ? leaders[0].label : 'Aguardando consenso';
    card.className = 'ai-triage-card' + (winnerId ? ` is-${winnerId}` : ' is-pending');
    signals.replaceChildren(...triage.categories.map(category => {
      const signal = element('i', `is-${category.id}`);
      signal.setAttribute('title', category.label);
      signal.innerHTML = `<b aria-hidden="true"></b><em>${totals[category.id] || 0}</em>`;
      return signal;
    }));
    if (root.classList.contains('is-revealed')) {
      badge.hidden = false;
      const correct = winnerId && winnerId === item.referenceCategory;
      badge.className = 'ai-triage-badge ' + (correct ? 'is-correct' : 'is-incorrect');
      badge.textContent = correct ? '✓ Classificação correta' : '↺ Rever classificação';
    }
    });
  }
  return render;
}

function openNote(note, record) {
  const dialog = element('dialog', 'ai-note-dialog ' + record.style.color);
  dialog.setAttribute('aria-label', 'Post-it ampliado');
  const content = element('p', '', record.text);
  const close = element('button', '', 'Fechar');
  close.onclick = () => dialog.close();
  dialog.append(content, close);
  dialog.onclick = event => {
    if (event.target !== dialog) return;
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
  };
  dialog.onclose = () => { dialog.remove(); note.focus(); };
  (document.fullscreenElement || document.body).append(dialog);
  dialog.showModal();
  const fit = () => {
    let low = 1, high = 80;
    while (high - low > 1) {
      const size = (low + high) / 2;
      content.style.fontSize = size + 'px';
      if (content.scrollHeight <= content.clientHeight) low = size;
      else high = size;
    }
    content.style.fontSize = low + 'px';
  };
  const observer = new ResizeObserver(fit);
  observer.observe(dialog);
  dialog.addEventListener('close', () => observer.disconnect(), { once: true });
  fit();
}

function buildBoard(root, definition) {
  const board = element('div', 'ai-note-board');
  const empty = element('span', '', 'Aguardando contribuições.');
  board.append(empty);
  root.append(board);
  const notes = new Map();
  let initialized = false;
  return session => {
    const records = session.postits?.[definition.id] || [];
    const visible = new Set(records.map(record => record.id));
    for (const [id, note] of notes) {
      if (!visible.has(id)) { note.remove(); notes.delete(id); }
    }
    empty.hidden = records.length > 0;
    for (const record of records) {
      if (notes.has(record.id)) continue;
      const note = element('button', 'ai-note ' + record.style.color, record.text);
      note.type = 'button';
      note.classList.toggle('is-new', initialized);
      note.style.left = record.style.x + '%';
      note.style.top = record.style.y + '%';
      note.style.zIndex = record.style.z;
      note.style.setProperty('--rotation', record.style.rotation + 'deg');
      note.onclick = () => openNote(note, record);
      board.append(note);
      notes.set(record.id, note);
    }
    initialized = true;
  };
}

// Um contêiner dedicado por tela. Guarde o callback entre atualizações.
export function mountInteraction(root, slide) {
  root.classList.add('ai-interaction');
  const updates = [];
  for (const [type, build] of Object.entries({ poll: buildPoll, diagnostic: buildDiagnostic, triage: buildTriage, postits: buildBoard })) {
    if (slide[type]) updates.push(build(root, slide[type]));
  }
  return session => updates.forEach(update => update(session));
}
