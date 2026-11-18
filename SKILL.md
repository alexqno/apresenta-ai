# Pra que serve

Criar páginas web interativas para palestras, em narrativa sequencial e
apresentáveis em tela cheia. A entrega é uma apresentação web, não um arquivo
de slides tradicional.

# Quando usar

Use quando o pedido for criar ou evoluir uma apresentação web a partir de um
roteiro, artigo-base ou conteúdo sequencial. O acionamento é manual no chat.

# O que precisa

- Roteiro sequencial, com expectativa de telas e pontos centrais. Um
  artigo-base ou texto completo pode complementar contexto e ser convertido em
  roteiro antes da implementação.
- Design pattern escolhido e disponível em `arquivos/designs/<instituicao>/`.
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
qualquer artefato visual. Não escolha `korporate` automaticamente apenas por
ser o primeiro design disponível.

Se o design necessário não existir, interrompa a criação da apresentação e
trate primeiro da criação ou inclusão desse design.

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

# Passos

1. Confirme insumos e escolha de design pattern.
2. Transforme conteúdo em sequência de telas, preservando ideias centrais e
   ritmo do roteiro. Divida telas densas; una telas curtas ou com o mesmo
   contexto quando isso melhorar a narrativa.
3. Planeje ritmo, hierarquia, imagens, gráficos e interações que reforcem a
   narrativa.
4. Crie `.apresentaAI/<titulo-da-apresentacao>/` na raiz do projeto onde a
   skill foi invocada, como projeto web autocontido.
5. Implemente HTML, CSS e JavaScript na menor complexidade que entregue a
   experiência pedida.
6. Inclua navegação por teclado: próxima, anterior, início e fim. Ofereça
   tela cheia e mantenha suporte a passador quando ele emular essas teclas.
7. Priorize tela horizontal Full HD (1920×1080), com layout seguro em telas de
   apresentação comuns. Adapte para outras resoluções sem comprometer leitura.
8. Inclua um arquivo local com instruções de execução e controles.
9. Faça revisão visual e funcional; incorpore ajustes solicitados pelo usuário
   no mesmo projeto.

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
- Próxima, anterior, início, fim e tela cheia funcionam.
- Layout mantém composição em 1920×1080 e em resoluções de apresentação
  compatíveis.
- Mídia, animações, links e recursos interativos funcionam sem erros visíveis
  no console.
- O usuário revisou a primeira versão e os ajustes solicitados foram aplicados
  ou registrados como pendentes.

# Casos que já deram errado

Ainda não há falhas históricas. Registre aqui somente falhas recorrentes
observadas em entregas reais e a contramedida específica; não transforme uma
preferência isolada em regra geral.

# Skills auxiliares

Crie uma skill auxiliar somente para capacidade independente, reutilizável e
não presente em toda apresentação. Exemplos: páginas secundárias sincronizadas
com a tela principal, QR codes de participação, enquetes e atualização de
resultados em tempo real.

Para essa interatividade, uma skill auxiliar deve definir requisitos de
publicação, sincronização e validação em múltiplos dispositivos antes de a
funcionalidade ser implementada.

Mantenha criação da apresentação, narrativa, design pattern e identidade
visual nesta skill principal. Não crie skill auxiliar apenas por haver um
recurso opcional em uma apresentação.
