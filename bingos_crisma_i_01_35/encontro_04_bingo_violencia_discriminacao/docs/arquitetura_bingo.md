# Arquitetura do bingo

## Objetivo pedagógico

O objetivo não é fazer os catequizandos decorarem palavras contra violência. O objetivo é treinar leitura moral de situações concretas: reconhecer o que fere a dignidade humana, perceber as desculpas usadas para normalizar isso, distinguir casos parecidos e escolher respostas proporcionais.

O jogo deve preservar a energia de um bingo de verdade: sorteio, cartelas diferentes, tensão de fechamento, validação e possibilidade real de disputa. A catequese entra principalmente na conferência, não em interrupções longas a cada chamada.

## Problema a evitar

Um bingo ruim vira uma lista de mandamentos fofos. Isso mata a dinâmica por três motivos:

1. Os adolescentes percebem que o jogo é apenas pretexto para lição moral.
2. As casas ficam óbvias demais e não exigem discernimento.
3. O catequista perde a chance de trabalhar casos reais com precisão.

Por isso, as casas devem ser termos de análise, não frases de comportamento.

Exemplos fracos:

- "Ser uma pessoa boa"
- "Respeitar sempre"
- "Não fazer bullying"
- "Ajudar o colega"

Exemplos fortes:

- "Humilhação pública"
- "Culpar a vítima"
- "Brincadeira ou humilhação"
- "Corte de circulação"
- "Reparação pública"

## Modelo matemático

Usar um bingo de 75 termos, inspirado no modelo clássico:

- 5 colunas;
- 15 termos por coluna;
- 5 casas por coluna na cartela;
- coluna central com 4 termos sorteados e 1 centro fixo;
- 24 termos variáveis por cartela.

Quantidade teórica de cartelas:

```text
C(15,5)^4 x C(15,4)
```

Isso equivale a mais de `10^17` combinações possíveis. Na prática, é suficiente para gerar dezenas ou centenas de cartelas sem repetição relevante.

## Edição oficial das cartelas

A edição 1.0 usa:

- 24 cartelas;
- seed `404`;
- algoritmo `balanced-column-assignments-v1`;
- manifesto oficial em `output/cartelas_manifest.json`.

O manifesto registra a grade completa das cartelas, o centro livre, as 12 linhas possíveis e a ordem de impressão. Para integração com app companion, o manifesto é a fonte de verdade das cartelas.

## Por que separar por colunas

Se as cartelas fossem sorteadas de um único banco de 75 termos, algumas poderiam ficar concentradas demais em conceitos abstratos ou situações de violência. A separação por colunas obriga cada cartela a conter um equilíbrio mínimo:

- fundamento moral;
- problema concreto;
- autoengano;
- critério de discernimento;
- resposta possível.

Assim, quando uma equipe fechar uma linha, quase sempre terá uma combinação interpretável.

## Colunas

### B - Base moral

Termos que sustentam a visão cristã da pessoa humana. Sem essa coluna, o encontro vira apenas convivência civil ou campanha antibullying.

### I - Injustiças concretas

Formas reais de violência, exclusão, humilhação e discriminação. Esta coluna mantém o jogo ligado a situações que adolescentes reconhecem.

### N - Narrativas falsas

Desculpas, frases e mecanismos de grupo que normalizam o mal. Esta é uma coluna decisiva, porque muitos atos violentos sobrevivem como "brincadeira", "meme", "opinião" ou "todo mundo fez".

### G - Discernimentos

Pares de distinção. A ideia é evitar respostas simplistas: nem todo conflito é bullying, nem toda crítica é ataque, nem perdão significa impunidade, nem defesa justifica vingança.

### O - Orientações de resposta

Respostas concretas e verificáveis. Não são frases de bondade; são movimentos possíveis: cortar circulação, preservar prova, restituir reputação, recusar plateia, proteger sem atacar.

## Centro fixo

Centro recomendado:

```text
LIVRE
Gn 1,27
```

O centro fixo não entra no baralho de chamadas. Ele é um espaço livre, já marcado, que ancora a cartela na criação do ser humano à imagem de Deus. Isso evita duplicar o termo `B01 - Imagem de Deus` e preserva o centro como eixo teológico: qualquer linha atravessando o centro precisa ser interpretada a partir da igual dignidade humana.

## Condições de vitória

Opções:

| Condição | Uso | Avaliação |
|---|---|---|
| Uma linha | grupos grandes ou pouco tempo | rápido demais em muitos casos |
| Duas linhas | formato principal | melhor equilíbrio |
| Cartela cheia | encontro inteiro ou gincana | longo demais para uso normal |

