import { DEFAULT_DECK } from './config';

interface Env {
  ASSETS: { fetch(request: Request): Promise<Response> };
  SESSIONS: DurableObjectNamespace;
}

type Definition = Record<string, unknown>;
type Session = {
  sessionId: string;
  presenterToken: string;
  deck: string;
  participationUrl: string;
  slideIndex: number;
  updatedAt: string;
  expiresAt: string;
  pollDefinitions: Record<string, { slideIndex: number; options: string[] }>;
  votes: Record<string, Record<string, string>>;
  diagnosticDefinitions: Record<string, { slideIndex: number; items: string[]; maxSelections: number }>;
  diagnostics: Record<string, Record<string, string[]>>;
  triageDefinitions: Record<string, { slideIndex: number; categories: string[]; items: string[] }>;
  triages: Record<string, Record<string, Record<string, string>>>;
  triageReferences: Record<string, boolean>;
  postitDefinitions: Record<string, { slideIndex: number; maxLength: number }>;
  postits: Record<string, Postit[]>;
};
type Postit = { id: string; text: string; status: 'pending' | 'approved' | 'discarded'; createdAt: string; style: PostitStyle };
type PostitStyle = { color: string; x: number; y: number; rotation: number; z: number };

const ID = /^[a-z0-9][a-z0-9-]{0,63}$/;
const SESSION = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const encoder = new TextEncoder();

class HttpError extends Error {
  constructor(readonly status: number, message: string) { super(message); }
}

