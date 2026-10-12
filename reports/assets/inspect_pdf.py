"""Create QtPdf previews and page-text metadata strictly under reports/assets.

Example:
    C:/Users/tuugu/anaconda3/python.exe reports/assets/inspect_pdf.py reports/example.pdf --pages 1 5 9
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSize
from PySide6.QtGui import QColor, QGuiApplication, QImage, QPainter
from PySide6.QtPdf import QPdfDocument

ROOT = Path(__file__).resolve().parents[2]

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--pages", type=int, nargs="*", help="One-based page numbers (default all)")
    args = parser.parse_args()
    app = QGuiApplication.instance() or QGuiApplication([])
    pdf = args.pdf.resolve(strict=True)
    document = QPdfDocument()
    error = document.load(str(pdf))
    if error != QPdfDocument.Error.None_:
        raise RuntimeError(f"Could not load {pdf.name}: {error}")
    count = document.pageCount()
    selected = sorted(set(args.pages or range(1, count + 1)))
    if any(page < 1 or page > count for page in selected):
        raise ValueError(f"Page numbers must be between 1 and {count}")
    output_dir = Path(__file__).resolve().parent / "previews" / pdf.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_digest = sha256(pdf.read_bytes()).hexdigest()
    old_metadata = output_dir / "metadata.json"
    previous_digest = None
    if old_metadata.exists():
        previous_digest = json.loads(old_metadata.read_text(encoding="utf-8")).get("pdf_sha256")
    if previous_digest != pdf_digest:
        # Remove only previews generated for this PDF, so screenshots from an
        # earlier pagination cannot be mistaken for current review evidence.
        for previous_preview in output_dir.glob("page-*.png"):
            previous_preview.unlink()
    pages = []
    for index in range(count):
        size = document.pagePointSize(index)
        page_text = document.getAllText(index).text()
        record = {
            "page": index + 1,
            "width_pt": size.width(),
            "height_pt": size.height(),
            "text": page_text,
        }
        if index + 1 in selected:
            width = 1600
            height = round(size.height() * width / size.width())
            image = document.render(index, QSize(width, height))
            # QtPdf preserves the PDF's transparent page backdrop. Composite to
            # white so preview clients do not display it against a black canvas.
            if not image.isNull():
                white_image = QImage(image.size(), QImage.Format.Format_RGB32)
                white_image.fill(QColor("white"))
                painter = QPainter(white_image)
                painter.drawImage(0, 0, image)
                painter.end()
                image = white_image
            destination = output_dir / f"page-{index + 1:03d}.png"
            if image.isNull() or not image.save(str(destination), "PNG"):
                raise RuntimeError(f"Could not render page {index + 1}")
            record["preview"] = destination.relative_to(ROOT).as_posix()
            print(f"Page {index + 1}/{count}: {destination}")
        pages.append(record)
    (output_dir / "metadata.json").write_text(
        json.dumps({"pdf": pdf.relative_to(ROOT).as_posix(),
                    "pdf_sha256": pdf_digest,
                    "page_count": count, "pages": pages}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"PDF page count: {count}")
    _ = app


if __name__ == "__main__":
    main()
