"""Atualiza apenas o material de leitura; reutiliza as cartelas já impressas."""
import json
import build


def main():
    root = build.ROOT
    lock = build.load_json(root / 'data/cartelas_impressas.lock.json')
    for relative, expected in lock['files'].items():
        if build.file_sha256(root / relative) != expected:
            raise SystemExit(f'Arquivo impresso alterado: {relative}. Geração interrompida.')
    manifest_path = root / 'output/cartelas_manifest.json'
    manifest = build.load_json(manifest_path)
    if {k: v for k, v in manifest.items() if k != 'source_hashes'} != lock['manifest']:
        raise SystemExit('A identidade ou disposição das cartelas foi alterada. Geração interrompida.')
    terms_data, calls_data, terms, calls = build.load_project_data()
    explanations_data = build.load_explanations_data()
    calls_pdf = build.build_call_deck(terms, calls)
    explanations_pdf = build.build_explanations_letter(terms, calls, explanations_data)
    for name in ('chamadas.json', 'explicacoes.json'):
        manifest['source_hashes'][name] = build.file_sha256(root / 'data' / name)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    explanations = {e['id']: e['explanation'] for e in explanations_data['entries']}
    markdown = ['# ' + terms_data['title'], '', terms_data['meeting'], '', terms_data['core_message'], '']
    for call in calls:
        markdown += ['## ' + call['call_label'], '', '**Caso:** ' + call['case'], '',
                     explanations[call['id']], '', '**Conferência:** ' + call['conference_question'], '',
                     '**Nota:** ' + call['facilitator_note'], '', '**Referências:** ' + '; '.join(call['anchors']), '']
    (root / 'output/bingo_completo.md').write_text('\n'.join(markdown), encoding='utf-8')
    out = build.OUT_DIR
    kit = build.merge_pdfs([out / 'cartelas_bingo_24_a4.pdf', calls_pdf, explanations_pdf,
                           out / 'cartoes_regras_equipes_a4.pdf', out / 'folha_controle_chamadas.pdf',
                           out / 'guia_do_catequista.pdf'])
    for path in (calls_pdf, explanations_pdf, kit):
        print(path)


if __name__ == '__main__':
    main()
