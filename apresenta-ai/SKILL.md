---
name: apresenta-ai
description: Crie ou evolua apresentações web interativas, sequenciais e em tela cheia a partir de roteiro ou conteúdo-base. Use para palestras, talks e apresentações; não use para arquivos PowerPoint, Keynote ou slides tradicionais.
metadata:
  short-description: Cria apresentações web narrativas
---

# Pra que serve

Criar páginas web interativas para palestras, em narrativa sequencial e
apresentáveis em tela cheia. A entrega é uma apresentação web, não um arquivo
de slides tradicional.

# Atualização

Esta skill e `$apresenta-design` devem permanecer na mesma versão. Em um
ambiente já instalado, use
`python3 ~/.codex/skills/apresenta-ai/scripts/update_skills.py --check` para
verificar uma versão nova e acrescente `--yes` para instalar. Depois da troca,
inicie uma nova conversa antes de invocar as skills.

# Quando usar

Use quando o pedido for criar ou evoluir uma apresentação web a partir de um
roteiro, artigo-base ou conteúdo sequencial. O acionamento é manual no chat.

# O que precisa

- Roteiro sequencial, com expectativa de telas e pontos centrais. Um
  artigo-base ou texto completo pode complementar contexto e ser convertido em
  roteiro antes da implementação.
- Design pattern escolhido e disponível em
  `.apresentaAI/designs/<instituicao>/` no projeto invocador.
- Título da apresentação, que nomeia sua pasta em
  `.apresentaAI/` na raiz do projeto onde a skill foi invocada.
- Orientações por projeto para imagens, gráficos ou recursos interativos, se
  existirem.
- Tom e público, quando eles alterarem a experiência. Não presuma que o tom de
  uma apresentação se aplica a outra.

# Fluxo de entrevista e início

Antes de criar artefatos visuais, confirme o que faltar que mude conteúdo,
design ou escopo. Descubra, conforme necessário:

1. público, objetivo, tom e contexto de uso;
2. roteiro, número de telas e conteúdo complementar;
3. design pattern;
4. identidade visual aplicável;
5. orientações de imagens, gráficos e interações;
6. requisitos de navegação, recursos auxiliares e publicação.

Se receber apenas texto corrido, proponha ou produza primeiro um roteiro
sequencial para validação. Estime a quantidade de telas quando o roteiro não
a informar.

# Escolha de design pattern

Se o pedido não informar o design pattern, pergunte qual usar antes de criar
qualquer artefato visual. Não escolha automaticamente o primeiro design
disponível.

Se o design necessário não existir, interrompa a criação da apresentação e
oriente o usuário a criar ou incluir o design. Quando a skill estiver
instalada, use `$apresenta-design` para criar um design local assistido.

# Uso de identidades visuais

Use marca, cores, fontes e referências do design selecionado como direção.
Adapte-os ao tema e à legibilidade: misture cores, use degradês e leve a
paleta às imagens geradas quando isso tornar a apresentação mais atraente.

Não trate componentes rígidos, fundos chapados ou cores fixas como limite
criativo quando reduzirem impacto visual. Preserve reconhecimento da marca,
proporções, contraste e uso correto dos ativos.

Defina estilo de imagens por projeto. Quando a imagem raster fizer sentido,
use a skill `imagegen`; mantenha paleta e estilo coerentes com o design e com
as orientações daquele projeto. Não use imagens geradas para substituir
elementos que funcionam melhor como HTML, CSS, SVG ou gráfico de dados.
Antes do Plano visual, leia a direção de imagens do design no racional e use-a
para propor imagens, fundos ou ilustrações. A direção orienta a proposta; não
torna imagem obrigatória onde ela não melhorar a narrativa.
Quando a direção de imagens mapear uma categoria semântica a um recurso visual,
a tela correspondente usa o recurso previsto pela direção de imagens ou
registra incompatibilidade concreta. O recurso não pode ser descartado só porque
fluxo, card ou diagrama também explica o conteúdo: use-o como camada
auxiliar, fora do grid, quando não reduzir legibilidade.

# Passos

