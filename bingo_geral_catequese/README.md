# Conhecer e viver a fé

Bingo de catequese geral para Primeira Eucaristia e Crisma. O centro é Jesus Cristo: a fé que professamos, celebramos, vivemos e rezamos. O conjunto é próprio, sem vínculo com um encontro numerado.

São 75 chamadas, 15 por coluna, e 24 cartelas de 5×5. O centro livre remete a Jo 14,6. Cada chamada contém caso, três pontos de leitura, pergunta de conferência, referências e nota de condução. As explicações rápidas reúnem os mesmos três pontos, para evitar versões diferentes da mesma carta.

## Uso

Leia código, termo, caso e explicação rápida. A equipe marca pelo código. Na conferência, depois de completar duas linhas, escolhe uma delas, explica três conceitos e relaciona ao menos um à fé cristã. Aceite palavras próprias; não exija decorar definições ou referências. Quem ainda está aprendendo a ler pode jogar em equipe com apoio.

O guia de uma página apresenta preparação, ritmo, conferência e fechamento. Os casos são fictícios e não pedem relatos pessoais.

## Arquivos

| Arquivo em `output/pdf/` | Conteúdo |
|---|---|
| `cartelas_bingo_24_a4.pdf` | 24 cartelas, duas por folha; 12 páginas |
| `baralho_chamadas_a4.pdf` | 75 cartas para recortar; 10 páginas |
| `carta_explicacoes_catequista.pdf` | Explicações rápidas por código; 6 páginas |
| `cartoes_regras_equipes_a4.pdf` | Regras para as mesas; 1 página |
| `folha_controle_chamadas.pdf` | Controle dos sorteios; 1 página |
| `guia_do_catequista.pdf` | Orientações de condução; 1 página |
| `kit_impressao_bingo_geral_catequese.pdf` | Todos os arquivos acima; 31 páginas |

Imprima apenas as cartelas necessárias. O baralho deve ser impresso só na frente. `output/bingo_completo.md` reúne os 75 textos para leitura e revisão.

## Organização editorial

A arquitetura segue `../metodologia_bingo_catequese.md` e as diretrizes do gerador de prompts. Os nomes das colunas foram adaptados, mantendo suas funções:

| Coluna | Função |
|---|---|
| B — Fundamentos da fé | Conteúdo central da fé cristã |
| I — Situações concretas | A fé diante de cenas da vida |
| N — Ideias equivocadas | Enganos a esclarecer pela explicação |
| G — Discernimentos | Distinções que evitam confusões |
| O — Fé em prática | Respostas concretas e possíveis |

O escopo geral substitui a vinculação a um encontro específico por um panorama próprio. Não foram criadas cópias dos materiais didáticos dos encontros.

## Fontes e cobertura

Foram consultados o Diretório de Catequese local, a Bíblia Ave-Maria e o Catecismo da Igreja Católica pelos índices do projeto. Cada carta identifica suas referências; casos e explicações são redação didática, não transcrições literais.

| Núcleo | Cartas principais |
|---|---|
| Pai, Filho, Espírito Santo; Trindade e criação | B01–B05 |
| Ressurreição, fé e vida eterna | B06, B08, B15, G01–G02, G11 |
| Palavra de Deus, Igreja, Maria e santos | B07, B09, G09–G10, N08–N09, O01 |
| Batismo, Crisma, Eucaristia e Reconciliação | B10–B13, N04, G15, O03–O04 |
| Unção dos Enfermos, Matrimônio e Ordem | I14, G13–G14 |
| Domingo, Missa e participação | I08, N05, G08, G14 |
| Oração e Pai-Nosso | B14, I09, N01, N07, N14, O02, O05 |
| Mandamentos, consciência, liberdade, pecado e conversão | G03–G07, N06, N13, N15, O06–O07, O15 |
| Dignidade, justiça, verdade, caridade e criação | I01–I07, I10–I13, I15, N03, N10, O08–O12 |
| Santidade, vocação, serviço e testemunho | G12, O13–O14 |

Na revisão conjunta, foram preservadas distinções essenciais: a vida cristã nasce da graça; os sacramentos são ação de Cristo; a Eucaristia é presença real; o sofrimento não prova falta de fé; perdoar não exige aceitar abuso; honrar Maria e os santos não é adorá-los.

## Edição e geração

As fontes canônicas são `data/termos.json`, `data/chamadas.json` e `data/explicacoes.json`. O panorama do aplicativo fica em `data/panorama.json`. `data/editorial.tsv` e `preparar_editorial.py` registram a importação inicial: não os execute sobre uma revisão posterior dos JSONs.

Na raiz de `liturgia`:

```powershell
python projects/catequese/dinamicas/bingo_geral_catequese/build.py
python projects/catequese/dinamicas/pwa/scripts/generate-game-data.py
```

O primeiro comando exporta o Markdown, gera as cartelas com semente fixa `171026`, registra o manifesto e produz os PDFs. O segundo distribui o material no PWA. Depois de encaminhar cartelas para impressão, preserve seus termos, códigos, distribuição e ordem nas próximas revisões.

Para revisar apenas os textos das cartas, preservando o PDF, a distribuição e a identidade das cartelas já publicadas:

```powershell
python projects/catequese/dinamicas/bingo_geral_catequese/build.py --somente-textos
python projects/catequese/dinamicas/pwa/scripts/generate-game-data.py
```

## Revisão editorial de 17/10/2026

As 75 cartas foram relidas como conjunto de termo, definição, caso, explicação, pergunta e nota. A revisão substituiu cenas artificiais, esclareceu ações e personagens, simplificou frases e corrigiu perguntas que não correspondiam ao caso. Os códigos e os termos impressos permanecem os mesmos.

Entre as mudanças: B01 passou a tratar do medo de procurar Deus depois de mentir; N08, do uso de "não julgar" para evitar uma correção; O05, da relação entre o Pai-Nosso e ajudar um vizinho; G08 recebeu uma explicação direta sobre atenção e participação na Missa. I13 trata da renúncia à vingança, enquanto G05 trata da reconstrução da confiança. As novas referências foram consultadas nos índices locais da Bíblia e do Catecismo.

`data/editorial.tsv` e `preparar_editorial.py` preservam a criação inicial e não contêm esta revisão. A versão atual está nos JSONs canônicos e em `output/bingo_completo.md`.

O aplicativo apresenta este bingo como **Catequese geral — Conhecer e viver a fé**, com seu próprio panorama. A publicação utiliza o repositório existente e o deploy automático por push.