function record(value: unknown, message = 'Objeto inválido.'): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new HttpError(400, message);
  return value as Record<string, unknown>;
}
function string(value: unknown, message: string): string {
  if (typeof value !== 'string' || !value) throw new HttpError(400, message);
  return value;
}
function id(value: unknown, message: string): string {
  const result = string(value, message);
  if (!ID.test(result)) throw new HttpError(400, message);
  return result;
}
function integer(value: unknown, message: string): number {
  if (!Number.isInteger(value) || (value as number) < 0) throw new HttpError(400, message);
  return value as number;
}
function now(): string { return new Date().toISOString(); }
function expires(): string { return new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(); }
function token(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  return btoa(String.fromCharCode(...bytes)).replaceAll('+', '-').replaceAll('/', '_').replaceAll('=', '');
}
function constantTimeEquals(left: string, right: string): boolean {
  if (left.length !== right.length) return false;
  let result = 0;
  for (let index = 0; index < left.length; index += 1) result |= left.charCodeAt(index) ^ right.charCodeAt(index);
  return result === 0;
}
function json(payload: unknown, status = 200): Response {
  return Response.json(payload, { status, headers: { 'cache-control': 'no-store' } });
}
function normalizePolls(source: unknown): Session['pollDefinitions'] {
  const definitions = source === undefined ? { 'ia-usage': { slideIndex: 2, options: ['explore', 'research', 'draft', 'agent', 'automate'] } } : record(source, 'polls inválido.');
  const output: Session['pollDefinitions'] = {};
  for (const [pollId, value] of Object.entries(definitions)) {
    if (!ID.test(pollId)) throw new HttpError(400, 'id de enquete inválido.');
    const definition = record(value, 'definição de enquete inválida.');
    const options = definition.options;
    if (!Array.isArray(options) || options.length < 2 || !options.every((option) => typeof option === 'string' && ID.test(option)) || new Set(options).size !== options.length) throw new HttpError(400, 'opções de enquete inválidas.');
    output[pollId] = { slideIndex: integer(definition.slideIndex, 'slideIndex de enquete inválido.'), options: options as string[] };
  }
  return output;
}
function normalizeDiagnostics(source: unknown): Session['diagnosticDefinitions'] {
  if (source === undefined) return {};
  const output: Session['diagnosticDefinitions'] = {};
  for (const [diagnosticId, value] of Object.entries(record(source, 'diagnostics inválido.'))) {
    if (!ID.test(diagnosticId)) throw new HttpError(400, 'id de diagnóstico inválido.');
    const definition = record(value, 'definição de diagnóstico inválida.');
    const items = definition.items;
    if (!Array.isArray(items) || !items.length || !items.every((item) => typeof item === 'string' && ID.test(item)) || new Set(items).size !== items.length) throw new HttpError(400, 'itens de diagnóstico inválidos.');
    const maxSelections = definition.maxSelections === undefined ? items.length : integer(definition.maxSelections, 'limite de seleção inválido.');
    if (maxSelections < 1 || maxSelections > items.length) throw new HttpError(400, 'limite de seleção inválido.');
    output[diagnosticId] = { slideIndex: integer(definition.slideIndex, 'slideIndex de diagnóstico inválido.'), items: items as string[], maxSelections };
  }
  return output;
}
function normalizeTriages(source: unknown): Session['triageDefinitions'] {
  if (source === undefined) return {};
  const output: Session['triageDefinitions'] = {};
  for (const [triageId, value] of Object.entries(record(source, 'triages inválido.'))) {
    if (!ID.test(triageId)) throw new HttpError(400, 'definição de triagem inválida.');
    const definition = record(value, 'definição de triagem inválida.');
    const categories = definition.categories;
    const items = definition.items;
    if (!Array.isArray(categories) || categories.length < 2 || !Array.isArray(items) || !items.length || ![...categories, ...items].every((item) => typeof item === 'string' && ID.test(item)) || new Set(categories).size !== categories.length || new Set(items).size !== items.length) throw new HttpError(400, 'categorias ou itens de triagem inválidos.');
    output[triageId] = { slideIndex: integer(definition.slideIndex, 'slideIndex de triagem inválido.'), categories: categories as string[], items: items as string[] };
  }
  return output;
}
function normalizePostits(source: unknown): Session['postitDefinitions'] {
  if (source === undefined) return {};
  const output: Session['postitDefinitions'] = {};
  for (const [postitId, value] of Object.entries(record(source, 'postits inválido.'))) {
    if (!ID.test(postitId)) throw new HttpError(400, 'definição de post-it inválida.');
    const definition = record(value, 'definição de post-it inválida.');
    const maxLength = definition.maxLength === undefined ? 280 : integer(definition.maxLength, 'definição de post-it inválida.');
    if (maxLength < 1 || maxLength > 1000) throw new HttpError(400, 'definição de post-it inválida.');
    output[postitId] = { slideIndex: integer(definition.slideIndex, 'definição de post-it inválida.'), maxLength };
  }
  return output;
}
function publicSession(session: Session): Record<string, unknown> {
  const polls = Object.fromEntries(Object.entries(session.pollDefinitions).map(([pollId, definition]) => {
    const votes = session.votes[pollId] || {};
    const totals = Object.fromEntries(definition.options.map((option) => [option, Object.values(votes).filter((vote) => vote === option).length]));
    return [pollId, { totals, totalVotes: Object.values(totals).reduce((sum, value) => sum + value, 0) }];
  }));
  const diagnostics = Object.fromEntries(Object.entries(session.diagnosticDefinitions).map(([diagnosticId, definition]) => {
    const answers = session.diagnostics[diagnosticId] || {};
    const totals = Object.fromEntries(definition.items.map((item) => [item, Object.values(answers).filter((answer) => answer.includes(item)).length]));
    return [diagnosticId, { totals, totalResponses: Object.values(answers).filter((answer) => answer.length).length }];
  }));
  const triages = Object.fromEntries(Object.entries(session.triageDefinitions).map(([triageId, definition]) => {
    const answers = session.triages[triageId] || {};
    const totals = Object.fromEntries(definition.items.map((item) => [item, Object.fromEntries(definition.categories.map((category) => [category, Object.values(answers).filter((answer) => answer[item] === category).length]))]));
    return [triageId, { totals, totalResponses: Object.keys(answers).length, referenceRevealed: Boolean(session.triageReferences[triageId]) }];
  }));
  return {
    sessionId: session.sessionId, deck: session.deck, participationUrl: session.participationUrl,
    slideIndex: session.slideIndex, updatedAt: session.updatedAt, expiresAt: session.expiresAt,
    polls, diagnostics, triages,
    postits: Object.fromEntries(Object.entries(session.postits).map(([postitId, records]) => [postitId, records.filter((record) => record.status === 'approved')]))
  };
}
function moderatorSession(session: Session): Record<string, unknown> {
  return { ...publicSession(session), postits: Object.fromEntries(Object.entries(session.postits).map(([postitId, records]) => [postitId, records.filter((record) => record.status !== 'discarded')])) };
}
function postitStyle(position: number, occupied: PostitStyle[]): PostitStyle {
  let seed = position * 7919 + 17;
  const random = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 2 ** 32; };
  const candidates = Array.from({ length: 120 }, () => ({ x: Math.round((12 + random() * 76) * 10) / 10, y: Math.round((31 + random() * 44) * 10) / 10 }));
  const overlap = (candidate: { x: number; y: number }, style: PostitStyle) => Math.max(0, 18 - Math.abs(candidate.x - style.x)) * Math.max(0, 18 - Math.abs(candidate.y - style.y));
  const available = candidates.filter((candidate) => !occupied.some((style) => overlap(candidate, style) > 0));
  const selected = (available.length ? available : candidates).reduce((best, candidate) => {
    if (!best) return candidate;
    const score = (point: { x: number; y: number }) => {
      const overlaps = occupied.map((style) => overlap(point, style));
      const separation = occupied.length ? Math.min(...occupied.map((style) => (point.x - style.x) ** 2 + (point.y - style.y) ** 2)) : 0;
      return [-Math.max(0, ...overlaps), -overlaps.reduce((sum, value) => sum + value, 0), separation];
    };
    const a = score(candidate); const b = score(best);
    return a[0] > b[0] || (a[0] === b[0] && (a[1] > b[1] || (a[1] === b[1] && a[2] > b[2]))) ? candidate : best;
  }, null as { x: number; y: number } | null)!;
  return { color: ['amber', 'peach', 'mint', 'sky', 'lilac'][position % 5], x: selected.x, y: selected.y, rotation: ((position * 7) % 9) - 4, z: position + 1 };
}

