# Roman Puzzle Solver

This context covers a solver for "Romans Mindbender", a physical tile puzzle of 12 square
cards that must be laid into a single 4x3 rectangle so that every picture split across two
touching edges is completed correctly.

## Language

### The puzzle

**Card**:
One of the 12 square tiles. Carries a card number, one symbol per edge, and an orientation.
_Avoid_: Square, tile, piece

**Arrangement**:
A complete placement of all 12 cards into the 4x3 grid, each at some orientation, such that
every pair of touching edges matches. The puzzle has exactly one.
_Avoid_: Solution, layout, board, configuration

**Orientation**:
The rotation of a card within the grid, always a multiple of 90 degrees (0, 90, 180, 270).
Rotating a card permutes which symbol sits on which side.
_Avoid_: Angle, rotation state, facing

### Cards and symbols

**Symbol**:
The half-picture printed on one edge of a card. It pairs a symbol type with a half.
_Avoid_: Picture, image, icon, tile face

**Symbol type**:
The subject of a symbol's picture: Chariot, Banner, Spearman, Swordsman, Dark Coin, or
Light Coin.
_Avoid_: Category, kind, class

**Half**:
Which portion of a picture a symbol shows, recorded as `1` or `-1`. The two halves of one
picture are complementary and carry opposite values.
_Avoid_: Polarity, sign, parity, side (of the picture)

**Side**:
An edge of a card, named Top, Right, Bottom, or Left. Each side holds exactly one symbol.
_Avoid_: Edge, face, direction

**Match**:
The relationship between two symbols that may legally touch: same symbol type and halves
that sum to zero. A symbol always matches against a missing neighbour.
_Avoid_: Fit, join, pair, compatible

**Card config**:
The `card_config.json` file describing each card by number and listing its four sides with
their symbol and half. The solver loads its cards from this file.
_Avoid_: Card data, deck file, puzzle input

### Solving

**Arranger**:
The component that searches for the arrangement. The current implementation
(`MCMCArranger`) is intended to explore placements via Markov chain Monte Carlo sampling.
_Avoid_: Solver, engine, searcher
