from __future__ import annotations

import json
import random
from pathlib import Path


PWA_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PWA_ROOT.parent
DATA_DIR = PROJECT_ROOT / "data"
SRC_DATA = PWA_ROOT / "src" / "data"
OUT_PATH = SRC_DATA / "game-data.json"

TERMS_PATH = DATA_DIR / "termos.json"
CALLS_PATH = DATA_DIR / "chamadas.json"
EXPLANATIONS_PATH = DATA_DIR / "explicacoes.json"
NUM_CARDS = 24
RANDOM_SEED = 404
COLUMN_ORDER = ["B", "I", "N", "G", "O"]


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def load_project_data() -> tuple[dict, dict, list[dict], list[dict]]:
    terms_data = load_json(TERMS_PATH)
    calls_data = load_json(CALLS_PATH)
    return terms_data, calls_data, terms_data["terms"], calls_data["cards"]


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
        for column_index, col in enumerate(COLUMN_ORDER):
            row_positions = [0, 1, 2, 3, 4]
            if col == "N":
                row_positions.remove(2)
            rng.shuffle(row_positions)
            for term, row in zip(assignments[col][card_index], row_positions):
                grid[row][column_index] = term

        grid[2][2] = {
            "id": "FREE",
            "column": "N",
            "label": "LIVRE",
            "definition": "Gn 1,27",
            "anchors": ["Gn 1,27"],
        }
        cards.append({"number": card_index + 1, "grid": grid})

    return cards


def main() -> None:
    terms_data, calls_data, terms, calls = load_project_data()
    explanations_data = load_explanations_data()
    boards = generate_bingo_cards(terms)

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
