---
name: apresenta-design
description: Crie ou evolua identidades visuais locais para apresentações web após entrevistar sobre marca, público e contexto. Use antes de apresenta-ai quando o projeto não tiver um design adequado.
metadata:
  short-description: Cria designs para apresentações
---

# Propósito

Criar um design reutilizável para apresentações web no projeto invocador. O
resultado fica em `.apresentaAI/designs/<instituicao>/` e pode ser usado por
`$apresenta-ai`.

# Quando usar

Use quando não houver design para a instituição, quando o design existente não
servir ao novo contexto ou quando o usuário pedir para criar ou evoluir uma
identidade visual de apresentações. Não use para produzir uma apresentação
específica: use `$apresenta-ai` depois que o design estiver definido.

# Entrevista

Antes de criar o design, descubra somente o que altera decisões visuais:

1. instituição, público e objetivo recorrente das apresentações;
2. marca disponível, licença de uso e ativos oficiais;
3. atributos de personalidade, referências desejadas e referências a evitar;
4. paleta, tipografia e restrições de marca já existentes;
5. contexto de exibição, acessibilidade e nível de contraste necessário;
6. padrões que precisam existir, como capa, capítulo, dados, comparação e
   encerramento.
7. estilo de imagens para apresentações: papel narrativo, linguagem visual
   (ilustração, fotografia, interface, diagrama ou mistura), paleta e luz,
   composição e área segura de texto, temas a evitar e quando imagem não deve
   ser usada.

Se faltar marca, tipografia ou referência, registre a limitação e proponha
alternativas genéricas. Não invente logotipo, fonte proprietária ou diretriz
institucional.

# Criação

1. Confirme nome do diretório e se ele já existe.
2. Se existir, inspecione-o e confirme antes de sobrescrever arquivos.
3. Copie `assets/design-template/` para
   `.apresentaAI/designs/<instituicao>/` no projeto invocador.
4. Adapte tokens, componentes, ativos e racional ao que foi confirmado. O
   racional inclui a seção `Direção de imagens`, com escolhas e limites que
   `$apresenta-ai` poderá aplicar sem nova entrevista.
5. Crie uma galeria ou exemplos de padrões apenas se ajudarem a validar o
   design; ela não substitui uma apresentação real.
6. Registre fontes dos ativos e licença ou autorização aplicável.

# Estrutura mínima

```text
.apresentaAI/designs/<instituicao>/
├── README.md
├── tokens.css
├── components.css
├── design-rationale.md
└── assets/
    └── README.md
```

# Pronto quando

- Tokens definem papéis semânticos de cor, tipografia, espaço e movimento.
- Componentes cobrem os padrões confirmados sem impor conteúdo de apresentação.
- Ativos têm origem e uso documentados.
- Racional registra decisões, limites e regras de contraste.
- Racional contém `Direção de imagens`: papel, linguagem visual, composição,
  paleta, área segura para texto e exclusões. Se não houver imagem gerada,
  registre essa decisão explicitamente.
- Design foi revisado em composição 16:9 e mantém leitura à distância.
