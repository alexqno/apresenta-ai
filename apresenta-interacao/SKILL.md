---
name: apresenta-interacao
description: Crie acompanhamento móvel e interações locais para apresentações web, com QR code, sessões e sincronização. Use quando participantes acessam uma apresentação pelo celular; não use para criar o deck principal.
metadata:
  short-description: Cria participação móvel para apresentações
---

# Pra que serve

Criar ou evoluir uma página móvel associada a uma apresentação web. A página
permite acompanhar o evento, explorar telas, acessar material complementar e,
quando requisitado, participar de interações.

# Antes de começar

- Confirme apresentação, design e se a experiência exige rede local ou
  publicação autorizada.
- Defina quem inicia sessão, como participantes entram e se acompanham ao vivo
  ou exploram livremente.
- Mantenha roteiro e design do deck como fontes de verdade para título, resumo,
  ordem e visual.
- Não assuma votação, coleta de dados, autenticação ou publicação externa.

# Primeira entrega local

Para acompanhamento por celular na mesma rede:

1. Crie manifesto por tela com número, título, resumo e links opcionais.
2. Gere sessão efêmera. `sessionId` é público; token do apresentador é secreto
   e não pode entrar no QR nem na página móvel.
3. Faça o QR da capa também criar `Nova sessão` ao ser clicado: descarte apenas
   a referência local da sessão e gere novo QR com resultados isolados. Não use
   reinício de servidor como mecanismo de limpeza; o mesmo comportamento deve
   funcionar publicado.
   Em toda tela com interação ativa, exiba também QR puro no canto superior
   direito, ligeiramente menor que o da capa. O QR da tela não cria sessão nem
   exibe rótulo; preserva apenas contraste e área silenciosa para leitura. A
   capa mantém QR, rótulo e ação de nova sessão.
4. Ofereça `Ao vivo` e `Explorar`. Ao vivo segue tela atual; Explorar preserva
   posição e mostra retorno explícito para tela em exibição.
5. Sirva projeto em `0.0.0.0` e use URL LAN explícita no QR. Nunca gere QR com
   `localhost` ou `127.0.0.1`.
6. Preserve orientação vertical e alvos de toque utilizáveis em celular.
7. Abra links externos em nova aba quando disponível e aceite somente URLs
   autorizadas pelo projeto.

# Votação ao vivo

Quando o pedido incluir votação, leia [o contrato de votação](references/votacao.md)
antes de implementar. Não transforme toda tela de pergunta em enquete: confirme
opções, uma escolha por participante, momento de abertura e visibilidade dos
resultados.

- Defina a enquete em `participacao.json`, dentro da tela: `id`, `question` e
  opções `{ id, label }`. O `id` deve ser estável, curto e único.
- Na criação da sessão, envie ao servidor cada enquete com `id`, `slideIndex`
  e IDs de opção. O servidor aceita voto somente na tela ativa, substitui o
  voto anterior do mesmo navegador e expõe apenas totais agregados.
- No palco, mostre total geral à direita. Use percentuais inteiros que somem
  100% por maiores restos; barras dos líderes ficam completas com gradiente de
  destaque e as demais são proporcionais ao líder, com contraste menor.
  Empates recebem o mesmo destaque. Ajuste cores pelos tokens do design.
- Cada atualização deve transitar da largura atual para o novo percentual,
  seja aumento ou redução. Não use `clip-path`, preenchimento até zero ou
  reinício visual: a barra deve sempre conservar seu estado visível e alcançar
  a nova proporção. Não anime em loop e respeite `prefers-reduced-motion`.
- No celular, não mostre totais nem percentuais. Destaque somente a escolha
  local com gradiente e mantenha as demais opções legíveis. Desabilite o voto
  fora da tela ativa da enquete.
- Copie `assets/galeria-interacoes/` para a entrega como
  `galeria-interacoes/` quando a apresentação tiver votação. Adapte os tokens
  ao design selecionado e use a galeria para validar os estados de palco e
  celular antes de finalizar.

# Diagnóstico ponderado

Quando a pergunta pedir que cada pessoa identifique mais de uma lacuna,
prioridade ou risco, leia [o contrato de diagnóstico](references/diagnostico.md)
antes de implementar. Use este modelo em vez de uma votação de escolha única.

- Defina `diagnostic` na tela de `participacao.json`: `id`, `question`, itens
  `{ id, label }`, `maxSelections` e `highlightThreshold`. O limiar define
  quantas seleções agregadas acendem cada item no palco.
- Na criação da sessão, envie `id`, `slideIndex`, IDs dos itens e
  `maxSelections`. Uma nova múltipla seleção substitui a anterior do mesmo
  navegador. O servidor publica apenas totais agregados.
- No celular, aplique gradiente apenas aos itens selecionados. Não mostre
  totais. Desabilite novos itens ao atingir o limite, mas sempre permita
  desfazer uma seleção.
- No palco, mostre densidade ou contagem antes do limiar e destaque itens que
  o alcançarem. Ao cruzar o limiar, o gradiente pode entrar uma vez da esquerda
  para a direita; atualizações posteriores não o reiniciam. Não inclua
  ilustrações específicas da apresentação no modelo.
- Copie `assets/galeria-interacoes/` para a entrega quando houver diagnóstico
  ponderado. A galeria deve mostrar estado neutro, seleção local e item acima
  do limiar, com tokens do design selecionado.

