from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path


PWA_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PWA_ROOT.parent
CONFIG_PATH = PWA_ROOT / "pwa.config.json"
SRC_DATA = PWA_ROOT / "src" / "data"
OUT_PATH = SRC_DATA / "game-data.json"
PUBLIC_DIR = PWA_ROOT / "public"
MATERIALS_DIR = PUBLIC_DIR / "materials"

DEFAULT_CONFIG = {
    "contentProject": "bingos_crisma_i_01_35/encontro_04_bingo_violencia_discriminacao",
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def display_subtitle(title: str) -> str:
    return re.sub(r"^bingo\s*[-—]\s*", "", title, flags=re.IGNORECASE).strip() or title


def encounter_number_from_path(path: Path) -> str:
    match = re.search(r"encontro_(\d{2})_", path.name)
    if not match:
        raise SystemExit(f"Could not infer encounter number from directory name: {path.name}")
    return match.group(1)


def load_config() -> dict:
    config = dict(DEFAULT_CONFIG)
    if CONFIG_PATH.exists():
        config.update(load_json(CONFIG_PATH))

    content_override = os.environ.get("BINGO_CONTENT_DIR")
    if content_override:
        config["contentProject"] = content_override
    return config


def resolve_from_repo(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def resolve_encounter_dir(config: dict) -> Path:
    content_project = config["contentProject"]
    encounter_dir = resolve_from_repo(content_project)
    if not encounter_dir.exists():
        raise SystemExit(f"Content project directory not found: {encounter_dir}")
    return encounter_dir


def load_project_data(data_dir: Path) -> tuple[dict, dict, list[dict], list[dict]]:
    terms_data = load_json(data_dir / "termos.json")
    calls_data = load_json(data_dir / "chamadas.json")
    return terms_data, calls_data, terms_data["terms"], calls_data["cards"]


def load_explanations_data(data_dir: Path) -> dict:
    return load_json(data_dir / "explicacoes.json")


def load_cartelas_manifest(encounter_dir: Path) -> dict:
    manifest_path = encounter_dir / "output" / "cartelas_manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"Missing canonical cartelas manifest: {manifest_path}")

    manifest = load_json(manifest_path)
    schema = manifest.get("schema")
    if schema != "bingo-catequese/cartelas-manifest.v1":
        raise SystemExit(f"Unsupported cartelas manifest schema in {manifest_path}: {schema}")
    return manifest


def default_materials(manifest: dict) -> list[dict]:
    return [
        {
            "title": "Cartelas",
            "meta": "24 cartelas em A4",
            "source": "output/pdf/cartelas_bingo_24_a4.pdf",
            "fileName": "cartelas_bingo_24_a4.pdf",
            "recommended": True,
        },
        {
            "title": "Kit completo",
            "meta": "guia, cartas e controles",
            "source": "output/pdf/kit_impressao_{output_slug}.pdf",
            "fileName": "kit_impressao_{output_slug}.pdf",
        },
    ]


def format_material_value(value: str, context: dict[str, str]) -> str:
    return value.format(**context)


def public_material_href(file_name: str) -> str:
    return f"./materials/{file_name}"


def publish_materials(config: dict, encounter_dir: Path, manifest: dict) -> list[dict]:
    MATERIALS_DIR.mkdir(parents=True, exist_ok=True)
    for stale_file in MATERIALS_DIR.glob("*"):
        if stale_file.is_file():
            stale_file.unlink()

    context = {
        "output_slug": manifest["project"]["output_slug"],
        "card_set_id": manifest["card_set_id"],
    }
    published = []
    for material in config.get("materials") or default_materials(manifest):
        source = encounter_dir / format_material_value(material["source"], context)
        if not source.exists():
            raise SystemExit(f"Material not found: {source}")

        file_name = format_material_value(material.get("fileName") or source.name, context)
        destination = MATERIALS_DIR / file_name
        shutil.copy2(source, destination)
        published.append(
            {
                "title": material["title"],
                "meta": material.get("meta", ""),
                "href": public_material_href(file_name),
                "fileName": file_name,
                "recommended": bool(material.get("recommended", False)),
            }
        )
    return published


def markdown_inline_text(text: str) -> str:
    return text.strip()


def parse_teaching_markdown(text: str) -> dict:
    title = ""
    meta = []
    sections = []
    current_section = None
    current_paragraph: list[str] = []

    def flush_paragraph() -> None:
        nonlocal current_paragraph
        if current_section is not None and current_paragraph:
            current_section["paragraphs"].append(" ".join(current_paragraph).strip())
        current_paragraph = []

    def flush_section() -> None:
        nonlocal current_section
        flush_paragraph()
        if current_section is not None:
            sections.append(current_section)
        current_section = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            continue
        if stripped == "---":
            flush_section()
            continue
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            continue
        meta_match = re.match(r"\*\*(.+?):\*\*\s*(.+)", stripped)
        if meta_match and current_section is None:
            meta.append({"label": meta_match.group(1).strip(), "value": meta_match.group(2).strip()})
            continue
        if not stripped.startswith(">"):
            continue

        quote = stripped[1:].strip()
        heading_match = re.fullmatch(r"\*\*(.+?)\*\*", quote)
        if heading_match:
            flush_section()
            current_section = {"title": heading_match.group(1).strip(), "paragraphs": []}
            continue

        if current_section is None:
            current_section = {"title": "Notas", "paragraphs": []}
        current_paragraph.append(markdown_inline_text(quote))

    flush_section()
    return {"title": title, "meta": meta, "sections": sections}


def publish_teaching_material(encounter_dir: Path) -> dict:
    encounter_number = encounter_number_from_path(encounter_dir)
    source_dir = encounter_dir / "material_didatico"
    source_pdf = source_dir / f"material_didatico_encontro_{encounter_number}.pdf"
    source_md = source_dir / f"material_didatico_encontro_{encounter_number}.md"

    if not source_pdf.exists():
        raise SystemExit(f"Missing teaching PDF: {source_pdf}")
    if not source_md.exists():
        raise SystemExit(f"Missing teaching Markdown: {source_md}")

    pdf_file_name = f"material_didatico_encontro_{encounter_number}.pdf"
    md_text = source_md.read_text(encoding="utf-8")
    shutil.copy2(source_pdf, MATERIALS_DIR / pdf_file_name)
    parsed = parse_teaching_markdown(md_text)

    return {
        "title": parsed["title"],
        "meta": parsed["meta"],
        "sections": parsed["sections"],
        "pdf": {
            "title": "Material didático",
            "meta": "PDF completo do encontro",
            "href": public_material_href(pdf_file_name),
            "fileName": pdf_file_name,
        },
    }


def pwa_cell_from_manifest(cell: dict, terms_by_id: dict[str, dict]) -> dict:
    if cell.get("free"):
        anchors = cell.get("anchors", [])
        return {
            "id": "FREE",
            "column": cell.get("column", "N"),
            "label": cell.get("label", "LIVRE"),
            "definition": " / ".join(anchors),
            "anchors": anchors,
            "free": True,
        }

    term_id = cell["id"]
    term = terms_by_id.get(term_id)
    if not term:
        raise SystemExit(f"Cartelas manifest references unknown term id: {term_id}")
    return {
        "id": term_id,
        "column": term.get("column", cell.get("column", "")),
        "label": term.get("label", cell.get("label", term_id)),
        "definition": term.get("definition", ""),
        "anchors": term.get("anchors", []),
    }


def boards_from_manifest(manifest: dict, terms_by_id: dict[str, dict]) -> list[dict]:
    return [
        {
            "id": card["id"],
            "number": card["number"],
            "termIds": card.get("term_ids", []),
            "grid": [
                [pwa_cell_from_manifest(cell, terms_by_id) for cell in row]
                for row in card["grid"]
            ],
        }
        for card in manifest["cards"]
    ]


def write_manifest(title: str) -> None:
    manifest = {
        "id": "/",
        "name": title.replace("—", "-"),
        "short_name": "Bingo",
        "description": f"PWA para conduzir {title}.",
        "lang": "pt-BR",
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "display_override": ["standalone", "minimal-ui"],
        "orientation": "portrait",
        "background_color": "#f4efe7",
        "theme_color": "#f4efe7",
        "categories": ["education", "games", "productivity"],
        "prefer_related_applications": False,
        "icons": [
            {"src": "./icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any"},
            {"src": "./icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "./icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "./icons/maskable-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
            {"src": "./icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
        "screenshots": [
            {
                "src": "./screenshots/iphone-portrait.png",
                "sizes": "1290x2796",
                "type": "image/png",
                "form_factor": "narrow",
                "label": "Tela principal do Bingo no iPhone",
            },
            {
                "src": "./screenshots/ipad-portrait.png",
                "sizes": "2048x2732",
                "type": "image/png",
                "form_factor": "wide",
                "label": "Tela principal do Bingo no iPad",
            },
        ],
        "shortcuts": [
            {
                "name": "Abrir Bingo",
                "short_name": "Abrir",
                "description": "Inicia o app do Bingo.",
                "url": "./",
                "icons": [{"src": "./icons/icon-192.png", "sizes": "192x192", "type": "image/png"}],
            }
        ],
    }
    write_json(PUBLIC_DIR / "manifest.webmanifest", manifest)


def main() -> None:
    config = load_config()
    encounter_dir = resolve_encounter_dir(config)
    data_dir = encounter_dir / "data"
    cartelas_manifest = load_cartelas_manifest(encounter_dir)
    manifest_project = cartelas_manifest["project"]
    slug = config.get("slug") or manifest_project["output_slug"]

    terms_data, calls_data, terms, calls = load_project_data(data_dir)
    explanations_data = load_explanations_data(data_dir)

    terms_by_id = {term["id"]: term for term in terms}
    explanations_by_id = {entry["id"]: entry["explanation"] for entry in explanations_data["entries"]}
    pwa_boards = boards_from_manifest(cartelas_manifest, terms_by_id)
    materials = publish_materials(config, encounter_dir, cartelas_manifest)
    teaching_material = publish_teaching_material(encounter_dir)

    call_cards = []
    for call in calls:
        term = terms_by_id[call["term_id"]]
        call_cards.append(
            {
                "id": call["id"],
                "termId": call["term_id"],
                "code": call["id"],
                "label": term["label"],
                "column": term["column"],
                "columnTitle": next(col["title"] for col in terms_data["columns"] if col["key"] == term["column"]),
                "definition": term["definition"],
                "case": call["case"],
                "readingPoints": call["reading_points"],
                "conferenceQuestion": call["conference_question"],
                "anchors": call["anchors"],
                "facilitatorNote": call["facilitator_note"],
                "explanation": explanations_by_id[call["id"]],
            }
        )

    title = manifest_project.get("title") or terms_data["title"]
    version = cartelas_manifest["card_set_id"]
    payload = {
        "version": version,
        "slug": slug,
        "cardSetId": cartelas_manifest["card_set_id"],
        "cardSetHash": cartelas_manifest["card_set_hash"],
        "title": title,
        "subtitle": display_subtitle(title),
        "meeting": manifest_project.get("meeting") or terms_data["meeting"],
        "meetingLabel": manifest_project.get("meeting_label"),
        "coreMessage": manifest_project.get("core_message"),
        "scripture": terms_data["scripture"],
        "catechism": terms_data["catechism"],
        "cardModel": terms_data["card_model"],
        "columns": terms_data["columns"],
        "lineModel": cartelas_manifest["line_model"],
        "printLayout": cartelas_manifest["print_layout"],
        "sourceHashes": cartelas_manifest["source_hashes"],
        "teachingMaterial": teaching_material,
        "method": calls_data["method"],
        "materials": materials,
        "cards": call_cards,
        "boards": pwa_boards,
    }

    write_json(OUT_PATH, payload)
    write_manifest(title)
    print(f"Generated {OUT_PATH.relative_to(PWA_ROOT)} from {encounter_dir.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
