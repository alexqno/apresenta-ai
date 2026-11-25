#!/usr/bin/env python3
"""Servidor HTTP local para acompanhamento móvel de apresentações."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
from random import Random
import secrets
from threading import Condition, RLock
from urllib.parse import unquote, urlparse
from uuid import uuid4


SESSION_ID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.I)
DEFAULT_POLLS = {
    "ia-usage": {
        "slideIndex": 2,
        "options": ("explore", "research", "draft", "agent", "automate"),
    }
}
POLL_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


class Forbidden(RuntimeError):
    pass


class NotFound(RuntimeError):
    pass


class Conflict(RuntimeError):
    pass


def validate_public_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("--public-url precisa ser uma URL HTTP acessível na rede local.")
    if (parsed.hostname or "").lower() in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("--public-url não pode usar localhost.")
    return value.rstrip("/")


def normalize_polls(value: object | None) -> dict[str, dict]:
    source = DEFAULT_POLLS if value is None else value
    if not isinstance(source, dict):
        raise ValueError("polls deve ser um objeto indexado por id.")
    normalized: dict[str, dict] = {}
    for poll_id, definition in source.items():
        if not isinstance(poll_id, str) or not POLL_ID_PATTERN.fullmatch(poll_id):
            raise ValueError("id de enquete inválido.")
        if not isinstance(definition, dict):
            raise ValueError("definição de enquete inválida.")
        slide_index = definition.get("slideIndex")
        options = definition.get("options")
        if not isinstance(slide_index, int) or slide_index < 0:
            raise ValueError("slideIndex de enquete inválido.")
        if not isinstance(options, (list, tuple)) or len(options) < 2:
            raise ValueError("enquete exige pelo menos duas opções.")
        if not all(isinstance(option, str) and POLL_ID_PATTERN.fullmatch(option) for option in options):
            raise ValueError("opções de enquete inválidas.")
        if len(set(options)) != len(options):
            raise ValueError("opções de enquete repetidas.")
        normalized[poll_id] = {"slideIndex": slide_index, "options": tuple(options)}
    return normalized


def normalize_diagnostics(value: object | None) -> dict[str, dict]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("diagnostics deve ser um objeto indexado por id.")
    normalized: dict[str, dict] = {}
    for diagnostic_id, definition in value.items():
        if not isinstance(diagnostic_id, str) or not POLL_ID_PATTERN.fullmatch(diagnostic_id):
            raise ValueError("id de diagnóstico inválido.")
        if not isinstance(definition, dict):
            raise ValueError("definição de diagnóstico inválida.")
        slide_index, items = definition.get("slideIndex"), definition.get("items")
        if not isinstance(slide_index, int) or slide_index < 0:
            raise ValueError("slideIndex de diagnóstico inválido.")
        if not isinstance(items, (list, tuple)) or not items or not all(isinstance(item, str) and POLL_ID_PATTERN.fullmatch(item) for item in items) or len(set(items)) != len(items):
            raise ValueError("itens de diagnóstico inválidos.")
        max_selections = definition.get("maxSelections", len(items))
        if not isinstance(max_selections, int) or not 1 <= max_selections <= len(items):
            raise ValueError("limite de seleção inválido.")
        normalized[diagnostic_id] = {"slideIndex": slide_index, "items": tuple(items), "maxSelections": max_selections}
    return normalized


def normalize_triages(value: object | None) -> dict[str, dict]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("triages deve ser um objeto indexado por id.")
    normalized: dict[str, dict] = {}
    for triage_id, definition in value.items():
        if not isinstance(triage_id, str) or not POLL_ID_PATTERN.fullmatch(triage_id) or not isinstance(definition, dict):
            raise ValueError("definição de triagem inválida.")
        slide_index, categories, items = definition.get("slideIndex"), definition.get("categories"), definition.get("items")
        if not isinstance(slide_index, int) or slide_index < 0 or not isinstance(categories, (list, tuple)) or len(categories) < 2 or not isinstance(items, (list, tuple)) or not items:
            raise ValueError("definição de triagem inválida.")
        if not all(isinstance(value, str) and POLL_ID_PATTERN.fullmatch(value) for value in [*categories, *items]) or len(set(categories)) != len(categories) or len(set(items)) != len(items):
            raise ValueError("categorias ou itens de triagem inválidos.")
        normalized[triage_id] = {"slideIndex": slide_index, "categories": tuple(categories), "items": tuple(items)}
    return normalized


def normalize_postits(value: object | None) -> dict[str, dict]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("postits deve ser um objeto indexado por id.")
    normalized: dict[str, dict] = {}
    for postit_id, definition in value.items():
        if not isinstance(postit_id, str) or not POLL_ID_PATTERN.fullmatch(postit_id) or not isinstance(definition, dict):
            raise ValueError("definição de post-it inválida.")
        slide_index = definition.get("slideIndex")
        max_length = definition.get("maxLength", 280)
        if not isinstance(slide_index, int) or slide_index < 0 or not isinstance(max_length, int) or not 1 <= max_length <= 1000:
            raise ValueError("definição de post-it inválida.")
        normalized[postit_id] = {"slideIndex": slide_index, "maxLength": max_length}
    return normalized


POSTIT_WIDTH = 18
POSTIT_HEIGHT = 18


def postit_style(position: int, occupied: list[dict[str, int | float | str]] | None = None) -> dict[str, int | float | str]:
    colors = ("amber", "peach", "mint", "sky", "lilac")
    occupied = occupied or []
    random = Random(position * 7919 + 17)
    candidates = [(round(random.uniform(12, 88), 1), round(random.uniform(31, 75), 1)) for _ in range(120)]

    def overlaps(candidate: tuple[int, int], style: dict[str, int | float | str]) -> bool:
        return abs(candidate[0] - float(style["x"])) < POSTIT_WIDTH and abs(candidate[1] - float(style["y"])) < POSTIT_HEIGHT

    available = [candidate for candidate in candidates if not any(overlaps(candidate, style) for style in occupied)]
    candidates = available or candidates
    if not occupied:
        x, y = candidates[0]
    else:
        def overlap_area(candidate: tuple[int, int], style: dict[str, int | float | str]) -> float:
            horizontal = max(0, POSTIT_WIDTH - abs(candidate[0] - float(style["x"])))
            vertical = max(0, POSTIT_HEIGHT - abs(candidate[1] - float(style["y"])))
            return horizontal * vertical

        def score(candidate: tuple[int, int]) -> tuple[float, float, float]:
            overlaps = [overlap_area(candidate, style) for style in occupied]
            separation = min((candidate[0] - float(style["x"])) ** 2 + (candidate[1] - float(style["y"])) ** 2 for style in occupied)
            return (-max(overlaps), -sum(overlaps), separation)

        x, y = max(candidates, key=score)
    return {
        "color": colors[position % len(colors)],
        "x": x,
        "y": y,
        "rotation": ((position * 7) % 9) - 4,
        "z": position + 1,
    }


def safe_path(root: Path, request_path: str) -> Path | None:
    relative = unquote(request_path).lstrip("/") or "index.html"
    target = (root / relative).resolve()
    return target if target == root.resolve() or root.resolve() in target.parents else None


def participation_path(root: Path, request_path: str) -> Path | None:
    parts = [part for part in request_path.split("/") if part]
    if len(parts) != 3 or parts[1] != "participar" or not SESSION_ID_PATTERN.fullmatch(parts[2]):
        return None
    target = safe_path(root, f"/{parts[0]}/participar/index.html")
    return target if target and target.is_file() else None


def moderator_path(root: Path, request_path: str) -> Path | None:
    parts = [part for part in request_path.split("/") if part]
    if len(parts) != 3 or parts[1] != "moderador" or not SESSION_ID_PATTERN.fullmatch(parts[2]):
        return None
    target = safe_path(root, f"/{parts[0]}/moderador/index.html")
    return target if target and target.is_file() else None


def revision_for(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part.startswith((".", "__")) for part in relative.parts) or path.name.endswith("~") or not path.is_file():
            continue
        stat = path.stat()
        digest.update(str(relative).encode())
        digest.update(str(stat.st_mtime_ns).encode())
        digest.update(str(stat.st_size).encode())
    return digest.hexdigest()[:16]


def live_reload_script() -> str:
    return """(() => {
  const revisionUrl = '/__apresenta/revision';
  const scrollKey = `__apresenta.scroll:${location.pathname}`;
  const previousScroll = sessionStorage.getItem(scrollKey);
  if (previousScroll !== null) { sessionStorage.removeItem(scrollKey); scrollTo(0, Number(previousScroll)); }
  let revision;
  async function poll() {
    try {
      const response = await fetch(revisionUrl, { cache:'no-store' });
      if (!response.ok) return;
      const next = (await response.json()).revision;
      if (!revision) { revision = next; return; }
      if (next !== revision) { sessionStorage.setItem(scrollKey, String(scrollY)); location.reload(); }
    } catch {}
  }
  poll();
  setInterval(poll, 1000);
})();"""


def inject_live_reload(html: str) -> str:
    tag = '<script src="/__apresenta/live-reload.js"></script>'
    return html.replace("</body>", f"{tag}</body>") if "</body>" in html else html + tag


class SessionStore:
    def __init__(self, public_url: str, ttl_seconds: int = 4 * 60 * 60):
        self.public_url = validate_public_url(public_url)
        self.ttl_seconds = ttl_seconds
        self.sessions: dict[str, dict] = {}
        self.lock = RLock()
        self.changed = Condition(self.lock)

    def create(self, deck: str, polls: object | None = None, diagnostics: object | None = None, triages: object | None = None, postits: object | None = None) -> dict:
        now = datetime.now(timezone.utc)
        definitions = normalize_polls(polls)
        diagnostic_definitions = normalize_diagnostics(diagnostics)
        triage_definitions = normalize_triages(triages)
        postit_definitions = normalize_postits(postits)
        session = {
            "sessionId": str(uuid4()),
            "presenterToken": secrets.token_urlsafe(32),
            "deck": deck,
            "slideIndex": 0,
            "updatedAt": now.isoformat(),
            "expiresAt": (now + timedelta(seconds=self.ttl_seconds)).isoformat(),
            "pollDefinitions": definitions,
            "votes": {poll_id: {} for poll_id in definitions},
            "diagnosticDefinitions": diagnostic_definitions,
            "diagnostics": {diagnostic_id: {} for diagnostic_id in diagnostic_definitions},
            "triageDefinitions": triage_definitions,
            "triages": {triage_id: {} for triage_id in triage_definitions},
            "postitDefinitions": postit_definitions,
            "postits": {postit_id: [] for postit_id in postit_definitions},
        }
        session["participationUrl"] = f"{self.public_url}/{deck}/participar/{session['sessionId']}"
        with self.lock:
            self.sessions[session["sessionId"]] = session
            self.changed.notify_all()
        return session.copy()

    def get(self, session_id: str) -> dict:
        with self.lock:
            session = self.sessions.get(session_id)
            if not session or datetime.fromisoformat(session["expiresAt"]) <= datetime.now(timezone.utc):
                self.sessions.pop(session_id, None)
                raise NotFound("Sessão não encontrada ou expirada.")
            return session.copy()

    def update_slide(self, session_id: str, presenter_token: str, slide_index: int) -> dict:
        session = self.get(session_id)
        if not secrets.compare_digest(session["presenterToken"], presenter_token):
            raise Forbidden("Token de apresentador inválido.")
        if not isinstance(slide_index, int) or slide_index < 0:
            raise ValueError("slideIndex inválido.")
        with self.lock:
            self.sessions[session_id]["slideIndex"] = slide_index
            self.sessions[session_id]["updatedAt"] = datetime.now(timezone.utc).isoformat()
            updated = self.sessions[session_id].copy()
            self.changed.notify_all()
            return updated

    def diagnose(self, session_id: str, participant_id: str, diagnostic_id: str, items: object) -> dict:
        if not isinstance(participant_id, str) or not participant_id:
            raise ValueError("participantId inválido.")
        if not isinstance(items, list) or not all(isinstance(item, str) for item in items):
            raise ValueError("itens inválidos.")
        session = self.get(session_id)
        definition = session["diagnosticDefinitions"].get(diagnostic_id)
        if not definition:
            raise ValueError("Diagnóstico inválido.")
        if session["slideIndex"] != definition["slideIndex"]:
            raise Conflict("O diagnóstico está disponível apenas na tela ativa.")
        if len(items) > definition["maxSelections"] or len(set(items)) != len(items) or any(item not in definition["items"] for item in items):
            raise ValueError("Item de diagnóstico inválido.")
        with self.lock:
            self.sessions[session_id]["diagnostics"][diagnostic_id][participant_id] = items
            self.sessions[session_id]["updatedAt"] = datetime.now(timezone.utc).isoformat()
            updated = self.sessions[session_id].copy()
            self.changed.notify_all()
            return updated

    def triage(self, session_id: str, participant_id: str, triage_id: str, assignments: object) -> dict:
        if not isinstance(participant_id, str) or not participant_id or not isinstance(assignments, dict):
            raise ValueError("triagem inválida.")
        session = self.get(session_id)
        definition = session["triageDefinitions"].get(triage_id)
        if not definition:
            raise ValueError("Triagem inválida.")
        if session["slideIndex"] != definition["slideIndex"]:
            raise Conflict("A triagem está disponível apenas na tela ativa.")
        if not assignments or not set(assignments).issubset(definition["items"]) or any(value not in definition["categories"] for value in assignments.values()):
            raise ValueError("Classificação de triagem inválida.")
        with self.lock:
            previous = self.sessions[session_id]["triages"][triage_id].get(participant_id, {})
            self.sessions[session_id]["triages"][triage_id][participant_id] = {**previous, **assignments}
            self.sessions[session_id]["updatedAt"] = datetime.now(timezone.utc).isoformat()
            updated = self.sessions[session_id].copy()
            self.changed.notify_all()
            return updated

    def submit_postit(self, session_id: str, participant_id: str, postit_id: str, text: object) -> dict:
        if not isinstance(participant_id, str) or not participant_id or not isinstance(text, str):
            raise ValueError("post-it inválido.")
        session = self.get(session_id)
        definition = session["postitDefinitions"].get(postit_id)
        cleaned = text.strip()
        if not definition or not cleaned or len(cleaned) > definition["maxLength"]:
            raise ValueError("post-it inválido.")
        if session["slideIndex"] != definition["slideIndex"]:
            raise Conflict("O quadro de post-its está disponível apenas na tela ativa.")
        with self.lock:
            records = self.sessions[session_id]["postits"][postit_id]
            records.append({
                "id": str(uuid4()),
                "text": cleaned,
                "status": "pending",
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "style": postit_style(len(records), [record["style"] for record in records]),
            })
            self.sessions[session_id]["updatedAt"] = datetime.now(timezone.utc).isoformat()
            updated = self.sessions[session_id].copy()
            self.changed.notify_all()
            return updated

    def decide_postit(self, session_id: str, presenter_token: str, postit_id: str, record_id: str, decision: str) -> dict:
        session = self.get(session_id)
        if not secrets.compare_digest(session["presenterToken"], presenter_token):
            raise Forbidden("Token de apresentador inválido.")
        if decision not in {"approved", "discarded"} or postit_id not in session["postitDefinitions"]:
            raise ValueError("Decisão de post-it inválida.")
        with self.lock:
            record = next((item for item in self.sessions[session_id]["postits"][postit_id] if item["id"] == record_id), None)
            if not record:
                raise NotFound("Post-it não encontrado.")
            record["status"] = decision
            self.sessions[session_id]["updatedAt"] = datetime.now(timezone.utc).isoformat()
            updated = self.sessions[session_id].copy()
            self.changed.notify_all()
            return updated

    def vote(self, session_id: str, participant_id: str, poll_id: str, option: str | None = None) -> dict:
        if option is None:
            option = poll_id
            poll_id = "ia-usage"
        if not isinstance(participant_id, str) or not participant_id:
            raise ValueError("participantId inválido.")
        session = self.get(session_id)
        definition = session["pollDefinitions"].get(poll_id)
        if not definition:
            raise ValueError("Enquete inválida.")
        if option not in definition["options"]:
            raise ValueError("Opção de voto inválida.")
        if session["slideIndex"] != definition["slideIndex"]:
            raise Conflict("A votação está disponível apenas na tela da enquete.")
        with self.lock:
            self.sessions[session_id]["votes"][poll_id][participant_id] = option
            self.sessions[session_id]["updatedAt"] = datetime.now(timezone.utc).isoformat()
            updated = self.sessions[session_id].copy()
            self.changed.notify_all()
            return updated

    def wait_for_change(self, session_id: str, updated_at: str | None, timeout: float = 20) -> dict:
        with self.changed:
            session = self.get(session_id)
            if updated_at == session["updatedAt"]:
                self.changed.wait_for(lambda: self.get(session_id)["updatedAt"] != updated_at, timeout)
            return self.get(session_id)

    @staticmethod
    def public(session: dict) -> dict:
        public = {key: value for key, value in session.items() if key not in {"presenterToken", "pollDefinitions", "votes", "diagnosticDefinitions", "diagnostics", "triageDefinitions", "triages", "postitDefinitions", "postits"}}
        public["polls"] = {}
        for poll_id, definition in session.get("pollDefinitions", {}).items():
            votes = session.get("votes", {}).get(poll_id, {})
            totals = {option: sum(value == option for value in votes.values()) for option in definition["options"]}
            public["polls"][poll_id] = {"totals": totals, "totalVotes": sum(totals.values())}
        public["diagnostics"] = {}
        for diagnostic_id, definition in session.get("diagnosticDefinitions", {}).items():
            responses = session.get("diagnostics", {}).get(diagnostic_id, {})
            totals = {item: sum(item in response for response in responses.values()) for item in definition["items"]}
            public["diagnostics"][diagnostic_id] = {"totals": totals, "totalResponses": sum(bool(response) for response in responses.values())}
        public["triages"] = {}
        for triage_id, definition in session.get("triageDefinitions", {}).items():
            responses = session.get("triages", {}).get(triage_id, {})
            totals = {item: {category: sum(response.get(item) == category for response in responses.values()) for category in definition["categories"]} for item in definition["items"]}
            public["triages"][triage_id] = {"totals": totals, "totalResponses": len(responses)}
        public["postits"] = {
            postit_id: [record.copy() for record in records if record["status"] == "approved"]
            for postit_id, records in session.get("postits", {}).items()
        }
        return public

    @staticmethod
    def presenter(session: dict) -> dict:
        return {**SessionStore.public(session), "presenterToken": session["presenterToken"]}

    def moderator(self, session_id: str, presenter_token: str) -> dict:
        session = self.get(session_id)
        if not secrets.compare_digest(session["presenterToken"], presenter_token):
            raise Forbidden("Token de apresentador inválido.")
        private = SessionStore.public(session)
        private["postits"] = {
            postit_id: [record.copy() for record in records if record["status"] != "discarded"]
            for postit_id, records in session.get("postits", {}).items()
        }
        return private


class ParticipationHandler(SimpleHTTPRequestHandler):
    root: Path
    store: SessionStore
    watch = False

    def translate_path(self, path: str) -> str:
        request_path = urlparse(path).path
        target = participation_path(self.root, request_path) or moderator_path(self.root, request_path) or safe_path(self.root, request_path)
        return str(target or self.root / "__not_found__")

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length) or b"{}")

    def respond_json(self, status: int, payload: dict) -> None:
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def respond_javascript(self, script: str) -> None:
        data = script.encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/javascript; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def respond_watched_html(self, target: Path) -> None:
        data = inject_live_reload(target.read_text(encoding="utf-8")).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def respond_session_ended(self, message: str) -> None:
        self.wfile.write(f"event: session-ended\ndata: {json.dumps({'error': message})}\n\n".encode())
        self.wfile.flush()

    def stream_events(self, session_id: str, last_event_id: str | None) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            while True:
                try:
                    session = self.store.wait_for_change(session_id, last_event_id)
                except NotFound as error:
                    self.respond_session_ended(str(error))
                    return
                if session["updatedAt"] == last_event_id:
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
                    continue
                payload = json.dumps(SessionStore.public(session))
                self.wfile.write(f"id: {session['updatedAt']}\nevent: slide\ndata: {payload}\n\n".encode())
                self.wfile.flush()
                last_event_id = session["updatedAt"]
        except (BrokenPipeError, ConnectionResetError):
            return

    def do_GET(self) -> None:
        request_path = urlparse(self.path).path
        parts = request_path.split("/")
        if self.watch and request_path == "/__apresenta/revision":
            self.respond_json(200, {"revision": revision_for(self.root)})
            return
        if self.watch and request_path == "/__apresenta/live-reload.js":
            self.respond_javascript(live_reload_script())
            return
        if len(parts) == 5 and parts[1:3] == ["api", "sessions"] and parts[4] == "events":
            self.stream_events(parts[3], self.headers.get("Last-Event-ID"))
            return
        if len(parts) == 4 and parts[1:3] == ["api", "sessions"]:
            try:
                self.respond_json(200, SessionStore.public(self.store.get(parts[3])))
            except NotFound as error:
                self.respond_json(404, {"error": str(error)})
            return
        if len(parts) == 5 and parts[1:3] == ["api", "sessions"] and parts[4] == "moderator":
            try:
                self.respond_json(200, self.store.moderator(parts[3], self.headers.get("X-Presenter-Token", "")))
            except Forbidden as error:
                self.respond_json(403, {"error": str(error)})
            except NotFound as error:
                self.respond_json(404, {"error": str(error)})
            return
        if self.watch:
            target = participation_path(self.root, request_path) or moderator_path(self.root, request_path) or safe_path(self.root, request_path)
            if target and target.is_file() and target.suffix.lower() in {".html", ".htm"}:
                self.respond_watched_html(target)
                return
        return super().do_GET()

    def do_POST(self) -> None:
        parts = urlparse(self.path).path.split("/")
        try:
            body = self.read_json()
            if parts == ["", "api", "sessions"]:
                deck = body.get("deck")
                if not isinstance(deck, str) or not deck:
                    raise ValueError("deck é obrigatório.")
                session = self.store.create(deck, body.get("polls"), body.get("diagnostics"), body.get("triages"), body.get("postits"))
                self.respond_json(201, SessionStore.presenter(session))
                return
            if len(parts) == 5 and parts[1:3] == ["api", "sessions"] and parts[4] == "slide":
                session = self.store.update_slide(parts[3], body.get("presenterToken", ""), body.get("slideIndex"))
                self.respond_json(200, SessionStore.public(session))
                return
            if len(parts) == 6 and parts[1:3] == ["api", "sessions"] and parts[4] == "votes":
                session = self.store.vote(parts[3], body.get("participantId", ""), parts[5], body.get("option"))
                self.respond_json(200, SessionStore.public(session))
                return
            if len(parts) == 6 and parts[1:3] == ["api", "sessions"] and parts[4] == "diagnostics":
                session = self.store.diagnose(parts[3], body.get("participantId", ""), parts[5], body.get("items"))
                self.respond_json(200, SessionStore.public(session))
                return
            if len(parts) == 6 and parts[1:3] == ["api", "sessions"] and parts[4] == "triages":
                session = self.store.triage(parts[3], body.get("participantId", ""), parts[5], body.get("assignments"))
                self.respond_json(200, SessionStore.public(session))
                return
            if len(parts) == 6 and parts[1:3] == ["api", "sessions"] and parts[4] == "postits":
                session = self.store.submit_postit(parts[3], body.get("participantId", ""), parts[5], body.get("text"))
                self.respond_json(200, SessionStore.public(session))
                return
            if len(parts) == 7 and parts[1:3] == ["api", "sessions"] and parts[4] == "postits":
                session = self.store.decide_postit(parts[3], self.headers.get("X-Presenter-Token", ""), parts[5], parts[6], body.get("decision"))
                self.respond_json(200, self.store.moderator(parts[3], self.headers.get("X-Presenter-Token", "")))
                return
            self.respond_json(404, {"error": "Rota não encontrada."})
        except Forbidden as error:
            self.respond_json(403, {"error": str(error)})
        except Conflict as error:
            self.respond_json(409, {"error": str(error)})
        except NotFound as error:
            self.respond_json(404, {"error": str(error)})
        except (TypeError, ValueError, json.JSONDecodeError) as error:
            self.respond_json(400, {"error": str(error)})


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve apresentação e participação na rede local.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--public-url", required=True)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        parser.error("--root deve apontar para diretório existente.")
    ParticipationHandler.root = root
    ParticipationHandler.store = SessionStore(args.public_url)
    ParticipationHandler.watch = args.watch
    server = ThreadingHTTPServer((args.host, args.port), ParticipationHandler)
    print(f"Servindo {root} em {args.public_url}")
    server.serve_forever()


if __name__ == "__main__":
    main()