export class PresentationSession {
  private session: Session | null = null;
  private readonly ready: Promise<void>;
  private subscribers = new Set<ReadableStreamDefaultController<Uint8Array>>();

  constructor(private readonly state: DurableObjectState) {
    this.ready = state.blockConcurrencyWhile(async () => { this.session = await state.storage.get<Session>('session') || null; });
  }

  async fetch(request: Request): Promise<Response> {
    await this.ready;
    try {
      const path = new URL(request.url).pathname.split('/').filter(Boolean);
      if (request.method === 'POST' && path[0] === 'create') return this.create(await request.json<Definition>());
      const session = await this.requireSession();
      if (request.method === 'GET' && path.length === 0) return json(publicSession(session));
      if (request.method === 'GET' && path[0] === 'events') return this.events(session);
      if (request.method === 'GET' && path[0] === 'moderator') return json(moderatorSession(this.authorize(session, request)));
      const body = await request.json<Definition>();
      if (request.method !== 'POST') throw new HttpError(404, 'Rota não encontrada.');
      if (path[0] === 'slide') return json(publicSession(await this.updateSlide(session, body)));
      if (path[0] === 'votes' && path[1]) return json(publicSession(await this.vote(session, path[1], body)));
      if (path[0] === 'diagnostics' && path[1]) return json(publicSession(await this.diagnose(session, path[1], body)));
      if (path[0] === 'triages' && path[1] && path[2] === 'reference') return json(moderatorSession(await this.revealReference(session, path[1], request)));
      if (path[0] === 'triages' && path[1]) return json(publicSession(await this.triage(session, path[1], body)));
      if (path[0] === 'postits' && path[1] && path[2]) return json(moderatorSession(await this.decidePostit(session, path[1], path[2], body, request)));
      if (path[0] === 'postits' && path[1]) return json(publicSession(await this.submitPostit(session, path[1], body)));
      throw new HttpError(404, 'Rota não encontrada.');
    } catch (error) {
      if (error instanceof HttpError) return json({ error: error.message }, error.status);
      console.error(error);
      return json({ error: 'Erro interno.' }, 500);
    }
  }

  private async create(body: Definition): Promise<Response> {
    const deck = string(body.deck, 'deck é obrigatório.');
    const publicOrigin = string(body.publicOrigin, 'Origem pública inválida.');
    if (!/^https?:\/\/[^/]+/.test(publicOrigin)) throw new HttpError(400, 'Origem pública inválida.');
    const sessionId = string(body.sessionId, 'Sessão inválida.');
    if (!SESSION.test(sessionId)) throw new HttpError(400, 'Sessão inválida.');
    const pollDefinitions = normalizePolls(body.polls);
    const diagnosticDefinitions = normalizeDiagnostics(body.diagnostics);
    const triageDefinitions = normalizeTriages(body.triages);
    const postitDefinitions = normalizePostits(body.postits);
    const session: Session = {
      sessionId, presenterToken: token(), deck, participationUrl: `${publicOrigin}/${deck}/participar/${sessionId}`,
      slideIndex: 0, updatedAt: now(), expiresAt: expires(), pollDefinitions, votes: Object.fromEntries(Object.keys(pollDefinitions).map((key) => [key, {}])),
      diagnosticDefinitions, diagnostics: Object.fromEntries(Object.keys(diagnosticDefinitions).map((key) => [key, {}])),
      triageDefinitions, triages: Object.fromEntries(Object.keys(triageDefinitions).map((key) => [key, {}])), triageReferences: Object.fromEntries(Object.keys(triageDefinitions).map((key) => [key, false])),
      postitDefinitions, postits: Object.fromEntries(Object.keys(postitDefinitions).map((key) => [key, []]))
    };
    this.session = session;
    await this.state.storage.put('session', session);
    return json({ ...publicSession(session), presenterToken: session.presenterToken }, 201);
  }

