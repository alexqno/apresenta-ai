import { mountInteraction } from '../palco/interacoes.mjs';

const { slides } = await fetch('./participacao.json').then(response => response.json());
const target = document.querySelector('#simulador');
const renderers = slides.map(slide => {
  const title = document.createElement('h3');
  title.textContent = slide.title;
  const host = document.createElement('div');
  target.append(title, host);
  return mountInteraction(host, slide);
});
const notes = [
  { id: 'a', status: 'approved', text: 'Reservar tempo para perguntas.', style: { color: 'mint', x: 27, y: 39, rotation: -3, z: 1 } },
  { id: 'b', status: 'approved', text: 'Compartilhar a agenda.', style: { color: 'amber', x: 69, y: 66, rotation: 2, z: 2 } }
];
function render(state) {
  const snapshots = [
    {},
    { polls: { prioridade: { totals: { prazo: 3, custo: 1, qualidade: 1 }, totalVotes: 5 } }, diagnostics: { atencao: { totals: { agenda: 2 } } }, triages: { atividades: { totals: { convite: { antes: 2 } } } }, postits: { ideias: notes.slice(0, 1) } },
    { polls: { prioridade: { totals: { prazo: 3, custo: 3, qualidade: 1 }, totalVotes: 7 } }, diagnostics: { atencao: { totals: { agenda: 3 } } }, triages: { atividades: { totals: { convite: { antes: 2, durante: 2 } } } }, postits: { ideias: notes } }
  ];
  renderers.forEach(update => update(snapshots[state]));
  const pending = document.querySelector('#pendencia');
  const decision = document.querySelector('#decisao');
  pending.hidden = false;
  decision.textContent = '';
  document.querySelector('#aprovar').onclick = () => {
    const approved = { id: 'demo', status: 'approved', text: pending.querySelector('p').textContent,
      style: { color: 'lilac', x: 49, y: 51, rotation: -1, z: 3 } };
    const currentNotes = snapshots[state].postits?.ideias || [];
    renderers.at(-1)({ postits: { ideias: [...currentNotes, approved] } });
    pending.hidden = true;
    decision.textContent = 'Publicado no quadro.';
  };
  document.querySelector('#descartar').onclick = () => {
    pending.hidden = true;
    decision.textContent = 'Contribuição descartada.';
  };
}
document.querySelectorAll('[data-state]').forEach(button => {
  button.onclick = () => render(Number(button.dataset.state));
});
render(0);
