from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import fitz
from reportlab.lib.pagesizes import A4, landscape


ROOT = Path(__file__).resolve().parent
PDF_DIR = ROOT / "output" / "pdf"
MANIFEST_PATH = ROOT / "output" / "cartelas_manifest.json"
LAYOUT_REPORT_PATH = ROOT / "output" / "baralho_layout_report.json"

EXPECTED_PAGES = {
    "cartelas_bingo_24_a4.pdf": 12,
    "baralho_chamadas_a4.pdf": 10,
    "carta_explicacoes_catequista.pdf": 7,
    "cartoes_regras_equipes_a4.pdf": 1,
    "folha_controle_chamadas.pdf": 1,
    "guia_conducao_bingo.pdf": 3,
    "kit_impressao_bingo_relacionamento_humano.pdf": 34,
}

PORTRAIT_PDFS = {
    "cartelas_bingo_24_a4.pdf",
    "carta_explicacoes_catequista.pdf",
    "cartoes_regras_equipes_a4.pdf",
    "guia_conducao_bingo.pdf",
}
LANDSCAPE_PDFS = {
    "baralho_chamadas_a4.pdf",
    "folha_controle_chamadas.pdf",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close_enough(left: float, right: float, tolerance: float = 1.0) -> bool:
    return abs(left - right) <= tolerance


def check_pdf(path: Path, expected_pages: int, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"PDF ausente: {path.name}")
        return
    doc = fitz.open(path)
    if len(doc) != expected_pages:
        errors.append(f"{path.name}: esperadas {expected_pages} páginas; encontrou {len(doc)}")

    expected_size = None
    if path.name in PORTRAIT_PDFS:
        expected_size = A4
    elif path.name in LANDSCAPE_PDFS:
        expected_size = landscape(A4)

    for page_index, page in enumerate(doc, start=1):
        rect = page.rect
        if expected_size and not (
            close_enough(rect.width, expected_size[0])
            and close_enough(rect.height, expected_size[1])
        ):
            errors.append(
                f"{path.name} p.{page_index}: tamanho {rect.width:.1f}x{rect.height:.1f} fora do A4 esperado"
            )
        text = page.get_text()
        if not text.strip():
            errors.append(f"{path.name} p.{page_index}: página sem texto")
        if "�" in text:
            errors.append(f"{path.name} p.{page_index}: caractere de substituição encontrado")
        for block in page.get_text("blocks"):
            x0, y0, x1, y1 = block[:4]
            if x0 < -0.5 or y0 < -0.5 or x1 > rect.width + 0.5 or y1 > rect.height + 0.5:
                errors.append(
                    f"{path.name} p.{page_index}: bloco de texto fora da página "
                    f"({x0:.1f}, {y0:.1f}, {x1:.1f}, {y1:.1f})"
                )
    doc.close()


def source_path(key: str) -> Path:
    if key in {"termos.json", "chamadas.json", "explicacoes.json"}:
        return ROOT / "data" / key
    if key in {"build.py", "validate.py", "qa.py"}:
        return ROOT / key
    path = Path(key)
    return path if path.is_absolute() else ROOT / path


def main() -> None:
    errors: list[str] = []
    for filename, expected_pages in EXPECTED_PAGES.items():
        check_pdf(PDF_DIR / filename, expected_pages, errors)

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    layout = json.loads(LAYOUT_REPORT_PATH.read_text(encoding="utf-8"))

    for key, expected_hash in manifest["source_hashes"].items():
        path = source_path(key)
        if not path.exists():
            errors.append(f"fonte registrada não existe: {key}")
        elif sha256(path) != expected_hash:
            errors.append(f"artefato desatualizado em relação à fonte: {key}")

    overlap = manifest["generation"]["overlap"]
    if overlap["maximum"] > 10:
        errors.append(f"sobreposição máxima inválida: {overlap['maximum']}")
    simulation = manifest["generation"]["game_simulation"]
    if not 28 <= simulation["mean_first_claim"] <= 40:
        errors.append(f"média simulada fora da faixa: {simulation['mean_first_claim']}")

    if layout["cards_per_page"] != 8 or layout["grid"] != "4x2":
        errors.append("baralho não está configurado em oito cartas por A4, grade 4x2")
    if not layout["all_cards_fit"]:
        errors.append("relatório informa carta fora da área segura")
    if min(card["minimum_font_pt"] for card in layout["cards"]) < 6.8:
        errors.append("baralho usa corpo inferior a 6,8 pt")
    if min(card["vertical_spare_mm"] for card in layout["cards"]) < 0:
        errors.append("baralho possui overflow vertical")

    call_doc = fitz.open(PDF_DIR / "baralho_chamadas_a4.pdf")
    codes = Counter(
        re.findall(r"\b[BINGO]\d{2}\b", "\n".join(page.get_text() for page in call_doc))
    )
    call_doc.close()
    expected_codes = {f"{column}{number:02d}" for column in "BINGO" for number in range(1, 16)}
    if set(codes) != expected_codes:
        errors.append("baralho não contém exatamente os 75 códigos esperados")
    repeated_codes = sorted(code for code, count in codes.items() if count != 1)
    if repeated_codes:
        errors.append(f"códigos repetidos no baralho: {repeated_codes}")

    component_total = sum(
        pages
        for filename, pages in EXPECTED_PAGES.items()
        if not filename.startswith("kit_impressao_")
    )
    if component_total != EXPECTED_PAGES["kit_impressao_bingo_relacionamento_humano.pdf"]:
        errors.append("número de páginas do kit não corresponde à soma dos componentes")

    if errors:
        for error in errors:
            print(f"ERRO: {error}")
        raise SystemExit(1)

    print(
        "OK: 7 PDFs, 34 páginas, A4 correto, 75 chamadas únicas, "
        "8 cartas por folha, fontes >= 6,8 pt, sem overflow e hashes sincronizados."
    )


if __name__ == "__main__":
    main()
