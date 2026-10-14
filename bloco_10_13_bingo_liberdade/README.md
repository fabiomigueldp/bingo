# Livres para escolher o bem

Bingo integrado dos encontros **10, 11, 12 e 13**, para a 1ª Fase da Crisma.
Jogo complementar: os quatro bingos individuais permanecem intactos.

## Material pronto

- `output/pdf/kit_impressao_bingo_liberdade_10_13.pdf`: kit completo.
- `output/pdf/cartelas_bingo_24_a4.pdf`: 24 cartelas, duas por folha A4.
- `output/pdf/baralho_chamadas_a4.pdf`: 75 cartas, oito por folha, impressão só na frente.
- `output/pdf/carta_explicacoes_catequista.pdf`: explicações curtas, organizadas por código.
- `output/pdf/cartoes_regras_equipes_a4.pdf`: regras para as mesas.
- `output/pdf/folha_controle_chamadas.pdf`: registro dos sorteios.
- `output/pdf/guia_do_catequista.pdf`: preparação, conferência e fechamento.
- `output/bingo_completo.md`: exportação de todo o conteúdo para revisão.

Uma cartela por pessoa ou equipe. Sorteie sem reposição. Leia código, termo, caso
e explicação rápida; use os três pontos da carta como alternativa à explicação,
sem ler ambos. As perguntas são para a conferência ou para esclarecer dúvidas.
Vence quem fecha duas linhas e explica três conceitos de uma delas, ligando pelo
menos um à fé. Não é necessário decorar referências. O centro livre conta para
fechar linha, mas não como conceito. Reserve aproximadamente 35 a 45 minutos;
o tempo varia conforme a turma e o sorteio.

## Decisões editoriais

Os materiais atuais dos quatro encontros e os quatro bingos anteriores foram
consultados. A seleção foi reescrita para servir ao bloco inteiro, em vez de
concatenar quatro baralhos. As cenas são fictícias; não são citações das fontes.

| Encontro | Conteúdos retomados |
| --- | --- |
| 10 | Juízo e formação da consciência; verdade; conselho; exame; cuidado com o outro. |
| 11 | Livre-arbítrio; compromissos; prudência, justiça, fortaleza e temperança; exercício da liberdade. |
| 12 | Ação, intenção e circunstâncias; omissão; acidente e descuido; responsabilidade; mortal e venial. |
| 13 | Graça e cooperação; vícios e conversão; Batismo, Reconciliação e Eucaristia; liberdade para servir. |

São 15 itens por coluna: B, fundamentos; I, situações; N, desculpas;
G, distinções; O, respostas concretas. Os títulos de leitura “Na cena”, “Critério”
e “Resposta” são marcadores estáveis de consulta, deliberadamente repetidos.
As narrativas falsas da coluna N são identificadas como erros pelo conjunto
caso/explicação; não são máximas propostas à turma.

As referências específicas ficam nos JSONs. Foram conferidos pelo índice local,
entre outros, os parágrafos sobre responsabilidade, intenção, consciência,
virtudes, contrição, reparação, graça e escândalo. As passagens Jo 8,31-36 e
Gl 5,13-16 foram consultadas pelo índice da Bíblia Ave-Maria. As demais passagens
centrais foram lidas nos materiais atuais. Não houve substituição de tradução.

Os excertos pontifícios presentes nos materiais orientaram a leitura do conjunto;
as cartas usam âncoras diretas na Bíblia e no CEC para facilitar a consulta.
Não se pedem relatos íntimos nem se tenta determinar a culpa interior de pessoas.

## Fontes e manutenção

### Cartelas impressas: conteúdo congelado

As primeiras dez cartelas já foram enviadas para impressão. Não alterar termos,
códigos, ordem, posições, identidade do conjunto nem os PDFs das cartelas.
`data/cartelas_impressas.lock.json` registra os arquivos e o manifesto congelados.
`build.py` passa a usar `build_textos.py`: atualiza apenas o baralho, as explicações,
o Markdown e o kit, reutilizando o PDF original das cartelas.

A revisão de 14/10/2026 apresenta os personagens antes de usar pronomes, substitui
situações vagas por acontecimentos concretos e sincroniza casos, explicações e
perguntas. O Batismo é relacionado à vida nova e à permanência das tentações,
conforme o encontro 13 e CEC 1264–1266. Os arquivos anteriores estão em
`data/historico/antes_revisao_2026_10_14/`; o TSV é o registro dessa revisão,
não uma segunda fonte canônica para futuras edições.

A segunda revisão releu os casos, os três pontos, as perguntas e as notas das
75 cartas; ajustou 69 e manteve I01, N11, N14, G14, O01 e O10. Corrigiu, entre
outros, a diferença entre tentação e consentimento (G01), pressão e culpa (G06),
pecado mortal e venial (G10) e medo da descoberta e arrependimento (G12).
As explicações rápidas acompanham os três pontos revisados. O registro está em
`revisao_editorial_02.py`, com cópias anteriores em `data/historico/antes_revisao_02/`.
Os scripts de revisão são registros históricos: não os execute para gerar PDFs.

A terceira revisão confrontou cada carta com o termo e a definição congelados,
e comparou sua função com as demais cartas. O registro completo, carta a carta,
está em `output/revisao_conjunto.md`. A revisão diferenciou os casos de B01 e I01,
aproximou G02 e O02 do discernimento moral e tornou G10 uma situação concreta.
Também ajustou personagens, respostas após erros já cometidos e a relação de B15
com a graça do Espírito Santo. As fontes anteriores estão preservadas em
`data/historico/antes_revisao_03/`.

Para atualizar os textos sem regenerar cartelas:

```powershell
python projects/catequese/dinamicas/bloco_10_13_bingo_liberdade/build_textos.py
```

`data/termos.json` permanece congelado. Para futuras revisões, edite somente
os textos de `data/chamadas.json` e `data/explicacoes.json`, sem alterar códigos
ou termos, e regenere os derivados:

```powershell
python projects/catequese/dinamicas/bloco_10_13_bingo_liberdade/build_textos.py
```

O motor gráfico deriva do bingo 10 e está isolado nesta pasta, com guia e
referências adaptados. As cartelas têm distribuição equilibrada e geração
determinística. O manifesto associa códigos, posições e hashes às fontes.
`data/fontes_sha256.json` registra os arquivos individuais e os quatro materiais
didáticos consultados, permitindo conferir sua preservação.

O bingo também integra o catálogo do PWA, ao lado dos 35 jogos individuais.
`teaching_encounters` identifica os quatro materiais compartilhados para leitura
e download no aplicativo. Não há cópias dos materiais didáticos nesta pasta.
