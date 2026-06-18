from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Iterable
from xml.sax.saxutils import escape

import fitz
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Flowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "output" / "pdf"
PREVIEW_DIR = ROOT / "output" / "preview"
FONT_DIR = Path(r"C:\Windows\Fonts")

TERMS_PATH = DATA_DIR / "termos.json"
CALLS_PATH = DATA_DIR / "chamadas.json"
EXPLANATIONS_PATH = DATA_DIR / "explicacoes.json"
CARDS_MANIFEST_PATH = ROOT / "output" / "cartelas_manifest.json"

NUM_CARDS = 24
RANDOM_SEED = 404
PROJECT_TITLE = "Bingo catequético"
MEETING_TITLE = "Encontro"
MEETING_LABEL = "Encontro"
OUTPUT_SLUG = "bingo_catequetico"
CORE_MESSAGE = "Frase-síntese doutrinal e pedagógica do encontro."

A4_W, A4_H = A4
LAND_W, LAND_H = landscape(A4)

PALETTE = {
    "paper": HexColor("#F7F4EE"),
    "paper_2": HexColor("#ECE2D2"),
    "field": HexColor("#FFFDF7"),
    "ink": HexColor("#25221D"),
    "muted": HexColor("#686056"),
    "hairline": HexColor("#D7CABC"),
    "hairline_dark": HexColor("#9A8E80"),
    "charcoal": HexColor("#2D2A26"),
    "petrol": HexColor("#1F3A4D"),
    "petrol_light": HexColor("#E8F0F2"),
    "petrol_line": HexColor("#B9C9CF"),
    "gold": HexColor("#B99546"),
    "clay": HexColor("#A84F3D"),
    "plum": HexColor("#6E536F"),
    "teal": HexColor("#2F6E70"),
    "olive": HexColor("#64703C"),
}

COLUMN_ACCENTS = {
    "B": PALETTE["gold"],
    "I": PALETTE["clay"],
    "N": PALETTE["plum"],
    "G": PALETTE["teal"],
    "O": PALETTE["olive"],
}

COLUMN_TITLES = {
    "B": "BASE",
    "I": "INJUSTIÇAS",
    "N": "NARRATIVAS",
    "G": "DISCERNIMENTOS",
    "O": "ORIENTAÇÕES",
}

COLUMN_FULL_TITLES = {
    "B": "Base moral",
    "I": "Injustiças concretas",
    "N": "Narrativas falsas",
    "G": "Discernimentos",
    "O": "Orientações de resposta",
}

COLUMN_SHORT_FUNCTIONS = {
    "B": "fundamento cristão da dignidade humana",
    "I": "situações concretas do tema",
    "N": "desculpas que normalizam o erro",
    "G": "distinções para não simplificar demais",
    "O": "respostas proporcionais e prudentes",
}

COLUMN_ORDER = ["B", "I", "N", "G", "O"]


def alpha(color, opacity: float) -> colors.Color:
    return colors.Color(color.red, color.green, color.blue, alpha=opacity)


def register_fonts() -> dict[str, str]:
    fonts = {
        "serif": "Times-Roman",
        "serif_bold": "Times-Bold",
        "serif_italic": "Times-Italic",
        "sans": "Helvetica",
        "sans_bold": "Helvetica-Bold",
        "label": "Helvetica-Bold",
    }

    def try_font(name: str, filename: str, *, subfont_index: int = 0) -> bool:
        path = FONT_DIR / filename
        if not path.exists():
            return False
        try:
            pdfmetrics.registerFont(TTFont(name, str(path), subfontIndex=subfont_index))
            return True
        except Exception:
            return False

    has_cambria = try_font("BingoCambria", "cambria.ttc")
    has_cambria_bold = try_font("BingoCambriaBold", "cambriab.ttf")
    has_cambria_italic = try_font("BingoCambriaItalic", "cambriai.ttf")

    if has_cambria and has_cambria_bold:
        italic_font = "BingoCambriaItalic" if has_cambria_italic else "BingoCambria"
        pdfmetrics.registerFontFamily(
            "BingoCambria",
            normal="BingoCambria",
            bold="BingoCambriaBold",
            italic=italic_font,
            boldItalic="BingoCambriaBold",
        )
        fonts["serif"] = "BingoCambria"
        fonts["serif_bold"] = "BingoCambriaBold"
        if has_cambria_italic:
            fonts["serif_italic"] = "BingoCambriaItalic"

    if try_font("BingoSegoe", "segoeui.ttf") and try_font("BingoSegoeBold", "segoeuib.ttf"):
        pdfmetrics.registerFontFamily(
            "BingoSegoe",
            normal="BingoSegoe",
            bold="BingoSegoeBold",
            italic="BingoSegoe",
            boldItalic="BingoSegoeBold",
        )
        fonts["sans"] = "BingoSegoe"
        fonts["sans_bold"] = "BingoSegoeBold"
        fonts["label"] = "BingoSegoeBold"

    return fonts


FONTS = register_fonts()

GUIDE = {
    "background": HexColor("#F7F4EE"),
    "surface": HexColor("#FFFDF7"),
    "surface_alt": HexColor("#F1EDE5"),
    "line": HexColor("#DDD3C6"),
    "line_soft": HexColor("#E9E1D7"),
    "ink": HexColor("#272520"),
    "dark": HexColor("#2D2A26"),
    "muted": HexColor("#6E675D"),
}


def pstyle(
    name: str,
    size: float,
    leading: float,
    *,
    font: str | None = None,
    color=PALETTE["ink"],
    alignment=TA_LEFT,
    space_after: float = 0,
    space_before: float = 0,
    left_indent: float = 0,
    right_indent: float = 0,
    char_space: float = 0,
) -> ParagraphStyle:
    return ParagraphStyle(
        name,
        fontName=font or FONTS["sans"],
        fontSize=size,
        leading=leading,
        textColor=color,
        alignment=alignment,
        spaceAfter=space_after,
        spaceBefore=space_before,
        leftIndent=left_indent,
        rightIndent=right_indent,
        charSpace=char_space,
    )


def para(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(text).replace("\n", "<br/>"), style)


def rich_para(text: str, style: ParagraphStyle) -> Paragraph:
    parts = text.split("**")
    rendered = []
    for index, part in enumerate(parts):
        safe = escape(part).replace("\n", "<br/>")
        if index % 2:
            rendered.append(f"<b>{safe}</b>")
        else:
            rendered.append(safe)
    return Paragraph("".join(rendered), style)


def draw_para(
    c: canvas.Canvas,
    text: str,
    style: ParagraphStyle,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    valign: str = "top",
) -> tuple[float, float]:
    p = para(text, style)
    pw, ph = p.wrap(w, h)
    if valign == "middle":
        draw_y = y + (h - ph) / 2
    elif valign == "bottom":
        draw_y = y
    else:
        draw_y = y + h - ph
    p.drawOn(c, x, draw_y)
    return pw, ph


def fit_style(
    name: str,
    text: str,
    width: float,
    height: float,
    *,
    font: str,
    color=PALETTE["ink"],
    alignment=TA_CENTER,
    sizes: Iterable[tuple[float, float]] = ((8.4, 9.2), (7.8, 8.6), (7.1, 7.9), (6.5, 7.2)),
) -> ParagraphStyle:
    for size, leading in sizes:
        style = pstyle(name, size, leading, font=font, color=color, alignment=alignment)
        p = para(text, style)
        _, ph = p.wrap(width, height)
        if ph <= height:
            return style
    size, leading = list(sizes)[-1]
    return pstyle(name, size, leading, font=font, color=color, alignment=alignment)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_project_data() -> tuple[dict, dict, list[dict], list[dict]]:
    global COLUMN_FULL_TITLES, COLUMN_SHORT_FUNCTIONS, PROJECT_TITLE, MEETING_TITLE, MEETING_LABEL, OUTPUT_SLUG, CORE_MESSAGE
    terms_data = load_json(TERMS_PATH)
    calls_data = load_json(CALLS_PATH)
    PROJECT_TITLE = terms_data.get("title", PROJECT_TITLE)
    MEETING_TITLE = terms_data.get("meeting", MEETING_TITLE)
    MEETING_LABEL = terms_data.get("meeting_label", MEETING_TITLE)
    OUTPUT_SLUG = terms_data.get("output_slug", OUTPUT_SLUG)
    CORE_MESSAGE = terms_data.get("core_message", CORE_MESSAGE)
    COLUMN_FULL_TITLES = {col["key"]: col["title"] for col in terms_data["columns"]}
    COLUMN_SHORT_FUNCTIONS = {
        col["key"]: col.get("short_function", col["function"]) for col in terms_data["columns"]
    }
    return terms_data, calls_data, terms_data["terms"], calls_data["cards"]


def project_subject() -> str:
    if "—" in PROJECT_TITLE:
        return PROJECT_TITLE.split("—", 1)[1].strip()
    if "-" in PROJECT_TITLE:
        return PROJECT_TITLE.split("-", 1)[1].strip()
    return PROJECT_TITLE


def load_explanations_data() -> dict:
    return load_json(EXPLANATIONS_PATH)


def terms_by_column(terms: list[dict]) -> dict[str, list[dict]]:
    return {col: [term for term in terms if term["column"] == col] for col in COLUMN_ORDER}


def balanced_column_assignments(
    column_terms: list[dict],
    *,
    cards_count: int,
    terms_per_card: int,
    rng: random.Random,
) -> list[list[dict]]:
    total_slots = cards_count * terms_per_card
    base_count, extra_count = divmod(total_slots, len(column_terms))
    shuffled_terms = column_terms[:]
    rng.shuffle(shuffled_terms)
    target_counts = {
        term["id"]: base_count + (1 if index < extra_count else 0)
        for index, term in enumerate(shuffled_terms)
    }
    term_lookup = {term["id"]: term for term in column_terms}

    for _attempt in range(250):
        assignments: list[list[str]] = [[] for _ in range(cards_count)]
        term_ids = list(target_counts)
        rng.shuffle(term_ids)

        failed = False
        for term_id in term_ids:
            for _ in range(target_counts[term_id]):
                candidates = [
                    card_index
                    for card_index, current_terms in enumerate(assignments)
                    if len(current_terms) < terms_per_card and term_id not in current_terms
                ]
                if not candidates:
                    failed = True
                    break
                min_len = min(len(assignments[index]) for index in candidates)
                candidates = [index for index in candidates if len(assignments[index]) == min_len]
                assignments[rng.choice(candidates)].append(term_id)
            if failed:
                break

        if not failed and all(len(card_terms) == terms_per_card for card_terms in assignments):
            for card_terms in assignments:
                rng.shuffle(card_terms)
            return [[term_lookup[term_id] for term_id in card_terms] for card_terms in assignments]

    raise RuntimeError("Não foi possível montar cartelas balanceadas sem repetição por coluna.")


