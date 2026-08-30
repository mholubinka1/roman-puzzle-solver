from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from typing import NamedTuple

from rich.console import Console, Group, RenderableType
from rich.live import Live
from rich.table import Table
from rich.text import Text

from arrangement import CELL_COUNT, COLS, ROWS, Placement
from arranger import SearchObserver
from card.card import Symbol
from card.side import Side
from card.symbol_type import SymbolType

# Two-letter grid code and legend name for each symbol type. Names match the
# glossary in .agent-docs/context.md.
_SYMBOLS = {
    SymbolType.CHARIOT: ("Ch", "Chariot"),
    SymbolType.BANNER: ("Bn", "Banner"),
    SymbolType.SPEARMAN: ("Sp", "Spearman"),
    SymbolType.SWORDSMAN: ("Sw", "Swordsman"),
    SymbolType.DARKCOIN: ("Dk", "Dark Coin"),
    SymbolType.LIGHTCOIN: ("Lt", "Light Coin"),
}

_LEGEND = "  ".join(f"{code} {name}" for code, name in _SYMBOLS.values())

Cell = tuple[int, int]


class Counts(NamedTuple):
    """The running search tallies shown on the status line."""

    placed: int
    backtracks: int
    steps: int


def symbol_label(symbol: Symbol) -> str:
    code, _name = _SYMBOLS[symbol.type]
    sign = "+" if symbol.half == 1 else "-"
    return f"{code}{sign}"


def format_cell(placement: Placement) -> str:
    """A three-line block: card number centred, oriented edge labels around it."""
    top = symbol_label(placement.symbol_at(Side.TOP))
    right = symbol_label(placement.symbol_at(Side.RIGHT))
    bottom = symbol_label(placement.symbol_at(Side.BOTTOM))
    left = symbol_label(placement.symbol_at(Side.LEFT))
    number = str(placement.card.number)
    return "\n".join(
        [
            f"   {top}   ",
            f"{left} {number:^3} {right}",
            f"   {bottom}   ",
        ]
    )


def render(
    cells: Mapping[Cell, Placement], current: Cell | None, counts: Counts
) -> RenderableType:
    grid = Table.grid(padding=(0, 1))
    for _ in range(COLS):
        grid.add_column(justify="center")
    for y in range(ROWS):
        row = []
        for x in range(COLS):
            placement = cells.get((x, y))
            text = format_cell(placement) if placement else "  --  "
            style = "reverse" if (x, y) == current else ""
            row.append(Text(text, style=style))
        grid.add_row(*row)
    stats = (
        f"placed {counts.placed}/{CELL_COUNT} · "
        f"backtracks {counts.backtracks} · steps {counts.steps}"
    )
    return Group(Text(_LEGEND, style="dim"), grid, Text(stats))


class ProgressObserver(SearchObserver):
    """Renders the backtracking search as a live 4x3 grid in the terminal.

    Every placement and backtrack updates the model; ``rich.Live`` repaints the
    screen on its own ~20fps timer, so the render cost is independent of how many
    events the search fires. ``delay_ms`` slows the search itself between events.
    """

    def __init__(
        self,
        *,
        delay_ms: int = 10,
        console: Console | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if delay_ms < 0:
            raise ValueError(f"delay_ms must be zero or greater, got {delay_ms}")
        self._delay = delay_ms / 1000
        self._sleep = sleep
        self._console = console or Console()
        self._live = Live(
            self,
            console=self._console,
            auto_refresh=True,
            refresh_per_second=20,
            transient=True,
        )
        self._cells: dict[Cell, Placement] = {}
        self._current: Cell | None = None
        self.placed = 0
        self.backtracks = 0
        self.steps = 0

    def __rich__(self) -> RenderableType:
        counts = Counts(self.placed, self.backtracks, self.steps)
        return render(self._cells, self._current, counts)

    def __enter__(self) -> ProgressObserver:
        self._live.start()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._current = None
        self._live.stop()
        if exc_type is None:
            # Leave one clean grid on screen; on a failed search main() reports why.
            self._console.print(self.__rich__())

    def on_placement(self, x: int, y: int, placement: Placement) -> None:
        self._cells[(x, y)] = placement
        self.placed += 1
        self._tick((x, y))

    def on_backtrack(self, x: int, y: int) -> None:
        if self._cells.pop((x, y), None) is not None:
            self.placed -= 1
        self.backtracks += 1
        self._tick((x, y))

    def _tick(self, current: Cell) -> None:
        self.steps += 1
        self._current = current
        if self._delay:
            self._sleep(self._delay)
