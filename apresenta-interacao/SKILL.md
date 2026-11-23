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
