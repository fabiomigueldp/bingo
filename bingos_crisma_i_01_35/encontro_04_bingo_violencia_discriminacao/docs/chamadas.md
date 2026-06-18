# Banco de chamadas

Fonte estruturada: `data/chamadas.json`.

Este documento explica como usar e revisar as chamadas. Ele não duplica as 75 cartas para evitar divergência entre Markdown e JSON.

As falas-base para o catequista estão em `data/explicacoes.json` e são geradas no PDF `output/pdf/carta_explicacoes_catequista.pdf`.

## Função das chamadas

Cada chamada faz quatro coisas:

1. Apresenta um caso curto.
2. Dá ao catequista uma leitura objetiva do que o caso mostra.
3. Chama um código e termo da cartela.
4. Guarda uma pergunta de conferência para quando a equipe fechar linhas.

O caso não é uma pergunta para a turma adivinhar durante a rodada. Ele serve para dar carne ao conceito anunciado. A marcação depende do código anunciado, não da interpretação livre do caso.

A seção `Leitura do caso` é apoio para o catequista explicar rapidamente a carta. Ela não precisa ser lida como lista completa toda vez. O ideal é transformar os pontos em uma explicação breve, de 20 a 40 segundos. Na conferência, esses pontos ajudam a puxar respostas mais precisas.

## Formato

Cada carta segue este modelo:

```json
{
  "id": "N04",
  "term_id": "N04",
  "call_label": "N04 - Só repassei",
  "case": "Um vídeo humilhante circula. Quem enviou diz: 'Eu não gravei, só encaminhei'.",
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
  "anchors": ["CEC 1931"],
  "facilitator_note": "Trabalhar cooperação com o dano, mesmo sem autoria original."
}
```

Campos:

| Campo | Uso |
|---|---|
| `id` | Código da chamada; deve coincidir com o termo. |
| `term_id` | Referência ao termo em `data/termos.json`. |
| `call_label` | Texto revelado depois do caso. |
| `case` | Caso curto lido em voz alta. |
| `reading_points` | Pontos breves que explicam o que a cena mostra. |
| `conference_question` | Pergunta usada apenas na conferência da linha. |
| `anchors` | Base bíblica ou catequética. |
| `facilitator_note` | Nota curta para apoiar a condução do catequista. |

## Modo de leitura

Ritmo padrão:

```text
1. Sortear uma carta do baralho.
2. Anunciar o código e o conceito.
3. Ler o caso.
4. Explicar brevemente a relação entre caso e conceito.
5. Dar poucos segundos para marcação.
6. Seguir para a próxima chamada.
```

Exemplo:

```text
B01 - Imagem de Deus.

Caso:
No grupo, alguém diz que um colega "não serve para nada"
porque sempre atrapalha os trabalhos e jogos.

Explicação breve:
Aqui o erro é medir a pessoa pela utilidade dela para o grupo.
A fé cristã começa antes disso: essa pessoa tem dignidade
porque é imagem de Deus.
```

Outro exemplo:

```text
N04 - Só repassei.

Um vídeo humilhante circula. Quem enviou diz:
"Eu não gravei, só encaminhei."

Explicação breve:
Quem repassa aumenta o alcance da humilhação.
Não ter gravado não torna inocente o ato de circular.
```

Não transformar cada chamada em debate. A explicação deve ser curta. O discernimento maior entra quando uma equipe fecha duas linhas.

## Uso da leitura do caso

Na rodada normal:

```text
Anuncie código e conceito.
Leia o caso.
Explique a relação em 20 a 40 segundos.
As equipes marcam.
Siga.
```

Na conferência:

```text
Use a pergunta de conferência.
Se a equipe ficar vaga, use os pontos de leitura do caso para puxar a explicação.
```

Exemplo em B01:

- **Valor antes da utilidade:** a pessoa não vale pelo quanto ajuda, rende ou facilita a vida do grupo.
- **Desempenho não define dignidade:** atrapalhar ou ter limites não autoriza desprezo.
- **Primeiro olhar cristão:** antes de avaliar eficiência, a fé reconhece uma criatura amada por Deus.

Paráfrase possível:

```text
O valor de alguém não depende de ser útil para o meu grupo.
Mesmo quando a pessoa atrapalha ou tem limites, ela continua
tendo dignidade porque é ser humano criado à imagem de Deus.
```

Exemplo em B04:

- **A pessoa virou meio:** o colega virou conteúdo para render risada.
- **Critério errado:** a pergunta deveria ser se respeita a pessoa, não se diverte o grupo.
- **O erro começa antes do post:** a violência nasce quando a pessoa é medida pelo entretenimento que pode gerar.

Essa camada melhora a didática sem transformar a rodada em palestra.

## Conferência

Quando uma equipe fechar duas linhas válidas, horizontais, verticais ou diagonais:

1. Conferir os códigos chamados.
2. Escolher uma linha fechada.
3. Explicar pelo menos três conceitos dessa linha escolhida.
4. Usar as perguntas de conferência das respectivas cartas para validar as respostas.
5. Ligar ao menos um termo a Gn 1,27, Mt 25,40 ou CEC 1931-1940.

O centro livre já conta como casa marcada para completar linhas. Na conferência, porém, ele não conta como um dos três conceitos explicados.

As duas linhas podem se cruzar.

A resposta deve mostrar compreensão do conceito, com palavras próprias e, se ajudar, um exemplo simples. Não é necessário repetir o caso exato da carta.

Se a equipe acertou a cartela, mas não consegue explicar minimamente, dê uma segunda tentativa curta. Se a resposta continuar vazia ou confusa, a vitória fica suspensa até uma explicação suficiente ou até outra equipe fechar.

## Critérios de qualidade

Uma chamada boa:

- cabe em até 30 segundos;
- tem caso reconhecível por adolescentes;
- não depende de experiência pessoal real da turma;
- não ridiculariza uma vítima;
- não transforma a dinâmica em julgamento de pessoas concretas;
- chama um termo que é realmente a melhor chave interpretativa do caso;
- permite uma pergunta de conferência não óbvia;
- tem âncora clara no encontro.

Uma chamada fraca:

- vira palestra;
- apresenta uma resposta pronta demais;
- depende de vocabulário técnico sem caso concreto;
- usa situação extrema desnecessária;
- cria ambiguidade que pode virar discussão lateral;
- pede que adolescentes contem coisas pessoais.

## Revisão editorial recomendada

Antes de gerar PDFs, revisar as chamadas em quatro passadas:

1. **Clareza:** o caso é entendido em uma leitura?
2. **Justiça do bingo:** o código revelado resolve qualquer ambiguidade?
3. **Força catequética:** a carta ajuda a chegar em dignidade, caridade, solidariedade ou discriminação injusta?
4. **Segurança pastoral:** o caso evita exposição pessoal, acusação direta e gatilhos desnecessários?

## Observação sobre tom

As chamadas devem ser ditas em tom seco e sério. Não precisam soar dramáticas. O peso vem da situação e do discernimento, não de performance do catequista.
