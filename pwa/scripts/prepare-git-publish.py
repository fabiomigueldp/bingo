"""Copy a validated PWA distribution to the existing Git deployment repository."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]


def main():
    target = Path(sys.argv[1]).resolve()
    remote = subprocess.check_output(["git", "-C", str(target), "remote", "get-url", "origin"], text=True).strip()
    if remote not in {"https://github.com/fabiomigueldp/bingo.git", "git@github.com:fabiomigueldp/bingo.git"}:
        raise SystemExit(f"Unexpected deployment repository: {remote}")
    if subprocess.check_output(["git", "-C", str(target), "status", "--porcelain"], text=True).strip():
        raise SystemExit("Deployment checkout must be clean before preparation.")
    subprocess.run([sys.executable, str(SOURCE.parent / "validar_integracao.py")], check=True)
    app = target / "pwa"
    # Copy only the reviewed application and public distribution, never credentials.
    for directory in ("src", "public", "scripts"):
        shutil.copytree(SOURCE / directory, app / directory, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for filename in ("package.json", "package-lock.json", "index.html", "vite.config.js", "pwa.config.json", "PRODUCT.md", "README.md"):
        if (SOURCE / filename).exists():
            shutil.copy2(SOURCE / filename, app / filename)
    config = json.loads((SOURCE / "vercel.json").read_text(encoding="utf-8"))
    config.update(buildCommand="cd pwa && npm ci && npm run build:published", outputDirectory="pwa/dist")
    (target / "vercel.json").write_text(json.dumps(config, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    ignore = target / ".gitignore"
    content = ignore.read_text(encoding="utf-8")
    content = "\n".join(line for line in content.splitlines() if line.strip() != "pwa/public/content/") + "\n"
    ignore.write_text(content, encoding="utf-8")
    (target / "PUBLICACAO.md").write_text(
        "# Publicação do bingo\n\n"
        "A fonte editorial está em liturgia/projects/catequese/dinamicas.\n"
        "Este repositório recebe o PWA e os bundles gerados para deploy por push em main.\n"
        "Use npm run build:published em pwa; não regenere com as pastas históricas.\n"
        "Os materiais publicados em pwa/public são derivados; edite as fontes no liturgia.\n"
        "A preparação é feita pelo script prepare-git-publish.py do workspace liturgia.\n",
        encoding="utf-8")
    print(f"Prepared deployment snapshot in {target}")


if __name__ == "__main__":
    main()