def generate_bingo_cards(terms: list[dict], count: int = NUM_CARDS, seed: int = RANDOM_SEED) -> list[dict]:
    rng = random.Random(seed)
    grouped = terms_by_column(terms)
    assignments = {
        col: balanced_column_assignments(
            grouped[col],
            cards_count=count,
            terms_per_card=4 if col == "N" else 5,
            rng=rng,
        )
        for col in COLUMN_ORDER
    }

    cards = []
    for card_index in range(count):
        grid: list[list[dict | None]] = [[None for _ in COLUMN_ORDER] for _ in range(5)]
        for c_index, col in enumerate(COLUMN_ORDER):
            row_positions = [0, 1, 2, 3, 4]
            if col == "N":
                row_positions.remove(2)
            rng.shuffle(row_positions)
            for term, row in zip(assignments[col][card_index], row_positions):
                grid[row][c_index] = term

        grid[2][2] = {
            "id": "FREE",
            "column": "N",
            "label": "LIVRE",
            "definition": "Gn 1,27",
            "anchors": ["Gn 1,27"],
        }
        cards.append({"number": card_index + 1, "grid": grid})

    return cards


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_line_model() -> list[dict]:
    lines: list[dict] = []
    for row in range(1, 6):
        lines.append({
            "type": "horizontal",
            "index": row,
            "cells": [[row, col] for col in range(1, 6)],
        })
    for col in range(1, 6):
        lines.append({
            "type": "vertical",
            "index": col,
            "cells": [[row, col] for row in range(1, 6)],
        })
    lines.append({
        "type": "diagonal",
        "index": 1,
        "cells": [[index, index] for index in range(1, 6)],
    })
    lines.append({
        "type": "diagonal",
        "index": 2,
        "cells": [[index, 6 - index] for index in range(1, 6)],
    })
    return lines


def card_cell_manifest(term: dict, row: int, col: int) -> dict:
    payload = {
        "row": row,
        "col": col,
        "id": term["id"],
        "column": term["column"],
        "label": term["label"],
    }
    if term["id"] == "FREE":
        payload["free"] = True
        payload["called"] = False
        payload["anchors"] = term.get("anchors", [])
    return payload


def print_layout_manifest(cards: list[dict]) -> list[dict]:
    pages = []
    for page_index, offset in enumerate(range(0, len(cards), 2), start=1):
        positions = [{"slot": "top", "card_id": f"C{cards[offset]['number']:02d}"}]
        if offset + 1 < len(cards):
            positions.append({"slot": "bottom", "card_id": f"C{cards[offset + 1]['number']:02d}"})
        pages.append({"page": page_index, "positions": positions})
    return pages


