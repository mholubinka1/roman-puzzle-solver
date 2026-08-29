# Backtracking Solver with Live Progress Display

## Problem Statement

The Roman Puzzle Solver does not work. `main.py` cannot even be imported: `arrange.py`
has a function with an empty body, `card/card.py` imports from the wrong paths and
references an undefined variable, and `card/loader.py` (currently `setup.py`) reads a key
that does not exist in the card config. Nobody can run the solver, and there is no way to
watch it search.

The user wants two things: the solver to actually find the puzzle's one true arrangement,
and something moving in the terminal that shows the search happening as it runs.

## Solution

Rebuild the card model and the arranger around a depth-first backtracking search. The
search is deterministic and complete, so it is guaranteed to find the unique arrangement.

Running `python main.py` loads the twelve cards, searches, and — unless `--no-animate` is
passed — draws a live 4x3 grid in the terminal that redraws as the search places cards,
rejects candidates, and backtracks. When the search succeeds the solved grid is left on
screen, the arrangement is written to `out/solution.json`, and a one-line confirmation
naming that path is printed.

## User Stories

1. As a puzzle owner, I want `python main.py` to find the puzzle's arrangement and tell me
   where it saved the answer, so that I can reproduce the physical solution.
2. As a puzzle owner, I want the arrangement written to `out/solution.json` keyed by grid
   coordinate, so that I can look up which card and orientation belongs in each position.
3. As a curious observer, I want to watch a live 4x3 grid in the terminal fill in, flicker
   through rejected candidates, and collapse back on dead ends, so that I can see how the
   backtracking search works.
4. As an observer, I want a `--delay` control on the animation, so that I can slow the
   search down enough to follow it or run it at full speed when I just want the answer.
5. As a user on a plain terminal or in a script, I want a `--no-animate` flag, so that I
   can solve the puzzle without any live rendering.
6. As a user with a different or broken card set, I want the loader to reject a malformed
   card config with a clear error, so that I know the input is wrong rather than seeing a
   confusing crash deep in the search.
7. As a maintainer, I want the arranger to run headless with no display dependency, so that
   it can be tested and reused without a terminal.
8. As a maintainer, I want the search to report its progress through an observer, so that
   the terminal rendering is decoupled from the search and other observers (e.g. a logger)
   can be added later.
9. As a maintainer, I want the domain glossary and README to describe the solver as it
   actually is, so that the docs stop referring to an MCMC implementation that no longer
   exists.

## Implementation Decisions

### Card model (rebuild)

- **`SymbolType`** (`card/symbol_type.py`): kept essentially as-is — the six symbol types
  (Chariot, Banner, Spearman, Swordsman, Dark Coin, Light Coin) plus a string parser.
- **`Side`** (`card/side.py`): the four sides Top, Right, Bottom, Left, ordered clockwise
  so that rotation is index arithmetic. Kept close to the current `Sides` enum.
- **`Symbol`** (`card/card.py`): an immutable pair of symbol type and half (`1` or `-1`).
  `is_match(other)` is true when `other` is a missing neighbour (`None`), or when the types
  are equal and the two halves sum to zero.
- **`Card`** (`card/card.py`): immutable. Holds a card number and its four symbols in
  canonical (orientation 0) positions. It does **not** hold an orientation. A card exposes
  `symbol_at(side, orientation)` which returns the symbol occupying `side` when the card is
  rotated `orientation` degrees clockwise. Orientation is always one of `0, 90, 180, 270`.
  The current mutable `rotate()` method is removed.

### Orientation convention

`orientation` is degrees of **clockwise** rotation. At orientation `90` each canonical
symbol moves one side clockwise: canonical Top occupies Right, Right occupies Bottom,
Bottom occupies Left, Left occupies Top. Equivalently, `symbol_at(Right, 90)` returns the
card's canonical Top symbol. This single convention is used by the loader (which reads
canonical positions verbatim), `symbol_at`, the progress display, and the `orientation`
value written to `out/solution.json`.

### Loader (rename + validation)

- `setup.py` becomes **`card/loader.py`**, exposing `load_cards(config_path)` returning a
  list of `Card`.
- Structural validation only, raising a clear error on any violation: exactly 12 cards;
  each card has exactly 4 sides; the side ids are exactly `top`, `right`, `bottom`, `left`
  (one of each); every `symbol` resolves to a known `SymbolType`; every `half` is `1` or
  `-1`.
- No global feasibility analysis — whether the deck can tile a 4x3 rectangle is the
  search's job.
- `card_config.json` is unchanged.

### Arrangement

- **`arrangement.py`**: a value type for the 4x3 grid. Each cell is either empty or a
  placement (a card plus an orientation). Coordinates are `(x, y)` with `x` the column
  `0..3` left to right and `y` the row `0..2` top to bottom; `(0, 0)` is top-left.
- Provides read access to the placement at a coordinate (used to find the left and top
  neighbours during the search) and a way to enumerate all twelve placements for output.

### Arranger (backtracking DFS)

- `arrange.py` becomes **`arranger.py`**, exposing **`Arranger`** (the `MCMCArranger`
  name is removed).
- `solve(cards, observer=None)` fills cells in row-major order from `(0, 0)`:
  `(0,0), (1,0), (2,0), (3,0), (0,1), ...`. At each cell it iterates the not-yet-placed
  cards in ascending card-number order, and for each card tries orientations
  `0, 90, 180, 270` in that order.
- A `(card, orientation)` candidate is **valid** for a cell when its left edge matches the
  placement already in the cell to its left and its top edge matches the placement above
  it. A neighbour off the grid edge counts as a missing neighbour and always matches.
