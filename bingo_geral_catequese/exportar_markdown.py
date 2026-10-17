"""Exporta o material de leitura a partir dos JSONs canônicos."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    load = lambda name: json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))
    terms = load('termos.json')
    calls = load('chamadas.json')['cards']
    definitions = {t['id']: t['definition'] for t in terms['terms']}
    out = ['# ' + terms['title'], '', terms['meeting'], '', terms['core_message'], '']
    for c in calls:
        out += ['## ' + c['call_label'], '', '**Conceito:** ' + definitions[c['id']], '',
                '**Caso:** ' + c['case'], '', ' '.join(p['body'] for p in c['reading_points']), '',
                '**Conferência:** ' + c['conference_question'], '', '**Nota:** ' + c['facilitator_note'], '',
                '**Referências:** ' + '; '.join(c['anchors']), '']
    (ROOT / 'output').mkdir(exist_ok=True)
    (ROOT / 'output/bingo_completo.md').write_text('\n'.join(out), encoding='utf-8')
    print('Exportado output/bingo_completo.md')


if __name__ == '__main__':
    main()