def build_cards_manifest(terms_data: dict, cards: list[dict]) -> Path:
    CARDS_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    source_hashes = {
        "termos.json": file_sha256(TERMS_PATH),
        "chamadas.json": file_sha256(CALLS_PATH),
        "explicacoes.json": file_sha256(EXPLANATIONS_PATH),
    }
    card_payload = [
        {
            "id": f"C{card['number']:02d}",
            "number": card["number"],
            "term_ids": [
                term["id"]
                for row in card["grid"]
                for term in row
                if term["id"] != "FREE"
            ],
            "grid": [
                [
                    card_cell_manifest(term, row_index, col_index)
                    for col_index, term in enumerate(row, start=1)
                ]
                for row_index, row in enumerate(card["grid"], start=1)
            ],
        }
        for card in cards
    ]
    card_set_basis = {
        "output_slug": OUTPUT_SLUG,
        "num_cards": len(cards),
        "seed": RANDOM_SEED,
        "cards": [
            [
                [
                    {
                        "id": term["id"],
                        "label": term["label"],
                        "column": term["column"],
                    }
                    for term in row
                ]
                for row in card["grid"]
            ]
            for card in cards
        ],
    }
    card_set_hash = hashlib.sha256(
        json.dumps(card_set_basis, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()

    manifest = {
        "schema": "bingo-catequese/cartelas-manifest.v1",
        "card_set_id": f"{OUTPUT_SLUG}_{len(cards)}_seed_{RANDOM_SEED}_{card_set_hash[:12]}",
        "card_set_hash": card_set_hash,
        "project": {
            "title": PROJECT_TITLE,
            "meeting": MEETING_TITLE,
            "meeting_label": MEETING_LABEL,
            "output_slug": OUTPUT_SLUG,
            "core_message": CORE_MESSAGE,
        },
        "generation": {
            "algorithm": "balanced-column-assignments-v1",
            "seed": RANDOM_SEED,
            "num_cards": len(cards),
            "columns": COLUMN_ORDER,
            "grid": "5x5",
            "center": terms_data.get("card_model", {}).get("center", {}),
            "win_condition": terms_data.get("card_model", {}).get("recommended_win_condition"),
        },
        "source_hashes": source_hashes,
        "line_model": manifest_line_model(),
        "print_layout": {
            "pdf": "output/pdf/cartelas_bingo_24_a4.pdf",
            "cards_per_page": 2,
            "page_order": print_layout_manifest(cards),
        },
        "cards": card_payload,
    }

    CARDS_MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return CARDS_MANIFEST_PATH


def draw_page_bg(c: canvas.Canvas, page_w: float, page_h: float) -> None:
    pass


def draw_plain_sheet_bg(c: canvas.Canvas, page_w: float, page_h: float) -> None:
    pass


def draw_cut_line(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float) -> None:
    pass


def draw_card_decorative_marks(c: canvas.Canvas, x: float, y: float, w: float, h: float, accent) -> None:
    c.saveState()
    c.setStrokeColor(alpha(accent, 0.6))
    c.setLineWidth(0.8)
    # Bottom-left bracket
    c.line(x + 4 * mm, y + 4 * mm, x + 10 * mm, y + 4 * mm)
    c.line(x + 4 * mm, y + 4 * mm, x + 4 * mm, y + 10 * mm)
    # Bottom-right bracket
    c.line(x + w - 4 * mm, y + 4 * mm, x + w - 10 * mm, y + 4 * mm)
    c.line(x + w - 4 * mm, y + 4 * mm, x + w - 4 * mm, y + 10 * mm)
    c.restoreState()


def draw_bingo_card(c: canvas.Canvas, card: dict, x: float, y: float, w: float, h: float) -> None:
    c.saveState()

    # Philosophy: the player holds this card and scans it at speed.
    # The CONCEPT is what they're looking for — not the code, not the column.
    # Every design decision should serve that one act: fast, confident recognition.

    # ── Card shell ──────────────────────────────────────────────────────────
    c.setFillColor(PALETTE["field"])
    c.setStrokeColor(HexColor("#C2B8A8"))
    c.setLineWidth(0.6)
    outer_radius = 6.0 * mm
    c.roundRect(x, y, w, h, outer_radius, stroke=1, fill=1)

    # ── Layout constants ─────────────────────────────────────────────────────
    # Apple-style mathematical concentricity: Inner Radius = Outer Radius - Padding
    pad_card = 3.5 * mm
    inner_radius = outer_radius - pad_card  # 2.5 mm

    # Header strip: compact identity bar
    header_strip_h = 11.5 * mm
    strip_x = x + pad_card
    strip_w = w - 2 * pad_card
    strip_top = (y + h) - pad_card
    hstrip_y = strip_top - header_strip_h

    # ── Grid Constants & Apple-Style Concentricity ───────────────────────────
    # We want the grid to share the same horizontal padding as the header strip
    # so that they align perfectly. This means grid_pad_x = pad_card = 3.5 mm.
    pad_grid = pad_card
    bot_margin = 6.0 * mm
    grid_x = x + pad_grid
    grid_w = w - 2 * pad_grid
    grid_y = y + bot_margin
    grid_top = hstrip_y - 3.5 * mm

    col_header_h = 12.0 * mm
    data_h = grid_top - grid_y - col_header_h
    cell_h = data_h / 5
    cell_w = grid_w / 5
    col_header_y = grid_top - col_header_h

    # The grid's outer radius must be mathematically concentric with the card's shell
    grid_radius = outer_radius - pad_grid  # 6.0 - 3.5 = 2.5 mm

    # ── Header strip (charcoal pill, mathematically inset) ──────────────────
    c.setFillColor(PALETTE["charcoal"])
    c.roundRect(strip_x, hstrip_y, strip_w, header_strip_h, inner_radius, stroke=0, fill=1)

    # Title — cream serif, prominent
    c.setFillColor(PALETTE["field"])
    c.setFont(FONTS["serif_bold"], 11.0)
    c.drawString(strip_x + 4.5 * mm, hstrip_y + 5.5 * mm, PROJECT_TITLE)

    # Sub-metadata — also cream (white), smaller, same color to maintain two-tone elegance
    c.setFont(FONTS["sans_bold"], 5.8)
    c.drawString(strip_x + 4.5 * mm, hstrip_y + 2.0 * mm, MEETING_LABEL)
    c.drawRightString(strip_x + strip_w - 4.5 * mm, hstrip_y + 2.0 * mm, f"Cartela {card['number']:02d}")

    # ── Grid Rendering (Clipped for perfect rounded corners) ─────────────────
    c.saveState()
    
    # 1. Create a mathematically perfect clipping path
    clip_path = c.beginPath()
    clip_path.roundRect(grid_x, grid_y, grid_w, grid_top - grid_y, grid_radius)
    c.clipPath(clip_path, stroke=0, fill=0)

    # 2. Draw Column Header Backgrounds
    for c_index, col in enumerate(COLUMN_ORDER):
        cx = grid_x + c_index * cell_w
        c.setFillColor(COLUMN_ACCENTS[col])
        c.rect(cx, col_header_y, cell_w, col_header_h, stroke=0, fill=1)

    # 3. Draw Row Tints (Every other row)
    for row in range(5):
        if row % 2 == 0:
            ry = grid_y + row * cell_h
            c.setFillColor(HexColor("#F7F3ED"))
            c.rect(grid_x, ry, grid_w, cell_h, stroke=0, fill=1)

    # 4. Draw FREE Cell Background
    for r in range(5):
        for c_index, col in enumerate(COLUMN_ORDER):
            term = card["grid"][r][c_index]
            if term["id"] == "FREE":
                cx = grid_x + c_index * cell_w
                cy = grid_y + (4 - r) * cell_h
                c.setFillColor(HexColor("#EDE4D6"))
                c.rect(cx, cy, cell_w, cell_h, stroke=0, fill=1)

    # 5. Draw Inner Grid Lines
    c.setStrokeColor(HexColor("#DCD3C6"))  # Slightly softer than before
    c.setLineWidth(0.4)
    # Horizontal dividers (only between data rows)
    for row in range(1, 5):
        yy = grid_y + row * cell_h
        c.line(grid_x, yy, grid_x + grid_w, yy)
    # Vertical dividers
    for col_i in range(1, 5):
        xx = grid_x + col_i * cell_w
        c.line(xx, grid_y, xx, grid_top)
    
    # Slightly thicker line separating headers from data
    c.setLineWidth(0.6)
    c.line(grid_x, col_header_y, grid_x + grid_w, col_header_y)

    c.restoreState()  # End Clipping

    # ── Grid Outer Border ────────────────────────────────────────────────────
    c.setStrokeColor(HexColor("#C2B8A8"))  # Match the outer shell's border color
    c.setLineWidth(0.6)
    c.roundRect(grid_x, grid_y, grid_w, grid_top - grid_y, grid_radius, stroke=1, fill=0)

    # ── Text Content ─────────────────────────────────────────────────────────
    # 1. Header Text
    for c_index, col in enumerate(COLUMN_ORDER):
        cx = grid_x + c_index * cell_w
        c.setFillColor(PALETTE["field"])
        c.setFont(FONTS["serif_bold"], 16.0)
        c.drawCentredString(cx + cell_w / 2, col_header_y + 4.8 * mm, col)
        
        # Add back the column titles (Base, Injustiças, etc) that were missing
        c.setFont(FONTS["sans_bold"], 4.5)
        c.drawCentredString(cx + cell_w / 2, col_header_y + 1.8 * mm, COLUMN_TITLES[col])

    # 2. Cell Text
    for r in range(5):
        for c_index, col in enumerate(COLUMN_ORDER):
            term = card["grid"][r][c_index]
            cx = grid_x + c_index * cell_w
            cy = grid_y + (4 - r) * cell_h
            
            if term["id"] == "FREE":
                c.setStrokeColor(PALETTE["gold"])
                c.setLineWidth(0.6)
                c.roundRect(cx + 1.2 * mm, cy + 1.2 * mm, cell_w - 2.4 * mm, cell_h - 2.4 * mm, 1.2 * mm, stroke=1, fill=0)
                
                c.setFillColor(PALETTE["gold"])
                c.setFont(FONTS["serif_bold"], 10.5)
                c.drawCentredString(cx + cell_w / 2, cy + cell_h / 2 + 0.8 * mm, "LIVRE")
                
                c.setFillColor(PALETTE["muted"])
                c.setFont(FONTS["serif"], 6.5)
                c.drawCentredString(cx + cell_w / 2, cy + cell_h / 2 - 3.8 * mm, "Gn 1,27")
            else:
                pad = 2.0 * mm
                text_w = cell_w - 2 * pad
                
                # Concept text
                style = fit_style(
                    f"Cell{term['id']}",
                    term["label"],
                    text_w,
                    cell_h - 3.5 * mm,
                    font=FONTS["serif_bold"],
                    color=PALETTE["ink"],
                    alignment=TA_CENTER,
                    sizes=((9.0, 10.2), (8.2, 9.4), (7.5, 8.6), (6.8, 7.8)),
                )
                draw_para(c, term["label"], style, cx + pad, cy + 2.0 * mm, text_w, cell_h - 3.5 * mm, valign="middle")
                
                # Ghost code — slightly larger, deeper color, refined padding
                c.setFillColor(HexColor("#9C8F7E"))
                c.setFont(FONTS["sans_bold"], 5.6)
                c.drawRightString(cx + cell_w - 1.8 * mm, cy + 1.4 * mm, term["id"])

    c.restoreState()





def build_bingo_cards(cards: list[dict]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "cartelas_bingo_24_a4.pdf"

    c = canvas.Canvas(str(path), pagesize=A4)
    c.setTitle(f"Cartelas do bingo — {project_subject()}")
    margin_x = 10 * mm
    margin_y = 9 * mm
    gap = 7 * mm
    card_w = A4_W - 2 * margin_x
    card_h = (A4_H - 2 * margin_y - gap) / 2

    for i in range(0, len(cards), 2):
        draw_page_bg(c, A4_W, A4_H)
        draw_cut_line(c, margin_x, A4_H / 2, A4_W - margin_x, A4_H / 2)
        draw_bingo_card(c, cards[i], margin_x, margin_y + card_h + gap, card_w, card_h)
        if i + 1 < len(cards):
            draw_bingo_card(c, cards[i + 1], margin_x, margin_y, card_w, card_h)
        c.showPage()
    c.save()
    return path


def call_card_positions() -> list[tuple[float, float, float, float]]:
    margin_x = 10 * mm
    margin_y = 9 * mm
    gap = 5 * mm
    w = (A4_W - 2 * margin_x - gap) / 2
    h = (A4_H - 2 * margin_y - gap) / 2
    return [
        (margin_x, margin_y + h + gap, w, h),
        (margin_x + w + gap, margin_y + h + gap, w, h),
        (margin_x, margin_y, w, h),
        (margin_x + w + gap, margin_y, w, h),
    ]


def team_rule_card_positions() -> list[tuple[float, float, float, float]]:
    """Six readable team-rule cards on A4 portrait."""
    margin_x = 9 * mm
    margin_y = 8 * mm
    gap_x = 5 * mm
    gap_y = 5 * mm
    w = (A4_W - 2 * margin_x - gap_x) / 2
    h = (A4_H - 2 * margin_y - 2 * gap_y) / 3
    positions = []
    for row in range(3):
        for col in range(2):
            px = margin_x + col * (w + gap_x)
            py = A4_H - margin_y - (row + 1) * h - row * gap_y
            positions.append((px, py, w, h))
    return positions


def playing_card_positions() -> list[tuple[float, float, float, float]]:
    """Eight poker-ratio cards on A4 landscape.

    Physical card size is about 66.5 x 93 mm, close to poker proportion
    2.5:3.5 while preserving enough space for catechist notes.
    """
    margin_x = 8 * mm
    gap_x = 5 * mm
    margin_y = 9.3 * mm
    gap_y = 5 * mm
    w = (LAND_W - 2 * margin_x - 3 * gap_x) / 4
    h = w * 3.5 / 2.5
    # Center vertically só printer margin drift is balanced.
    margin_y = (LAND_H - 2 * h - gap_y) / 2
    positions = []
    for row in range(2):
        for col in range(4):
            x = margin_x + col * (w + gap_x)
            y = LAND_H - margin_y - (row + 1) * h - row * gap_y
            positions.append((x, y, w, h))
    return positions


def draw_card_cut_guides(c: canvas.Canvas, positions: list[tuple[float, float, float, float]], page_w: float, page_h: float) -> None:
    pass


def draw_column_icon(c: canvas.Canvas, col: str, x: float, y: float, size: float, color) -> None:
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(colors.transparent)
    c.setLineWidth(0.55)
    if col == "B":
        # Cornerstone / keystone.
        c.rect(x, y, size * 0.32, size * 0.18, stroke=1, fill=0)
        c.rect(x + size * 0.34, y, size * 0.32, size * 0.18, stroke=1, fill=0)
        c.rect(x + size * 0.68, y, size * 0.32, size * 0.18, stroke=1, fill=0)
        p = c.beginPath()
        p.moveTo(x + size * 0.30, y + size * 0.22)
        p.lineTo(x + size * 0.70, y + size * 0.22)
        p.lineTo(x + size * 0.62, y + size * 0.62)
        p.lineTo(x + size * 0.38, y + size * 0.62)
        p.close()
        c.drawPath(p, stroke=1, fill=0)
    elif col == "I":
        p = c.beginPath()
        p.moveTo(x + size * 0.50, y + size * 0.66)
        p.lineTo(x + size * 0.86, y + size * 0.12)
        p.lineTo(x + size * 0.14, y + size * 0.12)
        p.close()
        c.drawPath(p, stroke=1, fill=0)
        c.line(x + size * 0.50, y + size * 0.50, x + size * 0.50, y + size * 0.28)
        c.circle(x + size * 0.50, y + size * 0.19, size * 0.025, stroke=1, fill=0)
    elif col == "N":
        c.roundRect(x + size * 0.10, y + size * 0.24, size * 0.80, size * 0.36, size * 0.08, stroke=1, fill=0)
        c.line(x + size * 0.25, y + size * 0.42, x + size * 0.75, y + size * 0.42)
        c.line(x + size * 0.38, y + size * 0.24, x + size * 0.30, y + size * 0.10)
    elif col == "G":
        c.circle(x + size * 0.42, y + size * 0.42, size * 0.24, stroke=1, fill=0)
        c.line(x + size * 0.60, y + size * 0.24, x + size * 0.84, y + size * 0.02)
        c.line(x + size * 0.28, y + size * 0.42, x + size * 0.55, y + size * 0.42)
    else:
        c.circle(x + size * 0.50, y + size * 0.45, size * 0.26, stroke=1, fill=0)
        c.line(x + size * 0.50, y + size * 0.45, x + size * 0.50, y + size * 0.72)
        c.line(x + size * 0.50, y + size * 0.45, x + size * 0.72, y + size * 0.34)
    c.restoreState()


def draw_tracked_label(c: canvas.Canvas, text: str, x: float, y: float, *, color=PALETTE["petrol"], font_size: float = 4.4, tracking: float = 1.05) -> None:
    c.saveState()
    c.setFillColor(color)
    text_obj = c.beginText(x, y)
    text_obj.setFont(FONTS["label"], font_size)
    text_obj.setCharSpace(tracking)
    text_obj.textOut(text)
    c.drawText(text_obj)
    c.restoreState()


def fit_html_style(
    name: str,
    text: str,
    width: float,
    height: float,
    *,
    font: str,
    color=PALETTE["ink"],
    alignment=TA_LEFT,
    sizes: Iterable[tuple[float, float]] = ((5.8, 7.2), (5.3, 6.6), (4.8, 6.0)),
) -> ParagraphStyle:
    for size, leading in sizes:
        style = pstyle(name, size, leading, font=font, color=color, alignment=alignment)
        p = Paragraph(text, style)
        _, ph = p.wrap(width, height)
        if ph <= height:
            return style
    size, leading = list(sizes)[-1]
    return pstyle(name, size, leading, font=font, color=color, alignment=alignment)


def draw_html_para(
    c: canvas.Canvas,
    text: str,
    style: ParagraphStyle,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    valign: str = "top",
) -> tuple[float, float]:
    p = Paragraph(text, style)
    pw, ph = p.wrap(w, h)
    if valign == "middle":
        draw_y = y + (h - ph) / 2
    elif valign == "bottom":
        draw_y = y
    else:
        draw_y = y + h - ph
    p.drawOn(c, x, draw_y)
    return pw, ph


def draw_call_card(c: canvas.Canvas, call: dict, term_lookup: dict[str, dict], x: float, y: float, w: float, h: float) -> None:
    term = term_lookup[call["term_id"]]
    col = term["column"]

    c.saveState()
    c.setFillColor(PALETTE["field"])
    c.setStrokeColor(alpha(PALETTE["petrol"], 0.52))
    c.setLineWidth(0.45)
    c.roundRect(x, y, w, h, 3.2 * mm, stroke=1, fill=1)

    # Subtle paper fiber lines; deterministic and intentionally sparse.
    c.setStrokeColor(alpha(PALETTE["gold"], 0.055))
    c.setLineWidth(0.18)
    for i in range(5):
        yy = y + h * (0.18 + i * 0.15)
        c.line(x + 5 * mm, yy, x + w - 5 * mm, yy + (0.25 if i % 2 else -0.15) * mm)

    pad = 5.0 * mm
    
    # Active vertical coordinate starting from top margin
    cy = y + h - pad

    # Header: B01 chip and Title centered vertically
    chip_w = 9.0 * mm
    chip_h = 6.2 * mm
    chip_y = cy - chip_h
    
    # Thin elegant golden border, white background for chip
    c.setStrokeColor(alpha(PALETTE["gold"], 0.90))
    c.setFillColor(PALETTE["field"])
    c.setLineWidth(0.38)
    c.roundRect(x + pad, chip_y, chip_w, chip_h, 1.0 * mm, stroke=1, fill=1)
    
    # Chip text (B01, etc.) - mathematically centered vertically and horizontally
    c.setFillColor(PALETTE["petrol"])
    chip_font_size = 5.8
    c.setFont(FONTS["sans"], chip_font_size)
    c.drawCentredString(x + pad + chip_w / 2, chip_y + (chip_h - 0.7 * chip_font_size) / 2, call["id"])

    # Title is to the right of the chip
    title_x = x + pad + chip_w + 3.0 * mm
    title_w = w - (title_x - x) - pad
    title_h = 9.0 * mm
    title_y = chip_y + (chip_h - title_h) / 2
    title_style = fit_style(
        f"CallTitle{call['id']}",
        term["label"],
        title_w,
        title_h,
        font=FONTS["serif"],
        color=PALETTE["petrol"],
        alignment=TA_LEFT,
        sizes=((14.5, 16.0), (13.0, 14.5), (11.5, 13.0), (10.0, 11.5)),
    )
    # Centered vertically relative to the chip
    draw_para(c, term["label"], title_style, title_x, title_y, title_w, title_h, valign="middle")
    
    # Move active y-coordinate past the header
    cy -= chip_h

    # Divider line
    cy -= 2.0 * mm
    c.setStrokeColor(alpha(PALETTE["petrol_line"], 0.75))
    c.setLineWidth(0.35)
    c.line(x + pad, cy, x + w - pad, cy)

    # Typography Rules: Unified label styling for AAA editorial quality
    LABEL_SIZE = 5.5
    LABEL_TRACKING = 1.6

    # Category name below the line
    cy -= 4.0 * mm
    category_text = COLUMN_FULL_TITLES[col].upper()
    draw_tracked_label(c, category_text, x + pad, cy, color=PALETTE["petrol"], font_size=LABEL_SIZE, tracking=LABEL_TRACKING)

    # CASO Section
    cy -= 4.8 * mm
    draw_tracked_label(c, "CASO", x + pad, cy, color=PALETTE["petrol"], font_size=LABEL_SIZE, tracking=LABEL_TRACKING)
    
    cy -= 2.2 * mm
    case_max_h = 12.0 * mm
    case_style = fit_style(
        f"Case{call['id']}",
        call["case"],
        w - 2 * pad,
        case_max_h,
        font=FONTS["sans"],
        color=PALETTE["ink"],
        alignment=TA_LEFT,
        sizes=((7.2, 9.4), (6.7, 8.8), (6.2, 8.2), (5.7, 7.6)),
    )
    # Draw from top (cy) downwards, retrieve actual paragraph height
    _, case_h = draw_para(c, call["case"], case_style, x + pad, cy - case_max_h, w - 2 * pad, case_max_h)
    cy -= case_h

    # LEITURA DO CASO Section
    cy -= 4.2 * mm
    draw_tracked_label(c, "LEITURA DO CASO", x + pad, cy, color=PALETTE["petrol"], font_size=LABEL_SIZE, tracking=LABEL_TRACKING)

    cy -= 2.2 * mm
    point_max_h = 5.2 * mm
    number_r = 1.6 * mm
    point_text_x = x + pad + 5.0 * mm
    point_w = w - 2 * pad - 5.0 * mm
    
    for index, point in enumerate(call["reading_points"], start=1):
        # Continuous paragraph text: Title in Bold, Body in Regular
        combined_text = f"<b>{point['title']}:</b> {point['body']}"
        point_style = fit_html_style(
            f"PointText{call['id']}{index}",
            combined_text,
            point_w,
            point_max_h,
            font=FONTS["sans"],
            color=PALETTE["ink"],
            alignment=TA_LEFT,
            sizes=((6.8, 8.4), (6.3, 7.8), (5.8, 7.2)),
        )
        
        # Draw paragraph and get its height
        _, point_h = draw_html_para(c, combined_text, point_style, point_text_x, cy - point_max_h, point_w, point_max_h)
        
        # Circle with number, centered vertically relative to the first line
        leading = point_style.leading
        circle_y = cy - (leading / 2)
        c.setStrokeColor(PALETTE["petrol"])
        c.setFillColor(PALETTE["field"])
        c.setLineWidth(0.42)
        c.circle(x + pad + number_r, circle_y, number_r, stroke=1, fill=0)
        c.setFillColor(PALETTE["petrol"])
        circle_font_size = 4.25
        c.setFont(FONTS["sans_bold"], circle_font_size)
        c.drawCentredString(x + pad + number_r, circle_y - (0.7 * circle_font_size) / 2, str(index))
        
        cy -= point_h + 1.2 * mm

    # CONFERÊNCIA Section
    cy -= 2.0 * mm
    draw_tracked_label(c, "CONFERÊNCIA", x + pad, cy, color=PALETTE["petrol"], font_size=LABEL_SIZE, tracking=LABEL_TRACKING)
    
    cy -= 1.8 * mm
    conf_box_h = 10.5 * mm
    conf_box_y = cy - conf_box_h
    
    # Beautiful light blue rounded box with thin border
    c.setFillColor(PALETTE["petrol_light"])
    c.setStrokeColor(PALETTE["petrol_line"])
    c.setLineWidth(0.38)
    c.roundRect(x + pad, conf_box_y, w - 2 * pad, conf_box_h, 1.7 * mm, stroke=1, fill=1)
    
    # Question text inside the box
    q_style = fit_style(
        f"Q{call['id']}",
        call["conference_question"],
        w - 2 * pad - 5.0 * mm,
        conf_box_h - 2.0 * mm,
        font=FONTS["sans"],
        color=PALETTE["petrol"],
        alignment=TA_LEFT,
        sizes=((7.2, 9.0), (6.7, 8.4), (6.2, 7.8), (5.7, 7.2)),
    )
    draw_para(c, call["conference_question"], q_style, x + pad + 2.5 * mm, conf_box_y + 1.0 * mm, w - 2 * pad - 5.0 * mm, conf_box_h - 2.0 * mm, valign="middle")
    
    cy -= conf_box_h

    # NOTA Section
    cy -= 3.2 * mm
    draw_tracked_label(c, "NOTA", x + pad, cy, color=PALETTE["petrol"], font_size=LABEL_SIZE, tracking=LABEL_TRACKING)
    
    cy -= 1.8 * mm
    tag = " · ".join(call["anchors"])
    tag_w = min(w - 2 * pad, max(21 * mm, pdfmetrics.stringWidth(tag, FONTS["sans"], 4.25) + 4.4 * mm))
    note_w = w - 2 * pad - tag_w - 2.5 * mm
    
    # Increased vertical space allowance to ensure large readable font sizes for note text
    note_max_h = 10.0 * mm
    note_style = fit_style(
        f"Note{call['id']}",
        call["facilitator_note"],
        note_w,
        note_max_h,
        font=FONTS["serif_italic"],
        color=PALETTE["muted"],
        alignment=TA_LEFT,
        sizes=((7.5, 9.2), (7.0, 8.6), (6.5, 8.0), (6.0, 7.4)),
    )
    # The note text flows naturally below the NOTA label
    _, note_h = draw_para(c, call["facilitator_note"], note_style, x + pad, cy - note_max_h, note_w, note_max_h)
    cy -= note_h

    # Reference / Anchor Badge is fixed at bottom right for perfect structural alignment
    badge_y = y + 2.0 * mm
    badge_h = 4.5 * mm
    c.setStrokeColor(alpha(PALETTE["petrol"], 0.75))
    c.setFillColor(PALETTE["field"])
    c.setLineWidth(0.38)
    c.roundRect(x + w - pad - tag_w, badge_y, tag_w, badge_h, 1.2 * mm, stroke=1, fill=1)
    
    c.setFillColor(PALETTE["petrol"])
    badge_font_size = 4.25
    c.setFont(FONTS["sans"], badge_font_size)
    c.drawCentredString(x + w - pad - tag_w / 2, badge_y + (badge_h - 0.7 * badge_font_size) / 2, tag)
    c.restoreState()


def build_call_deck(terms: list[dict], calls: list[dict]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "baralho_chamadas_a4.pdf"
    term_lookup = {term["id"]: term for term in terms}
    c = canvas.Canvas(str(path), pagesize=landscape(A4))
    c.setTitle(f"Baralho de chamadas — {PROJECT_TITLE}")
    positions = playing_card_positions()

    for i in range(0, len(calls), len(positions)):
        draw_plain_sheet_bg(c, LAND_W, LAND_H)
        draw_card_cut_guides(c, positions, LAND_W, LAND_H)
        for offset, pos in enumerate(positions):
            if i + offset >= len(calls):
                continue
            draw_call_card(c, calls[i + offset], term_lookup, *pos)
        c.showPage()
    c.save()
    return path


def draw_checkbox(c: canvas.Canvas, x: float, y: float, size: float = 3.2 * mm) -> None:
    c.saveState()
    c.setStrokeColor(PALETTE["hairline_dark"])
    c.setFillColor(PALETTE["field"])
    c.setLineWidth(0.55)
    c.roundRect(x, y, size, size, 0.6 * mm, stroke=1, fill=1)
    c.restoreState()


def build_control_sheet(terms: list[dict]) -> Path:
    path = OUT_DIR / "folha_controle_chamadas.pdf"
    grouped = terms_by_column(terms)
    c = canvas.Canvas(str(path), pagesize=landscape(A4))
    c.setTitle(f"Folha de controle de chamadas — {PROJECT_TITLE}")
    draw_page_bg(c, LAND_W, LAND_H)

    # ── Page Margins ─────────────────────────────────────────────────────────
    margin_x = 12.0 * mm
    margin_y = 12.0 * mm
    w = LAND_W - 2 * margin_x
    h = LAND_H - 2 * margin_y
    x0 = margin_x
    y0 = margin_y

    # ── Header Strip (Charcoal Pill) ─────────────────────────────────────────
    header_strip_h = 13.0 * mm
    hstrip_y = y0 + h - header_strip_h
    
    c.setFillColor(PALETTE["charcoal"])
    c.roundRect(x0, hstrip_y, w, header_strip_h, 3.0 * mm, stroke=0, fill=1)

    c.setFillColor(PALETTE["field"])
    c.setFont(FONTS["serif_bold"], 14.0)
    c.drawString(x0 + 6.0 * mm, hstrip_y + 4.5 * mm, "Folha de Controle das Chamadas")

    # ── Grid Geometry ────────────────────────────────────────────────────────
    grid_gap = 4.0 * mm
    grid_top = hstrip_y - grid_gap
    grid_y = y0
    grid_w = w
    grid_h = grid_top - grid_y
    grid_radius = 5.0 * mm
    
    header_h = 11.5 * mm
    row_h = (grid_h - header_h) / 15
    col_w = grid_w / 5
    col_header_y = grid_top - header_h

    # ── Grid Rendering (Clipped) ─────────────────────────────────────────────
    c.saveState()
    clip_path = c.beginPath()
    clip_path.roundRect(x0, grid_y, grid_w, grid_h, grid_radius)
    c.clipPath(clip_path, stroke=0, fill=0)

    # 1. Column Header Backgrounds
    for c_index, col in enumerate(COLUMN_ORDER):
        cx = x0 + c_index * col_w
        c.setFillColor(COLUMN_ACCENTS[col])
        c.rect(cx, col_header_y, col_w, header_h, stroke=0, fill=1)

    # 2. Row Tints (alternating)
    for row in range(15):
        if row % 2 == 0:
            ry = col_header_y - (row + 1) * row_h
            c.setFillColor(HexColor("#F7F3ED"))
            c.rect(x0, ry, grid_w, row_h, stroke=0, fill=1)

    # 3. Inner Grid Lines
    c.setStrokeColor(HexColor("#DCD3C6"))
    c.setLineWidth(0.4)
    # Horizontal dividers
    for row in range(1, 15):
        ry = col_header_y - row * row_h
        c.line(x0, ry, x0 + grid_w, ry)
    # Vertical dividers
    for col_i in range(1, 5):
        cx = x0 + col_i * col_w
        c.line(cx, grid_y, cx, grid_top)
    
    # Thicker line separating headers from data
    c.setLineWidth(0.6)
    c.line(x0, col_header_y, x0 + grid_w, col_header_y)

    c.restoreState()

    # ── Grid Outer Border ────────────────────────────────────────────────────
    c.setStrokeColor(HexColor("#C2B8A8"))
    c.setLineWidth(0.6)
    c.roundRect(x0, grid_y, grid_w, grid_h, grid_radius, stroke=1, fill=0)

    # ── Text Content ─────────────────────────────────────────────────────────
    for c_index, col in enumerate(COLUMN_ORDER):
        cx = x0 + c_index * col_w
        
        # Column Headers
        c.setFillColor(PALETTE["field"])
        c.setFont(FONTS["serif_bold"], 16.0)
        c.drawCentredString(cx + col_w / 2, col_header_y + 4.8 * mm, col)
        
        c.setFont(FONTS["sans_bold"], 5.0)
        c.drawCentredString(cx + col_w / 2, col_header_y + 1.8 * mm, COLUMN_TITLES[col])
        
        # Row Content
        for r, term in enumerate(grouped[col]):
            ry = col_header_y - (r + 1) * row_h
            
            # Checkbox - visually separated with proper stroke
            c.setStrokeColor(HexColor("#A49887"))
            c.setLineWidth(0.45)
            draw_checkbox(c, cx + 3.0 * mm, ry + (row_h - 3.2 * mm) / 2, size=3.2 * mm)
            
            # Code ID
            c.setFillColor(HexColor("#9C8F7E"))
            c.setFont(FONTS["sans_bold"], 6.2)
            c.drawString(cx + 8.0 * mm, ry + row_h / 2 - 2.0, term["id"])
            
            # Concept Label
            c.setFillColor(PALETTE["ink"])
            font_name = FONTS["serif_bold"]
            font_size = 7.8
            max_w = col_w - 17.0 * mm
            # Dynamically shrink font if it overflows
            while c.stringWidth(term["label"], font_name, font_size) > max_w and font_size > 5.5:
                font_size -= 0.2
            c.setFont(font_name, font_size)
            c.drawString(cx + 15.5 * mm, ry + row_h / 2 - (font_size * 0.28), term["label"])

    c.save()
    return path


def build_team_rule_cards() -> Path:
    path = OUT_DIR / "cartoes_regras_equipes_a4.pdf"
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setTitle(f"Cartões de regras para equipes — {PROJECT_TITLE}")
    positions = team_rule_card_positions()
    for page in range(1):
        draw_plain_sheet_bg(c, A4_W, A4_H)
        for pos in positions:
            draw_team_rule_card(c, *pos)
        c.showPage()
    c.save()
    return path


def draw_team_rule_card(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.saveState()
    # Draw outer card border
    c.setFillColor(GUIDE["surface"])
    c.setStrokeColor(GUIDE["line"])
    c.setLineWidth(0.55)
    c.roundRect(x, y, w, h, 2.2 * mm, stroke=1, fill=1)

    pad_x = 6.0 * mm
    pad_y = 5.5 * mm
    content_w = w - 2 * pad_x

    # Header calculations
    header_top = y + h - pad_y
    title_y = header_top - 4.5 * mm
    
    # 1. Title
    c.setFont(FONTS["serif_bold"], 12.5)
    c.setFillColor(GUIDE["dark"])
    c.drawString(x + pad_x, title_y, "Regras do Jogo")

    # 2. Header Divider Line
    line_y = title_y - 2.8 * mm
    c.setStrokeColor(GUIDE["line_soft"])
    c.setLineWidth(0.4)
    c.line(x + pad_x, line_y, x + w - pad_x, line_y)

    # Styles
    section_title_style = pstyle("TeamRuleSecTitle", 6.5, 8.0, font=FONTS["sans_bold"], color=GUIDE["dark"])
    body_style = pstyle("TeamRuleBodyText", 7.6, 10.2, font=FONTS["sans"], color=GUIDE["ink"])
    
    # Cursor coordinate for vertical flow
    cy = line_y

    def flow_html(text: str, style: ParagraphStyle, space_before: float) -> None:
        nonlocal cy
        cy -= space_before
        p = Paragraph(text, style)
        pw, ph = p.wrap(content_w, 40 * mm)  # wrap with generous height limit
        p.drawOn(c, x + pad_x, cy - ph)
        cy -= ph

    # --- Section 1: RODADA ---
    flow_html("A RODADA DE JOGO", section_title_style, 4.0 * mm)
    
    sec1_text = (
        "A cada rodada, uma carta é sorteada e são lidos o <b>código</b>, o <b>conceito</b>, o <b>caso</b> e a <b>explicação</b>.<br/>"
        "Se a equipe tiver o <b>código correspondente</b> em sua cartela, deve marcar esse quadrado."
    )
    flow_html(sec1_text, body_style, 2.5 * mm)

    # --- Section 2: PARA VENCER ---
    flow_html("COMO VENCER", section_title_style, 5.0 * mm)
    
    sec2_text = (
        "Depois de completar <b>duas linhas</b> na cartela, horizontais, verticais ou diagonais, "
        "a equipe escolhe <b>uma delas</b> e explica "
        "<b>três conceitos</b> dessa linha.<br/>"
        "As duas linhas podem se cruzar. "
        "Ao menos uma das respostas deve ligar o conceito à fé usando: <b>Gn 1,27</b>, <b>Mt 25,40</b> ou <b>CEC 1931-1940</b>."
    )
    flow_html(sec2_text, body_style, 2.5 * mm)

    # --- Section 3: BOA RESPOSTA ---
    # Draw a warm-neutral rounded panel at the bottom for Boa Resposta
    panel_h = 16.5 * mm
    panel_y = y + pad_y
    c.setFillColor(GUIDE["surface_alt"])
    c.roundRect(x + pad_x, panel_y, content_w, panel_h, 1.4 * mm, stroke=0, fill=1)
    
    # Text inside panel
    panel_style = pstyle("TeamRulePanelBody", 7.2, 8.8, font=FONTS["sans"], color=GUIDE["dark"])
    panel_text = (
        "<b>Boa resposta:</b> explique o conceito com suas palavras. Pode usar um exemplo simples, "
        "mas não precisa lembrar o caso exato. O centro livre conta para fechar linha, mas não conta como conceito."
    )
    draw_html_para(c, panel_text, panel_style, x + pad_x + 3.0 * mm, panel_y + 2.5 * mm, content_w - 6.0 * mm, panel_h - 4.5 * mm, valign="middle")
    
    c.restoreState()


def bullet_list(items: Iterable[str], style: ParagraphStyle, *, bullet_color=PALETTE["gold"]) -> ListFlowable:
    return ListFlowable(
        [
            ListItem(para(item, style), leftIndent=9, bulletColor=bullet_color)
            for item in items
        ],
        bulletType="bullet",
        start="circle",
        leftIndent=9,
        bulletFontName=FONTS["sans_bold"],
        bulletFontSize=5.5,
    )


class CallFlowDiagram(Flowable):
    def __init__(self, width: float):
        super().__init__()
        self.width = width
        self.height = 56 * mm

    def wrap(self, availWidth, availHeight):
        self.width = min(self.width, availWidth)
        return self.width, self.height

    def _arrow(self, c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float, *, opacity: float = 0.62) -> None:
        c.setStrokeColor(alpha(GUIDE["dark"], opacity * 0.75))
        c.setFillColor(alpha(GUIDE["dark"], opacity * 0.75))
        c.setLineWidth(0.5)
        c.line(x1, y1, x2, y2)
        size = 2.2 * mm
        if abs(x2 - x1) >= abs(y2 - y1):
            direction = 1 if x2 >= x1 else -1
            p = c.beginPath()
            p.moveTo(x2, y2)
            p.lineTo(x2 - direction * size, y2 + size * 0.55)
            p.lineTo(x2 - direction * size, y2 - size * 0.55)
            p.close()
            c.drawPath(p, stroke=0, fill=1)
        else:
            direction = 1 if y2 >= y1 else -1
            p = c.beginPath()
            p.moveTo(x2, y2)
            p.lineTo(x2 + size * 0.55, y2 - direction * size)
            p.lineTo(x2 - size * 0.55, y2 - direction * size)
            p.close()
            c.drawPath(p, stroke=0, fill=1)

    def _tag(self, c: canvas.Canvas, text: str, x: float, y: float) -> None:
        t = c.beginText(x, y)
        t.setFont(FONTS["label"], 4.5)
        t.setFillColor(GUIDE["muted"])
        t.setCharSpace(0.7)
        t.textOut(text)
        c.drawText(t)

    def _step_number(self, c: canvas.Canvas, num: int, cx: float, cy: float) -> None:
        r = 3.8 * mm
        c.setFillColor(alpha(PALETTE["petrol"], 0.12))
        c.circle(cx, cy, r, stroke=0, fill=1)
        c.setFillColor(PALETTE["petrol"])
        c.setFont(FONTS["sans_bold"], 7.5)
        c.drawCentredString(cx, cy - 2.6, str(num))

    def _station(
        self,
        c: canvas.Canvas,
        x: float,
        y: float,
        width: float,
        height: float,
        *,
        tag: str,
        title: str,
        subtitle: str,
        step: int = 0,
    ) -> None:
        c.saveState()
        c.setFillColor(GUIDE["surface"])
        c.setStrokeColor(GUIDE["line"])
        c.setLineWidth(0.32)
        c.roundRect(x, y, width, height, 1.7 * mm, stroke=1, fill=1)

        self._tag(c, tag, x + 4.5 * mm, y + height - 4.6 * mm)
        c.setFillColor(GUIDE["dark"])
        c.setFont(FONTS["serif_bold"], 9.5)
        c.drawString(x + 4.5 * mm, y + 6.5 * mm, title)
        c.setFillColor(GUIDE["muted"])
        c.setFont(FONTS["sans"], 5.6)
        c.drawString(x + 4.5 * mm, y + 2.8 * mm, subtitle)
        c.restoreState()

    def draw(self):
        c = self.canv
        w = self.width
        h = self.height
        c.saveState()

        c.setFillColor(GUIDE["surface_alt"])
        c.roundRect(0, 0, w, h, 2.5 * mm, stroke=0, fill=1)

        self._tag(c, "CICLO DE CONDUÇÃO", 6 * mm, h - 6.5 * mm)

        pad_x = 8.0 * mm
        node_w = 54.0 * mm
        node_h = 16.0 * mm
        top_y = h - 27.0 * mm
        bottom_y = 6.0 * mm
        left_x = pad_x
        right_x = w - pad_x - node_w

        self._station(
            c,
            left_x,
            top_y,
            node_w,
            node_h,
            tag="CHAMAR",
            title="Código",
            subtitle="e conceito",
            step=1,
        )
        self._station(
            c,
            right_x,
            top_y,
            node_w,
            node_h,
            tag="SITUAR",
            title="Caso",
            subtitle="cena concreta",
            step=2,
        )
        self._station(
            c,
            right_x,
            bottom_y,
            node_w,
            node_h,
            tag="EXPLICAR",
            title="Explicação",
            subtitle="chave de leitura",
            step=3,
        )
        self._station(
            c,
            left_x,
            bottom_y,
            node_w,
            node_h,
            tag="MARCAR",
            title="Marcação",
            subtitle="após a explicação",
            step=4,
        )

        top_mid = top_y + node_h / 2
        bottom_mid = bottom_y + node_h / 2
        left_mid = left_x + node_w / 2
        right_mid = right_x + node_w / 2
        gap = 3.2 * mm
        self._arrow(c, left_x + node_w + gap, top_mid, right_x - gap, top_mid)
        self._arrow(c, right_mid, top_y - 1.4 * mm, right_mid, bottom_y + node_h + 1.4 * mm)
        self._arrow(c, right_x - gap, bottom_mid, left_x + node_w + gap, bottom_mid)
        self._arrow(c, left_mid, bottom_y + node_h + 1.4 * mm, left_mid, top_y - 1.4 * mm)

        c.restoreState()


def guide_styles() -> dict[str, ParagraphStyle]:
    return {
        "title": pstyle("GuideTitle", 27.5, 30.0, font=FONTS["serif_bold"], color=GUIDE["dark"], space_before=1, space_after=3),
        "subtitle": pstyle("GuideSubtitle", 9.8, 12.6, color=GUIDE["muted"], space_after=8),
        "kicker": pstyle("GuideKicker", 6.0, 7.5, font=FONTS["label"], color=GUIDE["muted"], space_after=3, char_space=1.2),
        "h1": pstyle("GuideH1", 13.6, 16.2, font=FONTS["serif_bold"], color=GUIDE["ink"], space_before=4, space_after=4),
        "h2": pstyle("GuideH2", 9.0, 11.0, font=FONTS["sans_bold"], color=GUIDE["ink"], space_before=2, space_after=2),
        "body": pstyle("GuideBody", 8.7, 11.8, font=FONTS["serif"], color=GUIDE["ink"], space_after=3),
        "small": pstyle("GuideSmall", 7.25, 9.4, font=FONTS["sans"], color=GUIDE["muted"], space_after=2),
        "card_label": pstyle("GuideCardLabel", 5.25, 6.3, font=FONTS["label"], color=GUIDE["muted"], char_space=0.9),
        "card_title": pstyle("GuideCardTitle", 9.7, 11.2, font=FONTS["serif_bold"], color=GUIDE["dark"], space_after=1.5),
        "card_body": pstyle("GuideCardBody", 7.65, 9.9, font=FONTS["serif"], color=GUIDE["ink"], space_after=0),
        "table_head": pstyle("GuideTableHead", 6.2, 7.4, font=FONTS["label"], color=GUIDE["surface"], char_space=0.6),
        "table_cell": pstyle("GuideTableCell", 7.45, 9.35, font=FONTS["serif"], color=GUIDE["ink"]),
        "step_num": pstyle("GuideStepNum", 6.5, 7.8, font=FONTS["label"], color=GUIDE["dark"], alignment=TA_CENTER),
        "quote": pstyle(
            "GuideQuote",
            9.2,
            12.8,
            font=FONTS["serif"],
            color=GUIDE["ink"],
            space_after=0,
        ),
    }


def guide_header_footer(c: canvas.Canvas, doc) -> None:
    c.saveState()
    c.setFillColor(GUIDE["background"])
    c.rect(0, 0, A4_W, A4_H, stroke=0, fill=1)

    text_obj = c.beginText(doc.leftMargin, A4_H - 9.2 * mm)
    text_obj.setFont(FONTS["label"], 5.8)
    text_obj.setFillColor(GUIDE["muted"])
    text_obj.setCharSpace(1.6)
    text_obj.textOut("BINGO - GUIA DE CONDUÇÃO")
    c.drawText(text_obj)

    c.setFillColor(GUIDE["muted"])
    c.setFont(FONTS["sans"], 6.2)
    c.drawRightString(A4_W - doc.rightMargin, 8.0 * mm, str(doc.page))
    c.restoreState()


def guide_band(title: str, body: str, width: float, styles: dict[str, ParagraphStyle], *, accent=PALETTE["petrol"]) -> Table:
    table = Table(
        [
            [para(title.upper(), styles["card_label"])],
            [rich_para(body, styles["quote"])],
        ],
        colWidths=[width],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GUIDE["surface"]),
                ("BOX", (0, 0), (-1, -1), 0.25, GUIDE["line_soft"]),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
                ("TOPPADDING", (0, 1), (-1, 1), 1),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 7),
            ]
        )
    )
    return table


def guide_card(
    title: str,
    body: str,
    width: float,
    styles: dict[str, ParagraphStyle],
    *,
    label: str | None = None,
    height: float | None = None,
) -> Table:
    if label:
        rows = [
            [para(label.upper(), styles["card_label"])],
            [para(title, styles["card_title"])],
            [rich_para(body, styles["card_body"])],
        ]
    else:
        rows = [
            [para(title, styles["card_title"])],
            [rich_para(body, styles["card_body"])],
        ]
    row_heights = None
    if height:
        if label:
            label_h = 6.2 * mm
            title_h = 8.8 * mm
            body_h = max(10 * mm, height - label_h - title_h)
            row_heights = [label_h, title_h, body_h]
        else:
            title_h = 10.5 * mm
            body_h = max(11 * mm, height - title_h)
            row_heights = [title_h, body_h]
    table = Table(rows, colWidths=[width], rowHeights=row_heights, hAlign="LEFT")
    cmds = [
        ("BACKGROUND", (0, 0), (-1, -1), GUIDE["surface"]),
        ("BOX", (0, 0), (-1, -1), 0.25, GUIDE["line_soft"]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (0, 0), 2.0),
    ]
    table.setStyle(TableStyle(cmds))
    return table


def guide_card_grid(
    cards: list[tuple[str, str, str | None]],
    width: float,
    styles: dict[str, ParagraphStyle],
    *,
    columns: int = 2,
    card_height: float | None = None,
) -> Table:
    gutter = 5.0 * mm
    col_w = (width - gutter * (columns - 1)) / columns
    rows = []
    row_heights = []
    for i in range(0, len(cards), columns):
        row = []
        chunk = cards[i : i + columns]
        for index, item in enumerate(chunk):
            title, body, label = item
            row.append(guide_card(title, body, col_w, styles, label=label, height=card_height))
            if index < columns - 1:
                row.append("")
        while len(chunk) < columns:
            if row:
                row.append("")
            row.append("")
            chunk.append(("", "", None))
        rows.append(row)
        row_heights.append(card_height)
        if i + columns < len(cards):
            rows.append([""] * (columns * 2 - 1))
            row_heights.append(gutter)
    col_widths = []
    for index in range(columns):
        col_widths.append(col_w)
        if index < columns - 1:
            col_widths.append(gutter)
    table = Table(rows, colWidths=col_widths, rowHeights=row_heights if card_height else None, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("BACKGROUND", (0, 0), (-1, -1), GUIDE["background"]),
            ]
        )
    )
    return table