# Palco reutilizável

Copie `assets/palco/`, `assets/participar/`, `assets/moderador/` e
`assets/galeria-interacoes/` como diretórios irmãos na entrega. O adaptador
de palco cria as definições da sessão a partir do mesmo manifesto que o celular.
Use [o guia de integração](references/palco.md) e
[o manifesto funcional com as quatro interações](assets/galeria-interacoes/participacao.json).
Para decks que usam a base `apresenta-ai`, carregue
`palco/bootstrap.mjs`; ele conecta o evento `slidechange`, restaura a tela da
sessão depois de recarga e publica o índice sem tocar em estado interno do
controlador. Não copie lógica de sessão, QR ou SSE para `app.js` do deck.
Os painéis de acompanhamento e moderação usam o mesmo contrato tipográfico
para o título da apresentação; altere-o no template compartilhado, não em um
painel isolado.

# Ícones locais

Use somente os SVGs necessários de `assets/icons/`; não carregue bibliotecas
de ícones por CDN. Copie cada SVG usado para `assets/icons/` da entrega e
referencie-o pelo caminho local. Para ações de moderação, use
`user-round-star.svg`, com nome acessível no controle que o contém.

# Triagem de contexto

Quando pessoas precisarem classificar vários contextos em destinos exclusivos,
use `triage`, não enquete nem diagnóstico ponderado.

- Defina `triage` na tela: `id`, `question`, categorias `{ id, label }` e
  itens `{ id, label, detail, referenceCategory }`.
- Cada pessoa pode classificar um cartão por vez; nova escolha substitui apenas
  aquele cartão. O palco publica somente totais agregados.
- Mostre no palco o destino com maior consenso. Empates e ausência de resposta
  ficam neutros. Depois, exponha a orientação de referência sem chamar a
  resposta coletiva de erro.
- Registre o modelo e seus estados na galeria de interações.

# Quadro de post-its moderado

Quando objetivo for compartilhar práticas, relatos ou ideias livres, leia
[o contrato de post-its](references/postits.md) antes de implementar. Use
moderação privada por padrão: texto pendente não aparece no palco.

- Defina `postits` na tela: `id`, `question`, `placeholder` e `maxLength`.
- No celular, use somente campo de texto e botão de envio; permita múltiplos
  envios enquanto a tela estiver ativa.
- QR público permanece em `/participar/<sessionId>`. Painel privado usa
  `/moderador/<sessionId>#<presenterToken>`; token não pode entrar em query,
  resposta pública ou SSE público.
- Painel do moderador mostra miniaturas de todos os slides e controles apenas
  nas telas com post-its. Cada pendência é um card-papel em tom pastel único
  do design; texto ocupa corpo do card e ações ficam nos cantos inferiores,
  com botões fixos `✓` para aprovar e `×` para descartar. Preserve rótulos
  acessíveis e tooltip. Aprovar publica; descartar nunca publica.
- No palco, use cores pastéis variadas, gradientes discretos, distribuição
  persistente e distribuição orgânica. Escolha posições seguras que maximizem
  distância dos existentes; não use grade visual. Permita apenas sobreposição
  parcial quando não houver área livre e nunca cubra integralmente texto de
  outro post-it. A posição gravada não pode mudar após inserção.
- Quando aprovação introduzir novo post-it, aplique uma única animação de
  colagem: entrada acima do quadro, toque com pequeno rebote e assentamento.
  Não reanime itens existentes, não faça loop e respeite
  `prefers-reduced-motion`.
- Clique no palco abre diálogo de proporção fixa, com backdrop, `Esc` e clique
  externo. Dimensione texto até caber sem rolagem; mantenha distância visível
  entre texto e botão de fechar.
- Registre na galeria de interações os estados: vazio, pendente no moderador,
  aprovação com colagem, quadro preenchido e diálogo aberto.

# Limites

- Página móvel não altera roteiro ou deck sem pedido explícito.
- QR, sessão e sincronização continuam locais até que publicação seja
  explicitamente autorizada.
- Recursos bidirecionais, como votação e propostas, exigem contrato próprio de
  dados, moderação, retenção e atualização no palco antes de implementação.
- Preserve funcionamento offline da apresentação: falha de rede não pode
  impedir navegação do palestrante.

# Pronto quando

- QR abre página no celular pela mesma rede.
- Sessão atualiza modo Ao vivo sem expor token de apresentador.
- Explorar não é interrompido por mudança de tela e permite retorno à atual.
- Títulos, resumos e links vêm do manifesto revisável.
- Layout móvel vertical usa identidade aprovada e não corta conteúdo.
- Comando local, URL LAN e controles estão documentados.
- Templates de palco, participação e moderação não contêm nome, token, cor ou
  caminho de um design específico; recebem tokens do design copiado pela
  entrega e mantêm fallback neutro.
- Enquete mantém voto individual privado e resultados públicos agregados.
- Galeria de interações mostra estados sem voto, voto selecionado, líder e
  empate usando o design selecionado.
- Diagnóstico ponderado limita múltipla seleção, preserva privacidade e
  destaca itens somente quando atingem o limiar definido.
- Quadro moderado protege pendências, distribui post-its de modo legível e
  publica colagem aprovada sem reiniciar itens existentes.
