# Bingo — Relacionamento humano

Edição canônica de excelência do bingo do Encontro 09 da 1ª Fase da Crisma.

## Proveniência

O conteúdo didático é produzido no projeto `liturgia` a partir da fonte editorial tipada:

- `projects/catequese/material_didatico/data/encontro_09.json`

O script upstream `projects/catequese/material_didatico/build_encontro_09.py` gera, a partir dessa mesma fonte:

- `projects/catequese/material_didatico/output/encontro_09.pdf`;
- `projects/catequese/material_didatico/output/markdown/encontro_09.md`.

As cópias importadas e consumidas por este projeto ficam em `material_didatico/`. A resposta-modelo que originou a edição do bingo foi preservada em `sources/` para auditoria. Os hashes dessas fontes locais são gravados no manifesto das cartelas.

## Fontes de verdade

- `data/termos.json`: 75 conceitos do bingo;
- `data/chamadas.json`: casos, três pontos de leitura, pergunta e nota de condução;
- `data/explicacoes.json`: explicações rápidas para o catequista;
- `material_didatico/`: cópia sincronizada dos materiais gerados no projeto `liturgia`;
- `output/cartelas_manifest.json`: edição oficial das 24 cartelas.

O PWA deve consumir o manifesto e os JSONs publicados pelo build. Não deve reconstruir as cartelas apenas pela seed.

## Modelo pedagógico

As colunas cumprem funções diferentes:

- B — base moral;
- I — situações concretas;
- N — narrativas falsas;
- G — discernimentos;
- O — orientações de resposta.

A vitória recomendada exige duas linhas. Na conferência, a equipe escolhe uma linha completa, explica pelo menos três conceitos e relaciona ao menos um deles a Jo 15,12-15, CEC 357 ou CEC 2843.

Não se solicitam relatos pessoais. Menções a abuso, violência, ameaça ou risco grave devem ser acolhidas com discrição e encaminhadas conforme o protocolo de proteção da comunidade. Perdão não elimina proteção, justiça ou reparação; reconciliação não pode ser imposta.

## Gerar e validar

```powershell
python "bingos_crisma_i_01_35/encontro_09_bingo_relacionamento_humano/validate.py"
python "bingos_crisma_i_01_35/encontro_09_bingo_relacionamento_humano/build.py"
python "bingos_crisma_i_01_35/encontro_09_bingo_relacionamento_humano/qa.py"
```

O QA verifica dimensões A4, quantidade de páginas, 75 códigos únicos, oito cartas por folha, fonte mínima de 6,8 pt, ausência de overflow, equilíbrio das cartelas e sincronização dos hashes.