def guide_steps_table(width: float, styles: dict[str, ParagraphStyle]) -> Table:
    rows = [
        [
            para("1", styles["step_num"]),
            rich_para("**Chamar**\nAnuncie código e conceito com voz clara.", styles["table_cell"]),
        ],
        [
            para("2", styles["step_num"]),
            rich_para("**Situar**\nLeia o caso como cena concreta, sem transformar em sermão.", styles["table_cell"]),
        ],
        [
            para("3", styles["step_num"]),
            rich_para("**Explicar**\nUse a Leitura do caso para mostrar o erro, o critério cristão e a resposta moral.", styles["table_cell"]),
        ],
        [
            para("4", styles["step_num"]),
            rich_para("**Marcar**\nDepois da explicação, autorize as equipes a marcar o código sorteado.", styles["table_cell"]),
        ],
    ]
    table = Table(rows, colWidths=[11 * mm, width - 11 * mm], hAlign="LEFT")
    cmds = [
        ("BACKGROUND", (0, 0), (0, -1), GUIDE["surface_alt"]),
        ("BOX", (0, 0), (-1, -1), 0.25, GUIDE["line_soft"]),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, GUIDE["line_soft"]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    # Row-striping on content column
    for i in range(len(rows)):
        bg = GUIDE["surface"] if i % 2 == 0 else GUIDE["background"]
        cmds.append(("BACKGROUND", (1, i), (1, i), bg))
    table.setStyle(TableStyle(cmds))
    return table


def guide_timeline_table(width: float, styles: dict[str, ParagraphStyle]) -> Table:
    rows = [["Tempo", "Ação", "Critério"]]
    rows.extend(
        [
            ["5 min", "Abertura", "Gn 1,26-27 e Mt 25,40 como chave do encontro."],
            ["3 min", "Regras", "Explicar cartela, chamada, marcação e validação."],
            ["20-25 min", "Rodada principal", "Chamadas de 30 a 45 segundos, com ritmo firme."],
            ["5 min", "Conferência", "A equipe explica três conceitos de uma linha fechada."],
            ["5 min", "Fechamento", "Retomar dignidade, caridade, reparação e convivência."],
        ]
    )
    table = Table(rows, colWidths=[22 * mm, 39 * mm, width - 61 * mm], hAlign="LEFT")
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), GUIDE["dark"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), GUIDE["surface"]),
        ("FONTNAME", (0, 0), (-1, 0), FONTS["label"]),
        ("FONTSIZE", (0, 0), (-1, 0), 6.5),
        ("FONTNAME", (0, 1), (-1, -1), FONTS["serif"]),
        ("FONTSIZE", (0, 1), (-1, -1), 7.4),
        ("LEADING", (0, 1), (-1, -1), 9.2),
        ("BOX", (0, 0), (-1, -1), 0.25, GUIDE["line_soft"]),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, GUIDE["line_soft"]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    # Row-striping + tempo column highlight
    for i in range(1, len(rows)):
        bg = GUIDE["surface"] if i % 2 == 1 else GUIDE["background"]
        commands.append(("BACKGROUND", (1, i), (-1, i), bg))
        commands.append(("BACKGROUND", (0, i), (0, i), GUIDE["surface_alt"]))
    table.setStyle(TableStyle(commands))
    return table


