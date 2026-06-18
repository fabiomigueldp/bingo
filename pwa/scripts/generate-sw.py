from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
GAME_DATA = ROOT / "src" / "data" / "game-data.json"


def web_path(path: Path) -> str:
    return "./" + path.relative_to(DIST).as_posix()


def collect_precache() -> list[str]:
    patterns = [
        "index.html",
        "manifest.webmanifest",
        "icon.svg",
        "favicon.ico",
        "favicon-16x16.png",
        "favicon-32x32.png",
        "assets/*",
        "icons/*",
        "materials/*",
        "screenshots/*",
        "splash/*",
    ]
    files: list[Path] = []
    for pattern in patterns:
        files.extend(path for path in DIST.glob(pattern) if path.is_file() and path.suffix != ".map")

    content_dir = DIST / "content"
    if content_dir.exists():
        files.extend(path for path in content_dir.rglob("*") if path.is_file() and path.suffix != ".map")

    paths = ["./"]
    paths.extend(web_path(path) for path in sorted(set(files)))
    return paths


def main() -> None:
    if not DIST.exists():
        raise SystemExit("dist does not exist. Run vite build before generate-sw.py.")

    precache = collect_precache()
    version = "dev"
    if GAME_DATA.exists():
        version = json.loads(GAME_DATA.read_text(encoding="utf-8")).get("version", version)

    sw = f"""const CACHE_NAME = "bingo-pwa-{version}";
const APP_SHELL = {json.dumps(precache, indent=2)};

self.addEventListener("install", (event) => {{
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)).then(() => self.skipWaiting())
  );
}});

self.addEventListener("activate", (event) => {{
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
  );
}});

self.addEventListener("message", (event) => {{
  if (event.data?.type === "SKIP_WAITING") self.skipWaiting();
}});

self.addEventListener("fetch", (event) => {{
  if (event.request.method !== "GET") return;

  const requestUrl = new URL(event.request.url);
  if (requestUrl.origin !== self.location.origin) return;

  if (event.request.mode === "navigate") {{
    event.respondWith(
      fetch(event.request)
        .then((response) => {{
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put("./index.html", copy));
          return response;
        }})
        .catch(() => caches.match("./index.html").then((home) => home || caches.match("./")))
    );
    return;
  }}

  event.respondWith(
    caches.match(event.request, {{ ignoreSearch: true }}).then((cached) => {{
      if (cached) return cached;

      return fetch(event.request).then((response) => {{
        if (!response || response.status !== 200 || response.type === "opaque") return response;
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
        return response;
      }});
    }})
  );
}});
"""
    (DIST / "sw.js").write_text(sw, encoding="utf-8")
    print(f"Generated dist/sw.js with {len(precache)} precached entries")


if __name__ == "__main__":
    main()
