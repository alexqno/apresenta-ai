# Contrato de votação

Use este modelo para uma enquete de escolha única por participante.

## Manifesto

Cada tela pode conter `poll`. O índice da tela no array é o `slideIndex`.

```json
{
  "number": 3,
  "title": "Como a IA já entra no seu trabalho?",
  "summary": "Escolha o uso mais próximo do seu dia a dia.",
  "links": [],
  "poll": {
    "id": "ia-usage",
    "question": "Como você usa IA hoje?",
    "options": [
      { "id": "explore", "label": "Pergunto e exploro" },
      { "id": "agent", "label": "Coloco agente no fluxo" }
    ]
  }
}
```

No início da sessão, o apresentador envia ao servidor:

```json
{
  "polls": {
    "ia-usage": {
      "slideIndex": 2,
      "options": ["explore", "agent"]
    }
  }
}
```

## Estados e visual

O servidor guarda voto por `participantId` apenas enquanto a sessão efêmera
existe. O payload público contém somente totais e total geral.

No palco, calcule percentuais inteiros pelo método dos maiores restos: trunque,
depois distribua os pontos restantes aos maiores restos até totalizar 100%.
O maior total preenche a barra inteira; os demais usam essa barra como base.
Empates são líderes. Líderes usam gradiente de destaque; os demais usam
gradiente secundário derivado dos tokens do design.

No celular, `is-selected` representa somente voto do dispositivo. Não exponha
resultado coletivo, percentual ou ordem dos mais votados.

## Galeria

Copie `assets/galeria-interacoes/` para a entrega com interação. Ela deve
continuar separada da apresentação e ilustrar resultado no palco e escolha no
celular. Substitua os tokens de fallback pelos tokens reais do design quando
existirem.
