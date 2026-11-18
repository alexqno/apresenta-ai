# Sistema de Design Korporate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir um sistema de design reutilizável da Korporate e uma galeria web autocontida para apresentações 16:9.

**Architecture:** A pasta `arquivos/designs/korporate/` será um pacote estático, sem dependências de rede. Tokens CSS centralizam a identidade; componentes CSS montam padrões visuais; uma galeria HTML demonstra o sistema em telas navegáveis, controlada por JavaScript modular testável.

**Tech Stack:** HTML5, CSS3, SVG inline, JavaScript ES modules, Node.js `node:test`.

**Spec:** `docs/superpowers/specs/2026-11-18-korporate-design-system-design.md`

## Global Constraints

- Entregar em `arquivos/designs/korporate/`; não criar apresentação de conteúdo final nesta etapa.
- Usar logos somente das fontes oficiais registradas no design doc.
- Não depender de rede, frameworks ou bibliotecas externas.
- Priorizar 1920x1080, tela cheia, contraste para projeção e leitura à distância.
- Implementar teclas: `ArrowRight`, `Space`, `ArrowLeft`, `Home`, `End` e `F`.
- Respeitar `prefers-reduced-motion` e não comunicar estado apenas com cor.
- Linguagem visual: Industrial Premium Playful; evitar cyberpunk, robôs genéricos e fotos corporativas posadas.

## Review Focus

- Teclas pressionadas dentro de elementos interativos não devem avançar a galeria acidentalmente; teste na Task 4.
- Primeiro e último exemplos não podem ultrapassar limites da navegação; teste na Task 4.
- Modo reduzido deve remover transições e animações não essenciais; teste de regra CSS na Task 3.
- Exemplo de alerta e sucesso precisa ter rótulo textual além da cor; teste de marcação na Task 3.
- Galeria em 1366x768 deve manter conteúdo principal dentro do quadro, sem rolagem indesejada; inspeção visual na Task 5.

---

### Task 1: Fundar pacote e tokens de marca

**Files:**
- Create: `arquivos/designs/korporate/README.md`
- Create: `arquivos/designs/korporate/tokens.css`
- Create: `arquivos/designs/korporate/assets/README.md`
- Create: `arquivos/designs/korporate/assets/korporate-mark.svg`

**Interfaces:**
- Consumes: fontes oficiais de logo e manual listadas no design doc.
- Produces: custom properties `--kp-*` e arquivo local `assets/korporate-mark.svg`, consumidos por `components.css` e `gallery.html`.

- [ ] **Step 1: Criar teste estático de tokens e ativos**

Create `arquivos/designs/korporate/test/package.test.mjs` with assertions that `tokens.css` defines foreground, background, brand, data-positive, data-alert and motion tokens, and `assets/README.md` identifies the official source URL.

- [ ] **Step 2: Executar teste para confirmar falha**

Run: `node --test arquivos/designs/korporate/test/package.test.mjs`
Expected: FAIL because package files do not exist.

- [ ] **Step 3: Criar tokens, ativo e documentação de origem**

Extract official HEX values, font guidance and an approved logo variant from the referenced manual/assets. Record source URL, variant, retrieval date and any restriction in `assets/README.md`. Define colors, typography stack, spacing scale, radii, shadows, z-index and motion durations as `--kp-*` variables in `tokens.css`.

- [ ] **Step 4: Executar teste de pacote**

Run: `node --test arquivos/designs/korporate/test/package.test.mjs`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add arquivos/designs/korporate
git commit -m "feat: add korporate design tokens"
```

### Task 2: Documentar sistema e componentes reutilizáveis

**Files:**
- Modify: `arquivos/designs/korporate/README.md`
- Create: `arquivos/designs/korporate/design-rationale.md`
- Create: `arquivos/designs/korporate/components.css`
- Modify: `arquivos/designs/korporate/test/package.test.mjs`

**Interfaces:**
- Consumes: `tokens.css` custom properties and `assets/korporate-mark.svg` from Task 1.
- Produces: CSS classes `.kp-slide`, `.kp-card`, `.kp-kicker`, `.kp-metric`, `.kp-status`, `.kp-flow` and `.kp-code`, consumed by the gallery.

- [ ] **Step 1: Escrever testes de contrato para componentes**

Add assertions that `components.css` contains every produced class and that `design-rationale.md` defines color roles, typography hierarchy, logo placement, do/don't examples and accessibility rules.

- [ ] **Step 2: Executar testes para confirmar falha**

Run: `node --test arquivos/designs/korporate/test/package.test.mjs`
Expected: FAIL because reusable components and rationale are absent.

- [ ] **Step 3: Implementar primitives CSS e documentação**

Use 12-column slide grid, 7% safe margin, warm-light default surfaces, controlled dark/gradient variants, semantic data colors and `prefers-reduced-motion` override. Document when each component fits a narrative, not only its CSS class.

- [ ] **Step 4: Executar testes de componentes**

Run: `node --test arquivos/designs/korporate/test/package.test.mjs`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add arquivos/designs/korporate
git commit -m "feat: add korporate presentation components"
```

