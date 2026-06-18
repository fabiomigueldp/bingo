# Bingo — O problema das drogas

Dinâmica para o Encontro 05 da catequese: O problema das drogas.

Status editorial: **versão inicial importada**. O material já é estruturalmente válido e gera PDFs, mas ainda precisa de revisão editorial fina antes de ser tratado como edição 1.0 fechada.

## Fonte catequética

- Encontro: `projects/catequese/material_didatico/output/markdown/encontro_05.md`
- Tema: drogas, vícios, liberdade ferida, corpo como templo do Espírito Santo e proteção da família.
- Catecismo: CEC 2211; CEC 2291.
- Palavra: 1Cor 6,19-20.

Frase-síntese importada:

```text
As drogas ferem o corpo, escravizam a liberdade e atingem a família; por isso, cuidar da vida é glorificar a Deus no próprio corpo.
```

## Arquivos

- `data/termos.json`: fonte estruturada dos 75 termos.
- `data/chamadas.json`: fonte estruturada das 75 cartas de chamada.
- `data/explicacoes.json`: fonte estruturada das 75 explicações rápidas.
- `build.py`: gera PDFs, prévias e manifesto das cartelas.
- `validate.py`: valida estrutura, IDs, campos obrigatórios e centro livre.

## Validação

```powershell
python "projects/catequese/dinamicas/encontro_05_bingo_o_problema_das_drogas/validate.py"
```

Resultado atual:

```text
OK: 75 termos, 75 chamadas, 75 explicações, 15 termos por coluna, centro livre não chamável.
```

## Como gerar

```powershell
python "projects/catequese/dinamicas/encontro_05_bingo_o_problema_das_drogas/build.py"
```

## Artefatos gerados

- `output/cartelas_manifest.json`: manifesto das 24 cartelas.
- `output/pdf/cartelas_bingo_24_a4.pdf`: 24 cartelas, duas por A4.
- `output/pdf/baralho_chamadas_a4.pdf`: 75 cartas de chamada.
- `output/pdf/carta_explicacoes_catequista.pdf`: explicações rápidas.
- `output/pdf/cartoes_regras_equipes_a4.pdf`: cartões de regras.
- `output/pdf/folha_controle_chamadas.pdf`: folha de controle.
- `output/pdf/guia_conducao_bingo.pdf`: guia de condução.
- `output/pdf/kit_impressao_bingo_o_problema_das_drogas.pdf`: kit combinado.

## Edição das cartelas

- Quantidade: 24 cartelas.
- Seed: `404`.
- Gerador: `balanced-column-assignments-v1`.
- Centro livre: `LIVRE / 1Cor 6,19-20`.
- Identificador atual: `bingo_o_problema_das_drogas_24_seed_404_ac1977fd29b8`.

## Pendências editoriais

Antes de fechar como edição 1.0:

1. Revisar se todas as âncoras bíblicas auxiliares devem permanecer ou se convém concentrar o material em `1Cor 6,19-20`, CEC 2211 e CEC 2291.
2. Auditar pastoralmente os casos sensíveis: remédio sem receita, pornografia, ameaça, denúncia, menores, tráfico e tratamento.
3. Verificar se todos os termos têm linguagem suficientemente séria, concreta e não infantilizada.
4. Fazer leitura corrida das 75 explicações rápidas para cortar repetições e polir vocabulário.
5. Só depois marcar o material como edição 1.0 fechada.