def guide_column_table(terms_data: dict, width: float, styles: dict[str, ParagraphStyle]) -> Table:
    rows = [[para("COL.", styles["table_head"]), para("CAMPO", styles["table_head"]), para("FUNÇÃO NO JOGO", styles["table_head"])]]
    for col in terms_data["columns"]:
        rows.append(
            [
                para(col["key"], styles["card_title"]),
                para(col["title"], styles["table_cell"]),
                para(col["function"], styles["table_cell"]),
            ]
        )
    table = Table(rows, colWidths=[14 * mm, 42 * mm, width - 56 * mm], hAlign="LEFT")
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), GUIDE["dark"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), GUIDE["surface"]),
        ("BOX", (0, 0), (-1, -1), 0.25, GUIDE["line_soft"]),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, GUIDE["line_soft"]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 1), (0, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for row_index, col in enumerate(terms_data["columns"], start=1):
        commands.append(("BACKGROUND", (0, row_index), (0, row_index), GUIDE["surface_alt"]))
        bg = GUIDE["surface"] if row_index % 2 == 1 else GUIDE["background"]
        commands.append(("BACKGROUND", (1, row_index), (-1, row_index), bg))
    table.setStyle(TableStyle(commands))
    return table


def build_facilitator_guide(terms_data: dict, calls_data: dict) -> Path:
    path = OUT_DIR / "guia_conducao_bingo.pdf"
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title=f"Guia de condução — {PROJECT_TITLE}",
    )
    styles = guide_styles()
    story = []
    frame_w = doc.width

    story.append(Paragraph("Guia de condução", styles["title"]))
    story.append(Paragraph(f"{PROJECT_TITLE} · {MEETING_LABEL}", styles["subtitle"]))
    story.append(
        guide_band(
            "Critério central",
            CORE_MESSAGE.replace("igual dignidade diante de Deus", "**igual dignidade diante de Deus**"),
            frame_w,
            styles,
        )
    )
    story.append(Spacer(1, 3.5 * mm))
    story.append(
        guide_card_grid(
            [
                ("Equipes", "Entregue **uma cartela por equipe**, não por pessoa. A conversa interna ajuda a fixar os conceitos.", "Formato"),
                ("Baralho", "Use as **75 cartas de chamada**. Em cada rodada, sorteie uma carta e conduza o ciclo completo.", "Material"),
                ("Vitória", "A equipe só pede conferência depois de fechar **duas linhas** válidas: horizontais, verticais ou diagonais.", "Condição"),
                ("Catequese", "A vitória depende de explicar **três conceitos** de uma linha fechada, com critério cristão.", "Validação"),
            ],
            frame_w,
            styles,
            columns=2,
            card_height=30 * mm,
        )
    )
    story.append(Spacer(1, 5 * mm))
    story.append(CallFlowDiagram(frame_w))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Preparação", styles["h1"]))
    story.append(
        guide_card_grid(
            [
                ("Antes da turma entrar", "Separe cartelas, baralho, folha de controle e cartões de regras. Embaralhe o baralho somente quando for começar.", "Checklist"),
                ("Ao distribuir", "Explique que cada equipe marca apenas o **código chamado**. O centro livre já conta para fechar linha, mas não substitui um conceito da linha escolhida.", "Regra"),
            ],
            frame_w,
            styles,
            columns=2,
            card_height=30 * mm,
        )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(
        guide_band(
            "Regra de ritmo",
            "Não transforme cada chamada em debate. A explicação comum deve durar **30 a 45 segundos**; a discussão mais exigente entra na conferência da vitória.",
            frame_w,
            styles,
        )
    )

    story.append(PageBreak())
    story.append(Paragraph("Condução da rodada", styles["h1"]))
    story.append(Paragraph("A sequência da chamada mantém o jogo claro: conceito, caso, explicação breve e tempo de marcação.", styles["subtitle"]))
    story.append(guide_steps_table(frame_w, styles))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("Validação da vitória", styles["h1"]))
    story.append(
        guide_card_grid(
            [
                ("1. Conferir códigos", "Verifique se todos os códigos das linhas fechadas realmente foram chamados na folha de controle.", None),
                ("2. Escolher uma linha", "A equipe escolhe **uma** das linhas fechadas para a conferência. As duas linhas podem se cruzar; não precisa explicar as duas.", None),
                ("3. Explicar conceitos", "A equipe explica pelo menos **três conceitos da linha escolhida**. A resposta deve mostrar compreensão, não memória literal do caso.", None),
                ("4. Amarrar à fé", "Ao menos uma explicação deve ligar o jogo a **Gn 1,27**, **Mt 25,40** ou **CEC 1931-1940**.", None),
            ],
            frame_w,
            styles,
            columns=2,
            card_height=29 * mm,
        )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(
        guide_band(
            "Se a explicação falhar",
            "Dê uma segunda tentativa curta. Se a resposta continuar vazia ou confusa, a vitória fica suspensa e o jogo segue.",
            frame_w,
            styles,
        )
    )
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("Ritmo recomendado", styles["h1"]))
    story.append(guide_timeline_table(frame_w, styles))

    story.append(PageBreak())
    story.append(Paragraph("Falas de condução", styles["h1"]))
    story.append(Paragraph("Textos curtos para abrir o jogo, explicar a regra, conferir a vitória e fechar o encontro sem alongar a condução.", styles["body"]))
    story.append(Spacer(1, 2 * mm))
    story.append(
        guide_card_grid(
            [
                (
                    "Abertura",
                    "Hoje a cartela não traz palavras para decorar. Ela traz critérios para enxergar situações reais: fundamentos da fé, injustiças, desculpas falsas, discernimentos e respostas concretas.",
                    "Script",
                ),
                (
                    "Regra do jogo",
                    "A cada rodada, eu sorteio uma carta, anuncio o código e o conceito, leio o caso, explico a ligação e só então vocês marcam o código, se ele estiver na cartela.",
                    "Script",
                ),
                (
                    "Conferência",
                    "Quando uma equipe fechar duas linhas horizontais, verticais ou diagonais, ela escolhe uma delas e explica três conceitos dessa linha. O centro livre ajuda a fechar, mas não conta como conceito explicado.",
                    "Script",
                ),
                (
                    "Fechamento",
                    CORE_MESSAGE,
                    "Script",
                ),
            ],
            frame_w,
            styles,
            columns=2,
            card_height=36 * mm,
        )
    )
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("Arquitetura das colunas", styles["h1"]))
    story.append(guide_column_table(terms_data, frame_w, styles))
    story.append(Spacer(1, 4 * mm))
    story.append(
        guide_band(
            "Segurança pastoral",
            "Não peça relatos pessoais e não use nomes reais. Se aparecer relato sério de ameaça, agressão, exposição de imagem ou violência continuada, acolha com discrição e encaminhe à coordenação e aos responsáveis.",
            frame_w,
            styles,
        )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Uso das cartas", styles["h1"]))
    story.append(
        guide_card_grid(
            [
                (
                    "Regra de jogo",
                    calls_data["method"]["rule"],
                    "Rodada",
                ),
                (
                    "Regra de conferência",
                    calls_data["method"]["conference_rule"],
                    "Vitória",
                ),
            ],
            frame_w,
            styles,
            columns=2,
            card_height=43 * mm,
        )
    )
    story.append(Spacer(1, 1.5 * mm))
    story.append(Paragraph("A seção \"Leitura do caso\" é apoio do catequista: durante a rodada, use-a para uma explicação curta; na conferência, use-a para exigir respostas mais precisas.", styles["small"]))

    doc.build(story, onFirstPage=guide_header_footer, onLaterPages=guide_header_footer)
    return path


def explanation_styles() -> dict[str, ParagraphStyle]:
    return {
        "title": pstyle("ExplanationTitle", 25.5, 29.0, font=FONTS["serif_bold"], color=GUIDE["dark"], space_after=7),
        "subtitle": pstyle("ExplanationSubtitle", 9.8, 13.0, font=FONTS["sans"], color=GUIDE["muted"], space_after=10),
        "h1": pstyle("ExplanationH1", 13.0, 16.0, font=FONTS["serif_bold"], color=GUIDE["ink"], space_before=12, space_after=6),
        "body": pstyle("ExplanationBody", 8.9, 12.2, font=FONTS["serif"], color=GUIDE["ink"], space_after=4),
        "small": pstyle("ExplanationSmall", 7.2, 9.6, font=FONTS["sans"], color=GUIDE["muted"], space_after=3),
        "section": pstyle("ExplanationSection", 7.1, 8.6, font=FONTS["label"], color=GUIDE["dark"], space_after=0, char_space=1.2),
        "entry_code": pstyle("ExplanationCode", 6.8, 8.0, font=FONTS["label"], color=GUIDE["dark"], alignment=TA_CENTER),
        "entry_title": pstyle("ExplanationEntryTitle", 8.5, 10.0, font=FONTS["serif_bold"], color=GUIDE["dark"], space_after=1),
        "entry_body": pstyle("ExplanationEntryBody", 7.25, 9.45, font=FONTS["serif"], color=GUIDE["ink"], space_after=1.5),
        "entry_meta": pstyle("ExplanationEntryMeta", 5.9, 7.2, font=FONTS["sans"], color=GUIDE["muted"], space_after=0),
    }


def explanation_header_footer(c: canvas.Canvas, doc) -> None:
    c.saveState()
    c.setFillColor(GUIDE["background"])
    c.rect(0, 0, A4_W, A4_H, stroke=0, fill=1)

    text_obj = c.beginText(doc.leftMargin, A4_H - 9.4 * mm)
    text_obj.setFont(FONTS["label"], 5.8)
    text_obj.setFillColor(GUIDE["muted"])
    text_obj.setCharSpace(1.6)
    text_obj.textOut("BINGO - CARTA DE EXPLICAÇÕES")
    c.drawText(text_obj)

    c.setFillColor(GUIDE["muted"])
    c.setFont(FONTS["sans"], 6.2)
    c.drawRightString(A4_W - doc.rightMargin, 8.0 * mm, str(doc.page))
    c.restoreState()


def explanation_section_block(col: str, width: float, styles: dict[str, ParagraphStyle]) -> KeepTogether:
    label = f"{col} · {COLUMN_FULL_TITLES[col].upper()}"
    table = Table([[para(label, styles["section"])]], colWidths=[width])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GUIDE["surface_alt"]),
                ("BOX", (0, 0), (-1, -1), 0.25, GUIDE["line_soft"]),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 3.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ]
        )
    )
    return KeepTogether([Spacer(1, 2.8 * mm), table, Spacer(1, 2.0 * mm)])


