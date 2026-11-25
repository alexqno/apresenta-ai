# Quadro de post-its moderado

Use quando objetivo for coletar práticas, ideias ou relatos livres, não medir
conhecimento. O participante envia texto; o apresentador aprova antes de
publicar no palco.

- `postits`: `{ id, question, placeholder, maxLength }` no manifesto.
- Sem limite de envios por participante; `maxLength` limita somente texto.
- Dados públicos contêm apenas post-its aprovados. Pendentes e descartados
  ficam na sessão efêmera e só aparecem ao moderador autenticado.
- Link do moderador usa `#<presenterToken>`; nunca inclua token no QR, query
  string, manifesto ou rota pública.
- Texto entra por `textContent`. No palco, use cores pastéis variadas,
  gradiente leve, rotação discreta e posições persistentes na sessão.
- Posicione por busca maximin: cada novo item procura área segura mais distante
  dos existentes. Distribua em pontos orgânicos, não em grade visível. Quando
  quadro ficar denso, minimize área de interseção e preserve texto legível;
  sobreposição total é proibida.
- Use candidato pseudoaleatório estável por posição, nunca grade visual. A
  primeira passagem usa somente posições sem colisão; quando elas acabarem,
  compare área máxima de interseção, área total de interseção e distância
  mínima, nessa ordem. Grave `x`, `y`, `rotation` e `z` no registro, para que
  atualização de SSE ou polling nunca mova post-it já publicado.
- Item recém-aprovado entra uma única vez como se fosse colado: inicia acima,
  desce, toca com leve rebote e assenta. Não reanime itens existentes; respeite
  `prefers-reduced-motion`.
- Clique no palco abre diálogo de proporção fixa com backdrop. O texto deve se
  ajustar ao espaço sem rolagem, com distância entre conteúdo e fechar. Suporte
  `Esc` e clique no backdrop para fechar.
- Moderador usa card-papel em tom pastel único do design. Texto fica no corpo;
  botões fixos `✓` e `×` ocupam os cantos inferiores, com nomes acessíveis.

## Insumos reutilizáveis

- Servidor: `scripts/serve_participation.py` concentra contratos de sessão,
  moderação e `postit_style`; não replique algoritmo no cliente.
- Participante: `assets/participar/` contém formulário, estado ativo e envio
  por `Enter` sem `Shift`.
- Moderador: `assets/moderador/` contém rota privada, token no fragmento e
  decisões `approved` e `discarded`.
- Palco: copie `assets/palco/`. O renderer preserva o elemento de cada ID
  aprovado durante atualizações para manter foco, hover e animação de colagem.
