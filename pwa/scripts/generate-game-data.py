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
CONTENT_DIR = PUBLIC_DIR / "content"

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


def resolve_collection_dir(config: dict, default_encounter_dir: Path) -> Path:
    collection_value = config.get("contentCollection")
    collection_dir = resolve_from_repo(collection_value) if collection_value else default_encounter_dir.parent
    if not collection_dir.exists():
        raise SystemExit(f"Content collection directory not found: {collection_dir}")
    return collection_dir


def relative_to_repo(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def discover_encounter_dirs(collection_dir: Path) -> list[Path]:
    return sorted(
        [path for path in collection_dir.iterdir() if path.is_dir() and re.match(r"encontro_\d{2}_bingo_", path.name)],
        key=lambda path: path.name,
    )


def reset_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


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


def public_material_href(file_name: str, href_base: str) -> str:
    return f"{href_base.rstrip('/')}/{file_name}"


def publish_materials(
    config: dict,
    encounter_dir: Path,
    manifest: dict,
    destination_dir: Path,
    href_base: str,
) -> list[dict]:
    destination_dir.mkdir(parents=True, exist_ok=True)

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
        destination = destination_dir / file_name
        shutil.copy2(source, destination)
        published.append(
            {
                "title": material["title"],
                "meta": material.get("meta", ""),
                "href": public_material_href(file_name, href_base),
                "fileName": file_name,
                "recommended": bool(material.get("recommended", False)),
            }
        )
    return published


def markdown_inline_text(text: str) -> str:
    return text.strip()


def catechism_items_from_paragraphs(paragraphs: list[str]) -> list[dict]:
    text = "\n".join(paragraphs)
    matches = list(re.finditer(r"\*\*(\d+[A-Za-z]?)\.\*\*\s*", text))
    items = []

    for index, match in enumerate(matches):
        next_match = matches[index + 1] if index + 1 < len(matches) else None
        body_start = match.end()
        body_end = next_match.start() if next_match else len(text)
        body = text[body_start:body_end].strip()
        if body:
            items.append({"number": match.group(1), "body": body})

    return items


def strip_markdown_emphasis(text: str) -> str:
    stripped = text.strip()
    strong_match = re.fullmatch(r"\*\*(.+?)\*\*", stripped)
    if strong_match:
        return strong_match.group(1).strip()
    emphasis_match = re.fullmatch(r"\*(.+?)\*", stripped)
    if emphasis_match:
        return emphasis_match.group(1).strip()
    return stripped


def scripture_verses_from_paragraphs(paragraphs: list[str]) -> list[dict]:
    text = " ".join(paragraphs[1:]).strip()
    matches = list(re.finditer(r"(?<!\S)(\d{1,3})\s+", text))
    verses = []

    for index, match in enumerate(matches):
        next_match = matches[index + 1] if index + 1 < len(matches) else None
        body_start = match.end()
        body_end = next_match.start() if next_match else len(text)
        body = text[body_start:body_end].strip()
        if body:
            verses.append({"number": match.group(1), "body": body})

    if not verses and text:
        verses.append({"body": text})
    return verses


def enrich_teaching_section(section: dict) -> dict:
    title = section.get("title", "")
    upper_title = title.upper()
    paragraphs = section.get("paragraphs", [])

    if "CATECISMO" in upper_title:
        items = catechism_items_from_paragraphs(paragraphs)
        if items:
            return {**section, "kind": "catechism", "items": items}

    if upper_title == "PALAVRA DE DEUS" and paragraphs:
        return {
            **section,
            "kind": "scripture",
            "reference": strip_markdown_emphasis(paragraphs[0]),
            "verses": scripture_verses_from_paragraphs(paragraphs),
        }

    if upper_title == "GUARDAR NO CORAÇÃO":
        return {**section, "kind": "memory"}

    if upper_title == "PARA REFLETIR":
        return {**section, "kind": "reflection"}

    return section


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
            sections.append(enrich_teaching_section(current_section))
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
        if not quote:
            flush_paragraph()
            continue

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


def publish_teaching_material(encounter_dir: Path, destination_dir: Path, href_base: str) -> dict:
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
    destination_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_pdf, destination_dir / pdf_file_name)
    parsed = parse_teaching_markdown(md_text)

    return {
        "title": parsed["title"],
        "meta": parsed["meta"],
        "sections": parsed["sections"],
        "pdf": teaching_material_option(pdf_file_name, href_base),
    }