  private async requireSession(): Promise<Session> {
    if (!this.session || Date.parse(this.session.expiresAt) <= Date.now()) {
      this.session = null;
      await this.state.storage.delete('session');
      this.endSubscribers('Sessão não encontrada ou expirada.');
      throw new HttpError(404, 'Sessão não encontrada ou expirada.');
    }
    return this.session;
  }
  private authorize(session: Session, request: Request): Session {
    if (!constantTimeEquals(session.presenterToken, request.headers.get('X-Presenter-Token') || '')) throw new HttpError(403, 'Token de apresentador inválido.');
    return session;
  }
  private async persist(session: Session): Promise<Session> {
    session.updatedAt = now();
    this.session = session;
    await this.state.storage.put('session', session);
    this.broadcast(session);
    return session;
  }
  private async updateSlide(session: Session, body: Definition): Promise<Session> {
    this.authorize(session, { headers: new Headers({ 'X-Presenter-Token': String(body.presenterToken || '') }) } as Request);
    session.slideIndex = integer(body.slideIndex, 'slideIndex inválido.');
    return this.persist(session);
  }
  private active(session: Session, slideIndex: number, message: string): void { if (session.slideIndex !== slideIndex) throw new HttpError(409, message); }
  private async vote(session: Session, pollId: string, body: Definition): Promise<Session> {
    const definition = session.pollDefinitions[pollId];
    if (!definition) throw new HttpError(400, 'Enquete inválida.');
    this.active(session, definition.slideIndex, 'A votação está disponível apenas na tela da enquete.');
    const option = id(body.option, 'Opção de voto inválida.');
    if (!definition.options.includes(option)) throw new HttpError(400, 'Opção de voto inválida.');
    session.votes[pollId][string(body.participantId, 'participantId inválido.')] = option;
    return this.persist(session);
  }
  private async diagnose(session: Session, diagnosticId: string, body: Definition): Promise<Session> {
    const definition = session.diagnosticDefinitions[diagnosticId];
    if (!definition) throw new HttpError(400, 'Diagnóstico inválido.');
    this.active(session, definition.slideIndex, 'O diagnóstico está disponível apenas na tela ativa.');
    const items = body.items;
    if (!Array.isArray(items) || items.length > definition.maxSelections || new Set(items).size !== items.length || !items.every((item) => typeof item === 'string' && definition.items.includes(item))) throw new HttpError(400, 'Item de diagnóstico inválido.');
    session.diagnostics[diagnosticId][string(body.participantId, 'participantId inválido.')] = items as string[];
    return this.persist(session);
  }
  private async triage(session: Session, triageId: string, body: Definition): Promise<Session> {
    const definition = session.triageDefinitions[triageId];
    if (!definition) throw new HttpError(400, 'Triagem inválida.');
    this.active(session, definition.slideIndex, 'A triagem está disponível apenas na tela ativa.');
    const assignments = record(body.assignments, 'Classificação de triagem inválida.');
    if (!Object.keys(assignments).length || !Object.keys(assignments).every((item) => definition.items.includes(item)) || !Object.values(assignments).every((category) => typeof category === 'string' && definition.categories.includes(category))) throw new HttpError(400, 'Classificação de triagem inválida.');
    const participant = string(body.participantId, 'participantId inválido.');
    session.triages[triageId][participant] = { ...(session.triages[triageId][participant] || {}), ...assignments as Record<string, string> };
    return this.persist(session);
  }
  private async revealReference(session: Session, triageId: string, request: Request): Promise<Session> {
    this.authorize(session, request);
    const definition = session.triageDefinitions[triageId];
    if (!definition) throw new HttpError(400, 'Triagem inválida.');
    this.active(session, definition.slideIndex, 'A referência só pode ser revelada na tela ativa.');
    session.triageReferences[triageId] = true;
    return this.persist(session);
  }
  private async submitPostit(session: Session, postitId: string, body: Definition): Promise<Session> {
    const definition = session.postitDefinitions[postitId];
    if (!definition) throw new HttpError(400, 'post-it inválido.');
    this.active(session, definition.slideIndex, 'O quadro de post-its está disponível apenas na tela ativa.');
    const text = string(body.text, 'post-it inválido.').trim();
    if (!text || text.length > definition.maxLength) throw new HttpError(400, 'post-it inválido.');
    string(body.participantId, 'participantId inválido.');
    const records = session.postits[postitId];
    records.push({ id: crypto.randomUUID(), text, status: 'pending', createdAt: now(), style: postitStyle(records.length, records.map((record) => record.style)) });
    return this.persist(session);
  }
  private async decidePostit(session: Session, postitId: string, postitIdValue: string, body: Definition, request: Request): Promise<Session> {
    this.authorize(session, request);
    if (!session.postitDefinitions[postitId] || !['approved', 'discarded'].includes(String(body.decision))) throw new HttpError(400, 'Decisão de post-it inválida.');
    const postit = session.postits[postitId].find((record) => record.id === postitIdValue);
    if (!postit) throw new HttpError(404, 'Post-it não encontrado.');
    postit.status = body.decision as Postit['status'];
    return this.persist(session);
  }
  private events(session: Session): Response {
    const stream = new ReadableStream<Uint8Array>({
      start: (controller) => { this.subscribers.add(controller); this.send(controller, 'slide', publicSession(session), session.updatedAt); },
      cancel: () => { /* Controller is removed by the next broadcast if closed. */ }
    });
    return new Response(stream, { headers: { 'content-type': 'text/event-stream; charset=utf-8', 'cache-control': 'no-cache, no-transform', connection: 'keep-alive' } });
  }
  private send(controller: ReadableStreamDefaultController<Uint8Array>, event: string, data: unknown, eventId?: string): void {
    try { controller.enqueue(encoder.encode(`${eventId ? `id: ${eventId}\n` : ''}event: ${event}\ndata: ${JSON.stringify(data)}\n\n`)); } catch { this.subscribers.delete(controller); }
  }
  private broadcast(session: Session): void { for (const controller of this.subscribers) this.send(controller, 'slide', publicSession(session), session.updatedAt); }
  private endSubscribers(message: string): void { for (const controller of this.subscribers) { this.send(controller, 'session-ended', { error: message }); try { controller.close(); } catch {} } this.subscribers.clear(); }
}

