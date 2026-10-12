"""Export canonical FoodFlow Markdown to editable DOCX and searchable PDF.

Optional export dependencies: reportlab, markdown-it-py, pypdf, Pillow.
Local .codex-tools is supported without modifying the Python installation.
Diagrams are editable SVG/Mermaid sources; reports/assets contains their PNG
renderings made by render_diagrams.py with offscreen QtSvg.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from html import escape
import json
from importlib.metadata import version
from pathlib import Path
import re
import sys
from urllib.parse import quote, unquote, urljoin, urlparse
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex-tools"))
sys.path.insert(0, str(ROOT / "tools"))

from markdown_it import MarkdownIt
from PIL import Image as PILImage
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, Image, KeepTogether, NextPageTemplate,
    PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

from word_xml import NS, node as word_node, serialize

OUTPUT = ROOT / "reports"
REPO_URL = "https://github.com/Tuguldur0222/foodflow-documentation"
DATE = "2026-10-13"
AUTHOR = "Ю. Төгөлдөр · 23B1NUM2350"
NAVY, GREEN, MUTED = "#18334A", "#23725E", "#5F6F7D"
FONT_DIR = Path("C:/Windows/Fonts")
MARGIN = 18 * mm
PORTRAIT_WIDTH = A4[0] - 2 * MARGIN
LANDSCAPE_WIDTH = landscape(A4)[0] - 2 * MARGIN
MD = MarkdownIt("commonmark").enable(["table", "strikethrough"])
NS.update({
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
})
for _prefix, _uri in NS.items():
    ET.register_namespace(_prefix, _uri)


def node(parent, tag, text=None, **attrs):
    """Word attributes are qualified; DrawingML attributes are unqualified."""
    prefix, name = tag.split(":")
    if prefix in {"a", "wp", "pic"}:
        element = ET.SubElement(parent, "{" + NS[prefix] + "}" + name)
        for key, value in attrs.items():
            element.set(key, str(value))
        if text is not None:
            element.text = text
        return element
    return word_node(parent, tag, text, **attrs)


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def source_url(source: Path, target: str = "") -> str:
    """Use portable source links instead of machine-specific filesystem links."""
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
        return target
    if target.startswith("#"):
        return REPO_URL + "/blob/main/" + quote(relative(source)) + target
    path_text, marker, fragment = target.partition("#")
    resolved = (source.parent / unquote(path_text)).resolve() if path_text else source
    try:
        repo_path = relative(resolved)
    except ValueError:
        return target
    return REPO_URL + "/blob/main/" + quote(repo_path) + (marker + fragment if marker else "")


def inline_runs(tokens, source: Path) -> list[dict]:
    runs, style_stack = [], [{}]
    for token in tokens or []:
        kind = token.type
        if kind in ("strong_open", "em_open", "s_open", "link_open"):
            style = dict(style_stack[-1])
            if kind == "strong_open":
                style["bold"] = True
            elif kind == "em_open":
                style["italic"] = True
            elif kind == "s_open":
                style["strike"] = True
            else:
                style["url"] = source_url(source, token.attrGet("href") or "")
            style_stack.append(style)
        elif kind in ("strong_close", "em_close", "s_close", "link_close"):
            style_stack.pop()
        elif kind in ("text", "code_inline"):
            run = dict(style_stack[-1], text=token.content)
            if kind == "code_inline":
                run["code"] = True
            runs.append(run)
        elif kind in ("softbreak", "hardbreak"):
            runs.append(dict(style_stack[-1], text="\n" if kind == "hardbreak" else " "))
        elif kind == "image":
            runs.append(dict(style_stack[-1], text=token.content, image=token.attrGet("src")))
        elif kind == "html_inline":
            if re.match(r"<br\s*/?>", token.content, re.I):
                runs.append(dict(style_stack[-1], text="\n"))
            elif not token.content.startswith("<!--"):
                text = re.sub(r"<[^>]+>", "", token.content)
                if text:
                    runs.append(dict(style_stack[-1], text=text))
    return runs


def plain(runs) -> str:
    return "".join(run.get("text", "") for run in runs)


def image_path(source: Path, target: str, images: dict) -> str | None:
    svg = (source.parent / unquote(target)).resolve()
    if svg.suffix.lower() == ".svg":
        entry = images.get(relative(svg))
        if entry:
            return entry["image"]
        raise ValueError(f"SVG asset was not rendered: {svg}")
    if svg.is_file():
        return relative(svg)
    return None


def parse_markdown(source: Path, images: dict) -> dict:
    raw = source.read_text(encoding="utf-8")
    if "\ufffd" in raw:
        raise ValueError(f"Replacement character in source: {source}")
    tokens, blocks, lists, quote_depth = MD.parse(raw), [], [], 0
    i = 0
    while i < len(tokens):
        token = tokens[i]
        kind = token.type
        if kind in ("bullet_list_open", "ordered_list_open"):
            lists.append({"ordered": kind == "ordered_list_open",
                          "counter": int(token.attrGet("start") or 1) - 1, "first": False})
        elif kind in ("bullet_list_close", "ordered_list_close"):
            lists.pop()
        elif kind == "list_item_open":
            lists[-1]["counter"] += 1
            lists[-1]["first"] = True
        elif kind == "blockquote_open":
            quote_depth += 1
        elif kind == "blockquote_close":
            quote_depth -= 1
        elif kind == "heading_open":
            blocks.append({"type": "heading", "level": int(token.tag[1:]),
                           "runs": inline_runs(tokens[i + 1].children, source)})
            i += 2
        elif kind == "paragraph_open":
            runs = inline_runs(tokens[i + 1].children, source)
            image_runs = [run for run in runs if run.get("image")]
            if image_runs and all(run.get("image") or not run["text"].strip() for run in runs):
                for run in image_runs:
                    rendered = image_path(source, run["image"], images)
                    if rendered:
                        blocks.append({"type": "image", "path": rendered, "alt": run["text"]})
            else:
                block = {"type": "quote" if quote_depth else "paragraph", "runs": runs}
                if lists:
                    block["indent"] = len(lists)
                    if lists[-1]["first"]:
                        block["bullet"] = (str(lists[-1]["counter"]) + ".") if lists[-1]["ordered"] else "•"
                        lists[-1]["first"] = False
                blocks.append(block)
            i += 2
        elif kind == "table_open":
            rows, row = [], None
            j = i + 1
            while tokens[j].type != "table_close":
                current = tokens[j]
                if current.type == "tr_open":
                    row = []
                elif current.type == "inline":
                    row.append(inline_runs(current.children, source))
                elif current.type == "tr_close":
                    rows.append(row)
                j += 1
            blocks.append({"type": "table", "rows": rows})
            i = j
        elif kind in ("fence", "code_block"):
            language = token.info.strip().split()[0] if token.info.strip() else ""
            if language == "mermaid":
                normalized = token.content.strip().replace("\r\n", "\n")
                candidates = sorted(ROOT.glob("docs/architecture/diagrams/*.mmd"))
                match = next((p for p in candidates
                              if p.read_text(encoding="utf-8").strip().replace("\r\n", "\n") == normalized), None)
                if match and relative(match.with_suffix(".svg")) in images:
                    entry = images[relative(match.with_suffix(".svg"))]
                    blocks.append({"type": "image", "path": entry["image"],
                                   "alt": "Архитектурын диаграм · " + match.stem + " · Proposed"})
                    blocks.append({"type": "caption", "runs": [
                        {"text": "Засварлах эх: "},
                        {"text": relative(match), "url": source_url(source, str(match.relative_to(source.parent))
                         if match.is_relative_to(source.parent) else "../architecture/diagrams/" + match.name)}
                    ]})
            blocks.append({"type": "code", "text": token.content.rstrip("\n"), "language": language})
        elif kind == "hr":
            blocks.append({"type": "rule"})
        elif kind == "html_block" and not token.content.strip().startswith("<!--"):
            text = re.sub(r"<[^>]+>", "", token.content).strip()
            if text:
                blocks.append({"type": "paragraph", "runs": [{"text": text}]})
        i += 1
    title = next((plain(b["runs"]) for b in blocks if b["type"] == "heading"), source.stem)
    return {"source": relative(source), "sha256": sha256(source.read_bytes()).hexdigest(),
            "title": title, "blocks": blocks}


def fonts():
    for name, filename in [
        ("FFArial", "arial.ttf"), ("FFArialBold", "arialbd.ttf"),
        ("FFArialItalic", "ariali.ttf"), ("FFArialBoldItalic", "arialbi.ttf"),
        ("FFMono", "consola.ttf"), ("FFMonoBold", "consolab.ttf"),
    ]:
        pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename)))
    pdfmetrics.registerFontFamily("FFArial", normal="FFArial", bold="FFArialBold",
                                  italic="FFArialItalic", boldItalic="FFArialBoldItalic")
    pdfmetrics.registerFontFamily("FFMono", normal="FFMono", bold="FFMonoBold",
                                  italic="FFMono", boldItalic="FFMonoBold")


def pdf_styles(compact=False):
    size, leading = (9.4, 12.1) if compact else (10.1, 14.2)
    base = {"fontName": "FFArial", "fontSize": size, "leading": leading,
            "textColor": colors.HexColor(NAVY), "splitLongWords": True,
            "allowWidows": 0, "allowOrphans": 0}
    styles = {
        "body": ParagraphStyle("Body", **base, spaceAfter=5 if compact else 7),
        "quote": ParagraphStyle("Quote", **base, leftIndent=12, borderColor=colors.HexColor(GREEN),
                                borderWidth=.6, borderPadding=7, backColor=colors.HexColor("#F0F6F4"),
                                spaceBefore=5, spaceAfter=9),
        "caption": ParagraphStyle("Caption", **dict(base, fontSize=8.2, leading=11,
                                                  textColor=colors.HexColor(MUTED)), spaceAfter=8),
        "code": ParagraphStyle("Code", fontName="FFMono", fontSize=7.5, leading=10.4,
                               textColor=colors.HexColor("#20323E"), splitLongWords=True,
                               leftIndent=6, rightIndent=6, borderPadding=7, borderWidth=.4,
                               borderColor=colors.HexColor("#D8E0E4"), backColor=colors.HexColor("#F4F7F8"),
                               spaceBefore=4, spaceAfter=8, allowWidows=1, allowOrphans=1),
    }
    for level, heading_size in [(1, 20), (2, 13.5), (3, 11.4), (4, 10.5), (5, 10.1), (6, 10.1)]:
        if compact:
            heading_size = 15 if level == 1 else (10.7 if level == 2 else 10)
        styles[f"h{level}"] = ParagraphStyle(
            f"Heading{level}", fontName="FFArialBold", fontSize=heading_size,
            leading=heading_size * 1.23, textColor=colors.HexColor(GREEN if level == 2 else NAVY),
            spaceBefore=(7 if compact else 12) if level > 1 else 0,
            spaceAfter=5 if compact else 8, keepWithNext=True, splitLongWords=True,
        )
    return styles


def pdf_markup(runs, header=False):
    pieces = []
    for run in runs:
        content = escape(run["text"]).replace("\n", "<br/>")
        if run.get("code"):
            content = '<font name="FFMono" color="#245D50">' + content + "</font>"
        if run.get("bold") or header:
            content = "<b>" + content + "</b>"
        if run.get("italic"):
            content = "<i>" + content + "</i>"
        if run.get("strike"):
            content = "<strike>" + content + "</strike>"
        if run.get("url"):
            content = '<link href="' + escape(run["url"], quote=True) + '" color="#176D91">' + content + "</link>"
        pieces.append(content)
    return "".join(pieces)


def column_fractions(rows):
    count = len(rows[0])
    if count == 8:
        return [.07, .18, .12, .17, .12, .11, .14, .09]
    # Allocate space by content while preventing one column dominating.
    weights = []
    for c in range(count):
        lengths = sorted(len(plain(row[c])) for row in rows)
        percentile = lengths[min(len(lengths) - 1, int(len(lengths) * .8))]
        weights.append(min(130, max(24, percentile)) ** .5)
    total = sum(weights)
    return [weight / total for weight in weights]


class ExportPDF(BaseDocTemplate):
    def __init__(self, filename, title, compact=False):
        margin = 14 * mm if compact else MARGIN
        super().__init__(str(filename), pagesize=A4, leftMargin=margin, rightMargin=margin,
                         topMargin=margin + (0 if compact else 4 * mm), bottomMargin=margin,
                         title=title, author=AUTHOR, subject="FoodFlow editable documentation export",
                         pageCompression=1)
        self.export_title = title
        self.compact = compact
        self.bookmark_counter = 0
        self.outline_level = 0
        self.addPageTemplates([
            PageTemplate(id="portrait", pagesize=A4,
                         frames=[Frame(margin, margin, A4[0] - 2 * margin,
                                       A4[1] - 2 * margin - (0 if compact else 4 * mm),
                                       leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)],
                         onPage=self.decorate),
            PageTemplate(id="landscape", pagesize=landscape(A4),
                         frames=[Frame(margin, margin, A4[1] - 2 * margin,
                                       A4[0] - 2 * margin - 4 * mm,
                                       leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)],
                         onPage=self.decorate),
        ])

    def beforeDocument(self):
        self.bookmark_counter = 0
        self.outline_level = 0

    def decorate(self, canvas, document):
        width, height = canvas._pagesize
        margin = 14 * mm if self.compact else MARGIN
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D5DFE3"))
        canvas.setLineWidth(.5)
        canvas.line(margin, 10.5 * mm, width - margin, 10.5 * mm)
        canvas.setFont("FFArial", 7.5)
        canvas.setFillColor(colors.HexColor(MUTED))
        canvas.drawString(margin, 7 * mm, "FoodFlow · " + DATE + " · Markdown эхээс үүсгэв")
        canvas.drawRightString(width - margin, 7 * mm, str(document.page))
        if not self.compact:
            canvas.setFont("FFArial", 7.5)
            canvas.drawString(margin, height - 11 * mm, "FOODFLOW / SOFTWARE PROJECT DOCUMENTATION")
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if not hasattr(flowable, "export_heading"):
            return
        level, title = flowable.export_heading
        self.bookmark_counter += 1
        key = "heading-" + str(self.bookmark_counter)
        self.canv.bookmarkPage(key)
        outline_level = min(level - 1, self.outline_level + 1)
        if self.bookmark_counter == 1:
            outline_level = 0
        self.canv.addOutlineEntry(title, key, level=outline_level, closed=outline_level > 0)
        self.outline_level = outline_level
        if level == 1:
            self.notify("TOCEntry", (0, title, self.page, key))


def pdf_story(documents, compact=False, combined=False):
    styles = pdf_styles(compact)
    story = []
    width = (A4[0] - 28 * mm) if compact else PORTRAIT_WIDTH
    if combined:
        banner = OUTPUT / "assets/assets--foodflow-banner.png"
        if banner.exists():
            with PILImage.open(banner) as image:
                story.append(Image(str(banner), width=width, height=width * image.height / image.width))
        story += [Spacer(1, 24 * mm),
                  Paragraph("FoodFlow", ParagraphStyle("Cover", fontName="FFArialBold", fontSize=36,
                                                       leading=43, textColor=colors.HexColor(NAVY))),
                  Paragraph("Програм хангамжийн төслийн баримтжуулалт",
                            ParagraphStyle("CoverSubtitle", fontName="FFArial", fontSize=19, leading=25,
                                           spaceAfter=14, textColor=colors.HexColor(GREEN))),
                  Paragraph("Семинар 01–06 · шаардлага · архитектур · API · кодын баримтжуулалт", styles["body"]),
                  Paragraph(AUTHOR + " · МУИС · " + DATE, styles["body"]),
                  Spacer(1, 12 * mm),
                  Paragraph("Энэ хувилбар нь repository-ийн Markdown эхээс үүсгэсэн унших, хэвлэх баримт. "
                            "Шаардлага, санал болгосон загвар, локал тест, гаднын баталгааны төлөвийг эхийн утгаар хадгалсан. "
                            "DOCX хувилбарын текст, хүснэгт, холбоосыг засварлаж болно.", styles["body"]),
                  Paragraph('<link href="' + REPO_URL + '">' + REPO_URL + "</link>", styles["caption"]),
                  PageBreak(),
                  Paragraph("Агуулга", styles["h1"])]
        toc = TableOfContents()
        toc.levelStyles = [ParagraphStyle("TOC0", fontName="FFArial", fontSize=9.8, leading=14,
                                         spaceBefore=5, leftIndent=0, rightIndent=18)]
        story += [toc, PageBreak()]
    for document_index, document in enumerate(documents):
        if document_index:
            story.append(PageBreak())
        for block in document["blocks"]:
            kind = block["type"]
            if kind == "heading":
                paragraph = Paragraph(pdf_markup(block["runs"]), styles["h" + str(block["level"])])
                paragraph.export_heading = (block["level"], plain(block["runs"]))
                story.append(paragraph)
            elif kind in ("paragraph", "quote", "caption"):
                base_style = styles["body" if kind == "paragraph" else kind]
                if block.get("indent"):
                    base_style = ParagraphStyle("List", parent=base_style, leftIndent=12 * block["indent"],
                                                firstLineIndent=-8 if block.get("bullet") else 0)
                prefix = escape(block["bullet"]) + " " if block.get("bullet") else ""
                story.append(Paragraph(prefix + pdf_markup(block["runs"]), base_style))
            elif kind == "code":
                if block.get("language"):
                    story.append(Paragraph(escape(block["language"].upper()), styles["caption"]))
                lines = []
                for line in block["text"].splitlines():
                    leading = len(line) - len(line.lstrip(" "))
                    lines.append("&#160;" * leading + escape(line.lstrip(" ")))
                story.append(Paragraph("<br/>".join(lines) or " ", styles["code"]))
            elif kind == "table":
                rows = block["rows"]
                count = len(rows[0])
                wide = count >= 7
                table_width = LANDSCAPE_WIDTH if wide else width
                if wide:
                    story += [NextPageTemplate("landscape"), PageBreak()]
                font_size = 7.5 if wide else (8.6 if count >= 4 else 9.2)
                if compact:
                    font_size = 8.2
                cell_style = ParagraphStyle("Cell", fontName="FFArial", fontSize=font_size,
                                             leading=font_size * 1.3, textColor=colors.HexColor(NAVY),
                                             splitLongWords=True, spaceAfter=0,
                                             allowWidows=1, allowOrphans=1)
                rendered_rows = [[Paragraph(pdf_markup(cell, header=r == 0), cell_style)
                                  for cell in row] for r, row in enumerate(rows)]
                table = Table(rendered_rows, colWidths=[table_width * f for f in column_fractions(rows)],
                              repeatRows=1, hAlign="LEFT", splitByRow=1)
                table.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5EFEC")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F9FA")]),
                    ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#CDD9DE")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]))
                story += [table, Spacer(1, 8)]
                if wide:
                    story += [NextPageTemplate("portrait"), PageBreak()]
            elif kind == "image":
                path = ROOT / block["path"]
                # A heading and its figure are one reading unit. Keep them in
                # one explicit group; a keepWithNext heading followed by a
                # nested KeepTogether alone may still strand the heading.
                figure_heading = story.pop() if story and hasattr(story[-1], "export_heading") else None
                diagram = "architecture--diagrams--" in path.name
                if diagram:
                    story += [NextPageTemplate("landscape"), PageBreak()]
                with PILImage.open(path) as image:
                    max_width = LANDSCAPE_WIDTH if diagram else width
                    max_height = (146 if figure_heading else 158) * mm if diagram else 185 * mm
                    factor = min(max_width / image.width, max_height / image.height)
                    picture = Image(str(path), width=image.width * factor, height=image.height * factor)
                caption = Paragraph(escape(block["alt"]), styles["caption"])
                figure = ([figure_heading] if figure_heading is not None else []) + [picture, Spacer(1, 4), caption]
                story.append(KeepTogether(figure))
                if diagram:
                    story += [NextPageTemplate("portrait"), PageBreak()]
            elif kind == "rule":
                story.append(HRFlowable(width="100%", color=colors.HexColor("#CFDCE0"), spaceBefore=6, spaceAfter=9))
    return story


def export_pdf(documents, path, compact=False, combined=False):
    doc = ExportPDF(path, "FoodFlow · " + documents[0]["title"], compact=compact)
    story = pdf_story(documents, compact=compact, combined=combined)
    if combined:
        doc.multiBuild(story)
    else:
        doc.build(story)
    reader = PdfReader(path)
    page_texts = []
    for page in reader.pages:
        lines = (page.extract_text() or "").splitlines()
        # onPage draws the running footer/header before the body. Remove only
        # these exact decorations so a paragraph continued on the next page
        # remains contiguous for the complete-text check.
        if lines and lines[0].startswith("FoodFlow · " + DATE + " · "):
            lines = lines[1:]
            if lines and lines[0].isdigit():
                lines = lines[1:]
            if lines and lines[0] == "FOODFLOW / SOFTWARE PROJECT DOCUMENTATION":
                lines = lines[1:]
        page_texts.append("\n".join(lines))
    extracted = "\n".join(page_texts)
    if "\ufffd" in extracted:
        raise AssertionError(f"Replacement character in PDF extraction: {path}")
    if any("Монгол" in plain(b.get("runs", [])) for d in documents for b in d["blocks"]):
        assert "Монгол" in extracted, path
    return len(reader.pages), extracted


def word_run(parent, run, font_size=None, force_bold=False):
    element = node(parent, "w:r")
    props = node(element, "w:rPr")
    if run.get("bold") or force_bold:
        node(props, "w:b")
    if run.get("italic"):
        node(props, "w:i")
    if run.get("strike"):
        node(props, "w:strike")
    if run.get("code"):
        node(props, "w:rFonts", ascii="Consolas", hAnsi="Consolas", cs="Consolas")
        node(props, "w:shd", fill="F0F5F3", val="clear")
    if run.get("url"):
        node(props, "w:color", val="176D91")
        node(props, "w:u", val="single")
    if font_size:
        node(props, "w:sz", val=round(font_size * 2))
    for i, line in enumerate(run["text"].split("\n")):
        if i:
            node(element, "w:br")
        text = node(element, "w:t", line)
        text.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return element


class WordExport:
    def __init__(self, title, compact=False):
        self.title, self.compact = title, compact
        self.document = ET.Element("{" + NS["w"] + "}document")
        self.body = node(self.document, "w:body")
        self.links, self.media, self.image_counter = [], {}, 0

    def paragraph(self, runs, style="Normal", parent=None, bullet=None, indent=0,
                  force_bold=False, font_size=None):
        p = node(parent if parent is not None else self.body, "w:p")
        props = node(p, "w:pPr")
        node(props, "w:pStyle", val=style)
        if indent:
            node(props, "w:ind", left=indent * 240, hanging=160 if bullet else 0)
        if bullet:
            word_run(p, {"text": bullet + " "}, font_size)
        for run in runs:
            target = p
            if run.get("url"):
                identifier = "rIdLink" + str(len(self.links) + 1)
                self.links.append((identifier, run["url"]))
                target = node(p, "w:hyperlink")
                target.set("{" + NS["r"] + "}id", identifier)
            word_run(target, run, font_size, force_bold)
        return p

    def section(self, landscape_page=False, parent=None):
        section = node(parent if parent is not None else self.body, "w:sectPr")
        footer = node(section, "w:footerReference", type="default")
        footer.set("{" + NS["r"] + "}id", "rIdFooter")
        header = node(section, "w:headerReference", type="default")
        header.set("{" + NS["r"] + "}id", "rIdHeader")
        node(section, "w:type", val="nextPage")
        node(section, "w:pgSz", w=16838 if landscape_page else 11906,
             h=11906 if landscape_page else 16838, orient="landscape" if landscape_page else "portrait")
        margin = 795 if self.compact else 1021
        node(section, "w:pgMar", top=margin, right=margin, bottom=margin, left=margin,
             header=400, footer=400, gutter=0)
        return section

    def section_break(self, landscape_page=False):
        p = node(self.body, "w:p")
        self.section(landscape_page, node(p, "w:pPr"))

    def page_break(self):
        node(node(node(self.body, "w:p"), "w:r"), "w:br", type="page")

    def image(self, path, alt, max_width=6.8, max_height=7.0):
        with PILImage.open(path) as image:
            scale = min(max_width / image.width, max_height / image.height)
            width, height = int(image.width * scale * 914400), int(image.height * scale * 914400)
        self.image_counter += 1
        name = f"image{self.image_counter}.png"
        identifier = f"rIdImage{self.image_counter}"
        self.media[name] = (identifier, path)
        p = node(self.body, "w:p")
        image_properties = node(p, "w:pPr")
        node(image_properties, "w:jc", val="center")
        node(image_properties, "w:keepNext")
        drawing = node(node(p, "w:r"), "w:drawing")
        inline = node(drawing, "wp:inline", distT=0, distB=0, distL=0, distR=0)
        node(inline, "wp:extent", cx=width, cy=height)
        node(inline, "wp:docPr", id=self.image_counter, name=name, descr=alt)
        graphic = node(inline, "a:graphic")
        graphic_data = node(graphic, "a:graphicData", uri=NS["pic"])
        picture = node(graphic_data, "pic:pic")
        non_visual = node(picture, "pic:nvPicPr")
        node(non_visual, "pic:cNvPr", id=self.image_counter, name=name, descr=alt)
        node(non_visual, "pic:cNvPicPr")
        fill = node(picture, "pic:blipFill")
        blip = node(fill, "a:blip")
        blip.set("{" + NS["r"] + "}embed", identifier)
        node(node(fill, "a:stretch"), "a:fillRect")
        shape = node(picture, "pic:spPr")
        transform = node(shape, "a:xfrm")
        node(transform, "a:off", x=0, y=0)
        node(transform, "a:ext", cx=width, cy=height)
        node(node(shape, "a:prstGeom", prst="rect"), "a:avLst")
        self.paragraph([{"text": alt}], "Caption")

    def table(self, rows):
        wide = len(rows[0]) >= 7
        if wide:
            self.section_break(False)
        width = (16838 if wide else 11906) - 2042
        fractions = column_fractions(rows)
        widths = [round(width * fraction) for fraction in fractions]
        widths[-1] = width - sum(widths[:-1])
        table = node(self.body, "w:tbl")
        props = node(table, "w:tblPr")
        node(props, "w:tblW", w=width, type="dxa")
        node(props, "w:tblLayout", type="fixed")
        borders = node(props, "w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            node(borders, "w:" + edge, val="single", sz=4, color="CDD9DE")
        margins = node(props, "w:tblCellMar")
        for edge in ("top", "bottom", "left", "right"):
            node(margins, "w:" + edge, w=80, type="dxa")
        grid = node(table, "w:tblGrid")
        for value in widths:
            node(grid, "w:gridCol", w=value)
        for r, values in enumerate(rows):
            row = node(table, "w:tr")
            row_props = node(row, "w:trPr")
            node(row_props, "w:cantSplit")
            if r == 0:
                node(row_props, "w:tblHeader")
            for value, cell_width in zip(values, widths):
                cell = node(row, "w:tc")
                cell_props = node(cell, "w:tcPr")
                node(cell_props, "w:tcW", w=cell_width, type="dxa")
                node(cell_props, "w:vAlign", val="top")
                if r == 0 or r % 2 == 0:
                    node(cell_props, "w:shd", fill="E5EFEC" if r == 0 else "F6F9FA", val="clear")
                self.paragraph(value, "TableText", parent=cell, force_bold=r == 0,
                               font_size=7.5 if wide else (8.5 if len(values) >= 4 else 9))
        self.paragraph([], "Gap")
        if wide:
            self.section_break(True)

    def append(self, documents, combined=False):
        if combined:
            banner = OUTPUT / "assets/assets--foodflow-banner.png"
            if banner.exists():
                self.image(banner, "FoodFlow · Програм хангамжийн төслийн баримтжуулалт", 6.8)
            self.paragraph([{"text": "FoodFlow"}], "Title")
            self.paragraph([{"text": "Програм хангамжийн төслийн баримтжуулалт"}], "Subtitle")
            self.paragraph([{"text": "Семинар 01–06 · шаардлага · архитектур · API · кодын баримтжуулалт"}])
            self.paragraph([{"text": AUTHOR + " · МУИС · " + DATE}])
            self.paragraph([{"text": "Markdown нь үндсэн эх. DOCX-ийн текст, хүснэгт, код, холбоос засварлагдана; "
                                    "зураг нь repository дахь editable SVG/Mermaid эхтэй."}])
            self.paragraph([{"text": REPO_URL, "url": REPO_URL}], "Caption")
            self.page_break()
            contents_heading = self.paragraph([{"text": "Агуулга"}], "Heading1")
            # Keep the contents title out of its own updateable Word TOC.
            node(contents_heading.find("{" + NS["w"] + "}pPr"), "w:outlineLvl", val=9)
            p = self.paragraph([{"text": "Word дээр хүснэгт дээр дарж Update Field → Update entire table сонгоно."}], "Caption")
            p = self.paragraph([])
            field = node(p, "w:fldSimple", instr='TOC \\o "1-1" \\h \\z \\u')
            word_run(field, {"text": "Агуулгыг Word дээр шинэчилнэ."})
            self.page_break()
        for index, document in enumerate(documents):
            if index:
                self.page_break()
            for block in document["blocks"]:
                kind = block["type"]
                if kind == "heading":
                    self.paragraph(block["runs"], "Heading" + str(min(6, block["level"])))
                elif kind in ("paragraph", "quote", "caption"):
                    self.paragraph(block["runs"], {"paragraph": "Normal", "quote": "Quote", "caption": "Caption"}[kind],
                                   bullet=block.get("bullet"), indent=block.get("indent", 0))
                elif kind == "code":
                    if block.get("language"):
                        self.paragraph([{"text": block["language"].upper()}], "Caption")
                    self.paragraph([{"text": block["text"], "code": True}], "Code")
                elif kind == "table":
                    self.table(block["rows"])
                elif kind == "image":
                    path = ROOT / block["path"]
                    diagram = "architecture--diagrams--" in path.name
                    figure_heading = None
                    if diagram:
                        if len(self.body):
                            previous = self.body[-1]
                            style = previous.find("w:pPr/w:pStyle", NS)
                            if style is not None and style.get("{" + NS["w"] + "}val", "").startswith("Heading"):
                                figure_heading = previous
                                self.body.remove(previous)
                        self.section_break(False)
                        if figure_heading is not None:
                            self.body.append(figure_heading)
                    self.image(path, block["alt"], 10.2 if diagram else 6.8,
                               6.1 if diagram else 7.0)
                    if diagram:
                        self.section_break(True)
                elif kind == "rule":
                    self.paragraph([{"text": "────────────────────────"}], "Caption")
        self.section(False)

    def styles(self):
        root = ET.Element("{" + NS["w"] + "}styles")
        defaults = node(root, "w:docDefaults")
        props = node(node(defaults, "w:rPrDefault"), "w:rPr")
        node(props, "w:rFonts", ascii="Arial", hAnsi="Arial", cs="Arial", eastAsia="Arial")
        node(props, "w:lang", val="mn-MN")
        node(props, "w:sz", val=19 if self.compact else 21)
        node(props, "w:color", val=NAVY[1:])
        styles = [
            ("Normal", 9.5 if self.compact else 10.5, 245 if self.compact else 280, 85, False, None),
            ("Title", 34, 780, 160, True, None), ("Subtitle", 20, 500, 180, False, None),
            ("TableText", 8.8, 230, 0, False, None), ("Caption", 8.2, 210, 90, False, None),
            ("Code", 8, 210, 120, False, None), ("Quote", 10, 260, 120, False, None),
            ("Gap", 2, 40, 70, False, None), ("Footer", 8, 180, 0, False, None),
        ]
        for level in range(1, 7):
            size = {1: 19, 2: 13.5, 3: 11.5}.get(level, 10.5)
            if self.compact:
                size = 15 if level == 1 else 10.7
            styles.append(("Heading" + str(level), size, round(size * 26), 115, True, level - 1))
        for name, size, leading, after, bold, outline in styles:
            style = node(root, "w:style", type="paragraph", styleId=name)
            if name == "Normal":
                style.set("{" + NS["w"] + "}default", "1")
            node(style, "w:name", val=name)
            if name != "Normal":
                node(style, "w:basedOn", val="Normal")
            pprops = node(style, "w:pPr")
            node(pprops, "w:spacing", before=140 if outline is not None and outline > 0 else 0,
                 after=after, line=leading, lineRule="auto")
            node(pprops, "w:widowControl")
            if outline is not None:
                node(pprops, "w:keepNext")
                node(pprops, "w:outlineLvl", val=outline)
            if name in ("Code", "Quote"):
                node(pprops, "w:shd", fill="F4F7F8", val="clear")
                node(pprops, "w:ind", left=140, right=140)
            rprops = node(style, "w:rPr")
            node(rprops, "w:sz", val=round(size * 2))
            if bold:
                node(rprops, "w:b")
            if name == "Code":
                node(rprops, "w:rFonts", ascii="Consolas", hAnsi="Consolas", cs="Consolas")
        return root

    def write(self, path):
        relation_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
        relationship_type = NS["r"] + "/"
        relationships = ET.Element("Relationships", xmlns=relation_ns)
        for identifier, kind, target in [
            ("rIdStyles", "styles", "styles.xml"), ("rIdSettings", "settings", "settings.xml"),
            ("rIdFooter", "footer", "footer1.xml"), ("rIdHeader", "header", "header1.xml"),
        ]:
            ET.SubElement(relationships, "Relationship", Id=identifier, Type=relationship_type + kind, Target=target)
        for identifier, url in self.links:
            ET.SubElement(relationships, "Relationship", Id=identifier, Type=relationship_type + "hyperlink",
                          Target=url, TargetMode="External")
        for name, (identifier, _) in self.media.items():
            ET.SubElement(relationships, "Relationship", Id=identifier, Type=relationship_type + "image",
                          Target="media/" + name)
        root_rels = ET.Element("Relationships", xmlns=relation_ns)
        ET.SubElement(root_rels, "Relationship", Id="rIdDocument", Type=relationship_type + "officeDocument",
                      Target="word/document.xml")
        ET.SubElement(root_rels, "Relationship", Id="rIdCore",
                      Type=relation_ns + "/metadata/core-properties", Target="docProps/core.xml")
        content_types = ET.Element("Types", xmlns="http://schemas.openxmlformats.org/package/2006/content-types")
        for extension, mime in [
            ("rels", "application/vnd.openxmlformats-package.relationships+xml"),
            ("xml", "application/xml"), ("png", "image/png"),
        ]:
            ET.SubElement(content_types, "Default", Extension=extension, ContentType=mime)
        for part, suffix in [
            ("document", "document.main"), ("styles", "styles"), ("settings", "settings"),
            ("footer1", "footer"), ("header1", "header"),
        ]:
            ET.SubElement(content_types, "Override", PartName="/word/" + part + ".xml",
                          ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml." + suffix + "+xml")
        ET.SubElement(content_types, "Override", PartName="/docProps/core.xml",
                      ContentType="application/vnd.openxmlformats-package.core-properties+xml")
        core = ET.Element("{" + NS["cp"] + "}coreProperties")
        node(core, "dc:title", self.title)
        node(core, "dc:creator", AUTHOR)
        node(core, "dc:description", "Editable export from canonical FoodFlow Markdown. " + DATE)
        settings = ET.Element("{" + NS["w"] + "}settings")
        node(settings, "w:updateFields", val="true")
        node(settings, "w:defaultTabStop", val=360)
        footer = ET.Element("{" + NS["w"] + "}ftr")
        p = self.paragraph([{"text": "FoodFlow · " + DATE + " · " }], "Footer", parent=footer)
        field = node(p, "w:fldSimple", instr="PAGE")
        word_run(field, {"text": "1"})
        header = ET.Element("{" + NS["w"] + "}hdr")
        self.paragraph([{"text": "FOODFLOW / SOFTWARE PROJECT DOCUMENTATION"}], "Footer", parent=header)
        parts = {
            "[Content_Types].xml": content_types, "_rels/.rels": root_rels,
            "word/document.xml": self.document, "word/styles.xml": self.styles(),
            "word/settings.xml": settings, "word/footer1.xml": footer, "word/header1.xml": header,
            "word/_rels/document.xml.rels": relationships, "docProps/core.xml": core,
        }
        with ZipFile(path, "w", ZIP_DEFLATED) as archive:
            for name, element in parts.items():
                archive.writestr(name, serialize(element))
            for name, (_, image_path_value) in self.media.items():
                archive.write(image_path_value, "word/media/" + name)
        with ZipFile(path) as archive:
            assert archive.testzip() is None
            for name in archive.namelist():
                if name.endswith(".xml") or name.endswith(".rels"):
                    ET.fromstring(archive.read(name))
            document = ET.fromstring(archive.read("word/document.xml"))
            joined = "".join(n.text or "" for n in document.findall(".//w:t", NS))
        if "\ufffd" in joined:
            raise AssertionError(f"Replacement character in DOCX: {path}")
        return joined


def expected_texts(documents):
    for document in documents:
        for block in document["blocks"]:
            if "runs" in block:
                yield plain(block["runs"])
            elif block["type"] == "table":
                for row in block["rows"]:
                    for cell in row:
                        yield plain(cell)
            elif block["type"] == "code":
                yield block["text"]
            elif block["type"] == "image":
                yield block["alt"]


def compact_text(text):
    return re.sub(r"\s+", "", text)


def export_pair(name, documents, compact=False, combined=False):
    pdf_path, word_path = OUTPUT / (name + ".pdf"), OUTPUT / (name + ".docx")
    page_count, pdf_text = export_pdf(documents, pdf_path, compact, combined)
    writer = WordExport(documents[0]["title"], compact)
    writer.append(documents, combined)
    word_text = writer.write(word_path)
    # Word content validation is exact after line wrapping/whitespace normalization.
    normalized = compact_text(word_text)
    for text in expected_texts(documents):
        if compact_text(text) not in normalized:
            raise AssertionError(f"Missing DOCX content in {name}: {text[:100]}")
    # PDF text extraction must preserve each non-code paragraph/cell. Interleaved
    # repeated page headers/footers are excluded from this adjacency check.
    pdf_compact = compact_text(pdf_text)
    checks, missing = 0, []
    for text in expected_texts(documents):
        for line in text.splitlines():
            if len(line.strip()) >= 12:
                checks += 1
                if compact_text(line) not in pdf_compact:
                    missing.append(line[:160])
    if missing:
        raise AssertionError(f"PDF content check failed in {name}: {missing[:3]}")
    entry = {
        "name": name, "pdf": relative(pdf_path), "docx": relative(word_path),
        "pdf_pages": page_count, "sources": [d["source"] for d in documents],
        "source_sha256": {d["source"]: d["sha256"] for d in documents},
        "pdf_sha256": sha256(pdf_path.read_bytes()).hexdigest(),
        "docx_sha256": sha256(word_path.read_bytes()).hexdigest(),
        "validation": {"docx_zip_xml": "passed", "docx_complete_block_text": "passed",
                       "unicode_replacement_characters": 0, "pdf_text_segments_checked": checks,
                       "pdf_text_segments_needing_review": missing},
    }
    print(f"{name}: {page_count} PDF pages; {len(documents)} source document(s); "
          f"{len(missing)} PDF segments need review", flush=True)
    return entry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", help="Export names (e.g. Scope_Charter Week_01_FoodFlow).")
    args = parser.parse_args()
    OUTPUT.mkdir(exist_ok=True)
    fonts()
    asset_data = json.loads((OUTPUT / "assets/diagram_manifest.json").read_text(encoding="utf-8"))
    images = {item["source"]: item for item in asset_data["images"]}
    for item in images.values():
        actual_hash = sha256((ROOT / item["source"]).read_bytes()).hexdigest()
        if actual_hash != item["source_sha256"]:
            raise ValueError("Stale diagram PNG; run reports/assets/render_diagrams.py: " + item["source"])
        if "image_sha256" in item and sha256((ROOT / item["image"]).read_bytes()).hexdigest() != item["image_sha256"]:
            raise ValueError("Diagram PNG changed; run reports/assets/render_diagrams.py: " + item["image"])
    core_sources = [f"docs/semesters/week-{i:02d}.md" for i in range(1, 7)]
    supporting_sources = [
        "docs/glossary.md", "docs/audience/personas.md", "docs/requirements/scope.md",
        "docs/audience/corg-ly-exercise.md", "docs/requirements/srs.md",
        "docs/requirements/traceability.md", "docs/requirements/mockups/index.md",
        "docs/architecture/index.md", "docs/architecture/adr/index.md",
        "docs/architecture/adr/0001-web-app-stack.md",
        "docs/architecture/adr/0002-persistence-and-idempotency.md",
        "docs/architecture/adr/0003-versioned-api-contract.md",
        "docs/architecture/adr/0004-container-responsibilities.md",
        "docs/architecture/ue-4-rework.md", "docs/api/README.md",
        "docs/api/sample-audit.md", "docs/api/renderer-decision.md",
        "review/bhatti_audit_table.md", "review/technical_debt.md",
        "docs/project/status.md", "docs/project/provenance.md", "docs/project/roadmap.md",
    ]
    documents = {p: parse_markdown(ROOT / p, images) for p in core_sources + supporting_sources}
    (OUTPUT / "block_data.json").write_text(
        json.dumps({"format": "foodflow-markdown-blocks-v1", "documents": list(documents.values())},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    specifications = [(f"Week_{i:02d}_FoodFlow", [documents[p]], False, False)
                      for i, p in enumerate(core_sources, 1)]
    specifications += [
        ("Scope_Charter", [documents["docs/requirements/scope.md"]], True, False),
        ("UE_01_Corgly", [documents["docs/audience/corg-ly-exercise.md"]], False, False),
        ("FoodFlow_Documentation", list(documents.values()), False, True),
    ]
    old_manifest = OUTPUT / "manifest.json"
    entries = {}
    if args.only and old_manifest.exists():
        entries = {e["name"]: e for e in json.loads(old_manifest.read_text(encoding="utf-8"))["exports"]}
    for name, sources, compact, combined in specifications:
        if args.only and name not in args.only:
            continue
        entries[name] = export_pair(name, sources, compact, combined)
        if name == "Scope_Charter" and entries[name]["pdf_pages"] != 1:
            raise AssertionError("Scope Charter must be exactly one PDF page.")
        if name == "UE_01_Corgly" and entries[name]["pdf_pages"] > 4:
            raise AssertionError("UE-1 must not exceed four PDF pages.")
    ordered = [entries[s[0]] for s in specifications if s[0] in entries]
    manifest = {
        "generated_at": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "client_date": DATE, "canonical_source": "repository Markdown",
        "source_repository": REPO_URL,
        "generator": {"path": "tools/export_project.py", "sha256": sha256(Path(__file__).read_bytes()).hexdigest()},
        "diagram_manifest_sha256": sha256((OUTPUT / "assets/diagram_manifest.json").read_bytes()).hexdigest(),
        "dependencies": {package: version(package) for package in ["reportlab", "markdown-it-py", "pypdf", "Pillow"]},
        "renderer": {"pdf": "ReportLab " + __import__("reportlab").Version,
                     "word": "editable OpenXML; Word pagination depends on installed fonts/layout",
                     "fonts": "embedded Arial and Consolas in PDF; Arial/Consolas requested in DOCX",
                     "diagrams": "offscreen QtSvg PNG; original SVG/Mermaid retained"},
        "exports": ordered,
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# FoodFlow — Word ба PDF хувилбар", "",
        "Markdown нь үндсэн эх. Доорх Word файлын текст, хүснэгт, код, холбоосыг засварлаж болно. "
        "PDF-д фонтыг нь суулгасан тул Монгол Unicode текстийг сонгож, хайж, хуулж болно.", "",
        "| Баримт | Word | PDF | PDF хуудас | Засварлах эх |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for entry in ordered:
        title = {"FoodFlow_Documentation": "Нэгдсэн төслийн баримт", "Scope_Charter": "UE-2 Scope Charter",
                 "UE_01_Corgly": "UE-1 Corg.ly"}.get(entry["name"], entry["name"].replace("_", " "))
        source = "../docs/index.md" if entry["name"] == "FoodFlow_Documentation" else "../" + entry["sources"][0]
        lines.append(f"| {title} | [DOCX]({Path(entry['docx']).name}) | [PDF]({Path(entry['pdf']).name}) | "
                     f"{entry['pdf_pages']} | [Markdown]({source}) |")
    lines += [
        "", "Нэгдсэн баримт нь зургаан семинарын бүрэн эх, нэр томьёо, persona, хамрах хүрээ, "
        "SRS, traceability, mock UI, архитектур, дөрвөн ADR, UE-4, API лавлах ба аудит, "
        "техникийн өр, төлөв, эх сурвалж, roadmap-ийг агуулна. Сонгосон хэсгүүдийн текстийг товчлоогүй. "
        "Mermaid source кодыг хэвээр хадгалж, түүнд харгалзах SVG дүрслэлийг зураг болгон нэмж оруулсан.", "",
        "Өргөн traceability хүснэгт болон архитектурын зураг PDF/DOCX-ийн landscape хэсэгт байрлана. "
        "DOCX-ийн агуулгын хүснэгтийг Word дээр Update Field → Update entire table гэж шинэчилнэ. "
        "Word-ийн бодит хуудасны тоо тухайн төхөөрөмжийн фонт, хувилбараас хамаардаг; хүснэгтэд PDF-ийн бодит тоог үзүүлэв.", "",
        "Хуудасны тоо, source/output SHA-256, Unicode болон ZIP/XML шалгалт: [manifest.json](manifest.json). "
        "Эхээс уншсан бүтцийн өгөгдөл: [block_data.json](block_data.json). "
        "Зураг ба эхийн mapping: [diagram_manifest.json](assets/diagram_manifest.json).", "",
        "Дахин үүсгэхэд ReportLab, markdown-it-py, pypdf, Pillow болон Windows-ийн Arial/Consolas фонт хэрэгтэй. "
        "Туршсан dependency хувилбар: [requirements.txt](requirements.txt), "
        "SVG/PDF preview хэрэгсэл: [requirements-renderer.txt](requirements-renderer.txt). "
        "SVG-г шинэчилсэн бол эхлээд PySide6-тэй offscreen asset renderer ажиллуулна:", "",
        "    python reports/assets/render_diagrams.py",
        "    python tools/export_project.py", "",
        "Нэгдсэн PDF-ийн дүрслэл ба DOCX зургийн бүтэц, эх/гаралтын hash-ийг дахин шалгах:", "",
        "    python reports/assets/inspect_pdf.py reports/FoodFlow_Documentation.pdf --pages 1 2",
        "    python reports/assets/audit_exports.py", "",
        "Энэ аудит нь хуудасны хил, ZIP/XML, эхийн бүрэн байдлыг шалгана. "
        "Зургийн шошго, хүснэгтийн уншигдах байдлыг [preview](assets/previews/FoodFlow_Documentation/page-001.png) ашиглан нүдээр хянана.", "",
        "PDF/DOCX-ийг өөрчилснөөр Markdown автоматаар шинэчлэгдэхгүй. Дараагийн семинарын өөрчлөлтийг "
        "эхлээд canonical Markdown-д хийж, дараа нь экспорт ба manifest-ийг хамт шинэчилнэ.", "",
    ]
    (OUTPUT / "README.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
