import json
import re
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

FORBIDDEN_GENERIC_CASES = [
    "uma pessoa não respeita outra",
    "alguém não respeita outra pessoa",
    "uma pessoa faz algo errado",
    "alguém age sem caridade",
    "uma pessoa desrespeita a dignidade",
]

MAX_TERM_LABEL_CHARS = 34
WARN_TERM_LABEL_CHARS = 32
WARN_CASE_WORDS = 24
WARN_EXPLANATION_WORDS = 55

YOUTH_CONTEXT_SNIPPETS = [
    "adolescente",
    "adolescentes",
    "aluno",
    "aluna",
    "colega",
    "turma",
    "escola",
    "grupo de amigos",
]

ECCLESIAL_CONTEXT_SNIPPETS = [
    "catequese",
    "igreja",
    "paróquia",
    "paroquia",
    "grupo de jovens",
    "missa",
]

RAW_NARRATIVE_STARTS = (
    "eu ",
    "meu ",
    "minha ",
    "sou ",
    "não sou ",
    "ninguem ",
    "ninguém ",
)

GENERIC_RESPONSE_LABELS = (
    "ser ",
    "ter ",
    "fazer o bem",
    "respeitar",
    "acolher",
    "amar",
    "ajudar",
    "ter empatia",
)


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def fail(errors):
    for error in errors:
        print(f"ERRO: {error}")
    raise SystemExit(1)


def word_count(text: str) -> int:
    return len(re.findall(r"[\wÀ-ÿ]+", text or ""))


def sentence_count(text: str) -> int:
    parts = [part for part in re.split(r"[.!?]+", text or "") if part.strip()]
    return len(parts)


def has_youth_context(text: str) -> bool:
    lowered = (text or "").lower()
    return any(snippet in lowered for snippet in YOUTH_CONTEXT_SNIPPETS)


def has_ecclesial_context(text: str) -> bool:
    lowered = (text or "").lower()
    return any(snippet in lowered for snippet in ECCLESIAL_CONTEXT_SNIPPETS)


def contains_forbidden_snippet(text: str, snippet: str) -> bool:
    prefix = r"(?<![\wÀ-ÿ])" if snippet[:1].isalnum() else ""
    suffix = r"(?![\wÀ-ÿ])" if snippet[-1:].isalnum() else ""
    pattern = prefix + re.escape(snippet) + suffix
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def main():
    errors = []
    warnings = []

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

    for term in terms:
        term_id = term.get("id", "?")
        label = term.get("label", "")
        if not isinstance(label, str) or not label.strip():
            errors.append(f"termo {term_id} sem label")
        elif len(label) > MAX_TERM_LABEL_CHARS:
            errors.append(f"termo {term_id} com label longo demais para cartela: {label!r}")
        elif len(label) > WARN_TERM_LABEL_CHARS:
            warnings.append(f"termo {term_id} com label perto do limite da cartela: {label!r}")
        if isinstance(label, str):
            lowered_label = label.strip().lower()
            column = term.get("column")
            if lowered_label.startswith(RAW_NARRATIVE_STARTS):
                warnings.append(f"termo {term_id} com label em primeira pessoa ou narrativa crua: {label!r}")
            if column == "O" and lowered_label.startswith(GENERIC_RESPONSE_LABELS):
                warnings.append(f"termo {term_id} pode estar genérico demais para orientação de resposta: {label!r}")
            if column == "G" and " ou " not in lowered_label and " e " not in lowered_label:
                warnings.append(f"termo {term_id} em G não explicita contraste/distinção no label: {label!r}")
        if not term.get("definition", "").strip():
            errors.append(f"termo {term_id} sem definição")
        if not term.get("anchors"):
            errors.append(f"termo {term_id} sem âncoras")

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
        card_id = card.get("id")
        case = card.get("case", "")
        if not isinstance(case, str) or not case.strip():
            errors.append(f"chamada {card_id} sem case")
        else:
            lowered_case = case.lower()
            for generic_case in FORBIDDEN_GENERIC_CASES:
                if generic_case in lowered_case:
                    errors.append(f"chamada {card_id} tem caso genérico demais: {generic_case!r}")
            if "catequista" in lowered_case:
                warnings.append(
                    f"chamada {card_id} usa 'catequista' no case; revisar se é necessidade real e excepcional"
                )
            if word_count(case) > WARN_CASE_WORDS:
                warnings.append(f"chamada {card_id} tem case longo; revisar concisão e naturalidade")
        if not card.get("conference_question", "").strip():
            errors.append(f"chamada {card_id} sem pergunta de conferência")
        if not card.get("anchors"):
            errors.append(f"chamada {card_id} sem âncoras")
        if not card.get("facilitator_note", "").strip():
            errors.append(f"chamada {card_id} sem nota de condução")

        reading_points = card.get("reading_points", [])
        if not isinstance(reading_points, list) or len(reading_points) != 3:
            errors.append(f"chamada {card_id} deve ter exatamente 3 reading_points")
            continue
        for index, point in enumerate(reading_points, start=1):
            point_missing = {"title", "body"} - set(point)
            if point_missing:
                errors.append(
                    f"chamada {card_id} reading_point {index} sem campos: {sorted(point_missing)}"
                )
            elif not str(point.get("title", "")).strip() or not str(point.get("body", "")).strip():
                errors.append(f"chamada {card_id} reading_point {index} vazio")

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
        clean_explanation = explanation.replace("**", "")
        if word_count(clean_explanation) > WARN_EXPLANATION_WORDS:
            warnings.append(f"explicação {entry.get('id')} longa; revisar se virou palestra")
        count_sentences = sentence_count(clean_explanation)
        if count_sentences < 2 or count_sentences > 5:
            warnings.append(f"explicação {entry.get('id')} com {count_sentences} frases; alvo recomendado é 3 ou 4")

    case_youth_count = sum(1 for card in cards if has_youth_context(card.get("case", "")))
    if case_youth_count > 35:
        warnings.append(
            f"{case_youth_count} cases usam contexto adolescente/escolar; revisar se há escolarização artificial"
        )

    case_ecclesial_count = sum(1 for card in cards if has_ecclesial_context(card.get("case", "")))
    if case_ecclesial_count > 12:
        warnings.append(
            f"{case_ecclesial_count} cases usam cenário eclesial/catequético; revisar se o tema realmente exige isso"
        )

    reading_title_counts = Counter(
        point.get("title", "").strip().lower()
        for card in cards
        for point in card.get("reading_points", [])
    )
    repeated_titles = sorted(title for title, count in reading_title_counts.items() if title and count >= 3)
    if repeated_titles:
        warnings.append(
            "títulos de reading_points repetidos 3+ vezes; revisar variedade conceitual: "
            + ", ".join(repeated_titles[:10])
        )

    combined_text = json.dumps(
        {"termos": termos, "chamadas": chamadas, "explicacoes": explicacoes},
        ensure_ascii=False,
    )
    found_forbidden = [
        snippet
        for snippet in FORBIDDEN_TEXT_SNIPPETS
        if contains_forbidden_snippet(combined_text, snippet)
    ]
    if found_forbidden:
        errors.append(f"strings proibidas encontradas no texto-fonte: {found_forbidden}")

    if errors:
        fail(errors)

    print("OK: 75 termos, 75 chamadas, 75 explicações, 15 termos por coluna, centro livre não chamável.")
    for warning in warnings:
        print(f"AVISO: {warning}")


if __name__ == "__main__":
    main()
