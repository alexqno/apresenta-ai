from pathlib import Path
import json
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).parents[1]
SKILL = (ROOT / "apresenta-ai" / "SKILL.md").read_text()
DESIGN_SKILL = (ROOT / "apresenta-design" / "SKILL.md").read_text()
TEMPLATE = (ROOT / "apresenta-design" / "assets" / "design-template" / "components.css").read_text()
TOKENS = (ROOT / "apresenta-design" / "assets" / "design-template" / "tokens.css").read_text()
GALLERY = (ROOT / "apresenta-design" / "assets" / "design-template" / "gallery.html").read_text()
PALCO_BASE = (ROOT / "apresenta-ai" / "assets" / "palco-base" / "palco.js").read_text()
CAPTURE_TOOL = (ROOT / "apresenta-ai" / "scripts" / "capturar_palco.cjs").read_text()
PLAN_VALIDATOR = ROOT / "apresenta-ai" / "scripts" / "validar_planejamento.cjs"
VISUAL_REPORT = ROOT / "apresenta-ai" / "scripts" / "montar_comparacao_visual.cjs"
SKILL_COMPACT = " ".join(SKILL.split())


class PresentationContractsTests(unittest.TestCase):
    def test_capture_tool_supports_current_and_legacy_stage_contracts(self):
        self.assertIn(".presentation-stage", CAPTURE_TOOL)
        self.assertIn("#presentation", CAPTURE_TOOL)
        self.assertIn("data-slide-id", CAPTURE_TOOL)
        self.assertIn("data-slide", CAPTURE_TOOL)

    def test_skill_guides_human_readable_plan_and_visual_proximity_proof(self):
        for contract in [
            "planejamento.md",
            "planejamento.json",
            "validar_planejamento.cjs",
            "capturar_palco.cjs",
            "montar_comparacao_visual.cjs",
            "referência aprovada",
            "não peça ao usuário para editar JSON",
        ]:
            self.assertIn(contract, SKILL)

    def test_visual_comparison_report_pairs_reference_and_candidate_captures(self):
        manifest = {
            "version": 1,
            "captures": [{
                "width": 1366,
                "height": 768,
                "slides": [{"id": "abertura", "file": "1366x768/01-abertura.png"}]
            }]
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reference = root / "referencia"
            candidate = root / "candidata"
            report = root / "comparacao.html"
            reference.mkdir()
            candidate.mkdir()
            (reference / "manifest.json").write_text(json.dumps(manifest))
            (candidate / "manifest.json").write_text(json.dumps(manifest))
            result = subprocess.run(
                ["node", str(VISUAL_REPORT), str(reference), str(candidate), str(report)],
                capture_output=True,
                text=True,
            )
            content = report.read_text() if report.exists() else ""
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1366×768", content)
        self.assertIn("abertura", content)
        self.assertIn("Referência aprovada", content)
        self.assertIn("Nova versão", content)

    def test_planning_contract_validator_accepts_deck_with_matching_plan(self):
        plan = {
            "version": 1,
            "slides": [{
                "id": "abertura",
                "sources": [{"document": "roteiro.md", "section": "Abertura"}],
                "message": "Mensagem central.",
                "requiredContent": ["Contexto"],
                "prohibitedContent": ["Conclusão"],
                "composition": "tese",
                "component": ".presentation-heading",
                "image": {"decision": "nenhuma", "rationale": "Tese curta."},
                "verticalUse": "centro"
            }]
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan_path = root / "planejamento.json"
            index_path = root / "index.html"
            plan_path.write_text(json.dumps(plan))
            index_path.write_text('''<main class="presentation-stage">
              <section data-slide-id="abertura"><header class="presentation-heading"></header></section>
            </main>''')
            result = subprocess.run(
                ["node", str(PLAN_VALIDATOR), str(plan_path), str(index_path)],
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_skill_requires_visual_plan_and_design_component_contract(self):
        self.assertIn("Plano visual por tela", SKILL)
        self.assertIn("componentes literais do design", SKILL)
        self.assertIn("decisão explícita", SKILL)
        self.assertIn("variação semântica de card", SKILL)
        self.assertIn("não marque todas as telas como `nenhuma`", SKILL_COMPACT)
        self.assertIn("espessura definida pelo design, ou `0.5rem`", SKILL)

    def test_skill_requires_balanced_vertical_composition(self):
        self.assertIn("ocupação vertical", SKILL_COMPACT)

    def test_fullscreen_stage_requests_screen_wake_lock(self):
        for contract in [
            "navigator.wakeLock?.request",
            "fullscreenchange",
            "visibilitychange",
            "pagehide",
            "releaseScreenWakeLock",
        ]:
            self.assertIn(contract, PALCO_BASE)
        self.assertIn("Screen Wake Lock", SKILL)
        self.assertIn("`file://` não é modo suportado", " ".join(SKILL.split()))
        self.assertIn("espaço inferior", SKILL_COMPACT)
        self.assertIn("Não alinhe todo conteúdo ao topo", SKILL_COMPACT)

    def test_template_exposes_content_title_tracking_token(self):
        self.assertIn("--presentation-title-tracking", TEMPLATE)
        self.assertRegex(TEMPLATE, r"letter-spacing:\s*var\(--presentation-title-tracking\)")

    def test_template_has_one_card_frame_contract(self):
        self.assertIn("--presentation-card-accent", TEMPLATE)
        self.assertRegex(TEMPLATE, r"border-top:\s*0\.5rem solid var\(--presentation-card-accent\)")

    def test_template_exposes_generic_semantic_states(self):
        for token in [
            "--presentation-color-success",
            "--presentation-color-warning",
            "--presentation-color-danger",
            "--presentation-color-info",
        ]:
            self.assertIn(token, TOKENS)
        for component in [
            ".presentation-card--success",
            ".presentation-card--warning",
            ".presentation-card--danger",
            ".presentation-card--info",
            ".presentation-status--success",
            ".presentation-status--warning",
            ".presentation-status--danger",
            ".presentation-status--info",
        ]:
            self.assertIn(component, TEMPLATE)

    def test_template_gallery_covers_reusable_compositions(self):
        for component in [
            "presentation-card-grid--five",
            "presentation-card-grid--two",
            "presentation-card-grid--three",
            "presentation-chapter",
            "presentation-metric-bars",
            "presentation-code",
            "presentation-slide--art",
            "presentation-flow-grid--six",
            "presentation-contrast-grid",
            "presentation-sequence",
            "presentation-responsibility-rail",
            "presentation-evidence-rail",
            "presentation-checkpoints",
            "presentation-filter-flow",
            "presentation-mandate-flow",
            "presentation-signal-panel",
            "presentation-circuit",
            "presentation-closing",
        ]:
            self.assertIn(component, GALLERY)
        self.assertNotIn("Korporate", GALLERY)

    def test_design_interview_defines_image_direction_for_presentations(self):
        self.assertIn("estilo de imagens", DESIGN_SKILL)
        self.assertIn("Direção de imagens", DESIGN_SKILL)
        self.assertIn("direção de imagens do design", SKILL)

    def test_skill_cannot_discard_design_image_direction_for_matching_screens(self):
        self.assertIn("recurso previsto pela direção de imagens", SKILL)
        self.assertIn("não pode ser descartado só porque", SKILL)

    def test_skill_prevents_cards_from_becoming_default_layout(self):
        self.assertIn("Cards não são layout padrão", SKILL)
        self.assertIn("inventário de composições", SKILL)
