# Contrato de diagnóstico ponderado

Use diagnóstico ponderado quando cada participante puder marcar mais de uma
lacuna, prioridade ou risco. Não use para escolha exclusiva.

## Manifesto móvel

Em `participacao.json`, descreva a interação dentro da tela correspondente:

```json
{
  "diagnostic": {
    "id": "task-xray",
    "question": "Quais lacunas travam uma boa tarefa?",
    "maxSelections": 2,
    "highlightThreshold": 3,
    "items": [
      { "id": "objective", "label": "Objetivo pouco claro" },
      { "id": "scope", "label": "Escopo incompleto" },
      { "id": "risk", "label": "Risco implícito" }
    ]
  }
}
```

- `id`: estável, curto e único na apresentação.
- `maxSelections`: máximo de itens que cada navegador pode manter marcado.
- `highlightThreshold`: número de participantes que deve marcar um item antes
  de ele ganhar destaque no palco. Este valor é visual; o servidor não decide
  a aparência.
- `items`: IDs estáveis e rótulos legíveis no celular.

## Sessão local

Ao criar a sessão, envie somente a configuração necessária ao servidor:

```json
{
  "task-xray": {
    "slideIndex": 6,
    "maxSelections": 2,
    "items": ["objective", "scope", "risk"]
  }
}
```

Cada envio substitui a seleção anterior daquele navegador. O endpoint aceita
envios somente enquanto a tela estiver ativa e publica somente totais por
item e total de respostas; nunca publica identificadores individuais.

## Estados obrigatórios

- Celular: item neutro, item selecionado e limite atingido.
- Palco: item abaixo do limiar, item no limiar e contagem/densidade agregada.
- Acessibilidade: botão deve permanecer selecionável para desfazer a escolha,
  mesmo quando o limite foi atingido.

Não trate personagens, ilustrações ou animações narrativas como parte deste
contrato. Eles pertencem à apresentação que os pedir.
