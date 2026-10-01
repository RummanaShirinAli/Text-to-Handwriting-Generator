from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_FONT = PROJECT_ROOT / "fonts" / "Handwriting.ttf"

FONT_OPTIONS = {
    "Original": DEFAULT_FONT,
    "Caveat": PROJECT_ROOT / "fonts" / "Caveat.ttf",
    "Kalam": PROJECT_ROOT / "fonts" / "Kalam.ttf",
}

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"


@dataclass
class RenderConfig:
    page_width: int = 1240
    page_height: int = 1754
    margin_left: int = 90
    margin_right: int = 90
    margin_top: int = 95
    margin_bottom: int = 95
    font_size: int = 48
    line_spacing: int = 22
    ink_color: tuple[int, int, int] = (45, 70, 130)
    paper_color: tuple[int, int, int] = (250, 249, 244)
    add_processing: bool = True
    natural_variation: int = 4
    variation_seed: int = 2026
    output_format: str = "png"

    @property
    def content_width(self) -> int:
        return self.page_width - self.margin_left - self.margin_right

    @property
    def content_height(self) -> int:
        return self.page_height - self.margin_top - self.margin_bottom
