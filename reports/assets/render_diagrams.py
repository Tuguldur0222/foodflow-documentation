"""Render publication SVG assets for DOCX/PDF export without a browser.

Run from any directory with the project Python:
    C:/Users/tuugu/anaconda3/python.exe reports/assets/render_diagrams.py
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import __version__ as pyside_version
from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QFont, QFontDatabase, QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


def main() -> None:
    app = QGuiApplication.instance() or QGuiApplication([])
    # Conda's offscreen Qt may expose no system fonts until registered explicitly.
    # Arial covers both the English labels and Mongolian Cyrillic used in sources.
    font_files = ["arial.ttf", "arialbd.ttf", "ariali.ttf", "arialbi.ttf", "segoeui.ttf", "segoeuib.ttf"]
    loaded_fonts = []
    for filename in font_files:
        font_path = Path("C:/Windows/Fonts") / filename
        if font_path.is_file() and QFontDatabase.addApplicationFont(str(font_path)) >= 0:
            loaded_fonts.append(filename)
    if "Arial" not in QFontDatabase.families():
        raise RuntimeError("Arial is unavailable; refusing an export with missing text glyphs")
    app.setFont(QFont("Arial", 11))
    output_dir = Path(__file__).resolve().parent
    project_dir = output_dir.parents[1]
    source_dirs = [
        project_dir / "docs/assets",
        project_dir / "docs/architecture/diagrams",
        project_dir / "docs/requirements/mockups",
    ]
    records = []
    errors = []
    sources = sorted({svg for directory in source_dirs for svg in directory.rglob("*.svg")})
    for source in sources:
        relative = source.relative_to(project_dir).as_posix()
        source_bytes = source.read_bytes()
        renderer = QSvgRenderer(source_bytes)
        if not renderer.isValid():
            errors.append({"source": relative, "error": "Invalid SVG for QtSvg"})
            continue
        size = renderer.defaultSize()
        if size.width() <= 0 or size.height() <= 0:
            errors.append({"source": relative, "error": "SVG has no valid dimensions"})
            continue
        width = min(2400, max(1600, size.width() * 3))
        height = round(size.height() * width / size.width())
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(QColor("white"))
        painter = QPainter(image)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        renderer.render(painter, QRectF(0, 0, width, height))
        painter.end()
        name = "--".join(source.relative_to(project_dir / "docs").with_suffix("").parts) + ".png"
        destination = output_dir / name
        if not image.save(str(destination), "PNG"):
            errors.append({"source": relative, "error": "Could not save PNG"})
            continue
        records.append({
            "source": relative,
            "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
            "image": destination.relative_to(project_dir).as_posix(),
            "image_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
            "width": width,
            "height": height,
            "source_width": size.width(),
            "source_height": size.height(),
        })
        print(f"{relative} -> {name} ({width} x {height})")
    manifest = {
        "renderer": f"PySide6 {pyside_version} QtSvg (offscreen)",
        "background": "white",
        "registered_fonts": loaded_fonts,
        "rerun": "python reports/assets/render_diagrams.py",
        "images": records,
        "errors": errors,
    }
    (output_dir / "diagram_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Rendered {len(records)} SVG assets; errors: {len(errors)}")
    if errors:
        raise SystemExit(1)
    _ = app


if __name__ == "__main__":
    main()