1. Confirme insumos e escolha de design pattern.
2. Transforme conteúdo em sequência de telas, preservando ideias centrais e
   ritmo do roteiro. Divida telas densas; una telas curtas ou com o mesmo
   contexto quando isso melhorar a narrativa.
   Antes de implementar, crie uma Matriz por tela com: fonte no roteiro ou
   artigo, mensagem, conteúdo obrigatório, conteúdo proibido e recurso visual.
   Conteúdo proibido registra assunto pertencente a outra tela; evita repetição
   ou migração silenciosa entre telas.
   Copie `assets/planejamento/planejamento.md` para a raiz do deck e registre
   nele uma seção por tela. Este é o contrato revisado pelo usuário: use
   linguagem comum e não peça ao usuário para editar JSON. Depois da revisão,
   crie `planejamento.json` como espelho técnico, com os mesmos IDs, fontes,
   mensagem, conteúdos obrigatório e proibido, composição, componente, imagem
   e ocupação vertical. O JSON é responsabilidade da skill, não uma etapa do
   usuário.
3. Defina direção visual por tela: tese, padrão do design reutilizado,
   composição dominante, recurso visual e conteúdo de apoio. Tela com pouco
   texto ou relação representável não pode receber só título e parágrafo.
   Preencha um **Plano visual por tela** antes de implementar: composição,
   componentes literais do design, posição dos elementos, decisão explícita de
   imagem (`específica`, `padrão` ou `nenhuma`) e ocupação vertical. `Nenhuma`
   só é válida para pergunta, tese curta, encerramento ou composição gráfica
   já completa; não a use para deixar uma tela de conteúdo como texto puro.
   Imagem é opcional, mas a avaliação não é: em deck substantivo, não marque
   todas as telas como `nenhuma` sem reavaliar cena, ilustração, mockup, fundo
   ou elemento gráfico que possa esclarecer a mensagem. Registre por que a
   decisão escolhida sustenta a composição.
   Dimensione título, tese e apoio pela composição e leitura à distância; título
   não deve competir com conteúdo ou recurso visual. Reutilize componentes do
   design antes de criar CSS local: card, fluxo, rodapé, contador e variações
   de grid devem ter contrato visual único na apresentação.
   Fora de telas de interação, mantenha o mesmo espaçamento entre kicker e
   título em toda a apresentação. Não altere esse intervalo por tela para
   compensar área vazia; ajuste o conteúdo, o recurso visual ou sua composição.
   Agrupe kicker e título com o componente de cabeçalho do design, como
   `kp-heading-stack` no Korporate ou `presentation-heading` no template neutro.
   No template neutro, consulte `gallery.html` do design escolhido antes de
   compor a primeira tela: `presentation-*` cobre cards, contraste, fluxo,
   raias, evidências, checkpoints, filtros, mandato, sinais e circuito. Use o
   componente que representa a relação do roteiro; não recrie-o em CSS local.
   Quando o design tiver `components.css`, incorpore-o sem alterar os seletores
   do design e use suas classes nos elementos equivalentes. CSS local pode
   compor a tela, mas não pode recriar nem sobrescrever componente existente
   com aparência divergente. Se faltar um componente, registre a extensão no
   plano e crie-a como variação explícita do contrato do design.
   Quando o design definir card-padrão, aplique o mesmo fundo, borda, acento e
   tipografia a todos os cards equivalentes. Variação de cor ou borda só pode
   comunicar estado semântico explícito; não diferencie cards por decoração.
   O contrato de card inclui cor interna, sombra e borda superior na espessura definida pelo design, ou `0.5rem` se ele não a definir.
   Toda família de cards recebe essa moldura; uma variação semântica de card
   pode trocar os tokens de cor da moldura inteira, mas nunca remover sombra,
   cor interna ou borda superior. Antes de finalizar, revise todos os cards
   visíveis contra esse contrato.
   Cards não são layout padrão. Use-os para grupos de itens paralelos que
   precisam ser comparados ou percorridos; não os use apenas para acomodar
   qualquer texto. No Plano visual, registre a composição dominante de cada
   tela e, antes de implementar, consolide um inventário de composições. Se
   cards predominarem sem o roteiro exigir, replaneje telas com fluxo, escala,
   comparação, diagrama, linha do tempo, mockup, dado, tipografia expressiva,
   cena ou espaço negativo, conforme a relação que precisa ser entendida.
   Use imagem ou ilustração quando preencher composição; cards para itens
   paralelos; fluxos para processos; comparativos para escolhas opostas;
   diagramas para relações; e mockup fiel quando o roteiro nomear uma
   interface. Se o roteiro não definir o recurso, escolha pela semântica e
   registre a decisão no plano; não delegue essa decisão ao usuário.
   Ilustrações figurativas ficam à direita por padrão, preservando a coluna
   esquerda para título e tese; inverta somente quando a narrativa exigir.
   Para itens paralelos, proponha cards. Defina o grid pela quantidade: quatro
   itens em 2×2; seis em 3×2; para quantidade sem grade completa, distribua a
   última linha em toda a largura disponível. Para etapas ordenadas, use fluxo
   ou grid numerado e mantenha todas as etapas e sua ordem. Mockup de interface
   deve se aproximar da interface real sem inventar dados, funções ou marca.
   Questões ao público, teses curtas e encerramentos normalmente dispensam
   cards e imagens.
   Distribua a composição no eixo vertical: use título, conteúdo e recurso
   visual para ocupar uma faixa central proporcional ao palco. Não alinhe todo
   conteúdo ao topo nem aceite espaço inferior ocioso como consequência de um
   grid lateral. Use layout lado a lado somente quando título e recurso formam
   uma unidade visual; caso contrário, use empilhamento, centralização ou
   expansão controlada do recurso. Registre essa escolha no Plano visual por
   tela.