def explanation_entry_block(
    call: dict,
    term: dict,
    explanation: str,
    width: float,
    styles: dict[str, ParagraphStyle],
) -> KeepTogether:
    anchors = " · ".join(call["anchors"])
    table = Table(
        [
            [para(call["id"], styles["entry_code"]), para(term["label"], styles["entry_title"])],
            ["", rich_para(explanation, styles["entry_body"])],
            ["", para(anchors, styles["entry_meta"])],
        ],
        colWidths=[11.5 * mm, width - 11.5 * mm],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GUIDE["surface"]),
                ("BOX", (0, 0), (-1, -1), 0.25, GUIDE["line_soft"]),
                ("SPAN", (0, 0), (0, 2)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (0, 2), GUIDE["surface_alt"]),
                ("LINEAFTER", (0, 0), (0, 2), 0.25, GUIDE["line_soft"]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
                ("TOPPADDING", (0, 0), (-1, -1), 3.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ]
        )
    )
    return KeepTogether([table, Spacer(1, 2.3 * mm)])


def build_explanations_letter(terms: list[dict], calls: list[dict], explanations_data: dict) -> Path:
    path = OUT_DIR / "carta_explicacoes_catequista.pdf"
    term_lookup = {term["id"]: term for term in terms}
    explanation_lookup = {entry["id"]: entry["explanation"] for entry in explanations_data["entries"]}

    margin_x = 15 * mm
    margin_top = 17 * mm
    margin_bottom = 15 * mm
    frame_h = A4_H - margin_top - margin_bottom
    frame_y = margin_bottom
    frame_w = A4_W - 2 * margin_x
    gutter = 6 * mm
    col_w = (frame_w - gutter) / 2

    doc = BaseDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=margin_x,
        rightMargin=margin_x,
        topMargin=margin_top,
        bottomMargin=margin_bottom,
        title=f"Carta de explicações rápidas — {PROJECT_TITLE}",
    )
    intro_frame = Frame(margin_x, frame_y, frame_w, frame_h, id="intro")
    left_frame = Frame(margin_x, frame_y, col_w, frame_h, id="left")
    right_frame = Frame(margin_x + col_w + gutter, frame_y, col_w, frame_h, id="right")
    doc.addPageTemplates(
        [
            PageTemplate(id="Intro", frames=[intro_frame], onPage=explanation_header_footer),
            PageTemplate(id="Entries", frames=[left_frame, right_frame], onPage=explanation_header_footer),
        ]
    )

    styles = explanation_styles()
    story = []

    story.append(Paragraph("Carta de explicações rápidas", styles["title"]))
    story.append(Paragraph("Apoio objetivo para conduzir o baralho de chamadas com clareza, ritmo e unidade conceitual.", styles["subtitle"]))
    story.append(CallFlowDiagram(frame_w))
    story.append(Spacer(1, 5 * mm))

    story.append(Paragraph("Como usar", styles["h1"]))
    story.append(
        bullet_list(
            [
                "Sorteie a carta, anuncie o código e o conceito.",
                "Leia o caso do baralho de chamadas.",
                "Use a explicação do código como apoio para uma fala de 20 a 40 segundos.",
                "Depois dê alguns segundos para marcação e siga a rodada.",
                "Na conferência, volte à explicação e à pergunta da carta para validar a linha.",
            ],
            styles["body"],
            bullet_color=GUIDE["dark"],
        )
    )

    story.append(Paragraph("Mapa rápido", styles["h1"]))
    header_style = pstyle("IndexHeader", 6.8, 8.5, font=FONTS["label"], color=GUIDE["surface"], char_space=1.2)
    index_code_style = pstyle("IndexCode", 7.2, 9.0, font=FONTS["sans_bold"], color=GUIDE["dark"])
    index_title_style = pstyle("IndexTitle", 7.2, 9.0, font=FONTS["sans_bold"], color=GUIDE["ink"])
    index_desc_style = pstyle("IndexDesc", 7.2, 9.0, font=FONTS["sans"], color=GUIDE["ink"])
    
    index_rows = [[para("Código", header_style), para("Bloco", header_style), para("Função didática", header_style)]]
    for col in COLUMN_ORDER:
        index_rows.append(
            [
                para(f"{col}01-{col}15", index_code_style),
                para(COLUMN_FULL_TITLES[col], index_title_style),
                para(COLUMN_SHORT_FUNCTIONS[col], index_desc_style),
            ]
        )
    index_table = Table(index_rows, colWidths=[25 * mm, 43 * mm, frame_w - 68 * mm], hAlign="LEFT")
    index_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), GUIDE["dark"]),
                ("BACKGROUND", (0, 1), (-1, -1), GUIDE["surface"]),
                ("GRID", (0, 0), (-1, -1), 0.25, GUIDE["line_soft"]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(index_table)

    story.append(NextPageTemplate("Entries"))
    story.append(PageBreak())

    calls_by_column = {
        col: [call for call in calls if term_lookup[call["term_id"]]["column"] == col]
        for col in COLUMN_ORDER
    }
    for col in COLUMN_ORDER:
        story.append(explanation_section_block(col, col_w, styles))
        for call in calls_by_column[col]:
            term = term_lookup[call["term_id"]]
            story.append(explanation_entry_block(call, term, explanation_lookup[call["id"]], col_w, styles))

    doc.build(story)
    return path


def merge_pdfs(paths: list[Path]) -> Path:
    out = OUT_DIR / f"kit_impressao_{OUTPUT_SLUG}.pdf"
    writer = PdfWriter()
    for path in paths:
        reader = PdfReader(str(path))
        for page in reader.pages:
            writer.add_page(page)
    with out.open("wb") as fh:
        writer.write(fh)
    return out


def render_previews(paths: list[Path]) -> None:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    for old in PREVIEW_DIR.glob("*.png"):
        old.unlink()
    for path in paths:
        doc = fitz.open(path)
        if path.stem in {"cartelas_bingo_24_a4", "baralho_chamadas_a4"}:
            pages = [0, min(1, len(doc) - 1), len(doc) - 1]
        else:
            pages = [0, len(doc) - 1]
        for page_index in sorted(set(pages)):
            pix = doc[page_index].get_pixmap(matrix=fitz.Matrix(1.7, 1.7), alpha=False)
            pix.save(PREVIEW_DIR / f"{path.stem}_p{page_index + 1:02d}.png")
        doc.close()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    terms_data, calls_data, terms, calls = load_project_data()
    explanations_data = load_explanations_data()

    cards = generate_bingo_cards(terms)
    manifest = build_cards_manifest(terms_data, cards)
    cartelas = build_bingo_cards(cards)
    chamadas = build_call_deck(terms, calls)
    explicacoes = build_explanations_letter(terms, calls, explanations_data)
    regras = build_team_rule_cards()
    controle = build_control_sheet(terms)
    guia = build_facilitator_guide(terms_data, calls_data)
    kit = merge_pdfs([cartelas, chamadas, explicacoes, regras, controle, guia])
    render_previews([cartelas, chamadas, explicacoes, regras, controle, guia, kit])

    for path in [manifest, cartelas, chamadas, explicacoes, regras, controle, guia, kit]:
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
