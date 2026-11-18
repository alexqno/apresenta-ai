# apresenta-ai

Conjunto de skills para criar apresentações web e identidades visuais locais.

## Instalação

A pasta [`apresenta-ai/`](./apresenta-ai/) cria apresentações web. A pasta
[`apresenta-design/`](./apresenta-design/) cria ou evolui designs locais.

URLs individuais:

```text
https://github.com/alexqno/apresenta-ai/tree/master/apresenta-ai
https://github.com/alexqno/apresenta-ai/tree/master/apresenta-design
```

No instalador padrão de skills do Codex, instale ambas com um comando:

```bash
install-skill-from-github.py \
  --repo alexqno/apresenta-ai \
  --ref master \
  --path apresenta-ai apresenta-design
```

Após instalação, crie primeiro um design com `$apresenta-design` quando o
projeto ainda não tiver um. O design fica em:

```text
.apresentaAI/designs/<instituicao>/
```

Depois, invoque `$apresenta-ai` para criar uma apresentação web a partir de
roteiro ou conteúdo-base.

## Conteúdo do pacote

- `apresenta-ai/`: criação de apresentações; não inclui marca ou identidade.
- `apresenta-design/`: entrevista, template neutro e criação de designs locais.
