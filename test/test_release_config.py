import importlib.util
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).parents[1]


class ReleaseConfigurationTests(unittest.TestCase):
    def test_release_please_versions_both_skill_packages(self):
        config = json.loads((ROOT / "release-please-config.json").read_text())
        manifest = json.loads((ROOT / ".release-please-manifest.json").read_text())
        workflow = (ROOT / ".github/workflows/release-please.yml").read_text()
        versions = {
            json.loads((ROOT / skill / "version.json").read_text())["version"]
            for skill in ("apresenta-ai", "apresenta-design", "apresenta-interacao")
        }

        self.assertEqual({manifest["."]}, versions)
        self.assertEqual("simple", config["release-type"])
        self.assertIn("apresenta-ai/version.json", json.dumps(config))
        self.assertIn("apresenta-design/version.json", json.dumps(config))
        self.assertIn("apresenta-interacao/version.json", json.dumps(config))
        self.assertIn("branches: [master]", workflow)
        self.assertIn("googleapis/release-please-action@v4", workflow)
        self.assertIn("pull-requests: write", workflow)


class SkillUpdaterTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location(
            "update_skills", ROOT / "apresenta-ai/scripts/update_skills.py"
        )
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.source = self.root / "source"
        self.destination = self.root / "installed"
        for parent in (self.source, self.destination):
            for skill, version in (("apresenta-ai", "0.2.0"), ("apresenta-design", "0.2.0"), ("apresenta-interacao", "0.2.0")):
                folder = parent / skill
                folder.mkdir(parents=True)
                (folder / "SKILL.md").write_text(f"# {skill}\n")
                (folder / "version.json").write_text(json.dumps({"version": version}))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_check_reports_update_without_changing_installation(self):
        result = self.module.update_from_source(self.source, self.destination, check_only=True)

        self.assertEqual("0.2.0", result.available)
        self.assertFalse(result.updated)
        self.assertEqual("0.2.0", self.module.read_version(self.destination / "apresenta-ai"))

    def test_update_replaces_both_skill_packages(self):
        for skill in ("apresenta-ai", "apresenta-design", "apresenta-interacao"):
            (self.destination / skill / "version.json").write_text(json.dumps({"version": "0.1.0"}))
            (self.source / skill / "new-file").write_text("new")

        result = self.module.update_from_source(self.source, self.destination, check_only=False)

        self.assertTrue(result.updated)
        for skill in ("apresenta-ai", "apresenta-design", "apresenta-interacao"):
            self.assertEqual("0.2.0", self.module.read_version(self.destination / skill))
            self.assertTrue((self.destination / skill / "new-file").exists())

    def test_updater_installs_interaction_skill(self):
        for skill in ("apresenta-ai", "apresenta-design", "apresenta-interacao"):
            (self.destination / skill / "version.json").write_text(json.dumps({"version": "0.1.0"}))

        result = self.module.update_from_source(self.source, self.destination, check_only=False)

        self.assertTrue(result.updated)
        self.assertTrue((self.destination / "apresenta-interacao" / "SKILL.md").exists())

    def test_mismatched_source_versions_leave_installation_unchanged(self):
        (self.source / "apresenta-design/version.json").write_text(json.dumps({"version": "0.3.0"}))
        before = (self.destination / "apresenta-ai/version.json").read_text()

        with self.assertRaises(self.module.UpdateError):
            self.module.update_from_source(self.source, self.destination, check_only=False)

        self.assertEqual(before, (self.destination / "apresenta-ai/version.json").read_text())

    def test_failed_second_swap_restores_original_packages(self):
        for skill in ("apresenta-ai", "apresenta-design", "apresenta-interacao"):
            (self.destination / skill / "version.json").write_text(json.dumps({"version": "0.1.0"}))

        original_move = self.module.shutil.move

        def fail_second_staged_move(source, target):
            if Path(source).parent.name == "staging" and Path(source).name == "apresenta-design":
                raise OSError("simulated failure")
            return original_move(source, target)

        with patch.object(self.module.shutil, "move", side_effect=fail_second_staged_move):
            with self.assertRaises(self.module.UpdateError):
                self.module.update_from_source(self.source, self.destination, check_only=False)

        for skill in ("apresenta-ai", "apresenta-design", "apresenta-interacao"):
            self.assertEqual("0.1.0", self.module.read_version(self.destination / skill))


if __name__ == "__main__":
    unittest.main()