function routeSession(path: string): string | null {
  const parts = path.split('/').filter(Boolean);
  if (parts[0] !== 'api' || parts[1] !== 'sessions') return null;
  if (parts.length === 2) return 'create';
  return SESSION.test(parts[2] || '') ? parts.slice(3).join('/') : null;
}
function assetPath(pathname: string): string | null {
  const parts = pathname.split('/').filter(Boolean);
  if (parts.length === 3 && parts[1] === 'participar' && SESSION.test(parts[2])) return `/${parts[0]}/participar/index.html`;
  if (parts.length === 3 && parts[1] === 'moderador' && SESSION.test(parts[2])) return `/${parts[0]}/moderador/index.html`;
  return null;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const sessionRoute = routeSession(url.pathname);
    if (sessionRoute !== null) {
      if (sessionRoute === 'create' && request.method !== 'POST') return json({ error: 'Método não permitido.' }, 405);
      if (sessionRoute !== 'create' && !sessionRoute && request.method !== 'GET') return json({ error: 'Método não permitido.' }, 405);
      const sessionId = sessionRoute === 'create' ? crypto.randomUUID() : url.pathname.split('/')[3];
      const stub = env.SESSIONS.get(env.SESSIONS.idFromName(sessionId));
      const internalUrl = `https://session.internal/${sessionRoute === 'create' ? 'create' : sessionRoute}`;
      if (sessionRoute === 'create') {
        const body = record(await request.json(), 'Corpo da sessão inválido.');
        body.publicOrigin = url.origin;
        body.sessionId = sessionId;
        return stub.fetch(new Request(internalUrl, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) }));
      }
      return stub.fetch(new Request(internalUrl, request));
    }
    if (url.pathname === '/') return Response.redirect(new URL(`/${DEFAULT_DECK}/index.html?ao-vivo`, url), 302);
    const rewritten = assetPath(url.pathname);
    return env.ASSETS.fetch(rewritten ? new Request(new URL(rewritten, url), request) : request);
  }
} satisfies ExportedHandler<Env>;
