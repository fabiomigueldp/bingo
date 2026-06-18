# Template de bingo catequético

Este template define a estrutura mínima para criar um novo bingo catequético seguindo `../metodologia_bingo_catequese.md`.

## Como usar

Forma recomendada:

```powershell
python "projects/catequese/dinamicas/criar_bingo_catequese.py" 05 "Tema do encontro"
```

Isso cria a pasta do novo bingo, ajusta os metadados iniciais dos JSONs e copia `build.py` do bingo consolidado. O `validate.py` já faz parte do template.

Forma manual:

1. Copie esta pasta para uma nova pasta de encontro, por exemplo:

```text
encontro_05_bingo_<tema>/
```

2. Preencha os arquivos em `data/`:

- `termos.json`;
- `chamadas.json`;
- `explicacoes.json`.

3. Copie para a nova pasta o gerador físico reutilizável do bingo já consolidado:

- `build.py`;

4. Rode:

```powershell
python "projects/catequese/dinamicas/encontro_XX_bingo_<tema>/validate.py"
python "projects/catequese/dinamicas/encontro_XX_bingo_<tema>/build.py"
```

## Fonte de verdade

- O material didático do encontro governa doutrinalmente o tema.
- Os JSONs são a fonte canônica do bingo.
- PDFs, prévias e Markdown derivado são artefatos regeneráveis.

## Critério editorial

Não preencher o template com frases bonitas. Cada termo precisa gerar:

- caso concreto;
- leitura moral;
- pergunta de conferência;
- explicação rápida;
- ligação com a fé.
