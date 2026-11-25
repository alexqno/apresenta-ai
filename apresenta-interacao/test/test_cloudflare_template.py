import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).parents[2]
PREPARE = ROOT / "apresenta-interacao" / "scripts" / "prepare_cloudflare.py"


class CloudflareTemplateTests(unittest.TestCase):
    def create_fixture(self, directory: Path) -> tuple[Path, Path, Path]:
        presentation = directory / "pausa"
        design = directory / "designs" / "neutro"
        (presentation / "assets").mkdir(parents=True)
        (design / "assets").mkdir(parents=True)
        (presentation / "index.html").write_text("<main>pausa</main>")
        (presentation / "app.js").write_text("console.log('pausa')")
        (presentation / "assets" / "icone.svg").write_text("<svg/>")
        (design / "tokens.css").write_text(":root{}")
        (design / "components.css").write_text(".card{}")
        (design / "assets" / "marca.svg").write_text("<svg/>")
        manifest = presentation / "cloudflare-assets.json"
        manifest.write_text(json.dumps({
            "deck": ["index.html", "app.js", "assets/icone.svg"],
            "design": ["tokens.css", "components.css", "assets/marca.svg"],
        }))
        return presentation, design, manifest

    def test_prepares_neutral_cloudflare_project_with_only_declared_assets(self):
        with tempfile.TemporaryDirectory() as temporary:
            presentation, design, manifest = self.create_fixture(Path(temporary))
            result = subprocess.run([
                "python3", str(PREPARE), "--presentation", str(presentation),
                "--design", str(design), "--worker-name", "pausa-demo",
                "--manifest", str(manifest),
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            cloudflare = presentation / "cloudflare"
            self.assertTrue((cloudflare / "src" / "index.ts").is_file())
            self.assertTrue((cloudflare / "public" / "pausa" / "assets" / "icone.svg").is_file())
            self.assertTrue((cloudflare / "public" / "designs" / "neutro" / "assets" / "marca.svg").is_file())
            self.assertIn('"name": "pausa-demo"', (cloudflare / "wrangler.jsonc").read_text())
            self.assertIn('export const DEFAULT_DECK = "pausa";', (cloudflare / "src" / "config.ts").read_text())

    def test_rejects_asset_path_outside_declared_roots(self):
        with tempfile.TemporaryDirectory() as temporary:
            presentation, design, manifest = self.create_fixture(Path(temporary))
            manifest.write_text(json.dumps({"deck": ["../segredo.txt"], "design": []}))
            result = subprocess.run([
                "python3", str(PREPARE), "--presentation", str(presentation),
                "--design", str(design), "--worker-name", "pausa-demo",
                "--manifest", str(manifest),
            ], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("caminho", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
