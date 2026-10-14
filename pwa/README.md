# Aplicativo integrado de bingo catequético

Este PWA conduz os 35 bingos individuais e o bingo integrado dos encontros 10 a 13.
Os JSONs `data/termos.json`, `chamadas.json` e `explicacoes.json` de cada encontro
são as fontes editoriais do jogo. `output/cartelas_manifest.json` define as
cartelas oficiais; o aplicativo não as reconstrói pela seed.

## Material didático compartilhado

O gerador lê diretamente `projects/catequese/material_didatico/output/encontro_NN.pdf`
e `output/markdown/encontro_NN.md`. Não há cópias didáticas por bingo.
Edite o JSON em `material_didatico/data/`, execute o build editorial correspondente
e depois o build do aplicativo. Não edite os bundles publicados em `public/content/`.

## Comandos na raiz do liturgia

```powershell
npm --prefix projects/catequese/dinamicas/pwa ci
npm --prefix projects/catequese/dinamicas/pwa run build
python projects/catequese/dinamicas/validar_integracao.py
npm --prefix projects/catequese/dinamicas/pwa run dev
```

`predev` e `prebuild` publicam automaticamente os dados e PDFs atuais.
As cópias em `public/content/`, `public/materials/`, `src/data/` e `dist/`
são artefatos gerados para distribuição/offline, não fontes editoriais duplicadas.

## Seleção e publicação

`pwa.config.json` usa caminhos relativos a `dinamicas/`; `contentCollection: "."`
descobre os 35 encontros. `additionalProjects` inclui jogos integrados sem substituir
os individuais. Os integrados declaram `teaching_encounters` em `termos.json`; o
aplicativo reúne os textos e oferece os PDFs de cada encontro do bloco.
`BINGO_CONTENT_DIR` permite selecionar outro encontro.
Para publicar, use `projects/catequese/dinamicas/pwa` como Root Directory na Vercel.
O `vercel.json` local define o build e a saída `dist/`. A integração local não altera
a configuração nem publica o projeto remoto automaticamente.

## Histórico

A migração e o histórico Git anterior estão em `docs/archives/bingo/`.

## Publicação pelo Git

O repositório conectado à Vercel é `fabiomigueldp/bingo`, branch `main`.
A fonte editorial permanece neste workspace. O repositório remoto recebe o PWA
e seus bundles gerados como distribuição, sem reconstruir dados a partir das
pastas antigas de encontros. O comando remoto `npm run build:published` compila
a interface e gera o service worker sobre esses bundles já validados.

Após o build e `validar_integracao.py`, execute `scripts/prepare-git-publish.py`
com o caminho de um clone limpo desse repositório. Revise o diff, faça commit e
push. Não copie `.env`, credenciais, `node_modules` nem `.vercel`.
