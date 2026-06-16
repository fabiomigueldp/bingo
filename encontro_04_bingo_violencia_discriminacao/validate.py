import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

FORBIDDEN_TEXT_SNIPPETS = [
    "preçonceito",
    "férir",
    "férido",
    "individuos",
    "obstaculo",
    "construido",
    "diminuida",
    "migraçao",
    "dificuldade especifica",
    "Competencia",
    "substituido",
    "forcado",
    "obediencia",
    "Empurroes",
    "permanencia",
    "Comentarios",
    "forcar",
    "consciencia",
    "estetica",
    "expressao",
    "comecou",
    "logica",
    "sera ignorado",
    "acusação automatica",
    "inseguranca",
    "comunhao",
    "reciproca",
    "vira razao",
    "Reforcar",
    "Servico",
    "alcancar",
    "versao",
    "generico",
    "Não forcar",
    "desprezo máscarado",
    "lixo moral",
    "omissão covarde",
    "Pecado social pequeno",
]


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def fail(errors):
    for error in errors:
        print(f"ERRO: {error}")
    raise SystemExit(1)


def main():
    errors = []

    termos = load_json(DATA / "termos.json")
    chamadas = load_json(DATA / "chamadas.json")
    explicacoes = load_json(DATA / "explicacoes.json")

    terms = termos.get("terms", [])
    cards = chamadas.get("cards", [])
    explanation_entries = explicacoes.get("entries", [])

    term_ids = [term.get("id") for term in terms]
    card_ids = [card.get("id") for card in cards]
    card_term_ids = [card.get("term_id") for card in cards]
    explanation_ids = [entry.get("id") for entry in explanation_entries]

    if len(terms) != 75:
        errors.append(f"termos.json deve ter 75 termos; encontrou {len(terms)}")

    if len(cards) != 75:
        errors.append(f"chamadas.json deve ter 75 chamadas; encontrou {len(cards)}")

    if len(explanation_entries) != 75:
        errors.append(f"explicacoes.json deve ter 75 explicações; encontrou {len(explanation_entries)}")

    term_duplicates = [k for k, v in Counter(term_ids).items() if v > 1]
    if term_duplicates:
        errors.append(f"IDs duplicados em termos.json: {term_duplicates}")

    card_duplicates = [k for k, v in Counter(card_ids).items() if v > 1]
    if card_duplicates:
        errors.append(f"IDs duplicados em chamadas.json: {card_duplicates}")

    card_ref_duplicates = [k for k, v in Counter(card_term_ids).items() if v > 1]
    if card_ref_duplicates:
        errors.append(f"term_id duplicado em chamadas.json: {card_ref_duplicates}")

    explanation_duplicates = [k for k, v in Counter(explanation_ids).items() if v > 1]
    if explanation_duplicates:
        errors.append(f"IDs duplicados em explicacoes.json: {explanation_duplicates}")

    term_id_set = set(term_ids)
    card_term_id_set = set(card_term_ids)

    missing_calls = sorted(term_id_set - card_term_id_set)
    if missing_calls:
        errors.append(f"termos sem chamada: {missing_calls}")

    extra_calls = sorted(card_term_id_set - term_id_set)
    if extra_calls:
        errors.append(f"chamadas apontam para termos inexistentes: {extra_calls}")

    card_id_set = set(card_ids)
    explanation_id_set = set(explanation_ids)
    missing_explanations = sorted(card_id_set - explanation_id_set)
    if missing_explanations:
        errors.append(f"chamadas sem explicação: {missing_explanations}")

    extra_explanations = sorted(explanation_id_set - card_id_set)
    if extra_explanations:
        errors.append(f"explicações apontam para chamadas inexistentes: {extra_explanations}")

    mismatches = [
        (card.get("id"), card.get("term_id"))
        for card in cards
        if card.get("id") != card.get("term_id")
    ]
    if mismatches:
        errors.append(f"id é term_id divergentes: {mismatches}")

    column_counts = Counter(term.get("column") for term in terms)
    expected_columns = {"B", "I", "N", "G", "O"}
    if set(column_counts) != expected_columns:
        errors.append(f"colunas encontradas {sorted(column_counts)}; esperado {sorted(expected_columns)}")

    bad_columns = {key: value for key, value in column_counts.items() if value != 15}
    if bad_columns:
        errors.append(f"cada coluna deve ter 15 termos; divergencias: {bad_columns}")

    center = termos.get("card_model", {}).get("center", {})
    if center.get("called") is not False:
        errors.append("centro da cartela deve ter called=false")

    required_card_fields = {
        "id",
        "term_id",
        "call_label",
        "case",
        "reading_points",
        "conference_question",
        "anchors",
        "facilitator_note",
    }
    for card in cards:
        missing = required_card_fields - set(card)
        if missing:
            errors.append(f"chamada {card.get('id')} sem campos: {sorted(missing)}")
            continue
        reading_points = card.get("reading_points", [])
        if not isinstance(reading_points, list) or not 2 <= len(reading_points) <= 3:
            errors.append(f"chamada {card.get('id')} deve ter 2 ou 3 reading_points")
            continue
        for index, point in enumerate(reading_points, start=1):
            point_missing = {"title", "body"} - set(point)
            if point_missing:
                errors.append(
                    f"chamada {card.get('id')} reading_point {index} sem campos: {sorted(point_missing)}"
                )

    for entry in explanation_entries:
        missing = {"id", "explanation"} - set(entry)
        if missing:
            errors.append(f"explicação {entry.get('id')} sem campos: {sorted(missing)}")
            continue
        explanation = entry.get("explanation", "")
        if not isinstance(explanation, str) or len(explanation.strip()) < 80:
            errors.append(f"explicação {entry.get('id')} curta demais ou inválida")
        if explanation.count("**") % 2:
            errors.append(f"explicação {entry.get('id')} tem marcação de negrito desbalanceada")

    combined_text = json.dumps(
        {"termos": termos, "chamadas": chamadas, "explicacoes": explicacoes},
        ensure_ascii=False,
    )
    found_forbidden = [snippet for snippet in FORBIDDEN_TEXT_SNIPPETS if snippet in combined_text]
    if found_forbidden:
        errors.append(f"strings proibidas encontradas no texto-fonte: {found_forbidden}")

    if errors:
        fail(errors)

    print("OK: 75 termos, 75 chamadas, 75 explicações, 15 termos por coluna, centro livre não chamável.")


if __name__ == "__main__":
    main()
