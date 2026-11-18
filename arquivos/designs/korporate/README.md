# Korporate - Industrial Premium Playful

Sistema de design para apresentações web 16:9 da Korporate. Combina contraste industrial, energia laranja e interfaces leves para explicar temas técnicos sem perder proximidade.

## Uso

1. Inclua `tokens.css` antes de `components.css`.
2. Use `gallery.html` como catálogo de padrões, não como apresentação final.
3. Copie apenas os componentes necessários para uma nova apresentação e mantenha os papéis semânticos de cor.
4. Consulte `design-rationale.md` antes de criar variações de capa, dados ou fluxo.

## Abrir a galeria

Abra `gallery.html` em um navegador moderno. Não requer instalação ou servidor.

Controles: `→` ou espaço avança; `←` volta; `Home` vai ao início; `End` vai ao fim; `F` alterna tela cheia. Os botões inferiores oferecem as mesmas ações. Controles editáveis não disparam navegação.

O ativo de marca selecionado é `assets/korporate-mark.svg`, que encapsula a assinatura horizontal documentada em `assets/README.md`.

## Acessibilidade

A galeria respeita `prefers-reduced-motion`. Dados de sucesso e atenção usam rótulos textuais além de cor. A estrutura é dimensionada para 16:9, priorizando 1920x1080 e mantendo áreas seguras para apresentação.

## Princípios

- Fundo claro como padrão; fundo escuro para abertura, capítulos e encerramento.
- Laranja Korporate sinaliza intenção, ação e energia. Não use como cor de dado positivo.
- Azul, vermelho e cinza comunicam dados; cada estado exige também texto ou ícone.
- Toda animação deve continuar compreensível em modo reduzido.
- Preserve área livre, contraste e proporção da marca.
