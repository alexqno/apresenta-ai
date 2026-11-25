# Integração do palco

Sirva o diretório pai das entregas. Abra o deck em `/<pasta>/index.html`.
O servidor usa a pasta da página para construir a rota pública.
Copie `assets/galeria-interacoes/participacao.json` para a raiz do deck e
substitua os títulos, perguntas, opções e IDs. Inclua uma entrada por tela,
na ordem da apresentação, mesmo quando ela não tiver interação.

Inclua `<link rel="stylesheet" href="./palco/interacoes.css">` no HTML.
Reserve um `<aside data-entrada></aside>` na capa e um
`<div data-interacao></div>` em cada tela interativa. O adaptador adiciona QR
puro no canto superior direito; mantenha o contêiner dentro de uma `.slide` ou
elemento `[data-slide]`. Depois de carregar `palco.js`, use o bootstrap. Ele
consome `slidechange`, restaura a tela da sessão após recarga e não acessa
estado privado do controlador:

```js
async function conectarParticipacao() {
  try {
    const { connectParticipation } = await import('./palco/bootstrap.mjs');
    await connectParticipation();
  } catch {
    document.querySelector('[data-entrada]').textContent =
      'Participação indisponível. A apresentação continua local.';
  }
}
conectarParticipacao();
```

O bootstrap exige a base com `.presentation-stage` e `data-slide-id`. A
inicialização assíncrona mantém os controles disponíveis. O evento `slide`
entrega o estado público da sessão. A reconexão usa SSE com polling durante
indisponibilidade. O QR da capa cria nova sessão; QRs nas telas interativas
são somente de entrada. Somente moderação inclui token no fragmento.

Valide a galeria em `/<pasta>/galeria-interacoes/index.html`. Os três
botões exercitam os mesmos componentes da apresentação. A referência da
triagem é revelada somente no painel privado do moderador; o palco apenas
reflete o estado da sessão. O clique no papel abre o diálogo. Para validar
moderação de ponta a ponta, abra a página pelo QR, navegue até a tela do
quadro, envie texto, abra o painel privado e aprove ou descarte.
