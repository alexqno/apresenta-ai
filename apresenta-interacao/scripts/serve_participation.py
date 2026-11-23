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
import secrets
from threading import Condition, RLock
from urllib.parse import unquote, urlparse
from uuid import uuid4


SESSION_ID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.I)
IA_USAGE_OPTIONS = ("explore", "research", "draft", "agent", "automate")
IA_USAGE_SLIDE_INDEX = 2


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

    def create(self, deck: str) -> dict:
        now = datetime.now(timezone.utc)
        session = {
            "sessionId": str(uuid4()),
            "presenterToken": secrets.token_urlsafe(32),
            "deck": deck,
            "slideIndex": 0,
            "updatedAt": now.isoformat(),
            "expiresAt": (now + timedelta(seconds=self.ttl_seconds)).isoformat(),
            "votes": {"ia-usage": {}},
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

    def vote(self, session_id: str, participant_id: str, option: str) -> dict:
        if not isinstance(participant_id, str) or not participant_id:
            raise ValueError("participantId inválido.")
        if option not in IA_USAGE_OPTIONS:
            raise ValueError("Opção de voto inválida.")
        session = self.get(session_id)
        if session["slideIndex"] != IA_USAGE_SLIDE_INDEX:
            raise Conflict("A votação está disponível apenas na tela 3.")
        with self.lock:
            self.sessions[session_id]["votes"]["ia-usage"][participant_id] = option
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
        votes = session.get("votes", {}).get("ia-usage", {})
        totals = {option: sum(value == option for value in votes.values()) for option in IA_USAGE_OPTIONS}
        public = {key: value for key, value in session.items() if key not in {"presenterToken", "votes"}}
        public["polls"] = {"ia-usage": {"totals": totals, "totalVotes": sum(totals.values())}}
        return public


class ParticipationHandler(SimpleHTTPRequestHandler):
    root: Path
    store: SessionStore
    watch = False

    def translate_path(self, path: str) -> str:
        request_path = urlparse(path).path
        target = participation_path(self.root, request_path) or safe_path(self.root, request_path)
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
        if self.watch:
            target = participation_path(self.root, request_path) or safe_path(self.root, request_path)
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
                self.respond_json(201, self.store.create(deck))
                return
            if len(parts) == 5 and parts[1:3] == ["api", "sessions"] and parts[4] == "slide":
                session = self.store.update_slide(parts[3], body.get("presenterToken", ""), body.get("slideIndex"))
                self.respond_json(200, SessionStore.public(session))
                return
            if len(parts) == 6 and parts[1:3] == ["api", "sessions"] and parts[4:] == ["votes", "ia-usage"]:
                session = self.store.vote(parts[3], body.get("participantId", ""), body.get("option"))
                self.respond_json(200, SessionStore.public(session))
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
