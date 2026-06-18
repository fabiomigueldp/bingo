# Revisão de game design

## Veredito

O projeto está fechado como edição 1.0 aplicável. As cartas de chamada existem em `data/chamadas.json`, e `build.py` gera cartelas, manifesto das cartelas, baralho de chamadas, folha de controle, cartões de regras, guia de condução e kit combinado. A base de design está correta: há um banco grande, colunas equilibradas, condição de vitória viável e uma mecânica de conferência que liga o bingo ao encontro.

## Pontos fortes

- O banco de 75 termos dá escala suficiente para cartelas reais.
- As cinco colunas impedem cartelas desequilibradas.
- A vitória por duas linhas evita que o jogo acabe rápido demais.
- A conferência final impede que o bingo vire apenas sorte.
- Os termos funcionam como vocabulário moral, não como frases motivacionais.
- As chamadas usam casos curtos e código revelado, preservando ritmo e justiça.
- A estrutura preserva o tema central do encontro: dignidade, discriminação injusta, caridade e solidariedade.

## Problemas corrigidos

### Centro duplicado

Havia uma duplicidade entre o centro fixo `Gn 1,27 / Imagem de Deus` e o termo `B01 - Imagem de Deus`.

Correção aplicada:

- o centro agora é `LIVRE / Gn 1,27`;
- o centro não entra no baralho de chamadas;
- `B01 - Imagem de Deus` permanece como termo chamável.

Isso preserva o centro teológico sem desperdiçar uma casa com repetição.

## Riscos restantes

### 1. Chamada passiva demais

Se o catequista simplesmente falar `N04 - Só repassei`, os grupos só procuram a casa na cartela. Isso é bingo puro, mas reduz o discernimento durante a rodada.

Solução recomendada:

- anunciar código e termo;
- ler o caso;
- explicar brevemente a relação entre caso e termo usando a Leitura do caso;
- permitir a marcação e seguir.

Assim, a marcação continua justa pelo código, mas cada carta produz uma pequena leitura moral concreta.

### 2. Debate longo demais

Se cada chamada virar conversa, o bingo morre. O debate deve ficar para a conferência.

Regra recomendada:

```text
Durante a rodada: conceito, caso e explicação breve.
Na conferência: explicação e discernimento.
```

### 3. Termos abstratos na coluna B

A coluna de base moral é necessariamente mais abstrata. Isso não é erro, mas as cartas de chamada dessa coluna precisam ter casos bons. Por exemplo, `Igual dignidade` não pode ser chamado com definição teórica; precisa aparecer em uma situação concreta.

### 4. Alguns termos precisam de cuidado de linguagem

Termos como `Capacitismo`, `Xenofobia`, `Caridade social` e `Justiça social` são corretos, mas podem exigir chamada mais clara para adolescentes de 12 anos. A carta de chamada deve explicar pelo caso, não por palestra.

## Duração provável

Simulação prática do modelo 5x5 com 75 termos, centro livre e diferentes quantidades de equipes:

| Equipes | Uma linha (média) | Duas linhas (média) |
|---|---:|---:|
| 4 | 31 chamadas | 42 chamadas |
| 6 | 28 chamadas | 39 chamadas |
| 8 | 27 chamadas | 38 chamadas |
| 10 | 26 chamadas | 37 chamadas |
| 12 | 25 chamadas | 36 chamadas |

Conclusão:

- uma linha é rápida demais para a maioria dos grupos;
- duas linhas é a melhor condição principal;
- cartela cheia deve ser descartada para encontro normal.

Na edição oficial com 24 cartelas disponíveis, a primeira conferência de duas linhas tende a aparecer por volta de 34 chamadas. Se forem usadas menos cartelas, a partida tende a durar um pouco mais.

## Regra de conferência recomendada

Quando uma equipe fecha duas linhas:

1. O catequista confere os códigos.
2. A equipe escolhe uma das linhas fechadas.
3. A equipe explica pelo menos três conceitos dessa linha escolhida.
4. Pelo menos um termo precisa ser ligado a Gn 1,27, Mt 25,40 ou CEC 1931-1940.
5. A resposta deve mostrar compreensão do conceito, com palavras próprias e, se ajudar, um exemplo simples. Não é necessário repetir o caso exato da carta.
6. Se a explicação for fraca, a equipe tem uma segunda tentativa curta.
7. Se ainda não conseguir, a vitória fica suspensa e o jogo continua.

O centro livre já conta como casa marcada para completar linhas. Na conferência, porém, ele não conta como um dos três conceitos explicados.

Essa regra mantém o jogo sério sem virar prova oral pesada.

## Critério de manutenção

Esta edição está fechada. Em revisão futura, não alterar termos, chamadas, número de cartelas, seed ou algoritmo sem tratar o resultado como nova edição e regenerar o manifesto das cartelas.

Se houver nova edição, cada chamada precisa continuar passando por quatro testes:

1. O caso é reconhecível por adolescentes.
2. O caso não expõe experiências pessoais.
3. O termo chamado é a melhor chave interpretativa para aquele caso.
4. A pergunta de conferência gera discernimento, não resposta óbvia.
