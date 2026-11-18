# Sistema de design Korporate

## Intenção

Criar uma identidade reutilizável para apresentações web da Korporate. A primeira aplicação é uma apresentação interna sobre IA aplicada ao trabalho, de especificação a desenvolvimento. O sistema deve também atender futuras apresentações corporativas sem repetir o aspecto rígido e genérico da referência analisada.

## Público e tom

- Público inicial: colaboradores internos.
- Tom: tecnológico, descontraído, claro e confiável.
- Percepção prioritária: sofisticação tecnológica.
- Personalidade: `Industrial Premium Playful`.

## Objetivos

- Tornar apresentações reconhecíveis como Korporate sem depender de um único fundo ou layout.
- Sustentar narrativa, leitura à distância e visualização de dados.
- Dar à IA aplicada uma linguagem humana: fluxos, interfaces, metáforas e ilustrações leves.
- Manter o sistema autocontido e utilizável em navegador moderno, sem serviços externos obrigatórios.

## Não objetivos

- Não redesenhar a marca Korporate nem inventar uma identidade paralela.
- Não reproduzir a apresentação NPS fornecida.
- Não criar uma apresentação de conteúdo final nesta etapa.
- Não usar estética cyberpunk, robôs genéricos, fotos corporativas posadas ou decoração que concorra com o conteúdo.

## Evidências e restrições

- Fontes consultadas: manual de marca, variantes de logo, wallpapers e bases de apresentações no Drive; PDF NPS 2025 como referência negativa.
- A marca existente combina grafite/preto, laranja-vermelho e branco. Azul e vermelho deverão ser semânticos em dados, não cores decorativas recorrentes.
- A entrega ficará em `arquivos/designs/korporate/`, como material reutilizável.
- Logos oficiais deverão ser copiados apenas das fontes autorizadas do Drive e mantidos com proporções e área de proteção adequadas.
- Fonte primária de marca: [Manual de Marca - Korporate.pdf](https://drive.google.com/file/d/1eWMUsmnYu4gbChgbH3MTb2s8U7xm1vg4/view). Logos oficiais: [pasta Marca - PNG](https://drive.google.com/drive/folders/1qCSJV2pTpxz3LDK8kO1I0uL7Jfz7nBDs) e [pasta Marca - vetor](https://drive.google.com/drive/folders/1YFyGjjVfxFayaKZ0rxubdm7NjhVVMVz_). Referências complementares: [Wallpapers](https://drive.google.com/drive/folders/1cRUEamPvEIt2dsYPAoylSWvoMxl8hCmF) e [Base PPT](https://drive.google.com/drive/folders/1JM188tFMTgJipmz078koO4haS1jbAdR3).

## Abordagens consideradas

1. **Industrial Premium.** Grafite, laranja, vidro fumê e linhas técnicas. Sofisticado, mas sério demais para o público interno inicial.
2. **Data-luxury.** Fundo claro, espaço negativo e acentos mínimos. Muito executivo; menor presença em palco e menor ludicidade.
3. **Industrial Premium Playful - escolhida.** Mantém estrutura e acabamento premium, com respiro claro, ilustrações, metáforas e movimento discreto. Equilibra reconhecimento corporativo, leveza e reuso.

## Direção visual escolhida

### Cores

- Fundos predominantes: branco quente e cinza claro.
- Estrutura e contraste: grafite/preto Korporate.
- Ênfase de marca: laranja Korporate, em gradiente controlado para capas, capítulos e destaques.
- Dados: azul para positivo/informativo, vermelho para alerta e cinzas para neutro. Acessibilidade prevalece sobre a associação de marca.
- O construtor deve extrair e registrar valores HEX definitivos do manual de marca ou dos ativos oficiais antes de codificar tokens finais.

### Tipografia e composição

- Sans-serif de sistema, com pilha local segura até a fonte oficial ser confirmada no manual.
- Títulos amplos e concisos; corpo em frases curtas e blocos pequenos.
- Grid 12 colunas em tela 16:9 Full HD; margem segura de 7%.
- Blocos assimétricos, cartões com bordas suaves e espaços generosos.
- Marca discreta no rodapé ou em tela de abertura/encerramento; nunca como ornamento repetido em cada componente.

### Ilustração e movimento

- Ilustrações abstratas: nós, módulos, fluxos, cursores, documentos e estados de interface. Elas explicam uma ideia, não só decoram.
- Microanimações progressivas em entrada de etapas, contagem e comparação.
- Todo conteúdo deve manter entendimento integral com `prefers-reduced-motion`.

## Entregáveis

1. `README.md`: propósito, escopo, como reutilizar e regras de acessibilidade.
2. `tokens.css`: variáveis de cor, tipografia, espaçamento, raio, sombra e duração de movimento.
3. `components.css`: primitives reutilizáveis de apresentação.
4. `assets/`: logos oficiais autorizados e formas vetoriais próprias simples; arquivo de origem e licença/atribuição registrados quando aplicável.
5. `gallery.html` e `gallery.js`: galeria navegável em 16:9, tela cheia, com exemplos reais e teclado.
6. `design-rationale.md`: decisões, usos corretos/incorretos e papéis semânticos da paleta.

## Galeria de componentes

- Capas: premium clara, premium escura e energia em gradiente.
- Capítulo e transição: número, frase de tese e acento ilustrado.
- Conteúdo: título + argumento, duas colunas, citação, sequência de passos.
- Dados: número-chave, comparação, barras, linha de tendência e estado de atenção/sucesso. Gráficos serão HTML/SVG, não imagens de planilha.
- IA aplicada: fluxo `especificar -> colaborar -> desenvolver -> validar`, prompts, blocos de código e estados antes/depois.
- Encerramento: síntese, chamada à ação e contatos.

## Qualidade e aceitação

- Todos os exemplos devem funcionar em 1920x1080, escala responsiva e tela cheia.
- Navegação: seta direita/espaço/próxima, seta esquerda/anterior, Home/início, End/fim e `F`/tela cheia quando suportado.
- Contraste deve ser adequado para projeção; não depender apenas de cor para comunicar estado.
- Sem dependências de rede e sem erros visíveis no console.
- A galeria deve documentar os controles localmente e cumprir `prefers-reduced-motion`.

## Decisões do construtor

- Selecionar proporções exatas dos logos dentre os ativos oficiais.
- Criar ícones e formas em SVG próprio apenas quando não substituírem o logo.
- Escolher dados demonstrativos fictícios para a galeria, claramente rotulados como exemplo.
