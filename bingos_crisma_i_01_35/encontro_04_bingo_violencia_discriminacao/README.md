# Bingo — Violência e discriminação

Dinâmica para o Encontro 04 da catequese: Violência e discriminação.

Este projeto produz um kit de bingo catequético para impressão: cartelas, baralho de chamadas, folha de controle, cartões de regras e guia do catequista. A proposta é um bingo real, com banco de termos consistente, cartelas equilibradas e chamadas que levam ao discernimento cristão sem infantilizar os adolescentes.

Status editorial: **edição 1.0 fechada**.

## Fonte catequética

- Encontro: `projects/catequese/material_didatico/output/markdown/encontro_04.md`
- Tema: violência e discriminação
- Catecismo: CEC 1931-1940
- Palavra: Gn 1,26-27; Mt 25,40

Fundamento do encontro:

```text
Todo ser humano possui igual dignidade diante de Deus; por isso, combater violência, discriminação e ódio é exigência concreta da caridade cristã.
```

## Arquivos

- `docs/arquitetura_bingo.md`: modelo matemático, formato das cartelas, critérios de vitória e fluxo do jogo.
- `docs/termos.md`: banco de termos em formato editorial, para leitura e revisão.
- `docs/chamadas.md`: método de leitura, conferência e revisão das chamadas.
- `docs/producao_fisica.md`: especificação de impressão, tamanho real das cartas e critério de corte.
- `docs/revisao_game_design.md`: avaliação de jogabilidade, riscos e critérios para avançar.
- `data/termos.json`: fonte estruturada dos termos para futura geração de cartelas e cartas de chamada.
- `data/chamadas.json`: fonte estruturada das 75 cartas de chamada.
- `data/explicacoes.json`: fonte estruturada das 75 explicações rápidas para o catequista.
- `build.py`: gera todos os PDFs e as prévias PNG.
- `validate.py`: checagem estrutural de termos, chamadas, explicações, colunas e centro livre.

## Validação

```powershell
python "projects/catequese/dinamicas/encontro_04_bingo_violencia_discriminacao/validate.py"
```

## Como gerar

```powershell
python "projects/catequese/dinamicas/encontro_04_bingo_violencia_discriminacao/build.py"
```

## PDFs gerados

- `output/pdf/cartelas_bingo_24_a4.pdf`: 24 cartelas, duas por folha A4.
- `output/pdf/baralho_chamadas_a4.pdf`: 75 cartas de chamada, oito por folha A4 paisagem.
- `output/pdf/carta_explicacoes_catequista.pdf`: documento de consulta com explicação breve para cada chamada.
- `output/pdf/cartoes_regras_equipes_a4.pdf`: seis cartões de regras para entregar às equipes.
- `output/pdf/folha_controle_chamadas.pdf`: folha para o catequista marcar os códigos chamados.
- `output/pdf/guia_conducao_bingo.pdf`: guia do catequista.
- `output/pdf/kit_impressao_bingo_violencia_discriminacao.pdf`: kit combinado para impressão.
- `output/cartelas_manifest.json`: manifesto oficial das 24 cartelas, usado como contrato para app companion.

Prévias visuais:

- `output/preview/*.png`

## Edição oficial das cartelas

- Quantidade: 24 cartelas.
- Seed: `404`.
- Gerador: `balanced-column-assignments-v1`.
- Manifesto: `output/cartelas_manifest.json`.
- Identificador atual: `bingo_violencia_discriminacao_24_seed_404_2536130b98d1`.

O manifesto contém a grade 5x5 completa de cada cartela, o centro livre, as 12 linhas possíveis, a ordem de impressão e hashes dos JSONs fonte. Para integração externa, o app companion deve usar o manifesto como fonte de verdade, não tentar reconstruir as cartelas apenas pela seed.

## Direção de design

O bingo não deve funcionar como uma atividade de frases bonitas. Ele deve funcionar como um jogo de reconhecimento moral da realidade.

Princípios:

- linguagem direta, sem slogans artificiais;
- nenhum convite a exposição de experiências pessoais;
- termos curtos, com peso conceitual real;
- chamadas baseadas em casos concretos;
- leitura objetiva do caso para apoiar o catequista;
- explicações rápidas para conduzir cada carta com clareza e unidade;
- conferência das marcações com justificativa;
- catequista conduzindo o discernimento, não moralizando cada chamada;
- equilíbrio entre doutrina, situações reais, autoenganos, discernimentos e respostas.
- baralho de chamadas em formato físico econômico, legível e cortável: oito cartas por A4 paisagem, com proporção de carta de jogo.

## Fluxo do jogo

1. O catequista embaralha o baralho de chamadas.
2. A cada rodada, pega a carta de cima e anuncia o código e o conceito, por exemplo: `B01 - Imagem de Deus`.
3. Lê o caso da carta.
4. Explica em poucos segundos como o caso se liga ao conceito, usando a seção `Leitura do caso` como apoio.
5. As equipes que tiverem o código na cartela marcam a casa.
6. O ciclo continua até uma equipe fechar pelo menos duas linhas válidas: horizontais, verticais ou diagonais.
7. Na conferência, a equipe escolhe uma das linhas fechadas e explica pelo menos três conceitos dessa linha escolhida.
8. O catequista usa as perguntas de conferência das cartas para validar a resposta.
9. A resposta deve mostrar compreensão do conceito, com palavras próprias e, se ajudar, um exemplo simples. Não é necessário repetir o caso exato da carta.
10. Se a explicação for fraca, a equipe recebe uma segunda tentativa curta. Se continuar vazia ou confusa, a vitória fica suspensa e o jogo continua.

As duas linhas podem se cruzar. O centro livre (`Gn 1,27`) já conta como casa marcada para completar linhas; na conferência, porém, ele não conta como um dos três conceitos explicados.

## Arquitetura resumida

Modelo recomendado:

- 75 termos totais;
- 5 colunas de 15 termos;
- cartela 5x5;
- centro livre marcado, ancorado em `Gn 1,27`;
- 24 casas sorteadas por cartela;
- vitória por duas linhas para dar tempo de jogo suficiente;
- conferência obrigatória antes de validar a vitória.

As cinco colunas são:

| Coluna | Nome | Função |
|---|---|---|
| B | Base moral | Fundamentos bíblicos e doutrinais |
| I | Injustiças concretas | Formas reais de violência e discriminação |
| N | Narrativas falsas | Desculpas e racionalizações que sustentam o erro |
| G | Discernimentos | Distinções morais que evitam simplificação |
| O | Orientações de resposta | Ações concretas, proporcionais e prudentes |

## Fechamento da edição 1.0

Esta edição está fechada como referência para impressão e aplicação. Alterações futuras em termos, chamadas, explicações, seed, número de cartelas ou algoritmo devem ser tratadas como nova edição, porque podem invalidar o manifesto usado pelo app companion.

Antes de aplicar, basta regenerar os arquivos se necessário:

```powershell
python "projects/catequese/dinamicas/encontro_04_bingo_violencia_discriminacao/validate.py"
python "projects/catequese/dinamicas/encontro_04_bingo_violencia_discriminacao/build.py"
```
