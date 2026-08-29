# Issues: feature/backtracking-solver-live-progress

## Slice 1 — Card model and loader with validation

**Blocked by**: None

**User stories**: 6, 7 (foundation for all)

### What to build

Rebuild the card model as immutable value types and turn the config loader into a
validating function.

- `Symbol`: immutable pair of symbol type and half (`1` or `-1`). `is_match(other)` is
  true when `other` is `None` (a missing neighbour), or when the symbol types are equal
  and the two halves sum to zero.
- `Card`: immutable. Holds a card number and its four symbols in canonical (orientation 0)
  positions. No stored orientation, no mutation. `symbol_at(side, orientation)` returns the
  symbol occupying `side` when the card is rotated `orientation` degrees clockwise
  (`orientation` in `0, 90, 180, 270`). At orientation `90` the canonical Top symbol
  occupies Right.
- `Side` and `SymbolType` are salvaged from the current `card/side.py` and
  `card/symbol_type.py`; `Side` is ordered clockwise so rotation is index arithmetic.
- `setup.py` becomes `card/loader.py` exposing `load_cards(config_path)` returning a list
  of `Card`. It validates structure only and raises a clear error on any violation:
  exactly 12 cards; each card has exactly 4 sides; side ids are exactly `top`, `right`,
  `bottom`, `left` with one of each; every `symbol` resolves to a known `SymbolType`;
  every `half` is `1` or `-1`. No feasibility analysis.
- `card_config.json` is unchanged.

### Acceptance criteria

- [x] `Symbol.is_match` returns true for equal type with halves summing to zero, true for a
      `None` neighbour, false for a type mismatch, and false for a non-zero half sum.
- [x] `Card.symbol_at(side, orientation)` returns the correct canonical symbol for every
      side across all four orientations, consistent with a clockwise rotation.
- [x] `Card` and `Symbol` instances cannot be mutated after construction; there is no
      `rotate` method.
- [x] `load_cards("card_config.json")` returns 12 `Card` objects with the expected numbers
      and canonical symbols.
- [x] `load_cards` raises a clear error for each of: wrong card count, a card missing a
      side, a duplicated side id, an unknown symbol name, a half that is not `1` or `-1`.
- [x] The pre-commit suite passes on all changed files.

---

## Slice 2 — Headless backtracking solver, solution.json, and CLI

**Blocked by**: #4

**User stories**: 1, 2, 7

### What to build

The depth-first backtracking search, run end-to-end from `python main.py` with no
animation.

- `arrangement.py`: a value type for the 4x3 grid. Each cell is empty or a placement
  (card plus orientation). Coordinates are `(x, y)`, `x` column `0..3` left to right,
  `y` row `0..2` top to bottom, `(0, 0)` top-left. Read access to the placement at a
  coordinate; enumeration of all twelve placements.
- `arrange.py` becomes `arranger.py` exposing `Arranger`. `solve(cards, observer=None)`
  fills cells row-major from `(0, 0)`; at each cell iterates not-yet-placed cards in
  ascending card-number order, each at orientations `0, 90, 180, 270`. A candidate is
  valid when its left edge matches the placement to its left and its top edge matches the
  placement above; a neighbour off the grid edge is a missing neighbour and always
  matches. Place and recurse on a valid candidate; backtrack when a cell is exhausted.
  The first full grid is returned. If the space is exhausted, raise a clear
  "no arrangement exists for this card configuration" error.
- `observer` is accepted but may be `None`; when `None` the search runs silently. The
  call sites for placement and backtrack events exist so Slice 3 can attach a real
  observer without touching the search.
- A solution-dict builder turns an arrangement into a JSON object keyed by `"x,y"`
  strings, each value `{"card": <int>, "orientation": <0|90|180|270>}`.
- `main.py` uses `argparse` with `--config PATH` (default `card_config.json`) and
  `--out DIR` (default `out/`). It loads, solves headless, writes `<out>/solution.json`,
  and prints one confirmation line naming that path. On the no-solution error it writes
  nothing and exits non-zero.
