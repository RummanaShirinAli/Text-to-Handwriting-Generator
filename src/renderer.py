from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .config import DEFAULT_FONT, RenderConfig
from .image_processor import apply_paper_processing
from .text_processor import wrap_text_by_width


def load_font(
    font_path: str | Path,
    size: int
) -> ImageFont.FreeTypeFont:
    path = Path(font_path)

    if not path.exists():
        raise FileNotFoundError(f"Font not found: {path}")

    return ImageFont.truetype(str(path), size=size)


def _draw_word_with_variation(
    page: Image.Image,
    word: str,
    font: ImageFont.FreeTypeFont,
    x: int,
    y: int,
    ink_color: tuple[int, int, int],
    variation: int,
    rng: random.Random,
) -> int:
    """
    Draw one complete word with very small natural variation.

    Returns the horizontal width occupied by the word.
    """

    if not word:
        return 0

    amount = max(0, min(10, variation))

    draw = ImageDraw.Draw(page)

    # Normal rendering when variation is disabled.
    if amount == 0:
        draw.text(
            (x, y),
            word,
            font=font,
            fill=ink_color,
        )
        return int(draw.textlength(word, font=font))

    # Measure the complete word.
    bbox = font.getbbox(word)

    text_width = max(
        1,
        bbox[2] - bbox[0],
    )

    text_height = max(
        1,
        bbox[3] - bbox[1],
    )

    padding = max(
        6,
        int(font.size * 0.12),
    )

    layer = Image.new(
        "RGBA",
        (
            text_width + padding * 2,
            text_height + padding * 2,
        ),
        (0, 0, 0, 0),
    )

    layer_draw = ImageDraw.Draw(layer)

    layer_draw.text(
        (
            padding - bbox[0],
            padding - bbox[1],
        ),
        word,
        font=font,
        fill=ink_color + (255,),
    )

    # Very small scale variation.
    scale = rng.uniform(
        1.0 - 0.002 * amount,
        1.0 + 0.002 * amount,
    )

    if scale != 1.0:
        layer = layer.resize(
            (
                max(1, int(layer.width * scale)),
                max(1, int(layer.height * scale)),
            ),
            Image.Resampling.BICUBIC,
        )

    # Extremely small rotation.
    angle = rng.uniform(
        -0.012 * amount,
        0.012 * amount,
    )

    if abs(angle) > 0.001:
        layer = layer.rotate(
            angle,
            resample=Image.Resampling.BICUBIC,
            expand=True,
        )

    # Very small baseline movement.
    jitter_y = rng.uniform(
        -0.20 * amount,
        0.20 * amount,
    )

    paste_x = int(
        x
        + padding
        - layer.width / 2
        + (text_width + padding * 2) / 2
    )

    paste_y = int(
        y
        + padding
        - layer.height / 2
        + (text_height + padding * 2) / 2
        + jitter_y
    )

    page.paste(
        layer,
        (paste_x, paste_y),
        layer,
    )

    # IMPORTANT:
    # Cursor movement is based on the ORIGINAL word width,
    # not the transformed image dimensions.
    return int(
        draw.textlength(word, font=font)
    )

