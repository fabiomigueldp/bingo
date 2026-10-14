"""Revisão de coerência entre termo, caso, leitura e conjunto. Registro histórico."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHANGES = '''
B01|case|Um rapaz encontra um celular no banco do ônibus. Ninguém vê, mas percebe que ficar com o aparelho seria errado.
B01|p1|Encontrar o celular não torna o rapaz dono do aparelho.
B01|p3|O rapaz deve buscar um meio de devolver o celular ao dono.
B15|p2|Jesus nos chama a amar, com a ajuda do Espírito Santo.
I10|p3|O adolescente precisa reconhecer a falta e limitar o jogo para cumprir os próximos compromissos.
I11|p2|Evitar uma bronca não justifica deixar uma pessoa inocente receber a culpa.
I11|note|Mesmo se o copo quebrou por acidente, manter a acusação é injusto.
N05|p3|O irmão mais novo precisa corrigir a mentira e recusar novas ordens desse tipo.
N07|p3|O adolescente deve desistir de pegar o dinheiro; o perdão não é uma licença para furtar.
G02|case|Um aluno acha justo colar porque o professor cobrou um assunto difícil. Está convencido de que a dificuldade da prova lhe dá esse direito.
G02|p1|O aluno usa a dificuldade da prova para justificar a cola.
G02|p2|A consciência pode se enganar, mesmo quando a pessoa está convencida.
G02|p3|O aluno pode questionar a prova com respeito, mas precisa agir com honestidade.
G02|q|Por que a convicção do aluno não torna correta a decisão de colar?
G02|note|É preciso formar a consciência e corrigir seus julgamentos errados.
G05|case|Uma cozinheira recebe uma lista de alergias incompleta, sem saber da falha. Outra recebe a lista correta, mas decide não ler antes de preparar a comida.
G05|p1|Uma recebeu informação incompleta; a outra ignorou uma informação disponível.
G05|p2|Não conseguir saber é diferente de evitar aquilo que precisamos saber.
G05|p3|É preciso buscar e usar as informações necessárias antes de preparar a refeição.
G05|q|Que diferença existe entre confiar numa lista incompleta e decidir nem ler a lista?
G08|case|Para livrar a irmã de uma bronca, um rapaz acusa o primo de quebrar a janela, embora saiba que foi a irmã quem quebrou.
G08|p1|O rapaz quer proteger a irmã, mas acusa o primo inocente.
G08|p3|O rapaz precisa contar a verdade e corrigir a acusação contra o primo.
G08|q|O que o rapaz quer conseguir, e por que o modo escolhido é errado?
G08|note|Querer proteger a irmã não justifica acusar uma pessoa inocente.
G10|case|Um rapaz rouba o dinheiro do aluguel da mãe. Sabe que é uma falta grave e, mesmo podendo desistir, decide ficar com o dinheiro.
G10|p1|O caso reúne uma ação grave, o conhecimento dessa gravidade e uma escolha deliberada.
G10|p2|O pecado mortal exige essas três condições juntas e rompe a amizade com Deus.
G10|q|Quais detalhes do caso mostram as três condições do pecado mortal?
O02|case|Uma jovem descobre que uma amiga está sendo humilhada por colegas. Prometeu guardar segredo, mas teme que o silêncio deixe a amiga sem ajuda.
O02|p1|A jovem quer respeitar a amiga e evitar que as humilhações continuem.
O02|p2|Um bom conselho ajuda a reconhecer o dever e escolher como agir.
O02|p3|A jovem pode procurar um adulto de confiança e pedir orientação sobre como ajudar a amiga.
O02|q|Como pedir conselho pode ajudar a cuidar da amiga sem espalhar o caso?
O03|p2|O exame de consciência é uma revisão das próprias escolhas diante de Deus.
O04|p1|O jovem percebe que o chamado ao perdão vale também para aquela briga.
O04|p3|O jovem pode pedir desculpas pela própria ofensa e tentar conversar com o irmão.
O06|q|O que o irmão precisa acrescentar ao relato para assumir a própria parte?
O07|case|Uma moradora avisa no grupo que uma loja vendeu um produto vencido. Depois percebe que leu a data errada e apaga a mensagem.
O07|p1|Apagar o aviso não esclarece o engano para quem já leu.
O07|p3|A moradora deve explicar o engano no grupo e se desculpar com a loja.
O08|case|Um rapaz apoia o violão emprestado num lugar instável. O instrumento cai e quebra. O rapaz quer reparar, mas não consegue pagar tudo de uma vez.
O15|p1|A jovem se frustra porque esperava não voltar a ofender.
'''

# O foco distingue retomadas necessárias de repetições sem função.
FOCUS = '''
B01|Reconhecer o dever na própria ação; o caso do celular diferencia esta carta de I01.
B02|Aprender e corrigir o julgamento, em vez de apenas repetir um costume.
B03|Escolher considerando um compromisso; não confundir liberdade com ausência de dever.
B04|Escolher um meio prudente para informar, sem antecipar uma acusação.
B05|Distinguir pagamento devido de favor ou generosidade.
B06|Sustentar a recusa sob zombaria; a fortaleza não exige ausência de medo.
B07|Moderar um prazer legítimo para cuidar do descanso.
B08|Responder por um dano causado por descuido reconhecível.
B09|Avaliar a finalidade de uma ajuda, sem condenar a alegria de receber elogios.
B10|Considerar como a presença dos filhos agrava uma ofensa já errada.
B11|Reconhecer a ajuda gratuita de Deus e responder a ela livremente.
B12|Relacionar a vida nova do Batismo à necessidade de crescer e resistir às tentações.
B13|Apresentar o perdão sacramental e sua relação com arrependimento e reparação.
B14|Relacionar a Comunhão com Cristo ao exercício da caridade em casa.
B15|Apresentar o amor ao próximo com a ajuda do Espírito, conforme a definição congelada.
I01|Perceber o troco indevido e escolher ficar com ele; aplicação concreta da justiça.
I02|Repassar uma suspeita como fato; difere da correção de um erro comprovado em O07.
I03|Reconhecer a pressão de pertencer ao grupo sem justificar a humilhação.
I04|Avaliar a previsibilidade do dano, mesmo sem intenção de quebrar o vidro.
I05|Identificar quem depende do compromisso abandonado conscientemente.
I06|Reconhecer a omissão numa ajuda possível que vai sendo adiada.
I07|Mostrar concretamente como uma mentira exige outra para ser sustentada.
I08|Recusar a cobrança de um favor que exige mentir; gratidão não implica cumplicidade.
I09|Considerar uma ameaça explícita ao emprego e uma resposta com apoio.
I10|Relacionar o uso do tempo às consequências para um compromisso posterior.
I11|Distinguir o possível acidente de quebrar o copo da decisão de manter a acusação.
I12|Enfrentar a vergonha de voltar à Confissão, sem pedir exposição pessoal ao grupo.
I13|Distinguir dificuldade de mudar de usar desculpas para recusar a mudança.
I14|Reconhecer a responsabilidade de quem ensina uma fraude.
I15|Valorizar o serviço discreto, independentemente do reconhecimento.
N01|Rejeitar o costume do grupo como justificativa para uma fraude.
N02|Distinguir a emoção da decisão de humilhar e indicar reparação após a ofensa.
N03|Rejeitar a possibilidade de esconder o furto como critério moral.
N04|Distinguir uma finalidade boa de um meio desonesto numa campanha de ajuda.
N05|Corrigir uma mentira já contada, além de recusar novas ordens erradas.
N06|Rejeitar o temperamento como desculpa para desistir de mudar.
N07|Rejeitar o uso do perdão como autorização para uma falta planejada.
N08|Reconhecer a participação de quem mantém uma ofensa iniciada por outros.
N09|Reconhecer um dever simples de cuidado mesmo sem ser dono do lugar.
N10|Avaliar o ato escolhido, além do resultado favorável de evitar a discussão.
N11|Relacionar liberdade ao respeito pelo descanso dos vizinhos.
N12|Distinguir ignorância involuntária de recusa deliberada de esclarecer uma suspeita.
N13|Tratar a reconstrução da confiança, sem prometer que será imediata.
N14|Rejeitar o perdão como desculpa para reter o que foi retirado.
N15|Rejeitar a espera passiva por mudança enquanto se insiste nas provocações.
G01|Distinguir um impulso recusado de uma decisão de ofender.
G02|Distinguir certeza pessoal de juízo moral correto; não ficar só num engano factual.
G03|Distinguir avaliação do dever de uma desculpa construída para satisfazer um desejo.
G04|Comparar falha imprevisível e risco conhecido ignorado; foco no cuidado possível.
G05|Comparar informação recebida de boa-fé e informação disponível recusada.
G06|Considerar graus de liberdade sem justificar a mentira nem exigir exposição ao perigo.
G07|Condenar a ação errada sem negar a dignidade ou a possibilidade de mudança.
G08|Distinguir objetivo e meio numa acusação falsa, com personagens identificáveis.
G09|Comparar dano deliberado e acidente; foco na diferença entre prejuízo e culpa.
G10|Mostrar as três condições num caso concreto e explicar também o pecado venial.
G11|Relacionar escolhas repetidas à formação de virtudes e vícios morais.
G12|Distinguir evitar a descoberta de rejeitar o furto; o medo pode iniciar conversão.
G13|Explicar por que perdoar e pedir reparação são compatíveis.
G14|Distinguir um limite livremente assumido de uma perda de liberdade.
G15|Relacionar a iniciativa de Deus e a colaboração humana; evitar dois extremos.
O01|Indicar o que conferir antes de repassar; prevenir o boato tratado em I02.
O02|Buscar conselho para discernir um dever em tensão com uma promessa de segredo.
O03|Rever escolhas diante de Deus, reconhecendo tanto o bem quanto o que corrigir.
O04|Aplicar à própria conduta o chamado ouvido na Palavra, com uma ação possível.
O05|Formular uma recusa respeitosa e oferecer ajuda que não exige mentir.
O06|Completar o relato com a própria participação sem assumir a culpa alheia.
O07|Corrigir publicamente uma informação falsa já difundida, além de apagá-la.
O08|Combinar uma reparação possível após um descuido explícito com algo emprestado.
O09|Procurar proteção diante de ameaça concreta; difere da dúvida moral em O02.
O10|Dar o primeiro passo para procurar a Confissão, sem expor pecados ao grupo.
O11|Mudar uma condição que favorece a repetição de ofensas.
O12|Acompanhar a oração com uma resposta concreta no momento da irritação.
O13|Formar um hábito por uma prática pequena, específica e repetida.
O14|Renunciar a algo permitido por cuidado concreto com outra pessoa.
O15|Retomar o esforço após uma queda, com arrependimento e reparação.
'''


def main():
    archive = ROOT / 'data/historico/antes_revisao_03'
    archive.mkdir(parents=True, exist_ok=True)
    for name in ('chamadas.json', 'explicacoes.json'):
        path = ROOT / 'data' / name
        if not (archive / name).exists():
            (archive / name).write_bytes(path.read_bytes())
    path = ROOT / 'data/chamadas.json'
    calls = json.loads(path.read_text(encoding='utf-8'))
    cards = {c['id']: c for c in calls['cards']}
    changed = set()
    for line in CHANGES.strip().splitlines():
        code, field, text = line.split('|', 2)
        card = cards[code]
        if field in ('p1', 'p2', 'p3'):
            card['reading_points'][int(field[1]) - 1]['body'] = text
        else:
            card[{'q': 'conference_question', 'note': 'facilitator_note', 'case': 'case'}[field]] = text
        changed.add(code)
    cards['G10']['anchors'] = ['CEC 1857-1863']
    path.write_text(json.dumps(calls, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    path = ROOT / 'data/explicacoes.json'
    explanations = json.loads(path.read_text(encoding='utf-8'))
    for entry in explanations['entries']:
        entry['explanation'] = ' '.join(p['body'] for p in cards[entry['id']]['reading_points'])
    path.write_text(json.dumps(explanations, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    report = ['# Revisão de coerência do bingo integrado', '',
              'Foram relidas as 75 cartas como unidades: termo e definição congelados, caso, leitura, explicação rápida, pergunta, nota e referências.', '',
              'As colunas retomam assuntos com funções distintas: B apresenta o fundamento; I mostra a situação; N expõe uma justificativa errada; G distingue conceitos; O propõe uma resposta possível.', '',
              'As repetições de tema foram mantidas quando servem a essas funções. Foram corrigidos casos que desviavam do termo, ambiguidades entre personagens e explicações que não acompanhavam o momento da ação.', '',
              f'Esta rodada ajustou {len(changed)} cartas. As demais foram mantidas após leitura. Termos, definições, códigos, ordem e cartelas impressas não foram alterados.', '',
              'Consulta doutrinal: material didático dos encontros 10–13 e índice local do CEC, especialmente 1787–1793, 1857–1863 e 1972. Os textos das cartas são paráfrases didáticas, não citações.', '',
              '| Carta | Decisão | Foco e coerência no conjunto |', '| --- | --- | --- |']
    for line in FOCUS.strip().splitlines():
        code, reason = line.split('|', 1)
        report.append(f"| {cards[code]['call_label']} | {'Ajustada' if code in changed else 'Mantida'} | {reason} |")
    (ROOT / 'output/revisao_conjunto.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
    print(f'Revisão de conjunto: 75 cartas lidas, {len(changed)} ajustadas.')


if __name__ == '__main__':
    main()
