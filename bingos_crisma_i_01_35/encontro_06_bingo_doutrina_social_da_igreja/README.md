# Bingo — Doutrina Social da Igreja

Dinâmica para o Encontro 06 da catequese: Doutrina Social da Igreja.

Status editorial: **versão inicial importada**. O material já é estruturalmente válido e gera PDFs, mas ainda precisa de revisão editorial fina antes de ser tratado como edição 1.0 fechada.

## Fonte catequética

- Encontro: `projects/catequese/material_didatico/output/markdown/encontro_06.md`
- Tema: Doutrina Social da Igreja, trabalho, economia, bens terrenos, justiça social, bem comum e idolatria da riqueza.
- Catecismo: CEC 2419-2442, com ênfase nos parágrafos usados no encontro.
- Palavra: Mt 6,24.

Frase-síntese importada:

```text
A Doutrina Social da Igreja ensina que a economia, o trabalho, a política e os bens terrenos devem servir à pessoa humana, ao bem comum e a Deus, nunca à idolatria da riqueza.
```

## Arquivos

- `data/termos.json`: fonte estruturada dos 75 termos.
- `data/chamadas.json`: fonte estruturada das 75 cartas de chamada.
- `data/explicacoes.json`: fonte estruturada das 75 explicações rápidas.
- `build.py`: gera PDFs, prévias e manifesto das cartelas.
- `validate.py`: valida estrutura, IDs, campos obrigatórios e centro livre.

## Validação

```powershell
python "projects/catequese/dinamicas/encontro_06_bingo_doutrina_social_da_igreja/validate.py"
```

Resultado atual:

```text
OK: 75 termos, 75 chamadas, 75 explicações, 15 termos por coluna, centro livre não chamável.
```

## Como gerar

```powershell
python "projects/catequese/dinamicas/encontro_06_bingo_doutrina_social_da_igreja/build.py"
```

## Artefatos gerados

- `output/cartelas_manifest.json`: manifesto das 24 cartelas.
- `output/pdf/cartelas_bingo_24_a4.pdf`: 24 cartelas, duas por A4.
- `output/pdf/baralho_chamadas_a4.pdf`: 75 cartas de chamada.
- `output/pdf/carta_explicacoes_catequista.pdf`: explicações rápidas.
- `output/pdf/cartoes_regras_equipes_a4.pdf`: cartões de regras.
- `output/pdf/folha_controle_chamadas.pdf`: folha de controle.
- `output/pdf/guia_conducao_bingo.pdf`: guia de condução.
- `output/pdf/kit_impressao_bingo_doutrina_social_da_igreja.pdf`: kit combinado.

## Edição das cartelas

- Quantidade: 24 cartelas.
- Seed: `404`.
- Gerador: `balanced-column-assignments-v1`.
- Centro livre: `LIVRE / Mt 6,24`.
- Identificador atual: `bingo_doutrina_social_da_igreja_24_seed_404_ebf6cea02fa5`.

## Pendências editoriais

Antes de fechar como edição 1.0:

1. Revisar se todas as âncoras bíblicas e catequéticas auxiliares devem permanecer ou se convém concentrar mais o material nos parágrafos do encontro.
2. Decidir se âncoras internas como `B04`, `B10` e `G09` devem permanecer como referências cruzadas ou ser substituídas por Bíblia/CEC.
3. Auditar casos que envolvem política, voto, exploração, denúncia, protesto, mercado e pobreza para evitar confusão partidária ou simplificação ideológica.
4. Fazer leitura corrida das 75 explicações rápidas para cortar repetições e polir vocabulário.
5. Só depois marcar o material como edição 1.0 fechada.
