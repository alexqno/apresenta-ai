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
3. Ofereça `Ao vivo` e `Explorar`. Ao vivo segue tela atual; Explorar preserva
   posição e mostra retorno explícito para tela em exibição.
4. Sirva projeto em `0.0.0.0` e use URL LAN explícita no QR. Nunca gere QR com
   `localhost` ou `127.0.0.1`.
5. Preserve orientação vertical e alvos de toque utilizáveis em celular.
6. Abra links externos em nova aba quando disponível e aceite somente URLs
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
  o alcançarem. Não inclua ilustrações específicas da apresentação no modelo.
- Copie `assets/galeria-interacoes/` para a entrega quando houver diagnóstico
  ponderado. A galeria deve mostrar estado neutro, seleção local e item acima
  do limiar, com tokens do design selecionado.

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
- Enquete mantém voto individual privado e resultados públicos agregados.
- Galeria de interações mostra estados sem voto, voto selecionado, líder e
  empate usando o design selecionado.
- Diagnóstico ponderado limita múltipla seleção, preserva privacidade e
  destaca itens somente quando atingem o limiar definido.
