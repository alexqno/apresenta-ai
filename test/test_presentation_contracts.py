from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
SKILL = (ROOT / "apresenta-ai" / "SKILL.md").read_text()
DESIGN_SKILL = (ROOT / "apresenta-design" / "SKILL.md").read_text()
TEMPLATE = (ROOT / "apresenta-design" / "assets" / "design-template" / "components.css").read_text()
SKILL_COMPACT = " ".join(SKILL.split())


class PresentationContractsTests(unittest.TestCase):
    def test_skill_requires_visual_plan_and_design_component_contract(self):
        self.assertIn("Plano visual por tela", SKILL)
        self.assertIn("componentes literais do design", SKILL)
        self.assertIn("decisão explícita", SKILL)
        self.assertIn("variação semântica de card", SKILL)
        self.assertIn("não marque todas as telas como `nenhuma`", SKILL_COMPACT)

    def test_skill_requires_balanced_vertical_composition(self):
        self.assertIn("ocupação vertical", SKILL_COMPACT)
        self.assertIn("espaço inferior", SKILL_COMPACT)
        self.assertIn("Não alinhe todo conteúdo ao topo", SKILL_COMPACT)

    def test_template_exposes_content_title_tracking_token(self):
        self.assertIn("--presentation-title-tracking", TEMPLATE)
        self.assertIn("letter-spacing: var(--presentation-title-tracking)", TEMPLATE)

    def test_template_has_one_card_frame_contract(self):
        self.assertIn("--presentation-card-accent", TEMPLATE)
        self.assertIn("border-top: 0.5rem solid var(--presentation-card-accent)", TEMPLATE)

    def test_design_interview_defines_image_direction_for_presentations(self):
        self.assertIn("estilo de imagens", DESIGN_SKILL)
        self.assertIn("Direção de imagens", DESIGN_SKILL)
        self.assertIn("direção de imagens do design", SKILL)

    def test_skill_cannot_discard_design_image_direction_for_matching_screens(self):
        self.assertIn("recurso previsto pela direção de imagens", SKILL)
        self.assertIn("não pode ser descartado só porque", SKILL)
