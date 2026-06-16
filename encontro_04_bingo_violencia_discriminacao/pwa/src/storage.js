import data from "./data/game-data.json";

const STORAGE_KEY = "bingo-violencia-discriminacao-state";

export function loadSavedGame() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (parsed?.dataVersion !== data.version) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function saveGame(game) {
  if (!game) {
    localStorage.removeItem(STORAGE_KEY);
    return;
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(game));
}