Regra adotada: duas linhas horizontais, verticais ou diagonais.

Na edição oficial com 24 cartelas, simulações indicam primeira conferência de duas linhas por volta de 34 chamadas, com variação normal entre partidas. Isso deixa tempo suficiente para o jogo respirar sem consumir todo o encontro.

## Conferência

A vitória só vale depois da conferência.

Procedimento:

1. A equipe anuncia que fechou.
2. O catequista confere os códigos chamados.
3. A equipe escolhe uma das linhas fechadas.
4. A equipe explica três conceitos da linha escolhida.
5. Pelo menos uma explicação precisa ligar o termo a Gn 1,27, Mt 25,40 ou CEC 1931-1940.

As duas linhas podem se cruzar. O centro livre já conta como casa marcada para completar linhas, mas não substitui uma explicação. Se a linha passar pelo centro, a equipe ainda precisa explicar três conceitos da linha escolhida.

A resposta deve mostrar compreensão do conceito, com palavras próprias e, se ajudar, um exemplo simples. Não é necessário repetir o caso exato da carta.

Se a equipe não consegue explicar minimamente, a marcação física pode estar correta. Dê uma segunda tentativa curta; se a resposta continuar vazia ou confusa, a vitória fica suspensa até outra equipe fechar ou até a própria equipe formular melhor.

## Cartas de chamada

Cada termo terá uma carta de chamada com:

- código;
- termo;
- caso curto;
- leitura do caso;
- pergunta de conferência;
- âncora catequética;
- nota do catequista.

### Modo de chamada

O modo recomendado é em quatro movimentos:

1. O catequista sorteia uma carta e anuncia o código e o termo.
2. Lê o caso curto.
3. Explica em poucos segundos como o caso materializa o conceito, usando a seção `Leitura do caso`.
4. As equipes marcam o código, se ele estiver na cartela.

Isso preserva a justiça do bingo, porque a marcação depende do código chamado, mas impede que a carta vire apenas sorteio seco de palavras. O caso e a leitura do caso dão conteúdo catequético sem transformar a rodada em palestra.

Exemplo:

```text
Chamada:
N04 - Só repassei

Caso:
Um vídeo humilhante aparece no grupo. Quem enviou diz: "Eu não gravei, só encaminhei."

Explicação breve:
Quem repassa aumenta o alcance da humilhação. Não ter gravado não torna inocente o ato de circular.
```

Não convém deixar a marcação depender da interpretação do caso, porque várias cartas podem tocar temas parecidos. O código chamado é o que torna o jogo justo.

Exemplo de estrutura usada em `data/chamadas.json`:

```json
{
  "id": "N04",
  "term": "Só repassei",
  "case": "Um vídeo humilhante aparece no grupo. Quem enviou diz: 'Eu não gravei, só encaminhei.'",
  "reading_points": [
    {
      "title": "Cooperação com o dano",
      "body": "Quem repassa aumenta o alcance da humilhação."
    },
    {
      "title": "Neutralidade falsa",
      "body": "Não ter gravado não torna inocente o ato de circular."
    }
  ],
  "conference_question": "Por que repassar também participa da violência?",
  "anchors": ["CEC 1931", "Mt 25,40"],
  "facilitator_note": "Trabalhar a diferença entre autoria original e cooperação com a humilhação."
}
```

## Critérios para aceitar um termo

Um termo entra no banco se:

- cabe em uma casa de bingo;
- é compreensível por adolescentes;
- permite uma carta de chamada concreta;
- ajuda a ler uma situação real;
- não é apenas uma ordem moral genérica;
- pode ser explicado sem expor história pessoal;
- tem ligação possível com o encontro 4.

Um termo deve sair ou ser reescrito se:

- soa como slogan;
- depende de linguagem infantilizada;
- é amplo demais para gerar caso;
- é técnico demais para catequese;
- cria ambiguidade pastoral desnecessária;
- favorece exposição de vítimas ou acusações pessoais.

## Ritmo de aplicação

Tempo total recomendado: 40 a 50 minutos.

1. Abertura: 5 minutos.
2. Explicação das regras: 3 minutos.
3. Rodada de bingo: 20 a 25 minutos, com chamadas de no máximo 40 segundos.
4. Conferência da primeira equipe: 5 minutos.
5. Rodada curta até segunda linha ou segunda equipe: 5 a 8 minutos.
6. Fechamento: 5 minutos.

## Tom de condução

O catequista deve manter tom sério, simples e direto. Não é necessário teatralizar o tema. Violência e discriminação já são assuntos fortes; a dinâmica deve dar forma, vocabulário e critério para pensar, não tentar parecer divertida a todo custo.