### Task 3: Criar galeria visual de padrões

**Files:**
- Create: `arquivos/designs/korporate/gallery.html`
- Create: `arquivos/designs/korporate/gallery.css`
- Modify: `arquivos/designs/korporate/test/package.test.mjs`

**Interfaces:**
- Consumes: `tokens.css`, `components.css` and `assets/korporate-mark.svg`.
- Produces: semantic markup with `[data-slide]`, `[data-status]`, `[data-control]` and `#slide-counter`, consumed by `gallery.js`.

- [ ] **Step 1: Escrever testes de marcação e acessibilidade**

Assert that `gallery.html` contains examples of cover, chapter, content, data, IA flow and closing; verify explicit text labels for success/attention and viewport/meta description. Assert `gallery.css` includes `@media (prefers-reduced-motion: reduce)`.

- [ ] **Step 2: Executar testes para confirmar falha**

Run: `node --test arquivos/designs/korporate/test/package.test.mjs`
Expected: FAIL because gallery files are absent.

- [ ] **Step 3: Montar telas demonstrativas em 16:9**

Build six to eight examples: three covers, chapter transition, argument content, quote/steps, data comparison, IA applied flow and closing. Use SVG/HTML charts and abstract interface metaphors. Mark sample values as demonstrative. Provide visible controls and local usage instructions.

- [ ] **Step 4: Executar testes de marcação**

Run: `node --test arquivos/designs/korporate/test/package.test.mjs`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add arquivos/designs/korporate
git commit -m "feat: add korporate design gallery"
```

### Task 4: Implementar navegação, tela cheia e testes comportamentais

**Files:**
- Create: `arquivos/designs/korporate/gallery.js`
- Create: `arquivos/designs/korporate/test/gallery-controller.test.mjs`
- Modify: `arquivos/designs/korporate/gallery.html`

**Interfaces:**
- Consumes: `[data-slide]`, `[data-control]`, `#slide-counter` and `#gallery-status` from Task 3.
- Produces: `clampIndex(index, count)`, `keyToAction(event)` and `createGalleryController(options)` exported from `gallery.js`.

- [ ] **Step 1: Escrever testes de controlador**

Use `node:test` to assert `clampIndex(-1, 8) === 0`, `clampIndex(8, 8) === 7`, `ArrowRight`/`Space` map to `next`, `ArrowLeft` maps to `previous`, `Home`/`End` map to boundaries, and events from `INPUT`, `TEXTAREA`, `SELECT` and contenteditable map to no action.

- [ ] **Step 2: Executar testes para confirmar falha**

Run: `node --test arquivos/designs/korporate/test/gallery-controller.test.mjs`
Expected: FAIL because `gallery.js` is absent.

- [ ] **Step 3: Implementar módulo de galeria**

Implement exact exports above. Bind keyboard and button actions, maintain one active slide with `aria-hidden`, update `#slide-counter` and polite `#gallery-status`, and toggle `document.fullscreenElement` on `F` only when focus is not editable.

- [ ] **Step 4: Executar todos os testes Node**

Run: `node --test arquivos/designs/korporate/test/*.test.mjs`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add arquivos/designs/korporate
git commit -m "feat: add gallery navigation controls"
```

### Task 5: Validar entrega em navegador e documentar uso

**Files:**
- Modify: `arquivos/designs/korporate/README.md`
- Modify: `arquivos/designs/korporate/gallery.html`
- Modify: `arquivos/designs/korporate/gallery.css`

**Interfaces:**
- Consumes: pacote concluído nas Tasks 1-4.
- Produces: galeria visualmente aprovada e instruções locais completas.

- [ ] **Step 1: Abrir galeria em navegador e inspecionar 1920x1080**

Verify every slide has no overlap, cropped copy, accidental scrollbars or weak text contrast.

- [ ] **Step 2: Validar 1366x768 e tela cheia**

Verify responsive scale retains all key content in frame and `F` enters/exits fullscreen where browser permission permits.

- [ ] **Step 3: Validar teclado e modo reduzido**

Test forward, back, Home, End, Space, buttons, and enable reduced-motion emulation. Verify focus inside a control does not navigate slides.

- [ ] **Step 4: Registrar execução e controles**

Document a zero-install local command, every control, selected logo asset, design intent and accessibility behavior in `README.md`.

- [ ] **Step 5: Executar checks finais e commit**

Run: `node --test arquivos/designs/korporate/test/*.test.mjs`
Expected: PASS.

```bash
git add arquivos/designs/korporate
git commit -m "docs: finalize korporate design system"
```

## Self-review

- Spec coverage: Tasks 1-2 implement tokens, components, sources, rationale and accessibility; Tasks 3-4 implement the required gallery and controls; Task 5 validates all acceptance criteria. No gaps found.
- Interfaces: component class names, gallery data attributes and JavaScript exports are defined before consumption.
- Review focus: each likely input/failure mode has an owning task and test or visual inspection.
- Proportion: plan defines interfaces and checks, without prescribing component bodies or page copy beyond specification.
