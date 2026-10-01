from __future__ import annotations

from pathlib import Path
from PIL import Image


def save_png_pages(pages: list[Image.Image], output_dir: str | Path, stem: str = "handwritten") -> list[Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for index, page in enumerate(pages, start=1):
        path = output / f"{stem}_page_{index}.png"
        page.save(path, "PNG")
        paths.append(path)
    return paths


def save_pdf(pages: list[Image.Image], output_dir: str | Path, stem: str = "handwritten") -> Path:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    path = output / f"{stem}.pdf"
    rgb_pages = [page.convert("RGB") for page in pages]
    rgb_pages[0].save(path, "PDF", save_all=True, append_images=rgb_pages[1:], resolution=150.0)
    return path
