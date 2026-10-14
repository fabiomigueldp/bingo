"""Registro da segunda revisão, carta a carta. Não altera termos ou cartelas."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Apenas os campos abaixo são substituídos. Os demais foram relidos e mantidos.
CHANGES = '''
B01|p2|A consciência julga nossas ações e nos indica o bem que devemos fazer.
B01|q|O que a consciência ajuda a reconhecer nessa situação?
B02|p3|O aluno pode aprender com a Palavra de Deus, a Igreja e bons conselhos.
B02|q|O que mudou: a honestidade da cópia ou o entendimento do aluno?
B03|p2|O livre-arbítrio é a capacidade de escolher, usando a razão e a vontade.
B04|p2|A prudência ajuda a reconhecer o bem e escolher os meios para realizá-lo.
B04|note|Destacar o cuidado de verificar antes de agir.
B05|case|Um pintor termina o serviço conforme o combinado. Na hora de pagar, o dono da casa tenta reduzir o valor que havia aceitado.
B05|p1|O pintor cumpriu o acordo e tem direito ao pagamento.
B05|p3|O dono da casa deve pagar o valor combinado.
B06|case|Os amigos pedem a um adolescente que esconda a mochila de um colega para deixá-lo desesperado. O adolescente recusa e vira alvo de gozação.
B07|case|Já é tarde, e uma jovem precisa acordar cedo. Quando começa outro episódio da série, decide desligar a televisão e ir dormir.
B07|p3|A jovem pode aproveitar o lazer sem deixar de cuidar do descanso.
B07|q|Como a decisão de parar mostra temperança?
B08|case|Um ciclista olha o celular enquanto pedala e arranha um carro estacionado. Ninguém percebe, e o dono não está por perto.
B08|p1|A falta de atenção do ciclista causou um dano.
B08|note|O caso indica um descuido; nem todo dano envolve culpa.
B09|case|Um rapaz oferece ajuda numa campanha de alimentos apenas para aparecer nas fotos e receber elogios, sem se importar com as famílias atendidas.
B09|p1|O rapaz procura elogios, não o bem das famílias.
B09|p2|A intenção é o objetivo de quem age e também precisa ser boa.
B09|p3|É preciso ajudar por cuidado com as pessoas, sem usá-las para se promover.
B09|q|Qual é a intenção do rapaz, e o que precisa mudar nela?
B09|note|O problema é buscar só os elogios, não sentir alegria ao recebê-los.
B10|p1|A presença dos filhos pode aumentar a humilhação do vizinho.
B10|p2|As circunstâncias podem aumentar ou diminuir a gravidade e a responsabilidade.
B10|q|Como a presença dos filhos interfere nessa situação?
B10|note|Insultar também seria errado sem os filhos por perto.
B11|q|Como a jovem pode responder à ajuda que pede a Deus?
B12|p1|Mesmo depois do Batismo, podemos sentir tentações.
B12|q|O que recebemos no Batismo, mesmo continuando a enfrentar tentações?
B13|case|Um jovem gastou sem permissão o dinheiro do irmão. Está arrependido e quer se confessar, mas sente vergonha de contar o que fez.
B13|p3|O jovem pode confessar com sinceridade e combinar a devolução do dinheiro.
B14|case|Uma jovem comunga na Missa. Ao chegar em casa, vê o avô com dificuldade para guardar as compras, mas prefere continuar no celular.
B14|p1|A jovem tem uma oportunidade de cuidar do avô.
B14|p3|A Comunhão chama a jovem a viver esse amor também no cuidado com o avô.
B14|note|A Eucaristia é presença de Cristo, não apenas uma lição de solidariedade.
B15|case|Uma jovem percebe que a tia, que mora sozinha, anda sem companhia. Reserva uma tarde para visitá-la e ouvir suas histórias.
B15|p2|Jesus nos chama a amar o próximo, procurando o seu bem.
B15|q|Como essa visita expressa o amor ao próximo?
B15|note|Amar envolve atenção às necessidades concretas do outro.
I02|case|Uma moradora recebe uma mensagem dizendo que o vizinho furta encomendas. Sem saber se é verdade, encaminha ao grupo do bairro “para alertar”.
I02|p3|A moradora deve esclarecer no grupo que repassou uma acusação sem confirmação.
I02|note|O caso trata de espalhar uma suspeita como se fosse um fato.
I03|q|Como o medo de exclusão pesa na escolha, sem tornar a zombaria correta?
I04|q|Por que dizer “foi sem querer” não elimina o descuido?
I05|case|Uma jovem prometeu buscar o irmão na escola. Vê que está na hora, mas continua conversando com os amigos e não avisa a família.
I05|p3|A jovem deve buscar o irmão; se houver um impedimento, precisa avisar a família.
I05|q|Por que continuar a conversa não é uma decisão que afeta só a jovem?
I06|case|Uma passageira vê uma senhora passar mal no ônibus. Pensa em avisar o motorista, mas vai adiando, esperando que outra pessoa tome a iniciativa.
I06|p1|A passageira percebe uma necessidade e deixa a ajuda para depois.
I06|q|Por que esperar que outro ajude pode ser uma omissão?
I07|case|Um adolescente quebra o fone do irmão e diz que o emprestou a um amigo. Quando o irmão pede o fone, inventa que o amigo viajou.
I07|p1|Para esconder o dano, o adolescente sustenta uma mentira com outra.
I08|case|Uma aluna empresta o caderno à amiga. Depois cobra: “Diga à minha mãe que estudamos juntas”, embora o encontro de estudo não tenha acontecido.
I08|q|Por que agradecer o empréstimo não obriga a amiga a mentir?
I09|case|O dono de uma loja ameaça demitir o funcionário se contar ao cliente que o produto tem defeito. O funcionário fica com medo de perder o emprego.
I09|q|Como a ameaça interfere na liberdade de escolha do funcionário?
I10|p3|O adolescente precisa assumir a falta e combinar um horário para encerrar o jogo.
I11|note|Quebrar o copo pode ser um acidente; culpar o inocente é outra questão.
I12|case|Uma jovem volta a mentir aos pais depois de ter confessado esse pecado. Sente vergonha de procurar o padre novamente e acha que não será perdoada.
I12|p3|A jovem pode voltar à Confissão com arrependimento e buscar ajuda para mudar.
I13|p1|O rapaz usa o pedido de desculpas para evitar a conversa sobre a mudança.
I14|p3|O colega novo deve recusar a fraude; quem a ensinou precisa corrigir a orientação.
I14|note|Escândalo, aqui, significa levar outra pessoa ao pecado.
I15|p1|A neta percebe o trabalho que ficou para a avó.
I15|q|Qual é o valor dessa ajuda, mesmo que ninguém a elogie?
N01|p3|O aluno deve fazer a prova com honestidade, mesmo que outros colem.
N01|q|Por que o costume da turma não justifica colar?
N02|p3|A jovem precisa retirar a ofensa, pedir desculpas e conversar com calma.
N03|p1|O rapaz espera esconder o furto porque a quantia é pequena.
N04|case|Uma voluntária quer arrecadar dinheiro para reformar um abrigo. Inventa que falta comida para conseguir mais doações e diz: “O importante é ajudar”.
N04|p3|A voluntária pode pedir doações explicando a necessidade real da reforma.
N05|case|Um rapaz quebra um vaso e manda o irmão mais novo pôr a culpa no gato. O irmão mente e depois se justifica: “Só obedeci”.
N05|q|Por que receber uma ordem não torna a mentira correta?
N06|p3|O pai pode buscar ajuda e aprender a conversar sem gritar.
N07|p3|O adolescente precisa desistir do furto, em vez de planejar o pecado e o perdão.
N09|case|Um visitante vê uma torneira aberta enchendo uma pia entupida. Pode fechá-la, mas vai embora dizendo: “Isso não é problema meu”.
N10|q|Por que evitar a briga não torna correta a alteração da nota?
N12|case|Ao vender uma bicicleta usada, um homem suspeita de um defeito no freio. Evita conferir para depois poder dizer que não sabia.
N12|p1|O vendedor evita confirmar um problema que já suspeita existir.
N13|p1|A perda de confiança faz a jovem pensar em desistir.
N13|p3|Dizer a verdade com constância pode ajudar a recuperar a confiança, mesmo levando tempo.
N15|case|Uma jovem reza para parar de ofender a irmã, mas insiste nas provocações. Quando a mãe pede que pare, responde: “Se Deus quiser, Ele me muda”.
G01|case|Durante uma discussão, um rapaz sente vontade de insultar o irmão. Recusa esse impulso e pede um tempo para se acalmar.
G01|p1|O impulso de ofender apareceu, mas não foi aceito.
G01|p2|Sentir uma tentação não é o mesmo que escolher ceder a ela.
G01|p3|O rapaz pode esperar se acalmar e retomar a conversa sem insultos.
G01|q|O que mostra que o rapaz não consentiu no impulso?
G02|note|A consciência também pode errar e precisa buscar a verdade.
G03|case|Um jovem prometeu ajudar o pai na feira. Ao receber um convite para jogar, tenta se convencer de que o pai não precisa tanto da ajuda.
G03|p1|A vontade de jogar leva o jovem a procurar uma desculpa.
G03|p3|O jovem precisa avaliar honestamente o compromisso, sem decidir só pelo desejo.
G03|q|O que o jovem deve considerar além da vontade de jogar?
G04|case|Uma bola rasga por um defeito de fabricação que ninguém havia percebido. Outra rasga porque um menino insiste em jogar perto do arame farpado, apesar dos avisos.
G04|p3|No segundo caso, mudar o local do jogo poderia evitar o dano.
G05|p1|Uma cozinheira não recebeu o aviso; a outra decidiu ignorá-lo.
G06|case|Um aluno mente para encobrir uma agressão porque recebeu ameaças. Outro mente sobre a mesma agressão por vontade própria, para proteger o amigo que bateu.
G06|p1|Os dois mentem, mas a ameaça limita a liberdade de um deles.
G06|p2|O medo pode diminuir ou até eliminar a culpa, sem tornar correta a mentira.
G06|p3|O aluno ameaçado precisa de proteção para poder contar o que aconteceu.
G06|q|Por que não podemos atribuir a mesma culpa aos dois alunos?
G06|note|Não exigir que a vítima enfrente sozinha quem a ameaça.
G08|p2|É preciso avaliar tanto o objetivo quanto a ação escolhida para alcançá-lo.
G08|q|Qual é o objetivo da jovem, e que ação escolheu para alcançá-lo?
G08|note|Querer ajudar uma amiga não justifica acusar uma inocente.
G09|case|Um rapaz quebra de propósito uma cadeira do irmão. Outro quebra uma cadeira ao sentar normalmente, sem saber que a madeira estava danificada.
G09|q|Por que o mesmo prejuízo não significa a mesma culpa?
G10|case|Ao se preparar para a Confissão, um jovem pergunta se todo pecado tem a mesma gravidade.
G10|p1|Todo pecado fere o amor, mas nem todos têm a mesma gravidade.
G10|p2|O mortal exige algo grave, saber que é grave e escolher fazê-lo livremente.
G10|p3|O venial envolve matéria leve ou falta de pleno conhecimento ou consentimento em matéria grave.
G10|q|Quais três condições precisam estar juntas para um pecado ser mortal?
G10|note|Sem escolha voluntária, pode não haver pecado, nem mesmo venial.
G11|p2|Praticar o bem forma virtudes; repetir escolhas más favorece os vícios.
G12|case|Um cliente devolve um produto furtado ao perceber a câmera. Diz que não vê problema em furtar, desde que ninguém descubra.
G12|p1|O cliente evita ser descoberto, mas continua aprovando o furto.
G12|p2|Arrepender-se é reconhecer o pecado e querer abandoná-lo.
G12|p3|Além de devolver, o cliente precisa rejeitar o furto e decidir não repeti-lo.
G12|note|O temor pode levar ao arrependimento; aqui, o furto continua aprovado.
G13|p3|Quem estragou o livro deve combinar como consertá-lo ou substituí-lo.
G13|note|A reparação cabe a quem causou o dano, conforme suas possibilidades.
G15|p2|Deus nos oferece sua graça e nos chama a responder livremente.
O02|case|Um adolescente quer vender um videogame pela internet. Um interessado pede dados pessoais e insiste em conversar sem os pais. O adolescente fica em dúvida.
O02|p1|O pedido de segredo e de dados pessoais exige cuidado.
O02|p3|Antes de enviar dados ou combinar a venda, o adolescente deve procurar um adulto de confiança.
O02|q|Por que é importante pedir orientação antes de continuar a conversa?
O03|p3|A jovem pode agradecer a Deus pelo bem e pedir perdão à mãe pela grosseria.
O04|p2|A Palavra de Deus ajuda a formar a consciência e orientar nossas escolhas.
O05|case|Uma aluna pede à amiga: “Diga à professora que entreguei o trabalho com você”. A amiga sabe que o trabalho não foi entregue.
O05|p3|A amiga pode dizer: “Não vou mentir. Posso ajudar você a conversar com a professora”.
O06|p1|O irmão conta só uma parte da discussão para parecer inocente.
O07|p2|É preciso corrigir a acusação diante de quem recebeu a informação falsa.
O08|case|Um rapaz derruba o violão que pegou emprestado e quebra o braço do instrumento. Quer reparar o dano, mas não consegue pagar tudo de uma vez.
O09|case|Um adolescente recebe mensagens de um colega exigindo dinheiro. O colega ameaça agredi-lo se contar à família, e o adolescente fica com medo de pedir ajuda.
O09|p3|O adolescente deve mostrar as mensagens a um adulto de confiança e pedir proteção.
O11|case|Uma jovem percebe que costuma entrar num grupo de mensagens para rir de ofensas contra colegas. Quer parar de participar dessas conversas.
O11|p1|A participação no grupo facilita a repetição da ofensa.
O12|case|Um pai reza para ter mais paciência com os filhos. Ao perceber que está ficando irritado, para um pouco antes de responder.
O12|p2|A ajuda de Deus fortalece nossa liberdade e pede nossa colaboração.
O13|q|Como anotar e conferir as tarefas pode ajudar a formar um bom hábito?
O14|p1|O anfitrião quer apoiar o amigo na decisão de não beber.
O15|p2|Uma recaída não impede o recomeço, mas pede arrependimento e mudança.
B01|note|A consciência julga também quando ninguém está olhando.
B02|note|Formar a consciência inclui corrigir julgamentos equivocados.
B03|note|A liberdade não torna todas as escolhas igualmente boas.
B05|note|Pagar pelo serviço é cumprir um dever de justiça.
B07|note|O lazer é bom; o excesso pode prejudicar outros bens.
B11|note|Deus nos ajuda antes mesmo de começarmos a mudar.
B12|note|Sentir uma tentação não é, por si só, cometer um pecado.
I04|note|Conhecer o risco e ignorar o aviso pode trazer responsabilidade.
I08|note|A gratidão não obriga a aceitar um pedido errado.
I13|note|Distinguir a dificuldade de mudar da recusa de tentar.
N05|note|Uma ordem errada e a pressão para obedecer são questões distintas.
N08|note|Quem repete a ofensa também contribui para o dano.
N12|note|O vendedor escolheu não esclarecer uma suspeita importante.
N13|note|A pessoa ofendida pode precisar de tempo para voltar a confiar.
G07|note|Corrigir a ação sem humilhar a pessoa.
G09|note|A gravidade do prejuízo, sozinha, não revela a culpa.
G15|note|A graça não elimina a necessidade de escolher e agir.
O02|note|Um bom conselho ajuda a avaliar, mesmo quando contraria nossa vontade.
O03|note|Rever o dia inclui reconhecer o bem, não apenas procurar falhas.
O04|note|Aplicar a Palavra à própria conduta, não só à do irmão.
O08|note|Combinar uma reparação que possa ser cumprida.
O12|note|Rezar não faz a irritação desaparecer automaticamente.
O14|note|Acolher o amigo sem expor sua dificuldade aos demais.
'''


def main():
    archive = ROOT / 'data/historico/antes_revisao_02'
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
    path.write_text(json.dumps(calls, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    path = ROOT / 'data/explicacoes.json'
    explanations = json.loads(path.read_text(encoding='utf-8'))
    for entry in explanations['entries']:
        entry['explanation'] = ' '.join(p['body'] for p in cards[entry['id']]['reading_points'])
    path.write_text(json.dumps(explanations, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'75 cartas relidas; {len(changed)} cartas ajustadas. Termos e cartelas preservados.')


if __name__ == '__main__':
    main()
