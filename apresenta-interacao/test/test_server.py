import importlib.util
import json
from pathlib import Path
import tempfile
import time
import unittest


SERVER = Path(__file__).parents[1] / "scripts" / "serve_participation.py"


def load_server():
    spec = importlib.util.spec_from_file_location("serve_participation", SERVER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SessionStoreTests(unittest.TestCase):
    def setUp(self):
        self.server = load_server()
        self.store = self.server.SessionStore("http://192.168.1.20:8080", ttl_seconds=60)

    def test_only_presenter_token_updates_current_slide(self):
        session = self.store.create("pausa")

        self.assertEqual("http://192.168.1.20:8080/pausa/participar/" + session["sessionId"], session["participationUrl"])

        with self.assertRaises(self.server.Forbidden):
            self.store.update_slide(session["sessionId"], "wrong", 3)

        updated = self.store.update_slide(session["sessionId"], session["presenterToken"], 3)

        self.assertEqual(3, updated["slideIndex"])

    def test_rejects_localhost_public_url(self):
        with self.assertRaises(ValueError):
            self.server.validate_public_url("http://localhost:8080")

    def test_expired_session_cannot_be_read_or_updated(self):
        store = self.server.SessionStore("http://192.168.1.20:8080", ttl_seconds=-1)
        session = store.create("pausa")

        with self.assertRaises(self.server.NotFound):
            store.get(session["sessionId"])

    def test_serves_only_files_inside_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text("ok")
            self.assertEqual((root / "index.html").resolve(), self.server.safe_path(root, "/index.html"))
            self.assertIsNone(self.server.safe_path(root, "/../secret"))

    def test_participation_session_route_resolves_mobile_index(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "pausa" / "participar"
            target.mkdir(parents=True)
            (target / "index.html").write_text("mobile")
            self.assertEqual((target / "index.html").resolve(), self.server.participation_path(root, "/pausa/participar/00000000-0000-4000-8000-000000000000"))
            self.assertIsNone(self.server.participation_path(root, "/pausa/participar/app.js"))

    def test_mobile_client_keeps_one_sse_subscription(self):
        client = (Path(__file__).parents[1] / "assets" / "participar" / "app.js").read_text()
        server = (Path(__file__).parents[1] / "scripts" / "serve_participation.py").read_text()

        self.assertIn("function subscribeToSession()", client)
        self.assertNotIn("events.onmessage = (event) => receive", client)
        self.assertNotIn("events.addEventListener('slide', (event) => receive", client)
        self.assertIn("events.addEventListener('session-ended'", client)
        self.assertIn("event: session-ended", server)

    def test_event_stream_waits_for_updates_without_reconnecting(self):
        server = (Path(__file__).parents[1] / "scripts" / "serve_participation.py").read_text()

        self.assertIn("def stream_events(self, session_id: str, last_event_id: str | None)", server)
        self.assertIn("while True:", server)
        self.assertIn("if session[\"updatedAt\"] == last_event_id:", server)

    def test_current_mobile_card_animates_focus_and_spacing(self):
        styles = (Path(__file__).parents[1] / "assets" / "participar" / "styles.css").read_text()

        self.assertRegex(styles, r"\.slide-card\s*\{[^}]*transition:transform")
        self.assertRegex(styles, r"\.slide-card\s*\{[^}]*margin")
        self.assertRegex(styles, r"\.slide-card\.is-current\s*\{[^}]*transform:scale\(")
        self.assertRegex(styles, r"\.slide-card\.is-current\s*\{[^}]*margin-block:")

    def test_live_reload_revision_ignores_hidden_files_and_tracks_public_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            public = root / "index.html"
            hidden = root / ".cache"
            public.write_text("first")
            initial = self.server.revision_for(root)

            hidden.write_text("ignored")
            self.assertEqual(initial, self.server.revision_for(root))

            time.sleep(0.001)
            public.write_text("second")
            self.assertNotEqual(initial, self.server.revision_for(root))

    def test_watch_client_polls_revision_and_reloads_only_after_a_change(self):
        client = self.server.live_reload_script()
        server = (Path(__file__).parents[1] / "scripts" / "serve_participation.py").read_text()

        self.assertIn("/__apresenta/revision", client)
        self.assertIn("location.reload()", client)
        self.assertIn('parser.add_argument("--watch", action="store_true")', server)
        self.assertIn("inject_live_reload", server)

    def test_ia_usage_vote_replaces_prior_vote_and_keeps_identity_private(self):
        session = self.store.create("pausa")
        self.store.update_slide(session["sessionId"], session["presenterToken"], 2)

        self.store.vote(session["sessionId"], "browser-a", "explore")
        updated = self.store.vote(session["sessionId"], "browser-a", "automate")
        public = self.server.SessionStore.public(updated)
        poll = public["polls"]["ia-usage"]

        self.assertEqual(1, poll["totalVotes"])
        self.assertEqual(0, poll["totals"]["explore"])
        self.assertEqual(1, poll["totals"]["automate"])
        self.assertNotIn("browser-a", json.dumps(public))

    def test_ia_usage_vote_rejects_invalid_option_and_inactive_slide(self):
        session = self.store.create("pausa")

        with self.assertRaises(self.server.Conflict):
            self.store.vote(session["sessionId"], "browser-a", "explore")

        self.store.update_slide(session["sessionId"], session["presenterToken"], 2)
        with self.assertRaises(ValueError):
            self.store.vote(session["sessionId"], "browser-a", "not-an-option")

    def test_custom_poll_exposes_only_aggregated_totals(self):
        polls = {
            "delivery-readiness": {
                "slideIndex": 4,
                "options": ["ready", "blocked", "uncertain"],
            }
        }
        session = self.store.create("pausa", polls=polls)
        self.store.update_slide(session["sessionId"], session["presenterToken"], 4)

        updated = self.store.vote(session["sessionId"], "browser-a", "delivery-readiness", "ready")
        public = self.server.SessionStore.public(updated)

        self.assertEqual(1, public["polls"]["delivery-readiness"]["totalVotes"])
        self.assertEqual(1, public["polls"]["delivery-readiness"]["totals"]["ready"])
        self.assertNotIn("browser-a", json.dumps(public))

    def test_mobile_template_renders_poll_without_group_totals(self):
        root = Path(__file__).parents[1] / "assets" / "participar"
        client = (root / "app.js").read_text()
        styles = (root / "styles.css").read_text()

        self.assertIn("renderPoll", client)
        self.assertIn("data-poll-id", client)
        self.assertNotIn("poll-total", client)
        self.assertIn(".poll-option.is-selected", styles)

    def test_poll_gallery_shows_stage_and_mobile_states(self):
        gallery = Path(__file__).parents[1] / "assets" / "galeria-interacoes" / "index.html"

        self.assertTrue(gallery.is_file())
        content = gallery.read_text()
        self.assertIn("Resultado no palco", content)
        self.assertIn("Escolha no celular", content)
        self.assertIn("is-leading", content)
        self.assertIn("is-selected", content)

    def test_skill_documents_reusable_poll_contract(self):
        skill = (Path(__file__).parents[1] / "SKILL.md").read_text()

        self.assertIn("references/votacao.md", skill)
        self.assertIn("galeria-interacoes", skill)
        self.assertIn("100%", skill)


if __name__ == "__main__":
    unittest.main()
