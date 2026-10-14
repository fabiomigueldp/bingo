"""Checks the generated game and exports Markdown from canonical JSON only."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    terms = load(ROOT / "data/termos.json")
    calls = load(ROOT / "data/chamadas.json")["cards"]
    explanations = {x["id"]: x["explanation"] for x in load(ROOT / "data/explicacoes.json")["entries"]}
    manifest = load(ROOT / "output/cartelas_manifest.json")
    assert len(manifest["cards"]) == 24
    seen = set()
    frequency = Counter()
    for card in manifest["cards"]:
        ids = card["term_ids"]
        assert len(ids) == len(set(ids)) == 24
        assert Counter(i[0] for i in ids) == {"B": 5, "I": 5, "N": 4, "G": 5, "O": 5}
        key = tuple(sorted(ids))
        assert key not in seen, "Duplicate card"
        seen.add(key)
        frequency.update(ids)
    for col in "BINGO":
        counts = [frequency[t["id"]] for t in terms["terms"] if t["column"] == col]
        assert max(counts) - min(counts) <= 1
    for name, digest in manifest["source_hashes"].items():
        assert hashlib.sha256((ROOT / "data" / name).read_bytes()).hexdigest() == digest
    for path, digest in load(ROOT / "data/fontes_sha256.json").items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest, path
    deck = fitz.open(ROOT / "output/pdf/baralho_chamadas_a4.pdf")
    text = " ".join(page.get_text() for page in deck)
    normalize = lambda s: re.sub(r"\s+", " ", s).strip()
    for call in calls:
        assert call["id"] in text
        assert normalize(call["case"]) in normalize(text), call["id"]
        assert normalize(call["conference_question"]) in normalize(text), call["id"]
        for point in call["reading_points"]:
            assert normalize(point["body"]) in normalize(text), call["id"]
    pdf_pages = {}
    for path in sorted((ROOT / "output/pdf").glob("*.pdf")):
        doc = fitz.open(path)
        pdf_pages[path.name] = len(doc)
        for page in doc:
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        assert page.rect.contains(fitz.Rect(span["bbox"])), (path.name, page.number, span["text"])
    out = ["# " + terms["title"], "", terms["meeting"], "", terms["core_message"], ""]
    for call in calls:
        out += ["## " + call["call_label"], "", "**Caso:** " + call["case"], "", explanations[call["id"]], "", "**Conferência:** " + call["conference_question"], "", "**Nota:** " + call["facilitator_note"], "", "**Referências:** " + "; ".join(call["anchors"]), ""]
    (ROOT / "output/bingo_completo.md").write_text("\n".join(out), encoding="utf-8")
    words = [len(re.findall(r"[\wÀ-ÿ]+", c["case"])) for c in calls]
    report = dict(terms=75, cards=24, case_words_min=min(words), case_words_max=max(words), case_words_mean=round(sum(words)/len(words), 1), original_files_unchanged=True, balanced_cards=True, pdf_text_complete=True, pdf_pages=pdf_pages)
    (ROOT / "output/validacao.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
