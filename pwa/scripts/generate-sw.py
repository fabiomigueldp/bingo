from __future__ import annotations

import json
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
BOOTSTRAP_DATA = ROOT / "src" / "data" / "bootstrap-data.json"


def web_path(path: Path) -> str:
    return "./" + path.relative_to(DIST).as_posix()


def collect_precache(default_content_id: str) -> list[str]:
    exact_paths = [
        "index.html",
        "manifest.webmanifest",
        "icon.svg",
        "favicon.ico",
        "favicon-16x16.png",
        "favicon-32x32.png",
        "icons/apple-touch-icon.png",
        "icons/icon-192.png",
        "icons/icon-512.png",
        "icons/maskable-192.png",
        "icons/maskable-512.png",
        "content/catalog.json",
        f"content/{default_content_id}/game-data.json",
    ]

    files = [DIST / path for path in exact_paths]
    files.extend(path for path in DIST.glob("assets/*") if path.is_file() and path.suffix != ".map")

    missing = [path for path in files if not path.is_file()]
    if missing:
        missing_paths = ", ".join(path.relative_to(DIST).as_posix() for path in missing)
        raise SystemExit(f"Missing required precache files: {missing_paths}")

    paths = ["./"]
    paths.extend(web_path(path) for path in sorted(set(files)))
    return paths


def cache_fingerprint(paths: list[str]) -> str:
    digest = hashlib.sha256()
    for web_file in paths:
        if web_file == "./":
            path = DIST / "index.html"
        else:
            path = DIST / web_file.removeprefix("./")
        if not path.exists() or not path.is_file():
            continue
        digest.update(web_file.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()[:12]


def main() -> None:
    if not DIST.exists():
        raise SystemExit("dist does not exist. Run vite build before generate-sw.py.")

    if not BOOTSTRAP_DATA.exists():
        raise SystemExit(f"Bootstrap data does not exist: {BOOTSTRAP_DATA}")

    bootstrap = json.loads(BOOTSTRAP_DATA.read_text(encoding="utf-8"))
    default_content_id = bootstrap["defaultContentId"]
    version = bootstrap.get("defaultItem", {}).get("cardSetId", default_content_id)
    precache = collect_precache(default_content_id)
    cache_version = f"{version}-{cache_fingerprint(precache)}"

    sw = f"""const CACHE_PREFIX = "bingo-pwa-";
const CACHE_NAME = `${{CACHE_PREFIX}}{cache_version}`;
const APP_SHELL = {json.dumps(precache, indent=2)};

function responseForCache(response) {{
  const headers = new Headers(response.headers);
  [
    "connection",
    "content-encoding",
    "content-length",
    "keep-alive",
    "transfer-encoding",
    "vary"
  ].forEach((header) => headers.delete(header));
  return new Response(response.body, {{
    status: response.status,
    statusText: response.statusText,
    headers
  }});
}}

self.addEventListener("install", (event) => {{
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) =>
        Promise.all(
          APP_SHELL.map(async (url) => {{
            const response = await fetch(url, {{ cache: "reload" }});
            if (!response.ok) throw new Error(`Precache failed: ${{url}} (${{response.status}})`);
            await cache.put(url, responseForCache(response));
          }})
        )
      )
      .then(() => self.skipWaiting())
  );
}});

self.addEventListener("activate", (event) => {{
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((key) => key.startsWith(CACHE_PREFIX) && key !== CACHE_NAME)
            .map((key) => caches.delete(key))
        )
      )
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
          caches
            .open(CACHE_NAME)
            .then((cache) => cache.put("./index.html", responseForCache(copy)))
            .catch(() => {{}});
          return response;
        }})
        .catch(() => caches.match("./index.html", {{ ignoreVary: true }}).then(
          (home) => home || caches.match("./", {{ ignoreVary: true }})
        ))
    );
    return;
  }}

  if (requestUrl.pathname.endsWith(".json")) {{
    event.respondWith(
      fetch(event.request)
        .then((response) => {{
          if (!response || response.status !== 200 || response.type === "opaque") return response;
          const copy = response.clone();
          caches
            .open(CACHE_NAME)
            .then((cache) => cache.put(event.request, responseForCache(copy)))
            .catch(() => {{}});
          return response;
        }})
        .catch(() => caches.match(event.request, {{ ignoreSearch: true, ignoreVary: true }}))
    );
    return;
  }}

  event.respondWith(
    caches.match(event.request, {{ ignoreSearch: true, ignoreVary: true }}).then((cached) => {{
      if (cached) return cached;

      return fetch(event.request).then((response) => {{
        if (!response || response.status !== 200 || response.type === "opaque") return response;
        const copy = response.clone();
        caches
          .open(CACHE_NAME)
          .then((cache) => cache.put(event.request, responseForCache(copy)))
          .catch(() => {{}});
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
