# Template neutro de apresentações

Base local para criar um design antes de gerar uma apresentação. Não é uma
identidade pronta: adapte tokens, tipografia, imagens e exemplos ao contexto.

## Uso

1. Registre objetivo, público e direção visual em `design-rationale.md`.
2. Defina os tokens semânticos em `tokens.css`; preserve `success`, `warning`,
   `danger` e `info` para estados, nunca como decoração.
3. Carregue `tokens.css` antes de `components.css`.
4. Abra `gallery.html` localmente para escolher componentes e composições.
5. Copie somente os componentes que expressam a relação do conteúdo.

## Componentes

- Estrutura: `presentation-slide`, `presentation-heading`,
  `presentation-kicker`, `presentation-title`, `presentation-body`,
  `presentation-footer` e `presentation-chapter`.
- Itens paralelos: `presentation-card`, estados semânticos e grids de 2, 3 ou
  5 itens (3+2 na última linha).
- Argumento: contraste, citação, síntese, métrica, barras comparativas,
  sequência, fluxo e código.
- Relações: objetivos, riscos, raias, linha do tempo, evidências, checkpoints,
  filtro, mandato, método, sinais e circuito.
- Apoio: `presentation-work-item`, `presentation-keyboard-guide` e
  `presentation-closing`.

`circuit.js` é progressivo: sem JavaScript, as etapas continuam presentes em
ordem no HTML. Carregue-o depois da marcação e depois que a tela estiver
visível.

## Galeria

`gallery.html` funciona por arquivo local. Use `→`, `←`, `Home`, `End` e `F`.
Ela não é uma apresentação pronta nem deve ser copiada integralmente.

## Ativos

Inclua somente ativos autorizados em `assets/`. Documente origem, licença,
versão, fundos permitidos e texto alternativo quando aplicável.

`assets/template-art.svg` é um fundo abstrato neutro de demonstração. Troque-o
por imagem aprovada na apresentação final; preserve o fade de
`.presentation-slide--art` para proteger a leitura.
