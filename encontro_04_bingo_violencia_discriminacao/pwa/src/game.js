import data from "./data/game-data.json";

export const COLUMN_ORDER = ["B", "I", "N", "G", "O"];

export const COLUMN_COLORS = {
  B: "var(--col-b)",
  I: "var(--col-i)",
  N: "var(--col-n)",
  G: "var(--col-g)",
  O: "var(--col-o)"
};

export const cardById = Object.fromEntries(data.cards.map((card) => [card.id, card]));
export const cardByCode = Object.fromEntries(data.cards.map((card) => [card.code, card]));
export const boardByNumber = Object.fromEntries(data.boards.map((board) => [board.number, board]));
export const columnByKey = Object.fromEntries(data.columns.map((column) => [column.key, column]));
export const DRAW_MODES = {
  APP: "app",
  MANUAL: "manual"
};

export const lineDefinitions = [
  ...Array.from({ length: 5 }, (_, row) => ({
    id: `row-${row}`,
    kind: "horizontal",
    label: `Linha ${row + 1}`,
    cells: COLUMN_ORDER.map((_, col) => [row, col])
  })),
  ...Array.from({ length: 5 }, (_, col) => ({
    id: `col-${col}`,
    kind: "vertical",
    label: `Coluna ${COLUMN_ORDER[col]}`,
    cells: Array.from({ length: 5 }, (_, row) => [row, col])
  })),
  {
    id: "diag-main",
    kind: "diagonal",
    label: "Diagonal principal",
    cells: Array.from({ length: 5 }, (_, index) => [index, index])
  },
  {
    id: "diag-alt",
    kind: "diagonal",
    label: "Diagonal secundária",
    cells: Array.from({ length: 5 }, (_, index) => [index, 4 - index])
  }
];

function randomIndex(maxExclusive) {
  if (maxExclusive <= 1) return 0;

  if (window.crypto?.getRandomValues) {
    const buffer = new Uint32Array(1);
    const range = 2 ** 32;
    const limit = range - (range % maxExclusive);

    do {
      window.crypto.getRandomValues(buffer);
    } while (buffer[0] >= limit);

    return buffer[0] % maxExclusive;
  }

  return Math.floor(Math.random() * maxExclusive);
}

export function shuffleDeck() {
  const deck = data.cards.map((card) => card.id);
  for (let index = deck.length - 1; index > 0; index -= 1) {
    const swapIndex = randomIndex(index + 1);
    [deck[index], deck[swapIndex]] = [deck[swapIndex], deck[index]];
  }
  return deck;
}

export function createGame(activeBoardNumbers, drawMode = DRAW_MODES.APP) {
  return {
    dataVersion: data.version,
    createdAt: Date.now(),
    drawMode,
    activeBoardNumbers: [...activeBoardNumbers].sort((a, b) => a - b),
    deck: drawMode === DRAW_MODES.MANUAL ? data.cards.map((card) => card.id) : shuffleDeck(),
    drawnIds: [],
    notifiedLineSignatures: {},
    alertQueue: [],
    validatedWins: []
  };
}

export function markedIdsFromDrawn(drawnIds) {
  return new Set([...drawnIds, "FREE"]);
}

export function getLineCells(board, line) {
  return line.cells.map(([row, col]) => board.grid[row][col]);
}

export function getCompletedLines(board, drawnIds) {
  const marked = markedIdsFromDrawn(drawnIds);
  return lineDefinitions
    .map((line) => {
      const cells = getLineCells(board, line);
      const complete = cells.every((cell) => marked.has(cell.id));
      return {
        ...line,
        cells,
        conceptCells: cells.filter((cell) => cell.id !== "FREE"),
        complete
      };
    })
    .filter((line) => line.complete);
}

export function getBoardProgress(board, drawnIds) {
  const marked = markedIdsFromDrawn(drawnIds);
  const cells = board.grid.flat();
  const markedCells = cells.filter((cell) => marked.has(cell.id)).length;
  const completedLines = getCompletedLines(board, drawnIds);
  return {
    markedCells,
    totalCells: cells.length,
    completedLines,
    ready: completedLines.length >= 2
  };
}

export function lineSignature(lines) {
  return lines
    .map((line) => line.id)
    .sort()
    .join("|");
}

export function collectReadyAlerts(game, drawnIds) {
  const notified = { ...game.notifiedLineSignatures };
  const alerts = [];

  for (const boardNumber of game.activeBoardNumbers) {
    const board = boardByNumber[boardNumber];
    const completedLines = getCompletedLines(board, drawnIds);
    if (completedLines.length < 2) continue;

    const signature = lineSignature(completedLines);
    const previous = new Set(notified[boardNumber] || []);
    if (previous.has(signature)) continue;

    previous.add(signature);
    notified[boardNumber] = [...previous];
    alerts.push({
      id: `${Date.now()}-${boardNumber}-${signature}`,
      boardNumber,
      lineIds: completedLines.map((line) => line.id),
      signature,
      drawIndex: drawnIds.length
    });
  }

  return { notified, alerts };
}

export function recomputeNotifications(activeBoardNumbers, drawnIds) {
  const notified = {};
  for (const boardNumber of activeBoardNumbers) {
    const board = boardByNumber[boardNumber];
    const completedLines = getCompletedLines(board, drawnIds);
    if (completedLines.length >= 2) {
      notified[boardNumber] = [lineSignature(completedLines)];
    }
  }
  return notified;
}

export function drawNext(game) {
  if (!game || game.deck.length === 0) return game;
  const [nextId, ...deck] = game.deck;
  const drawnIds = [...game.drawnIds, nextId];
  const { notified, alerts } = collectReadyAlerts(game, drawnIds);
  return {
    ...game,
    deck,
    drawnIds,
    notifiedLineSignatures: notified,
    alertQueue: [...game.alertQueue, ...alerts]
  };
}

export function drawCardById(game, cardId) {
  if (!game || !cardById[cardId] || game.drawnIds.includes(cardId)) return game;
  const drawnIds = [...game.drawnIds, cardId];
  const { notified, alerts } = collectReadyAlerts(game, drawnIds);
  return {
    ...game,
    deck: game.deck.filter((id) => id !== cardId),
    drawnIds,
    notifiedLineSignatures: notified,
    alertQueue: [...game.alertQueue, ...alerts]
  };
}

export function undoLastDraw(game) {
  if (!game || game.drawnIds.length === 0) return game;
  const drawnIds = game.drawnIds.slice(0, -1);
  const restored = game.drawnIds.at(-1);
  return {
    ...game,
    deck: [restored, ...game.deck],
    drawnIds,
    alertQueue: [],
    notifiedLineSignatures: recomputeNotifications(game.activeBoardNumbers, drawnIds)
  };
}

export function dismissAlertBatch(game, drawIndex) {
  return {
    ...game,
    alertQueue: game.alertQueue.filter((alert) => alert.drawIndex !== drawIndex)
  };
}

export function dismissBoardAlert(game, boardNumber, drawIndex) {
  return {
    ...game,
    alertQueue: game.alertQueue.filter((alert) => alert.boardNumber !== boardNumber || alert.drawIndex !== drawIndex)
  };
}

export function recordValidatedWin(game, boardNumber, lineId) {
  return {
    ...game,
    validatedWins: [
      ...game.validatedWins,
      {
        boardNumber,
        lineId,
        drawIndex: game.drawnIds.length,
        at: Date.now()
      }
    ]
  };
}

export function visibleLineType(kind) {
  if (kind === "horizontal") return "Horizontal";
  if (kind === "vertical") return "Vertical";
  return "Diagonal";
}

export default data;