4. Avalie imagem como camada narrativa, não decoração. Use `imagegen` para
   ilustração, cena, mockup ou fundo quando ela esclarecer o assunto, sustentar
   a composição ou variar o ritmo. Não force imagem onde cards, fluxo, dado,
   diagrama ou espaço vazio cumprirem melhor essa função. Imagem de fundo fica
   atrás dos componentes, fora do grid, com fade forte à esquerda e visibilidade
   crescente da metade para a direita; preserve contraste. Sem imagem específica,
   use textura ou imagem-padrão prevista no design. Não aplique imagem automática
   às telas de questionamento.
5. Compare abertura, uma tela de conteúdo, uma tela de fluxo e encerramento
   com a galeria ou referência do design. Reproduza componentes aplicáveis,
   incluindo guia de teclado, contador e rodapé, salvo decisão documentada.
   Controles de navegação na tela são proibidos por padrão; use teclado e
   passador, salvo pedido explícito do usuário.
6. Crie `.apresentaAI/<titulo-da-apresentacao>/` na raiz do projeto onde a
   skill foi invocada, como projeto web autocontido.
7. Implemente HTML, CSS e JavaScript na menor complexidade que entregue a
   experiência pedida.
   Para um deck novo sem controlador próprio, copie
   [a base de palco](assets/palco-base/index.html) com `palco.css` e `palco.js`
   da mesma pasta. Inclua tokens e componentes do design. A base abre por
   arquivo ou HTTP, centraliza o palco 16:9, numera as telas pela ordem do DOM
   e emite `slidechange` com `detail.index` e `detail.id`. Use esse evento
   para conectar a participação opcional. Use classes de composição ou IDs
   semânticos estáveis nas regras locais. Ao trocar ou remover uma tela,
   confira a correspondência de roteiro, matriz, plano e manifesto móvel.
   Antes da revisão visual, execute
   `node scripts/validar_planejamento.cjs caminho/para/planejamento.json caminho/para/index.html`
   a partir da skill. Corrija o contrato ou a marcação até que IDs, ordem e
   componentes declarados coincidam.
8. Inclua navegação por teclado: próxima, anterior, início e fim. Ofereça
   tela cheia e mantenha suporte a passador quando ele emular essas teclas.
   Em tela cheia, use a Screen Wake Lock API para manter a tela ativa durante
   a apresentação. Solicite o bloqueio somente com `fullscreenElement` ativo e
   documento visível; libere-o ao sair da tela cheia ou em `pagehide`; volte a
   solicitá-lo após retorno de visibilidade. Falha ou indisponibilidade da API
   não pode interromper navegação. Registre no arquivo de execução que alguns
   navegadores exigem contexto seguro para esse recurso. `file://` não é modo
   suportado para prometer Wake Lock: para apresentação local, instrua abrir o
   deck por `http://localhost`; o URL de QR para participantes pode continuar
   usando IP local. Se o usuário exigir execução direta por arquivo, explique
   que a única alternativa confiável é bloqueio de repouso do sistema
   operacional, iniciado fora do navegador.
9. Garanta tela horizontal em `1366×768` (16:9) como resolução mínima e
   priorize Full HD (1920×1080). Adapte para resoluções maiores sem comprometer
   leitura. Quando a capa usar guia visual de teclado, use o componente do
   design sem recriá-lo localmente e valide em HD e Full HD todos os seus
   elementos: rótulos, teclas, padding e espaçamento.
