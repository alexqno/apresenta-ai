(() => {
  const ns = 'http://www.w3.org/2000/svg';
  const route = 'M 305 80 H 940 A 150 150 0 0 1 940 380 H 260 A 150 150 0 0 1 260 80 Z';
  const roadWidth = 30;
  const element = (name, attributes) => {
    const node = document.createElementNS(ns, name);
    Object.entries(attributes).forEach(([key, value]) => node.setAttribute(key, value));
    return node;
  };
  const place = (svg, label, point, radius) => {
    const box = element('foreignObject', { x: point.x - radius, y: point.y - radius, width: 2 * radius, height: 2 * radius });
    box.append(label);
    svg.append(box);
  };
  const enhance = () => document.querySelectorAll('.presentation-circuit:not([data-circuit-enhanced])').forEach((panel, index) => {
    const stops = [...panel.querySelectorAll(':scope > .presentation-circuit__stop')];
    if (!stops.length || panel.offsetParent === null) return;
    panel.dataset.circuitEnhanced = 'true';
    const svg = element('svg', { viewBox: '0 0 1200 460', preserveAspectRatio: 'xMidYMid meet', role: 'group', 'aria-label': 'Circuito de etapas' });
    const road = element('path', { d: route, fill: 'none', stroke: 'var(--presentation-color-surface-strong)', 'stroke-width': roadWidth });
    svg.append(road, element('path', { d: route, fill: 'none', stroke: 'var(--presentation-color-surface)', 'stroke-width': 2.5, 'stroke-dasharray': '13 13' }));
    const tile = roadWidth / 2;
    const patternId = `presentation-circuit-start-${index}`;
    const defs = element('defs', {});
    const pattern = element('pattern', { id: patternId, width: tile, height: tile, patternUnits: 'userSpaceOnUse' });
    pattern.append(element('rect', { width: tile, height: tile, fill: 'var(--presentation-color-surface)' }));
    [0, tile / 2].forEach(corner => pattern.append(element('rect', { x: corner, y: corner, width: tile / 2, height: tile / 2, fill: 'var(--presentation-color-surface-strong)' })));
    defs.append(pattern);
    const start = road.getPointAtLength(0);
    svg.append(defs, element('rect', { x: start.x - tile, y: start.y - roadWidth / 2, width: tile * 2, height: roadWidth, fill: `url(#${patternId})` }));
    const interval = road.getTotalLength() / stops.length;
    stops.forEach((stop, position) => place(svg, stop, road.getPointAtLength((position + .5) * interval), 68));
    const learning = panel.querySelector(':scope > .presentation-circuit__learning');
    if (learning) place(svg, learning, { x: 600, y: 230 }, 82);
    panel.append(svg);
  });
  enhance();
  document.addEventListener('presentation-gallery-change', enhance);
  document.addEventListener('slidechange', enhance);
})();