def _draw_original_line(
    page: Image.Image,
    line: str,
    font: ImageFont.FreeTypeFont,
    x: int,
    y: int,
    ink_color: tuple[int, int, int],
    variation: int,
    rng: random.Random,
) -> None:
    """Render the original handwriting font safely as one line."""

    if not line:
        return

    amount = max(0, min(10, variation))

    if amount == 0:
        ImageDraw.Draw(page).text(
            (x, y),
            line,
            font=font,
            fill=ink_color,
        )
        return

    bbox = font.getbbox(line)

    text_width = max(
        1,
        bbox[2] - bbox[0],
    )

    text_height = max(
        1,
        bbox[3] - bbox[1],
    )

    padding = max(
        12,
        int(font.size * 0.25),
    )

    layer = Image.new(
        "RGBA",
        (
            text_width + padding * 2,
            text_height + padding * 2,
        ),
        (0, 0, 0, 0),
    )

    layer_draw = ImageDraw.Draw(layer)

    layer_draw.text(
        (
            padding - bbox[0],
            padding - bbox[1],
        ),
        line,
        font=font,
        fill=ink_color + (255,),
    )

    scale = rng.uniform(
        1.0 - 0.008 * amount,
        1.0 + 0.008 * amount,
    )

    angle = rng.uniform(
        -0.05 * amount,
        0.05 * amount,
    )

    layer = layer.resize(
        (
            max(1, int(layer.width * scale)),
            max(1, int(layer.height * scale)),
        ),
        Image.Resampling.BICUBIC,
    )

    layer = layer.rotate(
        angle,
        resample=Image.Resampling.BICUBIC,
        expand=True,
    )

    jitter_x = rng.uniform(
        -1.2 * amount,
        1.2 * amount,
    )

    jitter_y = rng.uniform(
        -0.45 * amount,
        0.45 * amount,
    )

    paste_x = int(
        x
        + jitter_x
        - (layer.width - text_width) / 2
    )

    paste_y = int(
        y
        + jitter_y
        - (layer.height - text_height) / 2
    )

    page.paste(
        layer,
        (paste_x, paste_y),
        layer,
    )


def _draw_line_with_variation(
    page: Image.Image,
    line: str,
    font: ImageFont.FreeTypeFont,
    x: int,
    y: int,
    ink_color: tuple[int, int, int],
    variation: int,
    rng: random.Random,
) -> None:
    """
    Draw a complete line word-by-word.

    Variation is deliberately subtle to preserve readability
    and prevent overlapping text.
    """

    if not line:
        return

    draw = ImageDraw.Draw(page)

    words = line.split(" ")

    cursor_x = x

    space_width = draw.textlength(
        " ",
        font=font,
    )

    for word in words:

    # Original font is rendered normally because its font metrics
    # can cause transformed words to overlap.

        word_width = _draw_word_with_variation(
            page=page,
            word=word,
            font=font,
            x=int(cursor_x),
            y=y,
            ink_color=ink_color,
            variation=variation,
            rng=rng,
        )

        cursor_x += word_width
        cursor_x += space_width + 8


def render_pages(
    text: str,
    config: RenderConfig,
    font_path: str | Path = DEFAULT_FONT,
) -> list[Image.Image]:

    text = text.strip()

    if not text:
        raise ValueError(
            "Please enter some text before generating pages."
        )

    font = load_font(
        font_path,
        config.font_size,
    )

    is_original_font = (
        Path(font_path).name.lower() == "handwriting.ttf"
    )

    probe = Image.new(
        "RGB",
        (
            config.page_width,
            config.page_height,
        ),
        config.paper_color,
    )

    probe_draw = ImageDraw.Draw(probe)

    lines = wrap_text_by_width(
        text,
        probe_draw,
        font,
        config.content_width,
    )

    bbox = probe_draw.textbbox(
        (0, 0),
        "Ag",
        font=font,
    )

    line_height = (
        max(1, bbox[3] - bbox[1])
        + config.line_spacing
    )

    usable_lines = max(
        1,
        config.content_height // line_height,
    )

    rng = random.Random(
        config.variation_seed
    )

    pages: list[Image.Image] = []

    for start in range(
        0,
        len(lines),
        usable_lines,
    ):

        page_lines = lines[
            start:start + usable_lines
        ]

        image = Image.new(
            "RGB",
            (
                config.page_width,
                config.page_height,
            ),
            config.paper_color,
        )

        y = config.margin_top

        for line in page_lines:
            
            if is_original_font:
                _draw_original_line(
                    page=image,
                    line=line,
                    font=font,
                    x=config.margin_left,
                    y=y,
                    ink_color=config.ink_color,
                    variation=config.natural_variation,
                    rng=rng,
                )
            else:
                _draw_line_with_variation(
                    page=image,
                    line=line,
                    font=font,
                    x=config.margin_left,
                    y=y,
                    ink_color=config.ink_color,
                    variation=config.natural_variation,
                    rng=rng,
                )

            y += line_height

        if config.add_processing:
            image = apply_paper_processing(
                image,
                seed=config.variation_seed + start,
            )

        pages.append(image)

    return pages