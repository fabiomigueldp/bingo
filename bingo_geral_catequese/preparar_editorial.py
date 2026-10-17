"""Importação editorial inicial. Depois dela, os três JSONs são canônicos."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def save(name, data):
    (ROOT / 'data' / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    rows = [line.split('|') for line in (ROOT / 'data/editorial.tsv').read_text(encoding='utf-8').splitlines() if line.strip()]
    expected = [f'{col}{i:02}' for col in 'BINGO' for i in range(1, 16)]
    if [r[0] for r in rows] != expected or any(len(r) != 10 for r in rows):
        raise SystemExit('A edição precisa conter 75 linhas completas na ordem B01–O15.')
    extra = {'B01': 'Mt 6,9-13', 'B06': 'Lc 24,1-6', 'B07': 'Lc 10,30-37',
             'B09': 'At 2,42-47', 'I12': '1Cor 12,4-7', 'G10': 'Jo 2,1-5',
             'O05': 'Mt 6,9-13', 'O14': '1Pd 3,15-16'}
    terms, cards, entries = [], [], []
    for code, label, definition, case, first, second, third, question, refs, note in rows:
        anchors = refs.split('; ')
        if code in extra:
            anchors.append(extra[code])
        terms.append(dict(id=code, column=code[0], label=label, definition=definition, anchors=anchors, tags=['catequese-geral']))
        points = [dict(title=title, body=body) for title, body in zip(['Na cena', 'Fundamento', 'Aplicação'], [first, second, third])]
        if code == 'G07':
            points[2]['title'] = 'Distinção'
        cards.append(dict(id=code, term_id=code, call_label=f'{code} - {label}', case=case,
                          reading_points=points, conference_question=question, anchors=anchors, facilitator_note=note))
        entries.append(dict(id=code, explanation=' '.join([first, second, third])))
    references = list(dict.fromkeys(a for t in terms for a in t['anchors']))
    columns = [
        dict(key='B', title='Fundamentos da fé', function='O que a Igreja crê e anuncia sobre Deus e a vida cristã.', short_function='fundamentos da fé cristã'),
        dict(key='I', title='Situações concretas', function='Situações em que a fé ilumina a vida cotidiana.', short_function='a fé na vida cotidiana'),
        dict(key='N', title='Ideias equivocadas', function='Enganos e desculpas que distorcem a fé ou afastam do bem.', short_function='enganos sobre a fé e a vida'),
        dict(key='G', title='Discernimentos', function='Distinções que ajudam a compreender e viver a fé.', short_function='distinções para compreender'),
        dict(key='O', title='Fé em prática', function='Respostas concretas, possíveis e orientadas pela fé.', short_function='respostas concretas de fé'),
    ]
    common = dict(title='Bingo - Conhecer e viver a fé', meeting='Catequese geral - Primeira Eucaristia e Crisma',
                  meeting_label='Catequese geral', output_slug='bingo_geral_catequese',
                  core_message='Jesus Cristo nos revela o Pai e nos salva. Pelo Espírito Santo, aprendemos a crer, celebrar, rezar e amar na vida da Igreja.',
                  source_meeting_markdown=None, teaching_overview='data/panorama.json',
                  scripture=['Jo 14,6'] + [a for a in references if not a.startswith('CEC ')],
                  catechism=[a for a in references if a.startswith('CEC ')],
                  card_model=dict(total_terms=75, columns=5, terms_per_column=15, grid='5x5',
                                  center=dict(label='LIVRE / Jo 14,6', fixed=True, called=False), recommended_win_condition='duas_linhas'),
                  columns=columns, terms=terms)
    save('termos.json', common)
    method = dict(read_order=['call_label', 'case', 'reading_points'],
                  rule='Anuncie código e termo; leia o caso e a explicação rápida ou os três pontos, sem repetir ambos. Marquem pelo código. Use a pergunta na conferência ou para esclarecer uma dúvida.',
                  conference_rule='Após completar duas linhas (horizontal, vertical ou diagonal), a equipe escolhe uma delas, explica três conceitos e relaciona pelo menos um à fé cristã. As linhas podem se cruzar. O centro livre conta para fechar linha, mas não como conceito. Permita uma segunda tentativa breve quando necessário.')
    save('chamadas.json', dict(title='Chamadas - Conhecer e viver a fé', meeting=common['meeting'], source_terms='data/termos.json', method=method, cards=cards))
    save('explicacoes.json', dict(title='Explicações rápidas - Conhecer e viver a fé', meeting=common['meeting'], source_calls='data/chamadas.json', purpose='Apoio breve para quem conduz as chamadas.', entries=entries))
    save('panorama.json', dict(title='Conhecer e viver a fé',
        meta=[dict(label='Público', value='Catequese de Primeira Eucaristia e Crisma'), dict(label='Formato', value='75 chamadas e 24 cartelas')],
        sections=[
            dict(title='O centro: Jesus Cristo', paragraphs=[common['core_message'], 'O Filho de Deus se fez homem, morreu e ressuscitou para nos salvar. A vida cristã é resposta a esse amor, sustentada pela graça, e não apenas uma lista de regras.']),
            dict(title='A fé que professamos', paragraphs=['Pai, Filho e Espírito Santo; criação; Jesus Cristo; ressurreição e vida eterna; Palavra de Deus; fé; Igreja; Maria e comunhão dos santos. A Bíblia é lida no conjunto da Escritura e na fé da Igreja.']),
            dict(title='A fé que celebramos', paragraphs=['Batismo, Crisma e Eucaristia são os sacramentos da iniciação cristã. Reconciliação e Unção dos Enfermos oferecem perdão e fortalecimento. Ordem e Matrimônio estão a serviço da comunhão e da missão.', 'Os sete sacramentos aparecem nas cartas B10–B13, I14 e G13–G15. A Missa torna presente o único sacrifício de Cristo; nela recebemos sua Palavra e seu Corpo.']),
            dict(title='A fé que vivemos', paragraphs=['A graça nos ajuda a responder livremente ao amor de Deus. Os mandamentos e o Evangelho orientam a consciência. Justiça, verdade, misericórdia, dignidade e cuidado com a criação ganham forma em escolhas possíveis.', 'Os casos distinguem tentação e pecado, perdão e confiança, pecado e pessoa, liberdade e capricho. Ninguém precisa expor situações íntimas para participar.']),
            dict(title='A fé que rezamos', paragraphs=['A oração é relação com Deus: escuta, louvor, gratidão e súplica. Jesus nos ensina o Pai-Nosso. Rezar não compra favores nem elimina nossa responsabilidade; a fé pode permanecer em meio às dificuldades.']),
            dict(title='Como conduzir', paragraphs=[method['rule'], method['conference_rule'], 'O condutor lê; quem ainda está aprendendo pode jogar em equipe. Aceite respostas curtas e com palavras próprias. Explique termos novos sem exigir definições decoradas. Ninguém precisa conhecer todos os assuntos antes de começar.']),
            dict(title='Fontes', paragraphs=['Diretório de Catequese local, Bíblia Ave-Maria e Catecismo da Igreja Católica consultados pelos índices do projeto. As referências específicas acompanham cada carta. Casos e explicações são redação didática, não citações literais.']),
        ]))
    print('Criados termos, chamadas, explicações e panorama da catequese geral.')


if __name__ == '__main__':
    main()