- `out/` is added to `.gitignore`.

### Acceptance criteria

- [x] `Arranger.solve` against the real `card_config.json` returns an arrangement in which
      every interior edge (horizontal and vertical) matches and each card number `1..12`
      appears exactly once.
- [x] A deliberately unsolvable 12-card set makes `solve` raise the no-solution error.
- [x] The solution-dict builder produces `{"x,y": {"card", "orientation"}}` with `(0,0)`
      top-left and column-first keys for a known arrangement.
- [x] `python main.py` writes `out/solution.json` and prints a line naming that path.
- [x] `python main.py` with a config that has no solution exits non-zero and leaves the
      output directory untouched.
- [x] `out/` is gitignored.
- [x] The pre-commit suite passes on all changed files.

---

## Slice 3 — Live terminal progress display

**Blocked by**: #5

**User stories**: 3, 4, 5, 8

### What to build

An observer that renders the search live, wired into `main.py` as the default.

- Formalise the observer protocol: methods for an accepted placement (card, orientation,
  cell) and a backtrack (cell vacated). Rejected candidates produce **no** event — on the
  real puzzle the search rejects ~45,000 candidates vs ~1,700 placements, so rejects are
  unwatchable and a per-reject sleep makes a run take tens of minutes. ~3,400
  placement/backtrack events are the signal.
- `progress.py`: an observer implementation that renders a live 4x3 grid to the terminal
  with `rich`. The screen repaints on `rich.Live`'s own ~20fps timer (decoupled from the
  event rate); the live region is transient and one final grid is printed on completion.
  Each cell shows the card number centred with a two-character symbol-type code and half
  sign (`+` / `-`) on each edge (rotated to the placement's orientation); codes `Ch`,
  `Bn`, `Sp`, `Sw`, `Dk`, `Lt`, with a one-line legend above the grid. The cell being
  worked is highlighted. A status line shows cards placed out of 12, backtracks, and total
  steps. After each placement/backtrack the search sleeps for the configured delay in
  milliseconds; `0` disables the sleep. The solved grid is left on screen.
- `main.py` gains `--delay MS` (default `10`) and `--no-animate`. Animation is on by
  default; `--no-animate` solves without constructing or attaching the observer.
- `rich` is added to `[project].dependencies` in `pyproject.toml`.

### Acceptance criteria

- [x] Solving the real puzzle with a spy observer records only placement and backtrack
      events (both kinds occur), ending with the completed arrangement.
- [x] The `ProgressObserver` counters (placed / backtracks / steps) are correct across a
      scripted event sequence.
- [x] `python main.py` renders a live grid that changes as the search runs and leaves the
      solved grid on screen.
- [x] `python main.py --no-animate` produces no live rendering and still writes
      `out/solution.json`.
- [x] `--delay 0` runs with no inter-event sleep (verified with an injected sleep);
      a larger `--delay` slows the animation.
- [x] `rich` is declared as a runtime dependency.
- [x] The pre-commit suite passes on all changed files.

---

## Slice 4 — Documentation

**Blocked by**: #6

**User stories**: 9

### What to build

Bring the glossary and README in line with the rebuilt solver.

- `.agent-docs/context.md`: the `Arranger` entry no longer mentions MCMC or
  `MCMCArranger` and describes a depth-first backtracking search. The `Card` entry no
  longer says a card "carries ... an orientation". The `Orientation` and `Arrangement`
  entries make clear that orientation is a property of a card's placement within an
  arrangement, not of the card itself.
- `README.md`: replace the "work in progress and does not yet run" note with a short
  description of how to run the solver (`python main.py`) and its flags (`--delay`,
  `--config`, `--out`, `--no-animate`), and where the solution is written.

### Acceptance criteria

- [x] `.agent-docs/context.md` contains no reference to MCMC or `MCMCArranger`.
- [x] The `Card` glossary entry does not attribute an orientation to the card itself.
- [x] `README.md` documents `python main.py`, all four flags, and the `out/solution.json`
      output location.
- [x] The pre-commit suite passes on all changed files.

---
