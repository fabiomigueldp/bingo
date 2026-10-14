"""Aplica a revisão editorial uma única vez, preservando os arquivos impressos."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    archive = ROOT / 'data/historico/antes_revisao_2026_10_14'
    archive.mkdir(parents=True, exist_ok=True)
    for relative in ('data/chamadas.json', 'data/explicacoes.json', 'output/cartelas_manifest.json'):
        destination = archive / Path(relative).name
        if not destination.exists():
            destination.write_bytes((ROOT / relative).read_bytes())
    lock_path = ROOT / 'data/cartelas_impressas.lock.json'
    if not lock_path.exists():
        paths = ['data/termos.json', 'output/pdf/cartelas_bingo_24_a4.pdf',
                 'output/pdf/cartelas_01_a_10_bingo_liberdade_10_13.pdf']
        manifest = json.loads((ROOT / 'output/cartelas_manifest.json').read_text(encoding='utf-8'))
        lock = {'reason': 'Cartelas já enviadas para impressão. Não regenerar nem alterar termos, códigos, ordem ou posições.',
                'files': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths},
                'manifest': {k: v for k, v in manifest.items() if k != 'source_hashes'}}
        lock_path.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    calls_path = ROOT / 'data/chamadas.json'
    calls = json.loads(calls_path.read_text(encoding='utf-8'))
    rows = {}
    for line in (ROOT / 'data/revisao_chamadas.tsv').read_text(encoding='utf-8').splitlines():
        key, case, first, second, third, question = line.split('|')
        rows[key] = (case, first, second, third, question)
    notes = {
        'B09': 'A ajuda não deve servir para obter uma vantagem desonesta.',
        'B12': 'O Batismo dá vida nova; não elimina toda inclinação ao pecado.',
        'I09': 'Não presumir quanto o funcionário conseguia resistir à pressão.',
        'N10': 'Evitar uma discussão não justifica falsificar a nota.',
        'N14': 'O perdão não elimina a devolução do que foi retirado.',
        'G12': 'O medo pode iniciar a conversão, mas deve haver rejeição do pecado.',
    }
    for call in calls['cards']:
        case, first, second, third, question = rows[call['id']]
        call['case'] = case
        call['reading_points'] = [{'title': title, 'body': body} for title, body in
                                  zip(('Na cena', 'Critério', 'Resposta'), (first, second, third))]
        call['conference_question'] = question
        if call['id'] in notes:
            call['facilitator_note'] = notes[call['id']]
        if call['id'] == 'B12':
            call['anchors'] = ['CEC 1264-1266']
    calls_path.write_text(json.dumps(calls, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    explanations_path = ROOT / 'data/explicacoes.json'
    explanations = json.loads(explanations_path.read_text(encoding='utf-8'))
    by_id = {c['id']: c for c in calls['cards']}
    for entry in explanations['entries']:
        entry['explanation'] = ' '.join(p['body'] for p in by_id[entry['id']]['reading_points'])
    explanations_path.write_text(json.dumps(explanations, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Revisadas as chamadas e explicações. Cartelas preservadas.')


if __name__ == '__main__':
    main()
