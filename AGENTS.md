# AGENTS.md

## Propósito

Este repositório contém a skill `apresenta-ai` e suas referências. As páginas
web geradas ficam no projeto onde a skill foi invocada. Cada entrega deve ser
exibível em navegador, em tela cheia, com narrativa sequencial semelhante a
uma apresentação.

Não criar arquivos PowerPoint, Keynote ou equivalentes, salvo solicitação
explícita.

## Comunicação

- Comunique-se em português do Brasil, salvo pedido explícito em outro idioma.
- Seja direto. Diferencie fatos, hipóteses e decisões.
- Pergunte quando faltar informação que altere design, conteúdo ou escopo.

## Estrutura

- `SKILL.md`: instruções principais da skill.
- `arquivos/designs/<instituicao>/`: identidades visuais e referências.
- `.apresentaAI/<nome-da-apresentacao>/`: entrega completa de cada página web,
  na raiz do projeto onde a skill foi invocada.
- Skills auxiliares, quando justificadas, ficam em `skills/<nome-da-skill>/`.

Não criar conteúdo de entrega fora de `.apresentaAI/` no projeto invocador,
salvo materiais reutilizáveis em `arquivos/` deste repositório.

## Identidade visual

- Cada instituição possui design em `arquivos/designs/<instituicao>/`.
- Primeiro design disponível: `korporate`.
- Marca, cores, fontes e referências são guias; não são limites criativos.
- Preserve proporções, contraste, legibilidade e uso correto de marcas.
- Não invente logotipos, fontes proprietárias ou diretrizes institucionais.
- Se o design pattern não for informado, pergunte qual usar antes de criar
  qualquer artefato visual.

## Entregas

Cada página web interativa deve:

- funcionar em navegador moderno, sem depender de serviços externos não autorizados;
- ter navegação por teclado; suportar passador de slides quando tecnicamente viável;
- funcionar em tela cheia;
- ter sequência narrativa clara;
- priorizar legibilidade à distância, contraste e ritmo de apresentação;
- usar animações apenas quando reforçarem narrativa ou compreensão;
- permanecer utilizável sem animações, quando possível;
- declarar instruções de execução e controles disponíveis em arquivo local da entrega.

## Implementação

- Prefira HTML, CSS e JavaScript simples quando bastarem.
- Adicione dependências somente quando trouxerem ganho claro de qualidade,
  manutenção ou interação.
- Não altere identidade visual existente sem pedido explícito.
- Preserve arquivos e entregas existentes; não sobrescreva uma apresentação
  sem confirmar alvo exato.
- Antes de reutilizar material externo, confirme licença e atribuição exigida.
- Não inclua dados confidenciais, chaves, tokens ou credenciais no repositório.

## Qualidade

Antes de considerar entrega pronta, valide:

- navegação para frente, trás, início e fim;
- tela cheia;
- layout em resolução de apresentação;
- contraste, tamanho de texto e legibilidade;
- ausência de erros visíveis no console;
- funcionamento de mídia, animações e links usados;
- coerência com design selecionado;
- conteúdo e ordem narrativa aprovados.

## Evolução da skill

- Atualize `SKILL.md` quando uma regra recorrente mudar.
- Crie skill auxiliar somente para responsabilidade específica, reutilizável e
  independente.
- Evite transformar preferências de uma apresentação em regra global sem
  confirmação.
