import { useEffect, useMemo, useRef, useState } from "react";
import data, {
  COLUMN_COLORS,
  COLUMN_ORDER,
  DRAW_MODES,
  boardByNumber,
  cardByCode,
  cardById,
  columnByKey,
  createGame,
  dismissAlertBatch,
  dismissBoardAlert,
  drawCardById,
  drawNext,
  getBoardProgress,
  getCompletedLines,
  lineDefinitions,
  recordValidatedWin,
  undoLastDraw,
  visibleLineType
} from "./game";
import { loadSavedGame, saveGame } from "./storage";

function Icon({ name }) {
  const common = { width: 22, height: 22, viewBox: "0 0 24 24", fill: "none", "aria-hidden": "true" };
  if (name === "undo") {
    return (
      <svg {...common}>
        <path d="M9.5 7H5v-4.5" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M5.4 7.2A8 8 0 1 1 4 12" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" />
      </svg>
    );
  }
  if (name === "list") {
    return (
      <svg {...common}>
        <path d="M8 7h11M8 12h11M8 17h11" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" />
        <path d="M4.5 7h.1M4.5 12h.1M4.5 17h.1" stroke="currentColor" strokeWidth="3.3" strokeLinecap="round" />
      </svg>
    );
  }
  if (name === "grid") {
    return (
      <svg {...common}>
        <path d="M5 5h5v5H5zM14 5h5v5h-5zM5 14h5v5H5zM14 14h5v5h-5z" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
      </svg>
    );
  }
  if (name === "spark") {
    return (
      <svg {...common} viewBox="0 0 24 24">
        {/* Main curved star */}
        <path 
          d="M12 3 Q12 12 21 12 Q12 12 12 21 Q12 12 3 12 Q12 12 12 3 Z" 
          fill="currentColor"
        />
        {/* Secondary medium curved star */}
        <path 
          d="M18.5 5.5 Q18.5 7 20 7 Q18.5 7 18.5 8.5 Q18.5 7 17 7 Q18.5 7 18.5 5.5 Z" 
          fill="currentColor"
          opacity="0.85"
        />
        {/* Tertiary small curved star */}
        <path 
          d="M6.5 15.5 Q6.5 17 8 17 Q6.5 17 6.5 18.5 Q6.5 17 5 17 Q6.5 17 6.5 15.5 Z" 
          fill="currentColor"
          opacity="0.7"
        />
        {/* Floating stardust dots */}
        <circle cx="8" cy="6" r="0.75" fill="currentColor" opacity="0.6" />
        <circle cx="16" cy="16" r="0.75" fill="currentColor" opacity="0.8" />
        <circle cx="5" cy="9" r="0.5" fill="currentColor" opacity="0.5" />
      </svg>
    );
  }
  if (name === "x") {
    return (
      <svg {...common}>
        <path d="M6.5 6.5l11 11M17.5 6.5l-11 11" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" />
      </svg>
    );
  }
  if (name === "check") {
    return (
      <svg {...common}>
        <path d="M5 12.5l4.2 4.1L19 7" stroke="currentColor" strokeWidth="2.1" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  }
  if (name === "lightbulb") {
    return (
      <svg {...common} viewBox="0 0 24 24">
        <path
          d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A5.5 5.5 0 0 0 7.5 8c0 1.3.5 2.6 1.5 3.5.8.8 1.3 1.5 1.5 2.5"
          stroke="currentColor"
          strokeWidth="1.9"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path d="M9 18h6" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M10 22h4" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  }
  return null;
}

function renderRich(text) {
  return text.split("**").map((part, index) => {
    if (index % 2) return <strong key={`${part}-${index}`}>{part}</strong>;
    return <span key={`${part}-${index}`}>{part}</span>;
  });
}

function SetupScreen({ onStart }) {
  const [selection, setSelection] = useState([]);
  const [drawMode, setDrawMode] = useState(DRAW_MODES.APP);
  const [isStarting, setIsStarting] = useState(false);
  const startTimer = useRef(null);
  const selected = selection.length;

  useEffect(() => {
    return () => {
      if (startTimer.current) window.clearTimeout(startTimer.current);
    };
  }, []);

  function toggle(number) {
    setSelection((current) =>
      current.includes(number) ? current.filter((item) => item !== number) : [...current, number].sort((a, b) => a - b)
    );
  }

  function startGame() {
    if (!selected || isStarting) return;

    const selectedBoards = [...selection];
    const selectedMode = drawMode;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    setIsStarting(true);

    startTimer.current = window.setTimeout(() => {
      onStart(selectedBoards, selectedMode);
    }, reduceMotion ? 0 : 180);
  }

  return (
    <main className={isStarting ? "setup-screen starting" : "setup-screen"}>
      <section className="setup-hero" aria-labelledby="setup-title">
        <h1 id="setup-title">Bingo</h1>
        <p>Violência e discriminação</p>
      </section>

      <section className="board-picker" aria-label="Cartelas da partida">
        <div className="picker-head">
          <span>{selected} cartelas</span>
          <div className="picker-actions">
            <button type="button" onClick={() => setSelection(data.boards.map((board) => board.number))}>
              Todas
            </button>
            <button type="button" onClick={() => setSelection([])}>
              Limpar
            </button>
          </div>
        </div>

        <div className="board-grid">
          {data.boards.map((board) => {
            const isSelected = selection.includes(board.number);
            return (
              <button
                type="button"
                key={board.number}
                className={isSelected ? "board-button selected" : "board-button"}
                onClick={() => toggle(board.number)}
                aria-pressed={isSelected}
              >
                {board.number.toString().padStart(2, "0")}
              </button>
            );
          })}
        </div>
      </section>

      <section className="call-mode-picker" aria-label="Forma de chamada">
        <div className="mode-head">
          <span>Chamada</span>
        </div>
        <div className="mode-options" role="group" aria-label="Escolher forma de chamada">
          <button
            type="button"
            className={drawMode === DRAW_MODES.APP ? "mode-option selected" : "mode-option"}
            onClick={() => setDrawMode(DRAW_MODES.APP)}
            aria-pressed={drawMode === DRAW_MODES.APP}
          >
            <strong>App sorteia</strong>
          </button>
          <button
            type="button"
            className={drawMode === DRAW_MODES.MANUAL ? "mode-option selected" : "mode-option"}
            onClick={() => setDrawMode(DRAW_MODES.MANUAL)}
            aria-pressed={drawMode === DRAW_MODES.MANUAL}
          >
            <strong>Globo físico</strong>
          </button>
        </div>
      </section>

      <div className="setup-footer">
        <button
          className={`primary-action${selected ? " ready" : ""}${isStarting ? " starting" : ""}`}
          type="button"
          disabled={!selected}
          aria-busy={isStarting}
          onClick={startGame}
        >
          Iniciar jogo
        </button>
      </div>
    </main>
  );
}

function EmptyCard({ drawMode = DRAW_MODES.APP }) {
  const manualMode = drawMode === DRAW_MODES.MANUAL;
  return (
    <article className="call-card card-back" aria-label={manualMode ? "Aguardando bolinha" : "Baralho pronto"}>
      <div className="back-line" />
      <div className="back-symbol">
        <span>B</span>
        <span>I</span>
        <span>N</span>
        <span>G</span>
        <span>O</span>
      </div>
      <div className="back-title">{manualMode ? "Aguardando bolinha" : "Baralho pronto"}</div>
      <div className="back-subtitle">{manualMode ? "registre o código sorteado" : "75 cartas de chamada"}</div>
    </article>
  );
}

function CallCard({ card, drawCount, drawMode }) {
  if (!card) return <EmptyCard drawMode={drawMode} />;
  const columnColor = COLUMN_COLORS[card.column];

  return (
    <article
      key={`${card.id}-${drawCount}`}
      className="call-card card-front"
      style={{ "--card-accent": columnColor }}
      aria-label={`${card.code}, ${card.label}`}
    >
      <div className="card-sheen" aria-hidden="true" />
      <header className="card-head">
        <span className="code-chip">{card.code}</span>
        <span className="column-label">{columnByKey[card.column]?.title}</span>
      </header>

      <div className="card-section concept-section">
        <span className="field-label">Conceito</span>
        <h2>{card.label}</h2>
      </div>

      <div className="card-rule" aria-hidden="true" />

      <div className="card-section">
        <span className="field-label">Caso</span>
        <p>{card.case}</p>
      </div>

      <div className="card-section">
        <span className="field-label">Explicação</span>
        <p>{renderRich(card.explanation)}</p>
      </div>

      <div className="support-section">
        <div className="support-head">
          <Icon name="lightbulb" />
          <span className="support-title-label">Apoio de condução</span>
        </div>
        <ol className="support-list">
          {card.readingPoints.map((point) => (
            <li key={point.title}>
              <strong>{point.title}:</strong> {point.body}
            </li>
          ))}
        </ol>
        {card.conferenceQuestion && (
          <div className="conference-question">
            {card.conferenceQuestion}
          </div>
        )}
      </div>

      <footer className="card-foot">
        {card.anchors.map((anchor) => (
          <span key={anchor}>{anchor}</span>
        ))}
      </footer>
    </article>
  );
}

function CardFlight({ exitingCard, enteringCard, drawCount, phase }) {
  return (
    <div className={`card-flight ${phase}`} aria-hidden={phase === "dealing"}>
      {exitingCard && phase === "dealing" ? (
        <div className="flight-card exit-card">
          <CallCard card={exitingCard} drawCount={`exit-${drawCount}`} />
        </div>
      ) : null}
      <div className="flight-card enter-card">
        <CallCard card={enteringCard} drawCount={`enter-${drawCount}`} />
      </div>
    </div>
  );
}

function TopBar({ game, currentCard, onOpenBoards }) {
  const progress = game.drawnIds.length / data.cards.length;
  return (
    <header className="topbar">
      <div>
        <div className="app-title">Bingo</div>
        <div className="round-text">
          {game.drawnIds.length} de {data.cards.length}
          {currentCard ? ` · ${currentCard.code}` : ""}
        </div>
      </div>
      <button className="icon-button board-status" type="button" onClick={onOpenBoards} aria-label="Cartelas em jogo">
        <Icon name="grid" />
        <span>{game.activeBoardNumbers.length}</span>
      </button>
      <div className="progress-track" aria-hidden="true">
        <span style={{ transform: `scaleX(${progress})` }} />
      </div>
    </header>
  );
}

function BottomControls({ game, onUndo, onDraw, onHistory, busy = false }) {
  const hasDrawn = game.drawnIds.length > 0;
  const finished = game.deck.length === 0;
  return (
    <nav className="bottom-controls" aria-label="Controles da rodada">
      <button className="tool-button" type="button" onClick={onUndo} disabled={!hasDrawn || busy}>
        <Icon name="undo" />
        <span>Voltar</span>
      </button>
      <button className={busy ? "draw-button dealing" : "draw-button"} type="button" onClick={onDraw} disabled={finished || busy}>
        <span>{hasDrawn ? (finished ? "Baralho completo" : "Próxima carta") : "Sortear carta"}</span>
      </button>
      <button className="tool-button" type="button" onClick={onHistory} disabled={!hasDrawn || busy}>
        <Icon name="list" />
        <span>Histórico</span>
      </button>
    </nav>
  );
}

function ManualCallControls({ game, onUndo, onCall, onHistory, busy = false }) {
  const [activeColumn, setActiveColumn] = useState("");
  const lastColumnRef = useRef("");
  if (activeColumn && activeColumn !== lastColumnRef.current) {
    lastColumnRef.current = activeColumn;
  }
  const renderColumn = activeColumn || lastColumnRef.current;
  
  const [lastCode, setLastCode] = useState("");
  const [pulseKey, setPulseKey] = useState(0);
  const hasDrawn = game.drawnIds.length > 0;
  const drawnSet = useMemo(() => new Set(game.drawnIds), [game.drawnIds]);
  const finished = game.drawnIds.length >= data.cards.length;
  const numbers = useMemo(() => Array.from({ length: 15 }, (_, index) => (index + 1).toString().padStart(2, "0")), []);
  const currentCode = game.drawnIds.length ? cardById[game.drawnIds.at(-1)]?.code || "" : "";
  const displayCode = activeColumn || lastCode || "...";
  const ballState = activeColumn ? "selecting" : lastCode ? "called" : "idle";
  const ballColumn = activeColumn || (lastCode ? lastCode[0] : "");
  const ballAccentColor = ballColumn ? COLUMN_COLORS[ballColumn] : "oklch(92% 0.015 80)";

  useEffect(() => {
    setLastCode(currentCode);
    if (!currentCode) setActiveColumn("");
  }, [currentCode]);

  function chooseColumn(column) {
    setActiveColumn((current) => (current === column ? "" : column));
  }

  function columnAvailable(column) {
    return numbers.some((number) => {
      const card = cardByCode[`${column}${number}`];
      return card && !drawnSet.has(card.id);
    });
  }

  function submitNumber(number) {
    if (!activeColumn || busy) return;
    const code = `${activeColumn}${number}`;
    const card = cardByCode[code];
    if (!card || drawnSet.has(card.id)) return;

    onCall(card.id);
    setLastCode(code);
    setActiveColumn("");
    setPulseKey((current) => current + 1);
  }

  return (
    <nav className={activeColumn ? "manual-controls expanded" : "manual-controls"} aria-label="Registrar chamada física">
      <div className="manual-control-head">
        <button className="tool-button" type="button" onClick={onUndo} disabled={!hasDrawn || busy}>
          <Icon name="undo" />
          <span>Voltar</span>
        </button>

        <div className="manual-ball-wrap" aria-live="polite">
          <div
            key={pulseKey}
            className={`manual-ball ${ballState}`}
            style={{ "--ball-accent": ballAccentColor }}
          >
            <strong>{displayCode}</strong>
          </div>
        </div>

        <button className="tool-button" type="button" onClick={onHistory} disabled={!hasDrawn || busy}>
          <Icon name="list" />
          <span>Histórico</span>
        </button>
      </div>

      <div
        className="manual-pad"
        aria-label="Código da bolinha"
        style={{ "--pad-accent": ballAccentColor }}
      >
        <div className="manual-columns" aria-label="Letra da bolinha">
          {COLUMN_ORDER.map((column) => (
            <button
              type="button"
              key={column}
              className={activeColumn === column ? "manual-column selected" : "manual-column"}
              onClick={() => chooseColumn(column)}
              disabled={busy || finished || !columnAvailable(column)}
              aria-pressed={activeColumn === column}
              aria-label={`Letra ${column}`}
            >
              <span>{column}</span>
            </button>
          ))}
        </div>

        <div className="manual-numbers-shell" aria-hidden={!activeColumn}>
          <div className="manual-numbers" aria-label="Número da bolinha">
            {numbers.map((number) => {
              const card = renderColumn ? cardByCode[`${renderColumn}${number}`] : null;
              const used = card ? drawnSet.has(card.id) : false;
              // Provide a fallback disabled state if no active column
              const isActuallyDisabled = busy || !activeColumn || used;
              return (
                <button
                  type="button"
                  key={number}
                  className={used ? "manual-number used" : "manual-number"}
                  onClick={() => submitNumber(number)}
                  disabled={isActuallyDisabled}
                  aria-label={renderColumn ? `${renderColumn}${number}` : `Número ${number}`}
                >
                  {number}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}

function BottomSheet({ title, children, onClose, className = "" }) {
  const [closing, setClosing] = useState(false);
  const [drag, setDrag] = useState(0);
  const [dragging, setDragging] = useState(false);
  const gesture = useRef(null);
  const closeTimer = useRef(null);
  const suppressClick = useRef(false);

  function closeSheet(resetDrag = true) {
    if (closing) return;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduceMotion) {
      onClose();
      return;
    }
    setClosing(true);
    if (resetDrag) setDrag(0);
    closeTimer.current = window.setTimeout(onClose, 180);
  }

  function startGesture(clientY, target, pointerId = null) {
    if (closing) return false;
    if (target.closest("button:not(:disabled), a, input, textarea, select")) return false;

    gesture.current = {
      startY: clientY,
      lastY: clientY,
      startTime: performance.now(),
      active: false,
      pointerId,
      scrollEl: target.closest(".history-list, .boards-list")
    };
    return true;
  }

  function moveGesture(clientY, event) {
    const current = gesture.current;
    if (!current) return;

    const delta = clientY - current.startY;
    current.lastY = clientY;

    if (delta <= 0) {
      if (current.active) {
        setDrag(0);
        if (event?.cancelable !== false) event?.preventDefault?.();
      }
      return;
    }

    if (current.scrollEl && current.scrollEl.scrollTop > 1) return;

    if (delta > 6 || current.active) {
      current.active = true;
      suppressClick.current = delta > 10;
      setDragging(true);
      setDrag(Math.min(delta, 190));
      if (event?.cancelable !== false) event?.preventDefault?.();
    }
  }

  function endGesture() {
    const current = gesture.current;
    if (!current) return;

    const elapsed = Math.max(performance.now() - current.startTime, 1);
    const travel = Math.max(0, current.lastY - current.startY);
    const velocity = travel / elapsed;
    const shouldClose = current.active && (travel > 56 || (travel > 28 && velocity > 0.42));

    gesture.current = null;
    setDragging(false);

    if (shouldClose) {
      closeSheet(false);
    } else {
      setDrag(0);
    }
  }

  function beginTouch(event) {
    if (event.touches.length !== 1) return;
    startGesture(event.touches[0].clientY, event.target);
  }

  function moveTouch(event) {
    if (event.touches.length !== 1) return;
    moveGesture(event.touches[0].clientY, event);
  }

  function beginPointer(event) {
    if (event.pointerType === "touch") return;
    if (startGesture(event.clientY, event.target, event.pointerId)) {
      event.currentTarget.setPointerCapture?.(event.pointerId);
    }
  }

  function movePointer(event) {
    if (event.pointerType === "touch") return;
    moveGesture(event.clientY, event);
  }

  function endPointer(event) {
    if (event.pointerType === "touch") return;
    endGesture();
  }

  function beginMouse(event) {
    if (event.button !== 0) return;
    startGesture(event.clientY, event.target);
  }

  function moveMouse(event) {
    moveGesture(event.clientY, event);
  }

  function endMouse() {
    endGesture();
  }

  function captureClick(event) {
    if (!suppressClick.current) return;
    suppressClick.current = false;
    event.preventDefault();
    event.stopPropagation();
  }

  useEffect(() => {
    function onKeyDown(event) {
      if (event.key === "Escape") closeSheet();
    }
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      if (closeTimer.current) window.clearTimeout(closeTimer.current);
    };
  }, []);

  return (
    <div className={closing ? "sheet-layer closing" : "sheet-layer"} role="presentation">
      <button className="sheet-backdrop" type="button" aria-label="Fechar" onClick={closeSheet} />
      <section
        className={`bottom-sheet ${dragging ? "dragging" : ""} ${className}`}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        style={{ "--sheet-drag": `${drag}px` }}
        onClickCapture={captureClick}
        onTouchStart={beginTouch}
        onTouchMove={moveTouch}
        onTouchEnd={endGesture}
        onTouchCancel={endGesture}
        onPointerDown={beginPointer}
        onPointerMove={movePointer}
        onPointerUp={endPointer}
        onPointerCancel={endPointer}
        onMouseDown={beginMouse}
        onMouseMove={moveMouse}
        onMouseUp={endMouse}
        onMouseLeave={endMouse}
      >
        <div className="grabber" aria-hidden="true" />
        <header className="sheet-head">
          <h2>{title}</h2>
          <button className="icon-button" type="button" onClick={closeSheet} aria-label="Fechar">
            <Icon name="x" />
          </button>
        </header>
        {children}
      </section>
    </div>
  );
}

function HistorySheet({ game, onClose, onNewGame }) {
  const cards = [...game.drawnIds].reverse().map((id) => cardById[id]);
  return (
    <BottomSheet title="Chamadas" onClose={onClose}>
      <div className="history-list">
        {cards.map((card, index) => (
          <div className="history-row" key={`${card.id}-${index}`} style={{ "--row-accent": COLUMN_COLORS[card.column] }}>
            <span className="history-code">{card.code}</span>
            <span className="history-label">{card.label}</span>
          </div>
        ))}
      </div>
      <button className="quiet-danger" type="button" onClick={onNewGame}>
        Novo jogo
      </button>
    </BottomSheet>
  );
}

function MiniBoard({ board, drawnIds, highlightLineId, compact = false }) {
  const marked = new Set([...drawnIds, "FREE"]);
  const highlight = highlightLineId ? lineDefinitions.find((line) => line.id === highlightLineId) : null;
  const highlightedCells = new Set((highlight?.cells || []).map(([row, col]) => `${row}-${col}`));

  return (
    <div className={compact ? "mini-board compact" : "mini-board"} aria-label={`Cartela ${board.number}`}>
      {board.grid.map((row, rowIndex) =>
        row.map((cell, colIndex) => {
          const key = `${rowIndex}-${colIndex}`;
          const isMarked = marked.has(cell.id);
          const isHighlighted = highlightedCells.has(key);
          return (
            <span
              key={`${cell.id}-${key}`}
              className={`${isMarked ? "marked" : ""} ${isHighlighted ? "highlighted" : ""}`}
              title={cell.label}
              aria-label={cell.label}
            />
          );
        })
      )}
    </div>
  );
}

function BoardsSheet({ game, onClose, onConfer }) {
  const rows = game.activeBoardNumbers.map((number) => {
    const board = boardByNumber[number];
    const progress = getBoardProgress(board, game.drawnIds);
    return { board, progress };
  });

  return (
    <BottomSheet title="Cartelas" onClose={onClose}>
      <div className="boards-list">
        {rows.map(({ board, progress }) => (
          <button
            type="button"
            className={progress.ready ? "board-row ready" : "board-row"}
            key={board.number}
            onClick={() => progress.ready && onConfer(board.number)}
            disabled={!progress.ready}
          >
            <MiniBoard board={board} drawnIds={game.drawnIds} compact />
            <span>
              <strong>Cartela {board.number.toString().padStart(2, "0")}</strong>
              <small>{progress.completedLines.length} linhas completas</small>
            </span>
            {progress.ready ? <Icon name="check" /> : null}
          </button>
        ))}
      </div>
    </BottomSheet>
  );
}

function AlertSheet({ game, alerts, onClose, onConfer }) {
  const isMultiple = alerts.length > 1;
  const rows = alerts.map((alert) => {
    const board = boardByNumber[alert.boardNumber];
    const lines = getCompletedLines(board, game.drawnIds);
    return { alert, board, lines };
  });

  return (
    <BottomSheet title="Conferência" onClose={onClose} className="alert-sheet">
      <div className="alert-summary">
        <div>
          <h3>
            {isMultiple
              ? `${alerts.length} cartelas para conferência`
              : `Cartela ${alerts[0].boardNumber.toString().padStart(2, "0")} pronta`}
          </h3>
          <p>
            {isMultiple
              ? "Escolha uma cartela para conferir primeiro."
              : `${rows[0].lines.length} linhas completas para conferir.`}
          </p>
        </div>
      </div>

      <div className="alert-board-list">
        {rows.map(({ alert, board, lines }) => (
          <button
            type="button"
            className="alert-board-button"
            key={alert.id}
            onClick={() => onConfer(board.number, alert.drawIndex)}
          >
            <MiniBoard board={board} drawnIds={game.drawnIds} compact />
            <span className="alert-board-copy">
              <strong>Cartela {board.number.toString().padStart(2, "0")}</strong>
              <small>{lines.length} linhas completas</small>
              <span className="alert-lines">
                {lines.slice(0, 2).map((line) => (
                  <span key={line.id}>{line.label}</span>
                ))}
                {lines.length > 2 ? <span>+{lines.length - 2}</span> : null}
              </span>
            </span>
            <Icon name="check" />
          </button>
        ))}
      </div>

      <div className="sheet-actions">
        <button className="text-action" type="button" onClick={onClose}>
          Continuar
        </button>
      </div>
    </BottomSheet>
  );
}

function ConferenceSheet({ game, boardNumber, onClose, onValidated }) {
  const board = boardByNumber[boardNumber];
  const completedLines = getCompletedLines(board, game.drawnIds);
  const [selectedLineId, setSelectedLineId] = useState(completedLines[0]?.id);
  const selectedLine = completedLines.find((line) => line.id === selectedLineId) || completedLines[0];
  const cells = selectedLine?.cells || [];

  useEffect(() => {
    setSelectedLineId(completedLines[0]?.id);
  }, [boardNumber]);

  return (
    <BottomSheet title={`Cartela ${boardNumber.toString().padStart(2, "0")}`} onClose={onClose} className="conference-sheet">
      <div className="conference-grid">
        <MiniBoard board={board} drawnIds={game.drawnIds} highlightLineId={selectedLine?.id} />
        <div className="line-tabs" role="list" aria-label="Linhas completas">
          {completedLines.map((line) => (
            <button
              type="button"
              key={line.id}
              className={line.id === selectedLine?.id ? "selected" : ""}
              onClick={() => setSelectedLineId(line.id)}
            >
              <span>{visibleLineType(line.kind)}</span>
              <strong>{line.label}</strong>
            </button>
          ))}
        </div>
      </div>

      <div className="concept-checklist">
        {cells.map((cell) => (
          <div className={cell.id === "FREE" ? "concept-item free" : "concept-item"} key={`${selectedLine?.id}-${cell.id}`}>
            <span>{cell.id === "FREE" ? "Livre" : cell.id}</span>
            <strong>{cell.label}</strong>
          </div>
        ))}
      </div>

      <div className="sheet-actions">
        <button className="primary-action" type="button" onClick={() => onValidated(boardNumber, selectedLine?.id)}>
          Vitória validada
        </button>
        <button className="text-action" type="button" onClick={onClose}>
          Continuar jogo
        </button>
      </div>
    </BottomSheet>
  );
}

function Toast({ message }) {
  if (!message) return null;
  return <div className="toast">{message}</div>;
}

function ConfirmDialog({ isOpen, title, message, confirmLabel, cancelLabel, onConfirm, onCancel }) {
  const [shouldRender, setShouldRender] = useState(isOpen);
  const [isClosing, setIsClosing] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setShouldRender(true);
      setIsClosing(false);
    } else if (shouldRender) {
      setIsClosing(true);
      const timer = setTimeout(() => {
        setShouldRender(false);
      }, 400); // match CSS animation duration
      return () => clearTimeout(timer);
    }
  }, [isOpen, shouldRender]);

  if (!shouldRender) return null;

  return (
    <div className={`dialog-layer ${isClosing ? "closing" : ""}`} role="presentation">
      <button className="dialog-backdrop" type="button" aria-label="Cancelar" onClick={onCancel} />
      <section className="confirm-dialog" role="dialog" aria-modal="true" aria-label={title}>
        <h2 className="dialog-title">{title}</h2>
        <p className="dialog-message">{message}</p>
        <div className="dialog-actions">
          <button className="dialog-btn-cancel" type="button" onClick={onCancel}>
            {cancelLabel}
          </button>
          <button className="dialog-btn-danger" type="button" onClick={onConfirm}>
            {confirmLabel}
          </button>
        </div>
      </section>
    </div>
  );
}

function GameScreen({ game, setGame, onReset }) {
  const [sheet, setSheet] = useState(null);
  const [conferenceBoard, setConferenceBoard] = useState(null);
  const [toast, setToast] = useState("");
  const [flight, setFlight] = useState(null);
  const [showConfirmReset, setShowConfirmReset] = useState(false);
  const flightTimers = useRef([]);
  const drawMode = game.drawMode || DRAW_MODES.APP;
  const currentCard = game.drawnIds.length ? cardById[game.drawnIds.at(-1)] : null;
  const currentAlertBatch = useMemo(() => {
    const firstAlert = game.alertQueue[0];
    if (!firstAlert) return [];
    return game.alertQueue.filter((alert) => alert.drawIndex === firstAlert.drawIndex);
  }, [game.alertQueue]);

  const viewportClass = currentCard ? "playing" : "waiting";

  useEffect(() => {
    return () => {
      flightTimers.current.forEach((timer) => window.clearTimeout(timer));
    };
  }, []);

  function draw() {
    if (flight || game.deck.length === 0) return;

    const nextId = game.deck[0];
    const nextCard = cardById[nextId];
    const nextDrawCount = game.drawnIds.length + 1;
    const shouldAnimate = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (!shouldAnimate) {
      setGame((current) => drawNext(current));
      return;
    }

    setFlight({
      phase: "dealing",
      exitingCard: currentCard,
      enteringCard: nextCard,
      drawCount: nextDrawCount
    });

    flightTimers.current.forEach((timer) => window.clearTimeout(timer));
    flightTimers.current = [];

    flightTimers.current.push(window.setTimeout(() => {
      setGame((current) => drawNext(current));
    }, 560));

    flightTimers.current.push(window.setTimeout(() => {
      setFlight(null);
      flightTimers.current = [];
    }, 640));
  }

  function manualCall(cardId) {
    if (flight) return;
    setGame((current) => drawCardById(current, cardId));
  }

  function undo() {
    if (flight) return;
    setGame((current) => undoLastDraw(current));
  }

  function closeAlert() {
    const drawIndex = currentAlertBatch[0]?.drawIndex;
    if (typeof drawIndex === "number") {
      setGame((current) => dismissAlertBatch(current, drawIndex));
    }
  }

  function openConference(boardNumber, alertDrawIndex) {
    setConferenceBoard(boardNumber);
    setSheet(null);
    if (typeof alertDrawIndex === "number") {
      setGame((current) => dismissBoardAlert(current, boardNumber, alertDrawIndex));
    }
  }

  function validated(boardNumber, lineId) {
    setGame((current) => recordValidatedWin(current, boardNumber, lineId));
    setConferenceBoard(null);
    setToast(`Cartela ${boardNumber.toString().padStart(2, "0")} validada`);
    window.setTimeout(() => setToast(""), 2200);
  }

  function newGame() {
    setShowConfirmReset(true);
  }

  const drawnCount = game.drawnIds.length;

  return (
    <main className={`game-screen ${viewportClass}`}>
      <TopBar game={game} currentCard={currentCard} onOpenBoards={() => setSheet("boards")} />

      <section className="card-stage" aria-live="polite">
        <div className={flight ? "deck-shadow drawing" : "deck-shadow"} aria-hidden="true" />
        {flight ? (
          <CardFlight
            exitingCard={flight.exitingCard}
            enteringCard={flight.enteringCard}
            drawCount={flight.drawCount}
            phase={flight.phase}
          />
        ) : (
          <CallCard card={currentCard} drawCount={drawnCount} drawMode={drawMode} />
        )}
      </section>

      {drawMode === DRAW_MODES.MANUAL ? (
        <ManualCallControls game={game} onUndo={undo} onCall={manualCall} onHistory={() => setSheet("history")} busy={Boolean(flight)} />
      ) : (
        <BottomControls game={game} onUndo={undo} onDraw={draw} onHistory={() => setSheet("history")} busy={Boolean(flight)} />
      )}

      {sheet === "history" ? <HistorySheet game={game} onClose={() => setSheet(null)} onNewGame={newGame} /> : null}
      {sheet === "boards" ? <BoardsSheet game={game} onClose={() => setSheet(null)} onConfer={openConference} /> : null}
      {currentAlertBatch.length > 0 && !conferenceBoard && !flight ? (
        <AlertSheet game={game} alerts={currentAlertBatch} onClose={closeAlert} onConfer={openConference} />
      ) : null}
      {conferenceBoard ? (
        <ConferenceSheet
          game={game}
          boardNumber={conferenceBoard}
          onClose={() => setConferenceBoard(null)}
          onValidated={validated}
        />
      ) : null}
      <Toast message={toast} />
      
      <ConfirmDialog
        isOpen={showConfirmReset}
        title="Novo jogo?"
        message="Todo o progresso do jogo atual será perdido. Deseja mesmo reiniciar?"
        confirmLabel="Sim, reiniciar"
        cancelLabel="Cancelar"
        onConfirm={() => {
          setShowConfirmReset(false);
          // Wait for modal exit animation to start before resetting the board
          setTimeout(() => {
            onReset();
            setSheet(null);
          }, 300);
        }}
        onCancel={() => setShowConfirmReset(false)}
      />
    </main>
  );
}

export default function App() {
  const [game, setGame] = useState(() => loadSavedGame());

  useEffect(() => {
    saveGame(game);
  }, [game]);

  const appReady = useMemo(() => Boolean(data.cards.length && data.boards.length), []);

  if (!appReady) return null;

  if (!game) {
    return <SetupScreen onStart={(selection, drawMode) => setGame(createGame(selection, drawMode))} />;
  }

  return <GameScreen game={game} setGame={setGame} onReset={() => setGame(null)} />;
}