def teaching_material_option(file_name: str, href_base: str) -> dict:
    return {
        "title": "Material didático",
        "meta": "PDF completo do encontro",
        "href": public_material_href(file_name, href_base),
        "fileName": file_name,
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


def build_payload(
    config: dict,
    encounter_dir: Path,
    material_destination_dir: Path,
    material_href_base: str,
    slug_override: str | None = None,
) -> dict:
    data_dir = encounter_dir / "data"
    cartelas_manifest = load_cartelas_manifest(encounter_dir)
    manifest_project = cartelas_manifest["project"]
    slug = slug_override or config.get("slug") or manifest_project["output_slug"]

    terms_data, calls_data, terms, calls = load_project_data(data_dir)
    explanations_data = load_explanations_data(data_dir)

    terms_by_id = {term["id"]: term for term in terms}
    explanations_by_id = {entry["id"]: entry["explanation"] for entry in explanations_data["entries"]}
    pwa_boards = boards_from_manifest(cartelas_manifest, terms_by_id)
    teaching_material = publish_teaching_material(encounter_dir, material_destination_dir, material_href_base)
    materials = publish_materials(config, encounter_dir, cartelas_manifest, material_destination_dir, material_href_base)
    teaching_pdf = teaching_material.pop("pdf", None)
    if teaching_pdf:
        materials.append(teaching_pdf)

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
    return {
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


def catalog_item(payload: dict, encounter_dir: Path, href: str) -> dict:
    return {
        "id": payload["slug"],
        "href": href,
        "title": payload["title"],
        "subtitle": payload["subtitle"],
        "meeting": payload["meeting"],
        "meetingLabel": payload.get("meetingLabel"),
        "coreMessage": payload.get("coreMessage"),
        "cardSetId": payload["cardSetId"],
        "encounterNumber": encounter_number_from_path(encounter_dir),
        "directory": relative_to_repo(encounter_dir),
        "boardCount": len(payload["boards"]),
        "cardCount": len(payload["cards"]),
    }


def write_content_catalog(config: dict, default_encounter_dir: Path, default_payload: dict) -> dict:
    collection_dir = resolve_collection_dir(config, default_encounter_dir)
    encounter_dirs = discover_encounter_dirs(collection_dir)
    if not encounter_dirs:
        raise SystemExit(f"No bingo encounter directories found in {collection_dir}")

    reset_directory(CONTENT_DIR)
    items = []
    seen_ids = set()

    for encounter_dir in encounter_dirs:
        content_slug = load_cartelas_manifest(encounter_dir)["project"]["output_slug"]
        if content_slug in seen_ids:
            raise SystemExit(f"Duplicate content slug: {content_slug}")
        seen_ids.add(content_slug)

        content_root = CONTENT_DIR / content_slug
        material_dir = content_root / "materials"
        material_href_base = f"./content/{content_slug}/materials"
        payload = build_payload(
            config,
            encounter_dir,
            material_dir,
            material_href_base,
            slug_override=content_slug,
        )
        href = f"./content/{content_slug}/game-data.json"
        write_json(content_root / "game-data.json", payload)
        items.append(catalog_item(payload, encounter_dir, href))

    if default_payload["slug"] not in seen_ids:
        href = f"./content/{default_payload['slug']}/game-data.json"
        items.insert(0, catalog_item(default_payload, default_encounter_dir, href))

    catalog = {
        "schema": "bingo-catequese/content-catalog.v1",
        "defaultContentId": default_payload["slug"],
        "collection": relative_to_repo(collection_dir),
        "items": items,
    }
    write_json(CONTENT_DIR / "catalog.json", catalog)
    return catalog


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

    reset_directory(MATERIALS_DIR)
    default_payload = build_payload(config, encounter_dir, MATERIALS_DIR, "./materials")
    write_json(OUT_PATH, default_payload)
    write_manifest(default_payload["title"])
    catalog = write_content_catalog(config, encounter_dir, default_payload)

    print(
        "Generated "
        f"{OUT_PATH.relative_to(PWA_ROOT)} and {len(catalog['items'])} content bundles "
        f"from {relative_to_repo(resolve_collection_dir(config, encounter_dir))}"
    )


if __name__ == "__main__":
    main()
