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
  if (name === "chevron") {
    return (
      <svg {...common}>
        <path d="m8 10 4 4 4-4" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
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
  if (name === "printer") {
    return (
      <svg {...common}>
        <path d="M7 8V4.8h10V8" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M7 17H5.6A2.6 2.6 0 0 1 3 14.4v-3.8A2.6 2.6 0 0 1 5.6 8h12.8a2.6 2.6 0 0 1 2.6 2.6v3.8a2.6 2.6 0 0 1-2.6 2.6H17" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M7.5 14h9v6h-9z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
        <path d="M17.5 11.2h.1" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
      </svg>
    );
  }
  if (name === "rules") {
    return (
      <svg {...common}>
        <path d="M7 4.5h10A2.5 2.5 0 0 1 19.5 7v12.5H8A3.5 3.5 0 0 1 4.5 16V7A2.5 2.5 0 0 1 7 4.5Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
        <path d="M8 16h11.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        <path d="M9 8.5h6M9 11.5h5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    );
  }
  if (name === "download") {
    return (
      <svg {...common}>
        <path d="M12 4v9" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" />
        <path d="m8 10 4 4 4-4" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M5 19h14" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" />
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

function lineTone(line) {
  if (line.kind === "horizontal") return line.label;
  if (line.kind === "vertical") return line.label;
  return line.label.replace("Diagonal ", "");
}

function lineTabLabel(line) {
  if (line.kind === "diagonal") return line.label.replace("Diagonal ", "");
  return line.label;
}

function SetupScreen({ onStart }) {
  const [selection, setSelection] = useState([]);
  const [drawMode, setDrawMode] = useState(DRAW_MODES.APP);
  const [isStarting, setIsStarting] = useState(false);
  const [setupSheet, setSetupSheet] = useState(null);
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
      <div className="setup-content">
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

        <nav className="setup-secondary-actions" aria-label="Materiais de apoio">
          <button type="button" onClick={() => setSetupSheet("materials")}>
            <Icon name="printer" />
            <span>Imprimir</span>
          </button>
          <button type="button" onClick={() => setSetupSheet("rules")}>
            <Icon name="rules" />
            <span>Regras</span>
          </button>
        </nav>
      </div>

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

      {setupSheet === "materials" ? <MaterialsSheet onClose={() => setSetupSheet(null)} /> : null}
      {setupSheet === "rules" ? <RulesSheet onClose={() => setSetupSheet(null)} /> : null}
    </main>
  );
}

const MATERIAL_OPTIONS = [
  {
    title: "Cartelas",
    meta: "24 cartelas em A4",
    href: "./materials/cartelas_bingo_24_a4.pdf",
    fileName: "cartelas_bingo_24_a4.pdf",
    recommended: true
  },
  {
    title: "Kit completo",
    meta: "guia, cartas e controles",
    href: "./materials/kit_impressao_bingo_violencia_discriminacao.pdf",
    fileName: "kit_impressao_bingo_violencia_discriminacao.pdf"
  }
];

const RULES = [
  {
    title: "Selecione cartelas",
    detail: "Só as que estão em jogo."
  },
  {
    title: "Sorteie e leia",
    detail: "Código + conceito."
  },
  {
    title: "Marquem",
    detail: "Cada equipe marca se tiver."
  },
  {
    title: "Explique",
    detail: "Caso + apoios do card."
  },
  {
    title: "Vitória: 2 linhas",
    detail: "Explique 3 conceitos."
  }
];

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

function CardFlight({ exitingCard, enteringCard, drawCount, phase, drawMode }) {
  return (
    <div className={`card-flight ${phase}`} aria-hidden="true">
      <div className="flight-card exit-card">
        <CallCard card={exitingCard} drawCount={`exit-${drawCount}`} drawMode={drawMode} />
      </div>
      <div className="flight-card enter-card">
        <CallCard card={enteringCard} drawCount={`enter-${drawCount}`} drawMode={drawMode} />
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
      <button
        className="icon-button board-status"
        type="button"
        onClick={onOpenBoards}
        aria-label={`${game.activeBoardNumbers.length} cartelas em jogo`}
      >
        <Icon name="grid" />
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

function ManualCallControls({ game, onUndo, onCall, onHistory, onKeyboardOpenChange, busy = false }) {
  const [activeColumn, setActiveColumn] = useState("");
  const [pendingManualCode, setPendingManualCode] = useState("");
  const [motionPhase, setMotionPhase] = useState("idle");
  const [pressedNumber, setPressedNumber] = useState("");
  const lastColumnRef = useRef("");
  const manualCallTimers = useRef([]);
  if (activeColumn && activeColumn !== lastColumnRef.current) {
    lastColumnRef.current = activeColumn;
  }
  const renderColumn = activeColumn || lastColumnRef.current;
  
  const [lastCode, setLastCode] = useState("");
  const hasDrawn = game.drawnIds.length > 0;
  const drawnSet = useMemo(() => new Set(game.drawnIds), [game.drawnIds]);
  const finished = game.drawnIds.length >= data.cards.length;
  const numbers = useMemo(() => Array.from({ length: 15 }, (_, index) => (index + 1).toString().padStart(2, "0")), []);
  const currentCode = game.drawnIds.length ? cardById[game.drawnIds.at(-1)]?.code || "" : "";
  const displayCode = pendingManualCode || activeColumn || lastCode || "...";
  const codeState = pendingManualCode ? "confirming" : activeColumn ? "selecting" : lastCode ? "registered" : "idle";
  const ballState = pendingManualCode ? "committing" : activeColumn ? "selecting" : lastCode ? "called" : "idle";
  const ballColumn = activeColumn || (pendingManualCode ? pendingManualCode[0] : lastCode ? lastCode[0] : "");
  const ballAccentColor = ballColumn ? COLUMN_COLORS[ballColumn] : "oklch(92% 0.015 80)";
  const locked = busy || Boolean(pendingManualCode);
  const activeColumnIndex = COLUMN_ORDER.indexOf(activeColumn);
  const keyboardVisuallyOpen = Boolean(activeColumn && motionPhase !== "closing");
  const controlsClass = [
    "manual-controls",
    activeColumn ? "expanded" : "",
    pendingManualCode ? "committing" : "",
    motionPhase !== "idle" ? `motion-${motionPhase}` : ""
  ].filter(Boolean).join(" ");
  const availableColumns = useMemo(() => {
    return Object.fromEntries(
      COLUMN_ORDER.map((column) => [
        column,
        numbers.some((number) => {
          const card = cardByCode[`${column}${number}`];
          return card && !drawnSet.has(card.id);
        })
      ])
    );
  }, [drawnSet, numbers]);
  const numberStates = useMemo(() => {
    return numbers.map((number) => {
      const card = renderColumn ? cardByCode[`${renderColumn}${number}`] : null;
      return {
        number,
        used: card ? drawnSet.has(card.id) : false,
        label: renderColumn ? `${renderColumn}${number}` : `Número ${number}`
      };
    });
  }, [drawnSet, numbers, renderColumn]);

  useEffect(() => {
    setLastCode(currentCode);
    if (!currentCode) {
      setActiveColumn("");
      onKeyboardOpenChange?.(false);
      setMotionPhase("idle");
      setPressedNumber("");
    }
  }, [currentCode, onKeyboardOpenChange]);

  useEffect(() => {
    onKeyboardOpenChange?.(keyboardVisuallyOpen);
  }, [keyboardVisuallyOpen, onKeyboardOpenChange]);

  useEffect(() => {
    return () => {
      onKeyboardOpenChange?.(false);
    };
  }, [onKeyboardOpenChange]);

  useEffect(() => {
    return () => {
      clearManualCallTimers();
    };
  }, []);

  function clearManualCallTimers() {
    manualCallTimers.current.forEach((timer) => window.clearTimeout(timer));
    manualCallTimers.current = [];
  }

  function scheduleManualCall(callback, delay) {
    const timer = window.setTimeout(() => {
      manualCallTimers.current = manualCallTimers.current.filter((item) => item !== timer);
      callback();
    }, delay);
    manualCallTimers.current.push(timer);
  }

  function chooseColumn(column) {
    if (locked) return;
    setPressedNumber("");
    const nextColumn = activeColumn === column ? "" : column;
    onKeyboardOpenChange?.(Boolean(nextColumn));
    setActiveColumn(nextColumn);
    setMotionPhase(nextColumn ? "selecting" : "idle");
  }

  function submitNumber(number) {
    if (!activeColumn || locked) return;
    const code = `${activeColumn}${number}`;
    const card = cardByCode[code];
    if (!card || drawnSet.has(card.id)) return;

    setLastCode(code);
    setPressedNumber(number);
    setMotionPhase("committing");
    setPendingManualCode(code);

    clearManualCallTimers();

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduceMotion) {
      setActiveColumn("");
      onKeyboardOpenChange?.(false);
      onCall(card.id);
      setPendingManualCode("");
      setPressedNumber("");
      setMotionPhase("idle");
      return;
    }

    scheduleManualCall(() => {
      onKeyboardOpenChange?.(false);
      setMotionPhase("closing");
    }, 180);

    scheduleManualCall(() => {
      setActiveColumn("");
    }, 460);

    scheduleManualCall(() => {
      onCall(card.id);
    }, 430);

    scheduleManualCall(() => {
      setPendingManualCode("");
      setPressedNumber("");
      setMotionPhase("idle");
    }, 620);
  }

  return (
    <nav
      className={controlsClass}
      aria-label="Registrar chamada física"
      aria-busy={locked}
    >
      <div className="manual-control-head">
        <button className="tool-button" type="button" onClick={onUndo} disabled={!hasDrawn || locked}>
          <Icon name="undo" />
          <span>Voltar</span>
        </button>

        <div className="manual-ball-wrap" aria-live="polite">
          <div
            className={`manual-ball ${ballState}`}
            style={{ "--ball-accent": ballAccentColor }}
          >
            <strong className={`manual-code ${codeState}`}>{displayCode}</strong>
          </div>
        </div>

        <button className="tool-button" type="button" onClick={onHistory} disabled={!hasDrawn || locked}>
          <Icon name="list" />
          <span>Histórico</span>
        </button>
      </div>

      <div
        className="manual-pad"
        aria-label="Código da bolinha"
        style={{ "--pad-accent": ballAccentColor }}
      >
        <div
          className={activeColumn ? "manual-columns has-selection" : "manual-columns"}
          aria-label="Letra da bolinha"
          data-selected-index={activeColumnIndex >= 0 ? activeColumnIndex : undefined}
        >
          {COLUMN_ORDER.map((column) => (
            <button
              type="button"
              key={column}
              className={activeColumn === column ? "manual-column selected" : "manual-column"}
              onClick={() => chooseColumn(column)}
              disabled={locked || finished || !availableColumns[column]}
              aria-pressed={activeColumn === column}
              aria-label={`Letra ${column}`}
            >
              <span>{column}</span>
            </button>
          ))}
        </div>

        <div className="manual-numbers-shell" aria-hidden={!activeColumn}>
          <div className="manual-numbers" aria-label="Número da bolinha">
            {numberStates.map(({ number, used, label }) => {
              const isActuallyDisabled = locked || !activeColumn || used;
              const isChosen = pressedNumber === number && Boolean(pendingManualCode);
              return (
                <button
                  type="button"
                  key={number}
                  className={`manual-number${used ? " used" : ""}${isChosen ? " chosen" : ""}`}
                  onClick={() => submitNumber(number)}
                  disabled={isActuallyDisabled}
                  aria-label={label}
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
  const interactiveSelector = "button:not(:disabled), a, input, textarea, select";
  const dragHandleSelector = ".grabber, .sheet-head";

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

  function startGesture(clientX, clientY, target, pointerId = null) {
    if (closing) return false;
    if (target.closest(interactiveSelector)) return false;
    if (!target.closest(dragHandleSelector)) return false;

    gesture.current = {
      startX: clientX,
      startY: clientY,
      lastX: clientX,
      lastY: clientY,
      startTime: performance.now(),
      active: false,
      pointerId,
      locked: false
    };
    return true;
  }

  function moveGesture(clientX, clientY, event) {
    const current = gesture.current;
    if (!current) return;

    const deltaX = clientX - current.startX;
    const deltaY = clientY - current.startY;
    const absX = Math.abs(deltaX);
    const absY = Math.abs(deltaY);
    current.lastX = clientX;
    current.lastY = clientY;

    if (!current.locked && Math.max(absX, absY) > 10) {
      current.locked = true;
      if (absX > absY * 1.15) {
        gesture.current = null;
        return;
      }
    }

    if (deltaY <= 0) {
      if (current.active) {
        setDrag(0);
        if (event?.cancelable !== false) event?.preventDefault?.();
      }
      return;
    }

    if (deltaY > 18 || current.active) {
      current.active = true;
      suppressClick.current = deltaY > 12;
      setDragging(true);
      setDrag(Math.min(deltaY, 190));
      if (event?.cancelable !== false) event?.preventDefault?.();
    }
  }

  function endGesture() {
    const current = gesture.current;
    if (!current) return;

    const elapsed = Math.max(performance.now() - current.startTime, 1);
    const travel = Math.max(0, current.lastY - current.startY);
    const velocity = travel / elapsed;
    const shouldClose = current.active && (travel > 72 || (travel > 40 && velocity > 0.5));

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
    startGesture(event.touches[0].clientX, event.touches[0].clientY, event.target);
  }

  function moveTouch(event) {
    if (event.touches.length !== 1) return;
    moveGesture(event.touches[0].clientX, event.touches[0].clientY, event);
  }

  function beginPointer(event) {
    if (event.pointerType === "touch") return;
    if (startGesture(event.clientX, event.clientY, event.target, event.pointerId)) {
      event.currentTarget.setPointerCapture?.(event.pointerId);
    }
  }

  function movePointer(event) {
    if (event.pointerType === "touch") return;
    moveGesture(event.clientX, event.clientY, event);
  }

  function endPointer(event) {
    if (event.pointerType === "touch") return;
    endGesture();
  }

  function captureClick(event) {
    if (!suppressClick.current) return;
    suppressClick.current = false;
    if (event.target.closest(interactiveSelector)) return;
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

function HistoryDisclosure({ card, historyKey, isOpen, onToggle }) {
  return (
    <div
      className={isOpen ? "history-row open" : "history-row"}
      data-history-id={historyKey}
      style={{ "--row-accent": COLUMN_COLORS[card.column] }}
    >
      <button
        className="history-summary"
        type="button"
        aria-expanded={isOpen}
        onClick={onToggle}
      >
        <span className="history-code">{card.code}</span>
        <span className="history-label">{card.label}</span>
        <span className="history-cue" aria-hidden="true">
          <Icon name="chevron" />
        </span>
      </button>

      {isOpen ? (
        <div className="history-detail">
          <div className="history-detail-section">
            <span className="history-detail-label">Caso</span>
            <p>{card.case}</p>
          </div>
          <div className="history-detail-section">
            <span className="history-detail-label">Explicação</span>
            <p>{renderRich(card.explanation)}</p>
          </div>
          {card.readingPoints?.length ? (
            <ol className="history-points">
              {card.readingPoints.map((point) => (
                <li key={point.title}>
                  <strong>{point.title}:</strong> {point.body}
                </li>
              ))}
            </ol>
          ) : null}
          {card.conferenceQuestion ? <div className="history-question">{card.conferenceQuestion}</div> : null}
        </div>
      ) : null}
    </div>
  );
}

function HistorySheet({ game, onClose, onNewGame }) {
  const cards = [...game.drawnIds].reverse().map((id) => cardById[id]).filter(Boolean);
  const [openHistoryId, setOpenHistoryId] = useState(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (!openHistoryId) return undefined;
    const scrollEl = scrollRef.current;
    if (!scrollEl) return undefined;

    const frame = window.requestAnimationFrame(() => {
      const item = scrollEl.querySelector(`[data-history-id="${openHistoryId}"]`);
      if (!item) return;

      const scrollRect = scrollEl.getBoundingClientRect();
      const itemRect = item.getBoundingClientRect();
      const topRoom = 14;
      const bottomRoom = 72;
      const overflowTop = scrollRect.top + topRoom - itemRect.top;
      const overflowBottom = itemRect.bottom - (scrollRect.bottom - bottomRoom);
      const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      const behavior = reduceMotion ? "auto" : "smooth";

      if (overflowTop > 0) {
        scrollEl.scrollBy({ top: -overflowTop, behavior });
      } else if (overflowBottom > 0) {
        scrollEl.scrollBy({ top: overflowBottom, behavior });
      }
    });

    return () => window.cancelAnimationFrame(frame);
  }, [openHistoryId]);

  return (
    <BottomSheet title="Chamadas" onClose={onClose} className="history-sheet">
      <div className="history-list-shell">
        <div className="history-list" ref={scrollRef}>
          {cards.map((card) => (
            <HistoryDisclosure
              card={card}
              historyKey={card.id}
              isOpen={openHistoryId === card.id}
              key={card.id}
              onToggle={() => setOpenHistoryId((current) => (current === card.id ? null : card.id))}
            />
          ))}
          <div className="history-list-footer" aria-hidden="true" />
        </div>
      </div>
      <button className="quiet-danger" type="button" onClick={onNewGame}>
        Novo jogo
      </button>
    </BottomSheet>
  );
}

function MaterialsSheet({ onClose }) {
  return (
    <BottomSheet title="Imprimir" onClose={onClose} className="materials-sheet">
      <div className="materials-list">
        {MATERIAL_OPTIONS.map((item) => (
          <a className={item.recommended ? "material-row recommended" : "material-row"} href={item.href} download={item.fileName} key={item.href}>
            <span className="material-icon">
              <Icon name="download" />
            </span>
            <span className="material-copy">
              <strong>{item.title}</strong>
              <small>{item.meta}</small>
            </span>
          </a>
        ))}
      </div>
      <p className="materials-note">Com o app, normalmente basta imprimir as cartelas.</p>
    </BottomSheet>
  );
}

function RulesSheet({ onClose }) {
  return (
    <BottomSheet title="Regras" onClose={onClose} className="rules-sheet">
      <ol className="rules-list">
        {RULES.map((rule) => (
          <li key={rule.title}>
            <span className="rule-copy">
              <strong>{rule.title}</strong>
              <small>{rule.detail}</small>
            </span>
          </li>
        ))}
      </ol>
    </BottomSheet>
  );
}

function lineCountLabel(count) {
  if (count === 0) return "Nenhuma linha completa";
  if (count === 1) return "1 linha completa";
  return `${count} linhas completas`;
}

function MiniBoard({ board, drawnIds, highlightLineId, compact = false, decorative = false }) {
  const marked = new Set([...drawnIds, "FREE"]);
  const highlight = highlightLineId ? lineDefinitions.find((line) => line.id === highlightLineId) : null;
  const highlightedCells = new Set((highlight?.cells || []).map(([row, col]) => `${row}-${col}`));
  const markedCount = board.grid.flat().filter((cell) => marked.has(cell.id)).length;
  const boardLabel = board.number.toString().padStart(2, "0");
  const accessibilityProps = decorative
    ? { "aria-hidden": "true" }
    : { role: "img", "aria-label": `Cartela ${boardLabel}, ${markedCount} de 25 casas marcadas` };

  return (
    <div
      className={compact ? "mini-board compact" : "mini-board"}
      {...accessibilityProps}
    >
      {board.grid.map((row, rowIndex) =>
        row.map((cell, colIndex) => {
          const key = `${rowIndex}-${colIndex}`;
          const isMarked = marked.has(cell.id);
          const isHighlighted = highlightedCells.has(key);
          return (
            <span
              key={`${cell.id}-${key}`}
              className={[isMarked && "marked", isHighlighted && "highlighted"].filter(Boolean).join(" ")}
              title={cell.label}
              aria-hidden="true"
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
            aria-disabled={!progress.ready}
            tabIndex={progress.ready ? undefined : -1}
          >
            <MiniBoard board={board} drawnIds={game.drawnIds} compact decorative />
            <span>
              <strong>Cartela {board.number.toString().padStart(2, "0")}</strong>
              <small>{lineCountLabel(progress.completedLines.length)}</small>
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
              : `${lineCountLabel(rows[0].lines.length)} para conferir.`}
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
            <MiniBoard board={board} drawnIds={game.drawnIds} compact decorative />
            <span className="alert-board-copy">
              <strong>Cartela {board.number.toString().padStart(2, "0")}</strong>
              <small>{lineCountLabel(lines.length)}</small>
              <span className="alert-lines-text">
                {lines.slice(0, 2).map(lineTone).join(" · ")}
                {lines.length > 2 ? ` · +${lines.length - 2}` : ""}
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

function ConceptDisclosure({ cell, isOpen, onToggle }) {
  const card = cell.id === "FREE" ? null : cardById[cell.id];
  const accent = card ? COLUMN_COLORS[card.column] : "var(--gold)";

  if (!card) {
    return (
      <div className="concept-item free" data-concept-id={cell.id} style={{ "--concept-accent": accent }}>
        <div className="concept-summary static">
          <span className="concept-code">Livre</span>
          <strong>{cell.label}</strong>
        </div>
      </div>
    );
  }

  return (
    <div
      className={isOpen ? "concept-item open" : "concept-item"}
      data-concept-id={cell.id}
      style={{ "--concept-accent": accent }}
    >
      <button className="concept-summary" type="button" aria-expanded={isOpen} onClick={onToggle}>
        <span className="concept-code">{card.code}</span>
        <strong>{card.label}</strong>
        <span className="concept-cue" aria-hidden="true">
          <Icon name="chevron" />
        </span>
      </button>

      {isOpen ? (
        <div className="concept-detail">
          <div className="concept-detail-section">
            <span className="concept-detail-label">Caso</span>
            <p>{card.case}</p>
          </div>
          <div className="concept-detail-section">
            <span className="concept-detail-label">Explicação</span>
            <p>{renderRich(card.explanation)}</p>
          </div>
          <ol className="concept-points">
            {card.readingPoints.map((point) => (
              <li key={point.title}>
                <strong>{point.title}:</strong> {point.body}
              </li>
            ))}
          </ol>
          {card.conferenceQuestion ? (
            <div className="concept-question">{card.conferenceQuestion}</div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

function ConferenceSheet({ game, boardNumber, onClose, onValidated }) {
  const board = boardByNumber[boardNumber];
  const completedLines = getCompletedLines(board, game.drawnIds);
  const [selectedLineId, setSelectedLineId] = useState(completedLines[0]?.id);
  const [openConceptId, setOpenConceptId] = useState(null);
  const scrollRef = useRef(null);
  const selectedLine = completedLines.find((line) => line.id === selectedLineId) || completedLines[0];
  const cells = selectedLine?.cells || [];
  const selectedLineLabel = selectedLine ? `${visibleLineType(selectedLine.kind)} ${lineTabLabel(selectedLine)}` : "linha completa";
  const boardLabel = boardNumber.toString().padStart(2, "0");

  useEffect(() => {
    setSelectedLineId(completedLines[0]?.id);
    setOpenConceptId(null);
  }, [boardNumber]);

  useEffect(() => {
    setOpenConceptId(null);
  }, [selectedLineId]);

  useEffect(() => {
    if (!openConceptId) return undefined;
    const scrollEl = scrollRef.current;
    if (!scrollEl) return undefined;

    const frame = window.requestAnimationFrame(() => {
      const item = scrollEl.querySelector(`[data-concept-id="${openConceptId}"]`);
      if (!item) return;

      const scrollRect = scrollEl.getBoundingClientRect();
      const itemRect = item.getBoundingClientRect();
      const topRoom = 12;
      const bottomRoom = 60;
      const overflowTop = scrollRect.top + topRoom - itemRect.top;
      const overflowBottom = itemRect.bottom - (scrollRect.bottom - bottomRoom);
      const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      const behavior = reduceMotion ? "auto" : "smooth";

      if (overflowTop > 0) {
        scrollEl.scrollBy({ top: -overflowTop, behavior });
      } else if (overflowBottom > 0) {
        scrollEl.scrollBy({ top: overflowBottom, behavior });
      }
    });

    return () => window.cancelAnimationFrame(frame);
  }, [openConceptId]);

  return (
    <BottomSheet title={`Cartela ${boardLabel}`} onClose={onClose} className="conference-sheet">
      <div className="conference-grid">
        <MiniBoard board={board} drawnIds={game.drawnIds} highlightLineId={selectedLine?.id} />
        <div className="line-tabs" role="tablist" aria-label="Linhas completas">
          {completedLines.map((line) => (
            <button
              type="button"
              key={line.id}
              role="tab"
              className={line.id === selectedLine?.id ? "selected" : ""}
              onClick={() => setSelectedLineId(line.id)}
              aria-selected={line.id === selectedLine?.id}
              aria-controls="conference-line-details"
            >
              <span>{visibleLineType(line.kind)}</span>
              <strong>{lineTabLabel(line)}</strong>
            </button>
          ))}
        </div>
      </div>

      <div className="conference-scroll-shell">
        <div
          className="conference-scroll"
          ref={scrollRef}
          id="conference-line-details"
          role="tabpanel"
          aria-label={`Conceitos da ${selectedLineLabel}`}
        >
          <div className="concept-checklist">
            {cells.map((cell) => (
              <ConceptDisclosure
                cell={cell}
                isOpen={openConceptId === cell.id}
                key={`${selectedLine?.id}-${cell.id}`}
                onToggle={() => setOpenConceptId((current) => (current === cell.id ? null : cell.id))}
              />
            ))}
            <div className="conference-scroll-footer" aria-hidden="true" />
          </div>
        </div>
      </div>

      <div className="sheet-actions conference-actions">
        <button
          className="primary-action"
          type="button"
          onClick={() => onValidated(boardNumber, selectedLine?.id)}
          aria-label={`Validar vitória da cartela ${boardLabel}, ${selectedLineLabel}`}
        >
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
  const [manualKeyboardOpen, setManualKeyboardOpen] = useState(false);
  const flightTimers = useRef([]);
  const flightFrames = useRef([]);
  const drawMode = game.drawMode || DRAW_MODES.APP;
  const currentCard = game.drawnIds.length ? cardById[game.drawnIds.at(-1)] : null;
  const currentAlertBatch = useMemo(() => {
    const firstAlert = game.alertQueue[0];
    if (!firstAlert) return [];
    return game.alertQueue.filter((alert) => alert.drawIndex === firstAlert.drawIndex);
  }, [game.alertQueue]);

  const viewportClass = currentCard ? "playing" : "waiting";
  const screenClass = [
    "game-screen",
    viewportClass,
    drawMode === DRAW_MODES.MANUAL ? "manual-mode" : "",
    manualKeyboardOpen ? "manual-keyboard-open" : ""
  ].filter(Boolean).join(" ");

  useEffect(() => {
    return () => {
      flightTimers.current.forEach((timer) => window.clearTimeout(timer));
      flightFrames.current.forEach((frame) => window.cancelAnimationFrame(frame));
    };
  }, []);

  useEffect(() => {
    if (drawMode !== DRAW_MODES.MANUAL) {
      setManualKeyboardOpen(false);
    }
  }, [drawMode]);

  function presentCard(nextCard, nextDrawCount, commitGame) {
    if (!nextCard) return;

    const shouldAnimate = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (!shouldAnimate) {
      setGame(commitGame);
      return;
    }

    flightTimers.current.forEach((timer) => window.clearTimeout(timer));
    flightFrames.current.forEach((frame) => window.cancelAnimationFrame(frame));
    flightTimers.current = [];
    flightFrames.current = [];

    setFlight({
      phase: "preparing",
      exitingCard: currentCard,
      enteringCard: nextCard,
      drawCount: nextDrawCount
    });

    const startDealing = () => {
      flightFrames.current = [];
      setFlight((current) =>
        current?.drawCount === nextDrawCount
          ? {
              ...current,
              phase: "dealing"
            }
          : current
      );

      flightTimers.current.push(window.setTimeout(() => {
        setGame(commitGame);
        setFlight(null);
        flightTimers.current = [];
      }, 560));
    };

    const firstFrame = window.requestAnimationFrame(() => {
      const secondFrame = window.requestAnimationFrame(startDealing);
      flightFrames.current.push(secondFrame);
    });

    flightFrames.current.push(firstFrame);
  }

  function draw() {
    if (flight || game.deck.length === 0) return;

    const nextId = game.deck[0];
    const nextCard = cardById[nextId];
    const nextDrawCount = game.drawnIds.length + 1;
    presentCard(nextCard, nextDrawCount, (current) => drawNext(current));
  }

  function manualCall(cardId) {
    if (flight) return;
    const nextCard = cardById[cardId];
    const nextDrawCount = game.drawnIds.length + 1;
    presentCard(nextCard, nextDrawCount, (current) => drawCardById(current, cardId));
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
    <main className={screenClass}>
      <TopBar game={game} currentCard={currentCard} onOpenBoards={() => setSheet("boards")} />

      <section className="card-stage" aria-live="polite">
        {flight ? (
          <CardFlight
            exitingCard={flight.exitingCard}
            enteringCard={flight.enteringCard}
            drawCount={flight.drawCount}
            phase={flight.phase}
            drawMode={drawMode}
          />
        ) : (
          <CallCard card={currentCard} drawCount={drawnCount} drawMode={drawMode} />
        )}
      </section>

      {drawMode === DRAW_MODES.MANUAL ? (
        <ManualCallControls
          game={game}
          onUndo={undo}
          onCall={manualCall}
          onHistory={() => setSheet("history")}
          onKeyboardOpenChange={setManualKeyboardOpen}
          busy={Boolean(flight)}
        />
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
