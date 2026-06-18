import { createContext, memo, useCallback, useContext, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import defaultData from "./data/game-data.json";
import { DRAW_MODES, createGameModel } from "./game";
import { loadSavedGame, loadSelectedContentId, saveGame, saveSelectedContentId } from "./storage";

const CONTENT_CATALOG_URL = "./content/catalog.json";
const DEFAULT_CATALOG = {
  schema: "bingo-catequese/content-catalog.v1",
  defaultContentId: defaultData.slug,
  items: [catalogItemFromData(defaultData, "./data/game-data.json")]
};
const ContentContext = createContext(null);

function catalogItemFromData(contentData, href) {
  return {
    id: contentData.slug,
    href,
    title: contentData.title,
    subtitle: contentData.subtitle,
    meeting: contentData.meeting,
    meetingLabel: contentData.meetingLabel,
    coreMessage: contentData.coreMessage,
    cardSetId: contentData.cardSetId,
    boardCount: contentData.boards?.length || 0,
    cardCount: contentData.cards?.length || 0
  };
}

function useContent() {
  const context = useContext(ContentContext);
  if (!context) throw new Error("ContentContext is not available");
  return context;
}

async function fetchJson(url) {
  const response = await fetch(url, { cache: "force-cache" });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

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

function EncounterSelectButton({ isOpen, onClick }) {
  const { data, activeCatalogItem } = useContent();

  return (
    <button
      className={isOpen ? "encounter-select open" : "encounter-select"}
      type="button"
      onClick={onClick}
      aria-expanded={isOpen}
      aria-controls="encounter-picker"
      aria-label="Selecionar encontro e tema"
    >
      <span className="encounter-select-main">
        <small>{data.meetingLabel || data.meeting || "Encontro"}</small>
        <strong>{data.subtitle || activeCatalogItem?.subtitle || data.title}</strong>
      </span>
      <span className="encounter-select-cue" aria-hidden="true" />
    </button>
  );
}

function EncounterInlinePicker({ onSelect }) {
  const { catalog, contentId, onSelectContent } = useContent();

  function chooseContent(nextContentId) {
    onSelectContent(nextContentId);
    onSelect();
  }

  return (
    <div className="encounter-panel" id="encounter-picker">
      <div className="encounter-panel-scroll">
        {catalog.items.map((item) => {
          const selected = item.id === contentId;
          return (
            <button
              type="button"
              className={selected ? "encounter-option selected" : "encounter-option"}
              key={item.id}
              onClick={() => chooseContent(item.id)}
              aria-pressed={selected}
            >
              <span className="encounter-option-number">{item.encounterNumber || "..."}</span>
              <span className="encounter-option-copy">
                <strong>{item.subtitle || item.title}</strong>
                <small>{item.meetingLabel || item.meeting || `${item.cardCount || 75} chamadas`}</small>
              </span>
              <span className="encounter-option-state" aria-hidden="true">
                {selected ? <Icon name="check" /> : null}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

const MemoEncounterInlinePicker = memo(EncounterInlinePicker);

function SetupScreen({ onStart }) {
  const { data } = useContent();
  const teachingMaterial = data.teachingMaterial || null;
  const [selection, setSelection] = useState([]);
  const [drawMode, setDrawMode] = useState(DRAW_MODES.APP);
  const [isStarting, setIsStarting] = useState(false);
  const [setupSheet, setSetupSheet] = useState(null);
  const startTimer = useRef(null);
  const selected = selection.length;
  const closeSetupSheet = useCallback(() => setSetupSheet(null), []);
  const selectAllBoards = useCallback(() => setSelection(data.boards.map((board) => board.number)), [data.boards]);
  const clearSelection = useCallback(() => setSelection([]), []);
  const closeEncounter = useCallback(() => setSetupSheet((current) => (current === "encounter" ? null : current)), []);
  const toggleEncounter = useCallback(() => setSetupSheet((current) => (current === "encounter" ? null : "encounter")), []);
  const openTeaching = useCallback(() => setSetupSheet("teaching"), []);
  const openMaterials = useCallback(() => setSetupSheet("materials"), []);
  const openRules = useCallback(() => setSetupSheet("rules"), []);

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
        </section>

        <div className={setupSheet === "encounter" ? "encounter-control open" : "encounter-control"}>
          <EncounterSelectButton isOpen={setupSheet === "encounter"} onClick={toggleEncounter} />
          {setupSheet === "encounter" ? <MemoEncounterInlinePicker onSelect={closeEncounter} /> : null}
        </div>

        <section className="board-picker" aria-label="Cartelas da partida">
          <div className="picker-head">
            <span>{selected} cartelas</span>
            <div className="picker-actions">
              <button type="button" onClick={selectAllBoards}>
                Todas
              </button>
              <button type="button" onClick={clearSelection}>
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
          {teachingMaterial ? (
            <button type="button" onClick={openTeaching}>
              <Icon name="lightbulb" />
              <span>Tema</span>
            </button>
          ) : null}
          <button type="button" onClick={openMaterials}>
            <Icon name="printer" />
            <span>Imprimir</span>
          </button>
          <button type="button" onClick={openRules}>
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

      {setupSheet === "teaching" ? <MemoTeachingSheet onClose={closeSetupSheet} /> : null}
      {setupSheet === "materials" ? <MemoMaterialsSheet onClose={closeSetupSheet} /> : null}
      {setupSheet === "rules" ? <MemoRulesSheet onClose={closeSetupSheet} /> : null}
    </main>
  );
}

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
      <div className="back-symbol">
        <span>B</span>
        <span>I</span>
        <span>N</span>
        <span>G</span>
        <span>O</span>
      </div>
    </article>
  );
}

function CallCard({ card, drawCount, drawMode }) {
  const { model } = useContent();
  if (!card) return <EmptyCard drawMode={drawMode} />;
  const columnColor = model.COLUMN_COLORS[card.column];

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
        <span className="column-label">{model.columnByKey[card.column]?.title}</span>
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

const MemoCallCard = memo(CallCard);

function CardFlight({ exitingCard, enteringCard, drawCount, phase, drawMode }) {
  return (
    <div className={`card-flight ${phase}`} aria-hidden="true">
      <div className="flight-card exit-card">
        <MemoCallCard card={exitingCard} drawCount={`exit-${drawCount}`} drawMode={drawMode} />
      </div>
      <div className="flight-card enter-card">
        <MemoCallCard card={enteringCard} drawCount={`enter-${drawCount}`} drawMode={drawMode} />
      </div>
    </div>
  );
}

const MemoCardFlight = memo(CardFlight);

function TopBar({ game, currentCard, onOpenBoards, onOpenTeaching }) {
  const { data } = useContent();
  const teachingMaterial = data.teachingMaterial || null;
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
      <div className="topbar-actions">
        {teachingMaterial ? (
          <button
            className="icon-button"
            type="button"
            onClick={onOpenTeaching}
            aria-label="Abrir tema do encontro"
          >
            <Icon name="lightbulb" />
          </button>
        ) : null}
        <button
          className="icon-button board-status"
          type="button"
          onClick={onOpenBoards}
          aria-label={`${game.activeBoardNumbers.length} cartelas em jogo`}
        >
          <Icon name="grid" />
        </button>
      </div>
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
  const { data, model } = useContent();
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
  const currentCode = game.drawnIds.length ? model.cardById[game.drawnIds.at(-1)]?.code || "" : "";
  const displayCode = pendingManualCode || activeColumn || lastCode || "...";
  const codeState = pendingManualCode ? "confirming" : activeColumn ? "selecting" : lastCode ? "registered" : "idle";
  const ballState = pendingManualCode ? "committing" : activeColumn ? "selecting" : lastCode ? "called" : "idle";
  const ballColumn = activeColumn || (pendingManualCode ? pendingManualCode[0] : lastCode ? lastCode[0] : "");
  const ballAccentColor = ballColumn ? model.COLUMN_COLORS[ballColumn] : "oklch(92% 0.015 80)";
  const locked = busy || Boolean(pendingManualCode);
  const keyboardVisuallyOpen = Boolean(activeColumn && motionPhase !== "closing");
  const controlsClass = [
    "manual-controls",
    activeColumn ? "expanded" : "",
    pendingManualCode ? "committing" : "",
    motionPhase !== "idle" ? `motion-${motionPhase}` : ""
  ].filter(Boolean).join(" ");
  const availableColumns = useMemo(() => {
    return Object.fromEntries(
      model.COLUMN_ORDER.map((column) => [
        column,
        numbers.some((number) => {
          const card = model.cardByCode[`${column}${number}`];
          return card && !drawnSet.has(card.id);
        })
      ])
    );
  }, [drawnSet, model, numbers]);
  const numberStates = useMemo(() => {
    return numbers.map((number) => {
      const card = renderColumn ? model.cardByCode[`${renderColumn}${number}`] : null;
      return {
        number,
        used: card ? drawnSet.has(card.id) : false,
        label: renderColumn ? `${renderColumn}${number}` : `Número ${number}`
      };
    });
  }, [drawnSet, model, numbers, renderColumn]);

  useEffect(() => {
    setLastCode(currentCode);
    if (!currentCode) {
      setActiveColumn("");
      setMotionPhase("idle");
      setPressedNumber("");
    }
  }, [currentCode]);

  useLayoutEffect(() => {
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
      window.requestAnimationFrame(callback);
    }, delay);
    manualCallTimers.current.push(timer);
  }

  function chooseColumn(column) {
    if (locked) return;
    clearManualCallTimers();
    setPressedNumber("");
    const nextColumn = activeColumn === column ? "" : column;
    setActiveColumn(nextColumn);
    setMotionPhase(nextColumn ? "selecting" : "idle");
    if (nextColumn) {
      scheduleManualCall(() => {
        setMotionPhase("idle");
      }, 240);
    }
  }

  function submitNumber(number) {
    if (!activeColumn || locked) return;
    const code = `${activeColumn}${number}`;
    const card = model.cardByCode[code];
    if (!card || drawnSet.has(card.id)) return;

    setLastCode(code);
    setPressedNumber(number);
    setMotionPhase("committing");
    setPendingManualCode(code);

    clearManualCallTimers();

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduceMotion) {
      setActiveColumn("");
      onCall(card.id);
      setPendingManualCode("");
      setPressedNumber("");
      setMotionPhase("idle");
      return;
    }

    scheduleManualCall(() => {
      setMotionPhase("closing");
    }, 150);

    scheduleManualCall(() => {
      setActiveColumn("");
    }, 520);

    scheduleManualCall(() => {
      onCall(card.id);
    }, 560);

    scheduleManualCall(() => {
      setPendingManualCode("");
      setPressedNumber("");
      setMotionPhase("idle");
    }, 700);
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
        >
          {model.COLUMN_ORDER.map((column) => (
            <button
              type="button"
              key={column}
              className={[
                "manual-column",
                activeColumn === column ? "selected" : "",
                !availableColumns[column] ? "exhausted" : ""
              ].filter(Boolean).join(" ")}
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

const MemoManualCallControls = memo(
  ManualCallControls,
  (previous, next) => previous.game === next.game && previous.busy === next.busy
);

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

  function endGesture(event) {
    const current = gesture.current;
    if (!current) return;

    const elapsed = Math.max(performance.now() - current.startTime, 1);
    const travel = Math.max(0, current.lastY - current.startY);
    const velocity = travel / elapsed;
    const shouldClose = current.active && (travel > 72 || (travel > 40 && velocity > 0.5));

    gesture.current = null;
    setDragging(false);
    suppressClick.current = false;

    if (event?.currentTarget?.releasePointerCapture && current.pointerId != null) {
      event.currentTarget.releasePointerCapture(current.pointerId);
    }

    if (shouldClose) {
      closeSheet(false);
    } else {
      setDrag(0);
    }
  }

  function beginPointer(event) {
    if (startGesture(event.clientX, event.clientY, event.target, event.pointerId)) {
      event.currentTarget.setPointerCapture?.(event.pointerId);
    }
  }

  function movePointer(event) {
    moveGesture(event.clientX, event.clientY, event);
  }

  function endPointer(event) {
    endGesture(event);
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
  const { model } = useContent();
  return (
    <div
      className={isOpen ? "history-row open" : "history-row"}
      data-history-id={historyKey}
      style={{ "--row-accent": model.COLUMN_COLORS[card.column] }}
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
  const { model } = useContent();
  const cards = [...game.drawnIds].reverse().map((id) => model.cardById[id]).filter(Boolean);
  const [openHistoryId, setOpenHistoryId] = useState(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (!openHistoryId) return undefined;
    const scrollEl = scrollRef.current;
    if (!scrollEl) return undefined;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const behavior = reduceMotion ? "auto" : "smooth";

    // Aguarda a animação de expansão do item terminar antes de rolar.
    // Rolar durante o layout shift no iOS PWA costuma travar o scroll.
    const timer = window.setTimeout(() => {
      const item = scrollEl.querySelector(`[data-history-id="${openHistoryId}"]`);
      if (!item) return;
      item.scrollIntoView({ block: "nearest", behavior });
    }, 200);

    return () => window.clearTimeout(timer);
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

const MemoHistorySheet = memo(HistorySheet);

async function fetchMaterialBlob(href) {
  const response = await fetch(href, { cache: "force-cache" });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.blob();
}

function canShareFile(file) {
  return typeof navigator.canShare === "function" && navigator.canShare({ files: [file] });
}

async function shareOrDownloadPDF(href, fileName, title, meta) {
  let blob;
  try {
    blob = await fetchMaterialBlob(href);
  } catch {
    // Se não conseguir ler do cache/offline, tenta abrir o link direto.
    window.open(href, "_blank");
    return;
  }

  const file = new File([blob], fileName, { type: "application/pdf" });

  // iOS PWA e Android abrem o share sheet nativo com "Salvar em Arquivos", Imprimir, etc.
  if (canShareFile(file)) {
    try {
      await navigator.share({ files: [file], title, text: meta });
      return;
    } catch (shareError) {
      // Usuário cancelou ou share falhou — prossegue para o fallback.
      if (shareError?.name === "AbortError") return;
    }
  }

  // Fallback para desktop/navegadores que não suportam share de arquivos.
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = fileName;
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.setTimeout(() => URL.revokeObjectURL(objectUrl), 2000);
}

function MaterialRow({ item }) {
  const [busy, setBusy] = useState(false);

  async function handleClick(event) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    try {
      await shareOrDownloadPDF(item.href, item.fileName, item.title, item.meta);
    } finally {
      setBusy(false);
    }
  }

  return (
    <button
      type="button"
      className={item.recommended ? "material-row recommended" : "material-row"}
      onClick={handleClick}
      disabled={busy}
      aria-busy={busy}
    >
      <span className="material-icon">
        <Icon name="download" />
      </span>
      <span className="material-copy">
        <strong>{item.title}</strong>
        <small>{busy ? "Preparando arquivo…" : item.meta}</small>
      </span>
    </button>
  );
}

function MaterialsSheet({ onClose }) {
  const { data } = useContent();
  const materialOptions = data.materials || [];

  return (
    <BottomSheet title="Imprimir" onClose={onClose} className="materials-sheet">
      <div className="materials-list">
        {materialOptions.map((item) => (
          <MaterialRow item={item} key={item.href} />
        ))}
      </div>
      <p className="materials-note">Com o app, normalmente basta imprimir as cartelas.</p>
    </BottomSheet>
  );
}

const MemoMaterialsSheet = memo(MaterialsSheet);

function TeachingSheet({ onClose }) {
  const { data } = useContent();
  const material = data.teachingMaterial || null;
  if (!material) return null;

  const meta = material.meta || [];
  const sections = material.sections || [];

  return (
    <BottomSheet title="Tema" onClose={onClose} className="teaching-sheet">
      <div className="teaching-scroll">
        <section className="teaching-hero" aria-labelledby="teaching-title">
          <span>{data.meetingLabel || data.meeting || "Encontro"}</span>
          <h3 id="teaching-title">{material.title || data.subtitle || data.title}</h3>
          {data.coreMessage ? <p>{data.coreMessage}</p> : null}
        </section>

        {meta.length ? (
          <dl className="teaching-meta">
            {meta.map((item) => (
              <div key={item.label}>
                <dt>{item.label}</dt>
                <dd>{item.value}</dd>
              </div>
            ))}
          </dl>
        ) : null}

        {material.pdf ? (
          <section className="teaching-pdf" aria-label="PDF do material didático">
            <MaterialRow item={material.pdf} />
          </section>
        ) : null}

        <div className="teaching-sections">
          {sections.map((section, sectionIndex) => (
            <section className="teaching-section" key={`${section.title}-${sectionIndex}`}>
              <h3>{section.title}</h3>
              {section.paragraphs.map((paragraph, index) => (
                <p key={`${section.title}-${sectionIndex}-${index}`}>{renderRich(paragraph)}</p>
              ))}
            </section>
          ))}
        </div>
      </div>
    </BottomSheet>
  );
}

const MemoTeachingSheet = memo(TeachingSheet);

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

const MemoRulesSheet = memo(RulesSheet);

function lineCountLabel(count) {
  if (count === 0) return "Nenhuma linha completa";
  if (count === 1) return "1 linha completa";
  return `${count} linhas completas`;
}

function MiniBoard({ board, drawnIds, highlightLineId, compact = false, decorative = false }) {
  const { model } = useContent();
  const marked = new Set([...drawnIds, "FREE"]);
  const highlight = highlightLineId ? model.lineDefinitions.find((line) => line.id === highlightLineId) : null;
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
  const { model } = useContent();
  const rows = game.activeBoardNumbers.map((number) => {
    const board = model.boardByNumber[number];
    const progress = model.getBoardProgress(board, game.drawnIds);
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

const MemoBoardsSheet = memo(BoardsSheet);

function AlertSheet({ game, alerts, onClose, onConfer }) {
  const { model } = useContent();
  const isMultiple = alerts.length > 1;
  const rows = alerts.map((alert) => {
    const board = model.boardByNumber[alert.boardNumber];
    const lines = model.getCompletedLines(board, game.drawnIds);
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

const MemoAlertSheet = memo(AlertSheet);

function ConceptDisclosure({ cell, isOpen, onToggle }) {
  const { model } = useContent();
  const card = cell.id === "FREE" ? null : model.cardById[cell.id];
  const accent = card ? model.COLUMN_COLORS[card.column] : "var(--free)";

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
  const { model } = useContent();
  const board = model.boardByNumber[boardNumber];
  const completedLines = useMemo(() => model.getCompletedLines(board, game.drawnIds), [board, game.drawnIds, model]);
  const [selectedLineId, setSelectedLineId] = useState(completedLines[0]?.id);
  const [openConceptId, setOpenConceptId] = useState(null);
  const scrollRef = useRef(null);
  const selectedLine = completedLines.find((line) => line.id === selectedLineId) || completedLines[0];
  const cells = selectedLine?.cells || [];
  const selectedLineLabel = selectedLine ? `${model.visibleLineType(selectedLine.kind)} ${lineTabLabel(selectedLine)}` : "linha completa";
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
              <span>{model.visibleLineType(line.kind)}</span>
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

const MemoConferenceSheet = memo(ConferenceSheet);

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
      }, 200);
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

const MemoConfirmDialog = memo(ConfirmDialog);

function LoadingScreen({ message = "Carregando encontro" }) {
  return (
    <main className="setup-screen">
      <div className="setup-content loading-content">
        <section className="setup-hero" aria-label={message}>
          <h1>Bingo</h1>
        </section>
        <div className="loading-panel" role="status" aria-live="polite">
          <span className="loading-mark" aria-hidden="true" />
          <strong>{message}</strong>
        </div>
      </div>
    </main>
  );
}

function GameScreen({ game, setGame, onReset }) {
  const { model } = useContent();
  const [sheet, setSheet] = useState(null);
  const [conferenceBoard, setConferenceBoard] = useState(null);
  const [toast, setToast] = useState("");
  const [flight, setFlight] = useState(null);
  const [showConfirmReset, setShowConfirmReset] = useState(false);
  const [manualKeyboardOpen, setManualKeyboardOpen] = useState(false);
  const flightTimers = useRef([]);
  const flightFrames = useRef([]);
  const drawMode = game.drawMode || DRAW_MODES.APP;
  const currentCard = game.drawnIds.length ? model.cardById[game.drawnIds.at(-1)] : null;
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

  const closeSheet = useCallback(() => setSheet(null), []);
  const closeConference = useCallback(() => setConferenceBoard(null), []);
  const closeConfirmReset = useCallback(() => setShowConfirmReset(false), []);
  const openTeachingSheet = useCallback(() => setSheet("teaching"), []);
  const openBoardsSheet = useCallback(() => setSheet("boards"), []);
  const openHistorySheet = useCallback(() => setSheet("history"), []);
  const reportManualKeyboardOpen = useCallback((isOpen) => setManualKeyboardOpen(isOpen), []);

  const presentCard = useCallback((nextCard, nextDrawCount, commitGame) => {
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
  }, [currentCard, setGame]);

  const draw = useCallback(() => {
    if (flight || game.deck.length === 0) return;

    const nextId = game.deck[0];
    const nextCard = model.cardById[nextId];
    const nextDrawCount = game.drawnIds.length + 1;
    presentCard(nextCard, nextDrawCount, (current) => model.drawNext(current));
  }, [flight, game.deck, game.drawnIds.length, model, presentCard]);

  const manualCall = useCallback((cardId) => {
    if (flight) return;
    const nextCard = model.cardById[cardId];
    const nextDrawCount = game.drawnIds.length + 1;
    presentCard(nextCard, nextDrawCount, (current) => model.drawCardById(current, cardId));
  }, [flight, game.drawnIds.length, model, presentCard]);

  const undo = useCallback(() => {
    if (flight) return;
    setGame((current) => model.undoLastDraw(current));
  }, [flight, model, setGame]);

  const closeAlert = useCallback(() => {
    const drawIndex = currentAlertBatch[0]?.drawIndex;
    if (typeof drawIndex === "number") {
      setGame((current) => model.dismissAlertBatch(current, drawIndex));
    }
  }, [currentAlertBatch, model, setGame]);

  const openConference = useCallback((boardNumber, alertDrawIndex) => {
    setConferenceBoard(boardNumber);
    setSheet(null);
    if (typeof alertDrawIndex === "number") {
      setGame((current) => model.dismissBoardAlert(current, boardNumber, alertDrawIndex));
    }
  }, [model, setGame]);

  const validated = useCallback((boardNumber, lineId) => {
    setGame((current) => model.recordValidatedWin(current, boardNumber, lineId));
    setConferenceBoard(null);
    setToast(`Cartela ${boardNumber.toString().padStart(2, "0")} validada`);
    window.setTimeout(() => setToast(""), 2200);
  }, [model, setGame]);

  const newGame = useCallback(() => {
    setShowConfirmReset(true);
  }, []);

  const confirmReset = useCallback(() => {
    setShowConfirmReset(false);
    // Wait for modal exit animation to start before resetting the board
    setTimeout(() => {
      onReset();
      setSheet(null);
    }, 300);
  }, [onReset]);

  const drawnCount = game.drawnIds.length;

  return (
    <main className={screenClass}>
      <TopBar
        game={game}
        currentCard={currentCard}
        onOpenBoards={openBoardsSheet}
        onOpenTeaching={openTeachingSheet}
      />

      <section className="card-stage" aria-live="polite">
        {flight ? (
          <MemoCardFlight
            exitingCard={flight.exitingCard}
            enteringCard={flight.enteringCard}
            drawCount={flight.drawCount}
            phase={flight.phase}
            drawMode={drawMode}
          />
        ) : (
          <MemoCallCard card={currentCard} drawCount={drawnCount} drawMode={drawMode} />
        )}
      </section>

      {drawMode === DRAW_MODES.MANUAL ? (
        <MemoManualCallControls
          game={game}
          onUndo={undo}
          onCall={manualCall}
          onHistory={openHistorySheet}
          onKeyboardOpenChange={reportManualKeyboardOpen}
          busy={Boolean(flight)}
        />
      ) : (
        <BottomControls game={game} onUndo={undo} onDraw={draw} onHistory={openHistorySheet} busy={Boolean(flight)} />
      )}

      {sheet === "teaching" ? <MemoTeachingSheet onClose={closeSheet} /> : null}
      {sheet === "history" ? <MemoHistorySheet game={game} onClose={closeSheet} onNewGame={newGame} /> : null}
      {sheet === "boards" ? <MemoBoardsSheet game={game} onClose={closeSheet} onConfer={openConference} /> : null}
      {currentAlertBatch.length > 0 && !conferenceBoard && !flight ? (
        <MemoAlertSheet game={game} alerts={currentAlertBatch} onClose={closeAlert} onConfer={openConference} />
      ) : null}
      {conferenceBoard ? (
        <MemoConferenceSheet
          game={game}
          boardNumber={conferenceBoard}
          onClose={closeConference}
          onValidated={validated}
        />
      ) : null}
      <Toast message={toast} />
      
      <MemoConfirmDialog
        isOpen={showConfirmReset}
        title="Novo jogo?"
        message="Todo o progresso do jogo atual será perdido. Deseja mesmo reiniciar?"
        confirmLabel="Sim, reiniciar"
        cancelLabel="Cancelar"
        onConfirm={confirmReset}
        onCancel={closeConfirmReset}
      />
    </main>
  );
}

export default function App() {
  const [catalog, setCatalog] = useState(DEFAULT_CATALOG);
  const [contentId, setContentId] = useState(() => loadSelectedContentId() || DEFAULT_CATALOG.defaultContentId);
  const [activeData, setActiveData] = useState(defaultData);
  const [contentStatus, setContentStatus] = useState("ready");
  const [contentError, setContentError] = useState("");
  const [game, setGame] = useState(null);
  const model = useMemo(() => createGameModel(activeData), [activeData]);
  const activeCatalogItem = useMemo(
    () => catalog.items.find((item) => item.id === activeData.slug) || catalogItemFromData(activeData, ""),
    [activeData, catalog.items]
  );

  useEffect(() => {
    let cancelled = false;

    fetchJson(CONTENT_CATALOG_URL)
      .then((nextCatalog) => {
        if (cancelled) return;
        const nextItems = nextCatalog.items?.length ? nextCatalog.items : DEFAULT_CATALOG.items;
        const savedContentId = loadSelectedContentId();
        const defaultContentId = nextCatalog.defaultContentId || nextItems[0]?.id || defaultData.slug;
        const nextContentId = nextItems.some((item) => item.id === savedContentId) ? savedContentId : defaultContentId;
        setCatalog({ ...nextCatalog, defaultContentId, items: nextItems });
        setContentId(nextContentId);
      })
      .catch(() => {
        if (cancelled) return;
        setCatalog(DEFAULT_CATALOG);
        setContentId(DEFAULT_CATALOG.defaultContentId);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const item = catalog.items.find((candidate) => candidate.id === contentId);
    if (!item) return undefined;

    let cancelled = false;
    setContentStatus((current) => (current === "ready" ? "switching" : current));
    setContentError("");

    const applyContent = (nextData) => {
      if (cancelled) return;
      setActiveData(nextData);
      setGame(loadSavedGame(nextData));
      setContentStatus("ready");
    };

    if (item.href === "./data/game-data.json") {
      applyContent(defaultData);
      return () => {
        cancelled = true;
      };
    }

    fetchJson(item.href)
      .then(applyContent)
      .catch((error) => {
        if (cancelled) return;
        setContentError(error.message || "Não foi possível carregar este encontro.");
        applyContent(defaultData);
      });

    return () => {
      cancelled = true;
    };
  }, [catalog.items, contentId]);

  useEffect(() => {
    document.title = activeData.title || "Bingo";
  }, [activeData.title]);

  useEffect(() => {
    saveSelectedContentId(contentId);
  }, [contentId]);

  useEffect(() => {
    if (contentStatus !== "ready") return;
    saveGame(activeData, game);
  }, [activeData, contentStatus, game]);

  const selectContent = useCallback((nextContentId) => {
    if (!nextContentId || nextContentId === contentId) return;
    setContentStatus("switching");
    setContentId(nextContentId);
  }, [contentId]);

  const contextValue = useMemo(
    () => ({
      data: activeData,
      model,
      catalog,
      contentId,
      activeCatalogItem,
      contentError,
      onSelectContent: selectContent
    }),
    [activeCatalogItem, activeData, catalog, contentError, contentId, model, selectContent]
  );

  const appReady = Boolean(activeData.cards?.length && activeData.boards?.length);

  if (contentStatus === "loading" && !appReady) {
    return <LoadingScreen />;
  }

  if (!appReady) {
    return <LoadingScreen message="Conteúdo indisponível" />;
  }

  return (
    <ContentContext.Provider value={contextValue}>
      {!game ? (
        <SetupScreen onStart={(selection, drawMode) => setGame(model.createGame(selection, drawMode))} />
      ) : (
        <GameScreen game={game} setGame={setGame} onReset={() => setGame(null)} />
      )}
    </ContentContext.Provider>
  );
}
