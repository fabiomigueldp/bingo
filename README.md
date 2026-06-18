# Bingo Catequese

Repositório do PWA companion e dos bingos canônicos da Crisma I.

## Estrutura

- `bingos_crisma_i_01_35/`: coleção canônica dos bingos dos encontros 01 a 35.
- `pwa/`: app único, independente de encontro, usado para conduzir qualquer bingo canônico.
- `vercel.json`: configuração de deploy a partir da raiz do repositório.

Cada bingo canônico deve manter este contrato:

- `data/termos.json`: banco de 75 termos.
- `data/chamadas.json`: 75 cartas de chamada.
- `data/explicacoes.json`: 75 explicações rápidas.
- `material_didatico/material_didatico_encontro_NN.md`: conteúdo de apoio ao catequista, derivado do PDF do encontro.
- `material_didatico/material_didatico_encontro_NN.pdf`: PDF completo do material didático do encontro.
- `output/cartelas_manifest.json`: fonte oficial das 24 cartelas, linhas válidas, ordem de impressão e hashes.
- `output/pdf/`: materiais de impressão.

O PWA nunca deve reconstruir cartelas pela seed. A fonte de verdade é sempre
`output/cartelas_manifest.json`.

Durante o build, `pwa/scripts/generate-game-data.py` publica os PDFs em
`pwa/public/materials/` e grava o Markdown didático em `src/data/game-data.json`
como `teachingMaterial`. A interface deve consumir esse payload, não ler arquivos
do encontro diretamente.

## Trocar o Bingo Ativo

Edite `pwa/pwa.config.json`:

```json
{
  "contentProject": "bingos_crisma_i_01_35/encontro_04_bingo_violencia_discriminacao"
}
```

Ou use variável de ambiente:

```powershell
$env:BINGO_CONTENT_DIR = "bingos_crisma_i_01_35/encontro_09_bingo_relacionamento_humano"
npm --prefix pwa run build
```

## Validar

Validar um bingo:

```powershell
python "bingos_crisma_i_01_35/encontro_04_bingo_violencia_discriminacao/validate.py"
```

Validar todos:

```powershell
Get-ChildItem "bingos_crisma_i_01_35" -Directory | ForEach-Object {
  Push-Location $_.FullName
  python validate.py
  Pop-Location
}
```

Build do PWA:

```powershell
npm --prefix pwa run build
```