10. Construa layout defensivo: trilhas de grid flexíveis usam `minmax(0, 1fr)`
    ou equivalente, componentes internos podem encolher e conteúdo visual fica
    dentro da área segura. `overflow: hidden` nunca é correção para componente
    que escapou; corrija dimensão, trilha, espaçamento ou composição na origem.
    Dimensione o palco por uma dimensão primária e derive a outra; não combine
    largura fixa com limite de altura que quebre a razão 16:9. Antes de replicar
    o deck, calibre cada arquétipo de layout (pergunta, tese, cards, fluxo e
    comparação) com seu maior conteúdo previsto. O orçamento vertical inclui
    título, conteúdo, rodapé e área segura. Se não couber, divida conteúdo,
    reduza a composição ou escolha outro arquétipo; não reduza tudo por padrão.
11. Inclua um arquivo local com instruções de execução e controles.
12. Faça revisão visual e funcional; incorpore ajustes solicitados pelo usuário
   no mesmo projeto. Após uma versão ser aprovada, crie sua referência aprovada
   em `referencia-visual/aprovada/` dentro do deck com
   `node scripts/capturar_palco.cjs caminho/para/index.html caminho/para/referencia-visual/aprovada`.
   Para nova geração ou reestruturação, capture a candidata em
   `referencia-visual/candidata/` e gere
   `referencia-visual/comparacao.html` com
   `node scripts/montar_comparacao_visual.cjs referencia-visual/aprovada referencia-visual/candidata referencia-visual/comparacao.html`.
   Apresente o relatório lado a lado ao usuário. Ele compara composição,
   escala, distribuição e legibilidade; não aprova conteúdo automaticamente.

Use Git como histórico padrão. Não crie cópias versionadas da apresentação por
padrão; crie uma versão empacotada somente quando solicitada.

# Decisões

- O roteiro orienta quantidade e sequência de telas; ajuste a contagem quando
  dividir ou unir telas melhorar clareza, ritmo ou contexto. Interação pode ser
  decidida após a primeira visualização, salvo orientação antecipada.
- Use imagens e gráficos quando esclarecerem, variarem ritmo ou sustentarem a
  narrativa; não como preenchimento decorativo.
- Animação só entra quando reforçar compreensão ou passagem narrativa. A tela
  deve continuar utilizável sem ela.
- Páginas auxiliares sincronizadas, QR codes, enquetes e atualização em tempo
  real são opcionais por apresentação. Avalie-os como extensão, não requisito
  básico.
- Antes de incluir interatividade em tempo real, confirme publicação,
  conectividade, destino do QR code, comportamento de votação e infraestrutura
  autorizada. Não presuma que um projeto autocontido oferece sincronização
  entre dispositivos.
- Uma versão ruim pode estar tecnicamente correta, mas perder atenção por
  organização, cadência ou narrativa fraca. Corrija antes de polimento visual
  secundário.

# Pronto quando

- Conteúdo e ordem correspondem ao roteiro aprovado; ajustes de quantidade de
  telas melhoram clareza, ritmo ou contexto.
- Fluxo é claro em uma leitura de apresentação, não apenas como página longa.
- Não há texto cortado, oculto, sobreposto indevidamente ou fora do quadro.
- Tipografia continua legível e contraste continua suficiente em cenário de
  projetor com baixa fidelidade.
- Próxima, anterior, início, fim e tela cheia funcionam. Em tela cheia, a
  Screen Wake Lock mantém a tela ativa quando o navegador a suportar; sair da
  tela cheia libera o bloqueio sem erro. O teste de Wake Lock é feito por
  `localhost` ou HTTPS, nunca apenas por `file://`.
- Layout mantém composição em 1366×768 e 1920×1080, em proporção 16:9.
- Nas duas resoluções, confira a largura da grade renderizada, a folga até o
  rodapé e a distância entre as caixas do kicker e do título. Uma regra CSS
  que ainda aponta para a antiga posição da tela pode passar na prova de
  transbordamento e deixar o conteúdo concentrado à esquerda em Full HD.
- Cada tela usa imagem, mockup, cards, fluxo, comparação, dado ou outro
  recurso visual coerente; não entregue tela de conteúdo como texto puro.
- Cada tela possui Plano visual por tela com decisão explícita de imagem e
  decisão de composição vertical; o inventário final de assets confirma os
  recursos planejados.
- O inventário de composições demonstra variedade coerente com a narrativa;
  cards predominantes sem justificativa de conteúdo exigem novo planejamento.
- Para cada recurso visual previsto pela direção de imagens, o Plano visual
  registra uma tela que o usa ou incompatibilidade concreta; fluxo e cards não
  bastam para descartá-lo.
- Componentes equivalentes usam os componentes literais do design selecionado;
  CSS local não pode sobrescrever seus seletores para simular um componente.
- Conteúdo permanece visualmente distribuído no palco: nenhuma família de
  telas pode concentrar título e conteúdo no topo deixando espaço inferior
  ocioso sem justificativa narrativa.
