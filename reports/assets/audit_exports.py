"""Independently inspect exported PDF metadata and DOCX drawing XML."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".codex-tools"))
META = ROOT / "reports/assets/previews/FoodFlow_Documentation/metadata.json"
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def main() -> None:
    from pypdf import PdfReader

    manifest = json.loads((ROOT / "reports/manifest.json").read_text(encoding="utf-8"))
    manifest_errors = []
    generator = manifest.get("generator", {})
    if generator and sha256((ROOT / generator["path"]).read_bytes()).hexdigest() != generator["sha256"]:
        manifest_errors.append("Export generator changed; regenerate reports")
    if manifest.get("diagram_manifest_sha256") != sha256((ROOT / "reports/assets/diagram_manifest.json").read_bytes()).hexdigest():
        manifest_errors.append("Diagram asset manifest changed; regenerate reports")
    for export in manifest["exports"]:
        for source, digest in export["source_sha256"].items():
            if sha256((ROOT / source).read_bytes()).hexdigest() != digest:
                manifest_errors.append("Source changed: " + source)
        for kind in ("pdf", "docx"):
            path = ROOT / export[kind]
            if sha256(path.read_bytes()).hexdigest() != export[kind + "_sha256"]:
                manifest_errors.append("Output changed: " + export[kind])
        if len(PdfReader(ROOT / export["pdf"]).pages) != export["pdf_pages"]:
            manifest_errors.append("PDF page count mismatch: " + export["pdf"])
    metadata = json.loads(META.read_text(encoding="utf-8"))
    if metadata.get("pdf_sha256") != sha256((ROOT / "reports/FoodFlow_Documentation.pdf").read_bytes()).hexdigest():
        manifest_errors.append("PDF preview metadata is stale; rerun inspect_pdf.py")
    keywords = [
        "Архитектурын диаграм", "C4", "mock UI", "wireframe", "ACCEPTANCE",
        "Last-Reviewed", "Төлөвийн хүснэгт", "Traceability", "мөрдөх хүснэгт",
    ]
    keyword_pages = {
        keyword: [page["page"] for page in metadata["pages"] if keyword.lower() in page["text"].lower()]
        for keyword in keywords
    }
    landscape_pages = [page["page"] for page in metadata["pages"] if page["width_pt"] > page["height_pt"]]
    low_text_pages = [
        {"page": page["page"], "text_length": len(page["text"].strip())}
        for page in metadata["pages"] if len(page["text"].strip()) < 100
    ]
    pdf_reader = PdfReader(ROOT / "reports/FoodFlow_Documentation.pdf")
    out_of_page = []
    for page_number, pdf_page in enumerate(pdf_reader.pages, start=1):
        page_width, page_height = float(pdf_page.mediabox.width), float(pdf_page.mediabox.height)

        def check_coordinates(text, cm, tm, _font, font_size):
            if not text.strip():
                return
            x = tm[4] * cm[0] + tm[5] * cm[2] + cm[4]
            y = tm[4] * cm[1] + tm[5] * cm[3] + cm[5]
            if x < -1 or y < -1 or x > page_width + 1 or y > page_height + 1:
                out_of_page.append({"page": page_number, "x": x, "y": y, "font_size": font_size,
                                    "text": text.strip()[:100]})

        pdf_page.extract_text(visitor_text=check_coordinates)
    docx_path = ROOT / "reports/FoodFlow_Documentation.docx"
    drawings, drawing_errors, drawing_sections = [], [], []
    with ZipFile(docx_path) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
        relations = ET.fromstring(archive.read("word/_rels/document.xml.rels"))
        rel_map = {element.attrib["Id"]: element.attrib["Target"] for element in relations}
        for index, inline in enumerate(document.findall(".//wp:inline", NS), start=1):
            errors = []
            for element in inline.iter():
                namespace = element.tag.partition("}")[0].removeprefix("{")
                if namespace in (NS["wp"], NS["a"], NS["pic"]):
                    for attribute in element.attrib:
                        if attribute.startswith("{") and attribute != "{" + NS["r"] + "}embed":
                            errors.append(f"Qualified DrawingML attribute: {attribute}")
            extent = inline.find("wp:extent", NS)
            transform_extent = inline.find(".//a:xfrm/a:ext", NS)
            properties = inline.find("wp:docPr", NS)
            blip = inline.find(".//a:blip", NS)
            if extent is None or not all(int(extent.attrib.get(axis, 0)) > 0 for axis in ("cx", "cy")):
                errors.append("Missing/non-positive wp:extent cx/cy")
            if transform_extent is None or extent is None or transform_extent.attrib != extent.attrib:
                errors.append("Picture extent does not match inline extent")
            if properties is None or not properties.attrib.get("id") or not properties.attrib.get("name"):
                errors.append("Missing docPr id/name")
            embed_id = blip.attrib.get("{" + NS["r"] + "}embed", "") if blip is not None else ""
            target = rel_map.get(embed_id, "")
            if not target or "word/" + target not in archive.namelist():
                errors.append(f"Image relationship/media missing: {embed_id} {target}")
            record = {
                "drawing": index,
                "doc_pr_id": properties.attrib.get("id", "") if properties is not None else "",
                "name": properties.attrib.get("name", "") if properties is not None else "",
                "extent": extent.attrib if extent is not None else {},
                "embed_id": embed_id,
                "media": target,
                "errors": errors,
            }
            drawings.append(record)
            drawing_errors.extend(errors)
        ids = [item["doc_pr_id"] for item in drawings]
        if len(ids) != len(set(ids)):
            drawing_errors.append("Duplicate docPr IDs")
        section_drawings = []
        body = document.find("w:body", NS)
        for child in body:
            section_drawings.extend(blip.attrib.get("{" + NS["r"] + "}embed", "")
                                    for blip in child.findall(".//a:blip", NS))
            section = child if child.tag == "{" + NS["w"] + "}sectPr" else child.find("w:pPr/w:sectPr", NS)
            if section is None:
                continue
            size = section.find("w:pgSz", NS)
            orientation = size.attrib.get("{" + NS["w"] + "}orient", "portrait") if size is not None else "unknown"
            for embed_id in section_drawings:
                drawing_sections.append({"embed_id": embed_id, "orientation": orientation})
            section_drawings = []
    result = {
        "manifest_exports_checked": len(manifest["exports"]),
        "manifest_hash_errors": sorted(set(manifest_errors)),
        "pdf_pages": metadata["page_count"],
        "keyword_pages": keyword_pages,
        "landscape_pages": landscape_pages,
        "low_text_pages": low_text_pages,
        "pdf_text_outside_page": out_of_page,
        "docx_drawings": drawings,
        "docx_drawing_sections": drawing_sections,
        "docx_drawing_error_count": len(drawing_errors),
    }
    destination = ROOT / "reports/assets/export_audit.json"
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "docx_drawings"}, ensure_ascii=True))
    print(f"DOCX drawings: {len(drawings)}; drawing errors: {len(drawing_errors)}")
    print(destination)
    if drawing_errors or out_of_page or manifest_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
