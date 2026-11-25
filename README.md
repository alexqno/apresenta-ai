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

## Atualização

Cada release mantém `apresenta-ai` e `apresenta-design` na mesma versão.
Verifique atualizações antes de substituir a instalação:

```bash
python3 ~/.codex/skills/apresenta-ai/scripts/update_skills.py --check
```

Para atualizar para a versão estável mais recente:

```bash
python3 ~/.codex/skills/apresenta-ai/scripts/update_skills.py --yes
```

Para instalar uma versão específica, use sua tag:

```bash
python3 ~/.codex/skills/apresenta-ai/scripts/update_skills.py --yes --ref v0.2.0
```

O atualizador baixa os três pacotes, valida que `apresenta-ai` e
`apresenta-design` usam a mesma versão e só então substitui a instalação. A
skill auxiliar `apresenta-interacao` possui versão própria. Se a troca falhar,
restaura a versão anterior.
Abra uma nova conversa após atualizar para recarregar as instruções.

Instalações anteriores que não possuem `update_skills.py` exigem uma
reinstalação manual única. Remova ambas as pastas e execute novamente o comando
de instalação desta documentação.

## Releases

`master` recebe mudanças somente por PR. Após cada merge, Release Please cria
ou atualiza um PR de release. O merge desse PR publica tag, GitHub Release,
`CHANGELOG.md` e versões de `apresenta-ai` e `apresenta-design`.

Os commits seguem Conventional Commits: `fix` incrementa patch, `feat`
incrementa minor e uma alteração incompatível incrementa major.

No GitHub, habilite em **Settings > Actions > General** permissões de leitura e
escrita para workflows e autorização para GitHub Actions criar pull requests.

## Conteúdo do pacote

- `apresenta-ai/`: criação de apresentações; não inclui marca ou identidade.
- `apresenta-design/`: entrevista, template neutro e criação de designs locais.
