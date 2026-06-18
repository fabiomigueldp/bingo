const SELECTED_CONTENT_KEY = "bingo-pwa-selected-content";

function storageKeyFor(data) {
  return `bingo-pwa-state:${data.cardSetId || data.version || data.slug}`;
}

export function loadSelectedContentId() {
  try {
    return localStorage.getItem(SELECTED_CONTENT_KEY);
  } catch {
    return null;
  }
}

export function saveSelectedContentId(contentId) {
  try {
    if (contentId) localStorage.setItem(SELECTED_CONTENT_KEY, contentId);
  } catch {
    // Sem armazenamento persistente, o app continua com o conteúdo padrão.
  }
}

export function loadSavedGame(data) {
  try {
    const raw = localStorage.getItem(storageKeyFor(data));
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (parsed?.dataVersion !== data.version) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function saveGame(data, game) {
  try {
    const key = storageKeyFor(data);
    if (!game) {
      localStorage.removeItem(key);
      return;
    }
    localStorage.setItem(key, JSON.stringify(game));
  } catch {
    // O estado local é conveniência, não requisito para conduzir o bingo.
  }
}