- Cards mantêm título em negrito, corpo regular e escala tipográfica uniforme.
- Cards equivalentes seguem o componente-padrão do design; diferenças de fundo,
  borda ou acento representam significado, nunca variação acidental de layout.
- Todo card visível mantém cor interna, sombra e borda superior na espessura definida pelo design, ou `0.5rem` se ele não a definir.
  Variação semântica de card altera tokens da moldura completa e é registrada
  no Plano visual por tela.
- Elemento gráfico não suprime qualificador, contexto ou conclusão do roteiro;
  preserve tudo no gráfico, legenda ou conteúdo de apoio.
- Imagens geradas foram inspecionadas, são locais e preservam contraste. Fundos
  ficam fora do grid e discretos diante do conteúdo.
- Revisão de cobertura confronta cada tela com a Matriz por tela: conteúdo não
  pode sumir, duplicar ou migrar entre telas sem decisão registrada. Revise a
  composição de todas as telas, incluindo espaços vazios, texto repetido sobre
  gráfico, contraste do fundo e componentes do design.
- `planejamento.md` foi revisado em linguagem comum e `planejamento.json` foi
  validado contra o HTML: cada tela possui o mesmo ID e ordem, fonte, mensagem,
  conteúdo obrigatório e proibido, componente, composição, decisão de imagem
  e ocupação vertical.
- Abertura contém guia de teclado quando a referência o possuir; todas as
  telas exibem contador ou numeração equivalente.
- Valide em tela cheia e fora dela; rodapé, contador e marca nunca podem sair
  do enquadramento. Ao converter texto em gráfico, mantenha todas as
  informações do roteiro representadas no gráfico, legenda ou conteúdo apoio.
- Faça prova de geometria em todas as telas, em 1366×768 e 1920×1080, ambas
  em 16:9: todo componente visível deve permanecer dentro da área segura. Se o
  navegador ou inspeção de geometria não estiver disponível, registre a
  validação visual como pendente; validação estática não a substitui.
- Para a base de palco com `data-slide-id`, rode
  `node scripts/verificar_palco.cjs caminho/para/index.html` a partir da
  skill, em um ambiente com Playwright e Chromium. O script mede cada tela
  nas duas resoluções e em janela 1280×900, testa navegação, paginação e
  sobreposição entre rodapé e conteúdo textual.
  Para usar um Chrome já instalado, informe o executável em `CHROME_PATH`.
  A inspeção visual complementa essas medidas para contraste e distribuição.
- Uma versão aprovada possui capturas em HD e Full HD em
  `referencia-visual/aprovada/`. Nova versão possui capturas equivalentes em
  `referencia-visual/candidata/` e relatório local lado a lado. Diferença visual
  exige revisão humana; não trate proximidade de pixels como equivalência de
  conteúdo ou aprovação automática.
- A prova é reprovada se a razão do palco não ficar entre 1,76 e 1,79, se
  `scrollHeight` exceder `clientHeight`, ou se qualquer caixa visível exceder
  a área segura. Execute-a também no container incorporado ou janela reduzida
  que será usada para revisão; não valide apenas em tela cheia.
- Mídia, animações, links e recursos interativos funcionam sem erros visíveis
  no console.
- O usuário revisou a primeira versão e os ajustes solicitados foram aplicados
  ou registrados como pendentes.

# Casos que já deram errado

Ainda não há falhas históricas. Registre aqui somente falhas recorrentes
observadas em entregas reais e a contramedida específica; não transforme uma
preferência isolada em regra geral.

# Skills auxiliares

`$apresenta-design` é uma skill independente para entrevistar, criar e evoluir
designs locais antes da apresentação. Não a use para criar uma tela ou roteiro.

Crie uma skill auxiliar somente para capacidade independente, reutilizável e
não presente em toda apresentação. Exemplos: páginas secundárias sincronizadas
com a tela principal, QR codes de participação, enquetes e atualização de
resultados em tempo real.

Use `$apresenta-interacao` quando a entrega incluir acompanhamento pelo celular,
sessão ao vivo ou atividade de participação. A integração usa o manifesto e os
templates do palco, do espectador e do moderador fornecidos pela skill.
Para essa interatividade, a skill auxiliar deve definir requisitos de
publicação, sincronização e validação em múltiplos dispositivos antes de a
funcionalidade ser implementada.

Mantenha criação da apresentação, narrativa, design pattern e identidade
visual nesta skill principal. Não crie skill auxiliar apenas por haver um
recurso opcional em uma apresentação.
