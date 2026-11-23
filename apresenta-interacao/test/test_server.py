import importlib.util
import json
from pathlib import Path
import tempfile
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


if __name__ == "__main__":
    unittest.main()
