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

    def test_mobile_template_supports_weighted_multi_select_diagnostic(self):
        root = Path(__file__).parents[1] / "assets" / "participar"
        client = (root / "app.js").read_text()
        styles = (root / "styles.css").read_text()

        self.assertIn("renderDiagnostic", client)
        self.assertIn("maxSelections", client)
        self.assertIn("/diagnostics/", client)
        self.assertIn(".diagnostic-option.is-selected", styles)

    def test_mobile_template_is_generic_and_postit_can_submit_with_enter(self):
        root = Path(__file__).parents[1] / "assets" / "participar"
        client = (root / "app.js").read_text()
        styles = (root / "styles.css").read_text()
        moderator = (Path(__file__).parents[1] / "assets" / "moderador" / "styles.css").read_text()

        self.assertIn("event.key === 'Enter'", client)
        self.assertIn("slide.postits?.subtitle || slide.summary", client)
        self.assertIn("slide.links || []", client)
        self.assertNotIn("Korporate", client + styles + moderator)
        self.assertNotIn("--kp-", styles + moderator)

    def test_skill_documents_weighted_diagnostic_option(self):
        skill = (Path(__file__).parents[1] / "SKILL.md").read_text()

        self.assertIn("references/diagnostico.md", skill)
        self.assertIn("múltipla seleção", skill)
        self.assertIn("limiar", skill)

    def test_diagnostic_replaces_selection_and_keeps_identity_private(self):
        diagnostics = {"task-xray": {"slideIndex": 6, "items": ["objective", "scope", "risk"]}}
        session = self.store.create("pausa", diagnostics=diagnostics)
        self.store.update_slide(session["sessionId"], session["presenterToken"], 6)

        self.store.diagnose(session["sessionId"], "browser-a", "task-xray", ["objective", "risk"])
        updated = self.store.diagnose(session["sessionId"], "browser-a", "task-xray", ["scope"])
        public = self.server.SessionStore.public(updated)

        self.assertEqual({"objective": 0, "scope": 1, "risk": 0}, public["diagnostics"]["task-xray"]["totals"])
        self.assertEqual(1, public["diagnostics"]["task-xray"]["totalResponses"])
        self.assertNotIn("browser-a", json.dumps(public))

    def test_diagnostic_rejects_unknown_item_and_inactive_slide(self):
        diagnostics = {"task-xray": {"slideIndex": 6, "items": ["objective", "scope"]}}
        session = self.store.create("pausa", diagnostics=diagnostics)

        with self.assertRaises(self.server.Conflict):
            self.store.diagnose(session["sessionId"], "browser-a", "task-xray", ["objective"])
        self.store.update_slide(session["sessionId"], session["presenterToken"], 6)
        with self.assertRaises(ValueError):
            self.store.diagnose(session["sessionId"], "browser-a", "task-xray", ["unknown"])

    def test_diagnostic_rejects_more_than_configured_selection_limit(self):
        diagnostics = {"task-xray": {"slideIndex": 6, "items": ["objective", "scope", "risk"], "maxSelections": 2}}
        session = self.store.create("pausa", diagnostics=diagnostics)
        self.store.update_slide(session["sessionId"], session["presenterToken"], 6)

        with self.assertRaises(ValueError):
            self.store.diagnose(session["sessionId"], "browser-a", "task-xray", ["objective", "scope", "risk"])

    def test_triage_replaces_card_classifications_and_keeps_identity_private(self):
        triages = {"context-filter": {"slideIndex": 13, "categories": ["send", "treat", "never"], "items": ["public-brief", "access-token"]}}
        session = self.store.create("pausa", triages=triages)
        self.store.update_slide(session["sessionId"], session["presenterToken"], 13)

        self.store.triage(session["sessionId"], "browser-a", "context-filter", {"public-brief": "send", "access-token": "treat"})
        updated = self.store.triage(session["sessionId"], "browser-a", "context-filter", {"public-brief": "send", "access-token": "never"})
        public = self.server.SessionStore.public(updated)

        self.assertEqual(1, public["triages"]["context-filter"]["totals"]["access-token"]["never"])
        self.assertEqual(0, public["triages"]["context-filter"]["totals"]["access-token"]["treat"])
        self.assertNotIn("browser-a", json.dumps(public))

    def test_triage_rejects_inactive_slide_and_unknown_category(self):
        triages = {"context-filter": {"slideIndex": 13, "categories": ["send", "treat", "never"], "items": ["public-brief"]}}
        session = self.store.create("pausa", triages=triages)

        with self.assertRaises(self.server.Conflict):
            self.store.triage(session["sessionId"], "browser-a", "context-filter", {"public-brief": "send"})
        self.store.update_slide(session["sessionId"], session["presenterToken"], 13)
        with self.assertRaises(ValueError):
            self.store.triage(session["sessionId"], "browser-a", "context-filter", {"public-brief": "unknown"})

    def test_presenter_session_includes_aggregate_triage_totals(self):
        triages = {"context-filter": {"slideIndex": 13, "categories": ["send", "treat", "never"], "items": ["public-brief"]}}
        session = self.store.create("pausa", triages=triages)

        presenter = self.server.SessionStore.presenter(session)

        self.assertEqual(session["presenterToken"], presenter["presenterToken"])
        self.assertEqual({"send": 0, "treat": 0, "never": 0}, presenter["triages"]["context-filter"]["totals"]["public-brief"])
        self.assertNotIn("triageDefinitions", presenter)
        self.assertNotIn("browser-a", json.dumps(presenter))

    def test_postit_submission_stays_private_until_approved(self):
        postits = {"practices": {"slideIndex": 16, "maxLength": 280}}
        session = self.store.create("pausa", postits=postits)
        self.store.update_slide(session["sessionId"], session["presenterToken"], 16)

        submitted = self.store.submit_postit(session["sessionId"], "browser-a", "practices", "<b>Reviso o diff</b>")
        public = self.server.SessionStore.public(submitted)
        private = self.store.moderator(session["sessionId"], session["presenterToken"])

        self.assertEqual([], public["postits"]["practices"])
        self.assertEqual("pending", private["postits"]["practices"][0]["status"])
        self.assertEqual("<b>Reviso o diff</b>", private["postits"]["practices"][0]["text"])

    def test_postit_approval_exposes_stable_pastel_style(self):
        postits = {"practices": {"slideIndex": 16, "maxLength": 280}}
        session = self.store.create("pausa", postits=postits)
        self.store.update_slide(session["sessionId"], session["presenterToken"], 16)
        submitted = self.store.submit_postit(session["sessionId"], "browser-a", "practices", "Reviso o diff")
        postit = self.store.moderator(session["sessionId"], session["presenterToken"])["postits"]["practices"][0]

        approved = self.store.decide_postit(session["sessionId"], session["presenterToken"], "practices", postit["id"], "approved")
        visible = self.server.SessionStore.public(approved)["postits"]["practices"]

        self.assertEqual("approved", visible[0]["status"])
        self.assertEqual(postit["style"], visible[0]["style"])
        self.assertIn(visible[0]["style"]["color"], {"amber", "peach", "mint", "sky", "lilac"})

    def test_postit_layout_uses_safe_organic_positions_with_only_small_overlaps(self):
        styles = []
        for position in range(15):
            style = self.server.postit_style(position, styles)
            self.assertGreaterEqual(style["x"], 12)
            self.assertLessEqual(style["x"], 88)
            self.assertGreaterEqual(style["y"], 31)
            self.assertLessEqual(style["y"], 75)
            for existing in styles:
                overlap = max(0, 18 - abs(style["x"] - existing["x"])) * max(0, 18 - abs(style["y"] - existing["y"]))
                self.assertLessEqual(overlap, 90)
            styles.append(style)
        self.assertGreater(len({style["x"] for style in styles}), 5)
        self.assertGreater(len({style["y"] for style in styles}), 3)

    def test_postit_layout_distributes_second_layer_before_reusing_a_position(self):
        styles = [self.server.postit_style(position, []) for position in range(15)]
        for position in range(1, len(styles)):
            styles[position] = self.server.postit_style(position, styles[:position])

        second_layer = []
        for position in range(15, 23):
            style = self.server.postit_style(position, styles)
            second_layer.append((style["x"], style["y"]))
            styles.append(style)

        self.assertEqual(len(second_layer), len(set(second_layer)))
        self.assertGreater(len({x for x, _ in second_layer}), 3)

    def test_private_moderator_template_reads_token_from_fragment(self):
        moderator = Path(__file__).parents[1] / "assets" / "moderador" / "app.js"

        self.assertTrue(moderator.is_file())
        content = moderator.read_text(encoding="utf-8")
        self.assertIn("location.hash", content)
        self.assertIn("X-Presenter-Token", content)
        self.assertIn("history.replaceState", content)

    def test_moderator_uses_same_live_navigation_contract_as_participant(self):
        app = (Path(__file__).parents[1] / "assets" / "moderador" / "app.js").read_text(encoding="utf-8")
        html = (Path(__file__).parents[1] / "assets" / "moderador" / "index.html").read_text(encoding="utf-8")

        self.assertIn("IntersectionObserver", app)
        self.assertIn("scrollIntoView", app)
        self.assertIn("live-jump", html)
        self.assertIn("new EventSource", app)

    def test_poll_gallery_shows_stage_and_mobile_states(self):
        gallery = Path(__file__).parents[1] / "assets" / "galeria-interacoes" / "index.html"

        self.assertTrue(gallery.is_file())
        content = gallery.read_text()
        self.assertIn("Resultado no palco", content)
        self.assertIn("Escolha no celular", content)
        self.assertIn("is-leading", content)
        self.assertIn("is-selected", content)
        self.assertIn("Diagnóstico ponderado", content)
        self.assertIn("diagnostic-option", content)
        self.assertIn("limiar", content)

    def test_skill_documents_reusable_poll_contract(self):
        skill = (Path(__file__).parents[1] / "SKILL.md").read_text()

        self.assertIn("references/votacao.md", skill)
        self.assertIn("galeria-interacoes", skill)
        self.assertIn("100%", skill)

    def test_skill_documents_stage_width_transition_motion(self):
        skill = (Path(__file__).parents[1] / "SKILL.md").read_text()
        gallery = (Path(__file__).parents[1] / "assets" / "galeria-interacoes" / "index.html").read_text()

        self.assertIn("largura atual para o novo percentual", skill)
        self.assertIn("clip-path", skill)
        self.assertIn("prefers-reduced-motion", skill)
        self.assertIn("transition:width", gallery)


if __name__ == "__main__":
    unittest.main()
