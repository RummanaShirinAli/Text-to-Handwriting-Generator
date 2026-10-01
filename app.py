from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from src.config import DEFAULT_OUTPUT_DIR, FONT_OPTIONS, RenderConfig
from src.exporter import save_pdf, save_png_pages
from src.renderer import render_pages


class HandwritingApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Text-to-Handwriting Generator")
        self.root.geometry("980x760")
        self.root.minsize(860, 680)

        self.pages = []
        self.preview_photo = None

        self.font_size = tk.StringVar(value="42")
        self.line_spacing = tk.StringVar(value="22")
        self.font_style = tk.StringVar(value="Original")
        self.ink = tk.StringVar(value="Blue")
        self.process = tk.BooleanVar(value=True)
        self.natural_variation = tk.StringVar(value="4")
        self.status = tk.StringVar(value="Ready")

        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=18)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Text-to-Handwriting Generator", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(
            container,
            text="Convert text into customizable handwriting-style pages for notes and study material.",
        ).pack(anchor="w", pady=(3, 14))

        ttk.Label(container, text="Text input").pack(anchor="w")
        text_frame = ttk.Frame(container)
        text_frame.pack(fill="both", expand=True, pady=(5, 12))
        self.text_box = tk.Text(text_frame, wrap="word", height=12, font=("Segoe UI", 11))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_box.yview)
        self.text_box.configure(yscrollcommand=scrollbar.set)
        self.text_box.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        controls = ttk.LabelFrame(container, text="Layout & output settings", padding=12)
        controls.pack(fill="x", pady=(0, 12))

        ttk.Label(controls, text="Font size").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Spinbox(controls, from_=20, to=80, textvariable=self.font_size, width=8).grid(row=0, column=1, sticky="w")
        ttk.Label(controls, text="Line spacing").grid(row=0, column=2, sticky="w", padx=(25, 5))
        ttk.Spinbox(controls, from_=0, to=60, textvariable=self.line_spacing, width=8).grid(row=0, column=3, sticky="w")
        ttk.Label(controls, text="Ink color").grid(row=0, column=4, sticky="w", padx=(25, 5))
        ttk.Combobox(controls, textvariable=self.ink, values=["Blue", "Black"], state="readonly", width=10).grid(row=0, column=5, sticky="w")
        ttk.Checkbutton(
            controls,
            text="Apply OpenCV image processing",
            variable=self.process
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(8, 2))

        ttk.Label(
            controls,
            text="Handwriting variation"
        ).grid(
            row=1,
            column=3,
            sticky="w",
            padx=(18, 5),
            pady=(8, 2)
        )

        ttk.Spinbox(
            controls,
            from_=0,
            to=10,
            textvariable=self.natural_variation,
            width=8
        ).grid(
            row=1,
            column=4,
            sticky="w",
            pady=(8, 2)
        )

        ttk.Label(
            controls,
            text="Handwriting style"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=5,
            pady=5
        )

        ttk.Combobox(
            controls,
            textvariable=self.font_style,
            values=list(FONT_OPTIONS.keys()),
            state="readonly",
            width=14
        ).grid(
            row=2,
            column=1,
            sticky="w",
            padx=5,
            pady=5
        )

        ttk.Button(
            controls,
            text="Load .txt file",
            command=self.load_text_file
        ).grid(
            row=2,
            column=3,
            padx=(18, 5),
            pady=(8, 2)
        )

        ttk.Button(
            controls,
            text="Generate",
            command=self.generate
        ).grid(
            row=2,
            column=4,
            pady=(8, 2)
        ) 
        ttk.Label(controls, text="Handwriting style").grid(row=2, column=0, sticky="w", padx=5, pady=5)

        ttk.Combobox(
            controls,
            textvariable=self.font_style,
            values=list(FONT_OPTIONS.keys()),
            state="readonly",
            width=14,
        ).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(controls, text="Handwriting variation").grid(row=1, column=3, sticky="w", padx=(18, 5), pady=(8, 2))
        ttk.Spinbox(controls, from_=0, to=10, textvariable=self.natural_variation, width=8).grid(row=1, column=4, sticky="w", pady=(8, 2))
        ttk.Button(controls, text="Load .txt file", command=self.load_text_file).grid(row=2, column=3, padx=(18, 5), pady=(8, 2))
        ttk.Button(controls, text="Generate", command=self.generate).grid(row=2, column=4, pady=(8, 2))

        preview_frame = ttk.LabelFrame(container, text="Preview", padding=10)
        preview_frame.pack(fill="both", expand=True)
        self.preview_label = ttk.Label(preview_frame, text="Generated page preview will appear here.", anchor="center")
        self.preview_label.pack(fill="both", expand=True)

        footer = ttk.Frame(container)
        footer.pack(fill="x", pady=(10, 0))
        ttk.Label(footer, textvariable=self.status).pack(side="left")
        ttk.Button(footer, text="Save PNG pages", command=self.save_png).pack(side="right", padx=(8, 0))
        ttk.Button(footer, text="Save PDF", command=self.save_pdf).pack(side="right")

    def load_text_file(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        try:
            text = Path(path).read_text(encoding="utf-8")
            self.text_box.delete("1.0", "end")
            self.text_box.insert("1.0", text)
            self.status.set(f"Loaded: {Path(path).name}")
        except Exception as exc:
            messagebox.showerror("Could not load file", str(exc))

    def _config(self) -> RenderConfig:
        return RenderConfig(
            font_size=int(self.font_size.get()),
            line_spacing=int(self.line_spacing.get()),
            ink_color=(45, 70, 130) if self.ink.get() == "Blue" else (30, 30, 30),
            add_processing=self.process.get(),
            natural_variation=int(self.natural_variation.get()),
        )

    def generate(self) -> None:
        try:
            text = self.text_box.get("1.0", "end").strip()
            font_path = FONT_OPTIONS[self.font_style.get()]
            self.pages = render_pages(text, self._config(), font_path)
            self._show_preview(self.pages[0])
            self.status.set(f"Generated {len(self.pages)} page(s).")
        except ValueError as exc:
            messagebox.showwarning("Input required", str(exc))
            self.status.set("Please enter some text.")

        except Exception as exc:
            messagebox.showerror("Generation failed", str(exc))
            self.status.set("Generation failed")

    def _show_preview(self, page: Image.Image) -> None:
        preview = page.copy()
        preview.thumbnail((520, 520))
        self.preview_photo = ImageTk.PhotoImage(preview)
        self.preview_label.configure(image=self.preview_photo, text="")

    def _ensure_pages(self) -> bool:
        if not self.pages:
            self.generate()
        return bool(self.pages)

    def save_png(self) -> None:
        if not self._ensure_pages():
            return
        paths = save_png_pages(self.pages, DEFAULT_OUTPUT_DIR)
        self.status.set(f"Saved {len(paths)} PNG page(s) to output/")

    def save_pdf(self) -> None:
        if not self._ensure_pages():
            return
        path = save_pdf(self.pages, DEFAULT_OUTPUT_DIR)
        self.status.set(f"Saved PDF: {path.name}")


def main() -> None:
    root = tk.Tk()
    HandwritingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
