from __future__ import annotations

import json
import sys
from pathlib import Path


PWA_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PWA_ROOT.parent
SRC_DATA = PWA_ROOT / "src" / "data"
OUT_PATH = SRC_DATA / "game-data.json"

sys.path.insert(0, str(PROJECT_ROOT))
import build  # noqa: E402


def main() -> None:
    terms_data, calls_data, terms, calls = build.load_project_data()
    explanations_data = build.load_explanations_data()
    boards = build.generate_bingo_cards(terms)

    terms_by_id = {term["id"]: term for term in terms}
    explanations_by_id = {entry["id"]: entry["explanation"] for entry in explanations_data["entries"]}

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

    pwa_boards = []
    for board in boards:
        pwa_boards.append(
            {
                "number": board["number"],
                "grid": [
                    [
                        {
                            "id": cell["id"],
                            "column": cell["column"],
                            "label": cell["label"],
                            "definition": cell.get("definition", ""),
                            "anchors": cell.get("anchors", []),
                        }
                        for cell in row
                    ]
                    for row in board["grid"]
                ],
            }
        )

    payload = {
        "version": "encontro-04-seed-404-v1",
        "title": terms_data["title"],
        "meeting": terms_data["meeting"],
        "scripture": terms_data["scripture"],
        "catechism": terms_data["catechism"],
        "cardModel": terms_data["card_model"],
        "columns": terms_data["columns"],
        "method": calls_data["method"],
        "cards": call_cards,
        "boards": pwa_boards,
    }

    SRC_DATA.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {OUT_PATH.relative_to(PWA_ROOT)}")


if __name__ == "__main__":
    main()