- On a valid candidate the arranger places it and recurses to the next cell. When a cell
  exhausts every card/orientation with nothing valid, it backtracks to the previous cell
  and resumes that cell's iteration.
- The first fully populated grid is the result. Because the puzzle has exactly one
  arrangement the search stops there.
- If the whole space is exhausted without filling the grid, `solve` raises a clear
  "no arrangement exists for this card configuration" error.

### Observer protocol

- `solve` reports progress by calling methods on the `observer` when one is supplied:
  a placement was accepted, a candidate was rejected (card, orientation, cell), and a
  backtrack occurred (cell vacated). This is "medium" granularity — accepted placements,
  rejected candidates, and backtracks all produce an event; per-edge checks do not.
- When `observer` is `None` the search runs silently with no rendering dependency.
- The observer is a plain protocol/interface; `progress.py` provides one implementation
  and a logger or test spy could provide others.

### Progress display

- **`progress.py`**: an observer implementation that renders a live 4x3 grid to the
  terminal using `rich`, redrawing in place on every observer event.
- Each cell shows the card number centred, with a two-character symbol-type code and the
  half sign (`+` / `-`) on each of the four edges. Codes: `Ch`, `Bn`, `Sp`, `Sw`, `Dk`,
  `Lt`. A one-line legend for those codes sits above the grid.
- The cell currently being worked is highlighted. A status line shows counts:
  cards placed out of 12, backtracks, and total steps.
- After each event the renderer sleeps for the configured delay (milliseconds) so the
  animation is watchable; a delay of `0` disables the sleep.
- On success the solved grid is left on screen.

### CLI and output

- `main.py` uses `argparse`:
  - `--delay MS` — per-event animation delay in milliseconds. Default `50`. `0` runs at
    full speed.
  - `--config PATH` — card config file. Default `card_config.json`.
  - `--out DIR` — output directory. Default `out/`.
  - `--no-animate` — solve without constructing or attaching the progress observer.
- On success `main.py` writes `<out>/solution.json` and prints a single confirmation line
  naming that path.
- `out/solution.json` is a JSON object keyed by `"x,y"` strings (`x` column `0..3`,
  `y` row `0..2`, `(0,0)` top-left), each value `{"card": <int>, "orientation": <0|90|180|270>}`.
- On the no-solution error nothing is written to the output directory and the process
  exits non-zero.
- `out/` is added to `.gitignore`.

### Dependencies

- `rich` is added to `[project].dependencies` in `pyproject.toml` — the first runtime
  dependency.
- `pytest` and `pytest-cov` are added to the `dev` dependency group.

### Documentation

- `.agent-docs/context.md`: the **Arranger** entry no longer mentions MCMC or
  `MCMCArranger`; it describes a depth-first backtracking search. The **Card** entry no
  longer states that a card "carries ... an orientation"; the **Orientation** and
  **Arrangement** entries make clear that orientation is a property of a card's placement
  within an arrangement, not of the card itself.
- `README.md`: the "work in progress and does not yet run" note is replaced with a short
  description of how to run the solver and its flags.

## Testing Decisions

Tests verify external behaviour at the seams agreed with the user; internals of the
`rich` rendering and the argparse wiring are not tested directly.

- **`Symbol.is_match`**: equal type with halves summing to zero matches; a `None`
  neighbour always matches; a type mismatch and a non-zero half sum each fail.
- **`Card.symbol_at(side, orientation)`**: for a card with four distinct known symbols,
  every `(side, orientation)` pair returns the expected canonical symbol, covering all
  four orientations and confirming the clockwise convention.
- **`load_cards(path)`** (`card/loader.py`): a valid config yields 12 `Card` objects with
  the expected numbers and canonical symbols. Separate malformed fixtures — wrong card
  count, a card missing a side, a duplicated side id, an unknown symbol name, a half that
  is not `1` or `-1` — each raise. Prior art: the existing `load_cards` reads
  `card_config.json`; fixtures live beside the tests.
- **`Arranger.solve(cards)`** — the acceptance test: run against the real
  `card_config.json` with no observer and independently verify the returned arrangement —
  every interior edge (horizontal and vertical) is a match, and each card number `1..12`
  appears exactly once. A deliberately unsolvable 12-card set raises the no-solution
  error.
- **Solution-dict builder**: a known small arrangement serialises to the expected
  `{"x,y": {"card", "orientation"}}` shape with `(0,0)` top-left and column-first keys.
- **Observer protocol**: solving a tiny hand-constructed puzzle with a spy observer
  records at least one accepted placement and, for a case that forces a dead end, at least
  one rejection and one backtrack, ending in the completed arrangement.
- Coverage is enforced at >= 80% (`.agent-docs/agent.md` section 3), measured with
  `pytest-cov`. `progress.py` is expected to be largely uncovered and that is acceptable;
  the coverage target is met by the model, loader, arranger, and output code.

## Out of Scope

- Any HTML or graphical visualiser. The live display is terminal-only.
- Global feasibility analysis of a card deck before searching.
- Alternative search strategies (MCMC, exact cover / dancing links).
- Solving grids other than 4x3, or decks other than 12 cards.
- A `console_scripts` entry point — `pyproject.toml` keeps `package = false`.
- Re-keying, editing, or validating the *content* of `card_config.json` beyond structural
  checks.
- Reading the physical puzzle from a photograph or any other input path.

## Further Notes

- The puzzle has exactly one arrangement, so "find a valid arrangement" and "find the
  solution" are the same thing; the search does not need to prove uniqueness.
- `symbol_type.py` and `side.py` are close to correct already and should be salvaged
  rather than rewritten wholesale.
- The two-axis grilling for this work was done in a preceding wayfinder session; its
  locked decisions (Q1-Q15) are the source of the Implementation Decisions above.
