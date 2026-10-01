## Text-to-Handwriting Generator

A Python desktop application that converts typed text into customizable handwriting-style pages for notes and study material.

The project combines text measurement, font rendering, controlled visual variation, OpenCV-based image processing, multi-page layout, and document export into a single desktop workflow.

## Features

- Convert typed text into handwriting-style pages using bundled TrueType fonts.

- Choose between multiple handwriting styles: Original, Caveat, and Kalam.

- Measure rendered text width for reliable word wrapping.

- Automatically split longer content across multiple pages.

- Configure font size, line spacing, and ink color.

- Control the amount of handwriting-style visual variation.

- Apply optional OpenCV post-processing for subtle paper texture and tonal variation.

- Load content directly from `.txt` files.

- Preview generated pages inside the desktop application.

- Export generated pages as PNG images.

- Export generated pages as a multi-page PDF.

- Validate empty input and missing font files through the GUI.

## Tech Stack

- Python

- Tkinter

- Pillow

- OpenCV

- NumPy

## Architecture


User text / .txt file
        |
        v
   Tkinter GUI
        |
        v
Text wrapping & measurement
        |
        v
 Handwriting renderer
        |
        +--> controlled visual variation
        |
        v
OpenCV image processing
        |
        +----> PNG pages
        |
        +----> Multi-page PDF


## Project Structure

Text To Handwriting/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── fonts/
│   ├── Handwriting.ttf
│   ├── Caveat.ttf
│   ├── Kalam.ttf
│   ├── CAveat OFL.txt
│   └── Kalam OFL.txt
│
├── output/
│   └── .gitkeep
│
└── src/
    ├── config.py
    ├── exporter.py
    ├── image_processor.py
    ├── renderer.py
    └── text_processor.py

## How to Run

1. Install Python
Python 3.10 or newer is recommended.

2. Install dependencies
python -m pip install -r requirements.txt

3. Start the application
python app.py

4. Generate handwriting-style pages
- Enter text manually or load a `.txt` file.
- Select a handwriting style.
- Adjust font size, line spacing, ink color, and variation.
- Enable or disable OpenCV image processing.
- Click Generate.

5. Export
Use Save PNG pages to export individual page images or Save PDF to export the generated pages as a multi-page PDF.

## Technical Highlights

1. Text Layout

Rendered pixel measurements are used for text wrapping instead of fixed character counts. This allows the layout to adapt to different font sizes and handwriting fonts.

2. Pagination

Page capacity is calculated from the configured margins, font metrics, and line spacing. Longer content is automatically distributed across multiple pages.

3. Controlled Rendering Variation

The renderer applies bounded visual variation to create a less uniform handwriting appearance.

For the primary handwriting font, variation is applied at the line level. Alternative handwriting fonts use subtle word-level transformations to preserve readability while introducing small differences in scale, rotation, and baseline position.

A seeded random generator is used so that generated output can be reproduced consistently.

4. OpenCV Image Processing

Generated pages can optionally pass through an OpenCV processing pipeline that applies:

- Fine paper grain

- Low-frequency paper variation

- Subtle illumination changes

- Mild local contrast enhancement using CLAHE

- Light smoothing

- Subtle tonal variation

The processing is intentionally low intensity so that the generated text remains readable.

5. Export

Pillow is used to save generated pages as PNG images and combine multiple pages into a PDF document.

## Input Validation

The application handles common input errors through the GUI, including:

- Empty text input

- Missing handwriting font files

- Invalid generation requests

## Use Case

The project was created to explore a practical way of preparing handwriting-style personal notes and study material while applying concepts in desktop GUI development, text rendering, image processing, layout calculation, and document generation.

## Future Improvements

Possible future improvements include:

- Additional handwriting fonts

- More advanced page templates

- Adjustable margins

- Custom paper/background styles

- Improved handwriting personalization

- Automated test coverage

- Additional export formats

## License

This project is intended as a personal portfolio project.

Font files included in the project are subject to their respective font licenses. Refer to the accompanying font license files for licensing information.

