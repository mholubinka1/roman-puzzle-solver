from __future__ import annotations

import time
from collections.abc import Callable, Mapping

from rich.console import Console, Group, RenderableType
from rich.live import Live
from rich.table import Table
from rich.text import Text

from arrangement import COLS, ROWS, Placement
from arranger import SearchObserver
from card.card import Symbol
from card.side import Side
from card.symbol_type import SymbolType

SYMBOL_CODES = {
    SymbolType.CHARIOT: "Ch",
    SymbolType.BANNER: "Bn",
    SymbolType.SPEARMAN: "Sp",
    SymbolType.SWORDSMAN: "Sw",
    SymbolType.DARKCOIN: "Dk",
    SymbolType.LIGHTCOIN: "Lt",
}

_LEGEND = "  ".join(
    f"{code} {kind.name.title()}" for kind, code in SYMBOL_CODES.items()
)

Cell = tuple[int, int]


def symbol_label(symbol: Symbol) -> str:
    sign = "+" if symbol.half == 1 else "-"
    return f"{SYMBOL_CODES[symbol.type]}{sign}"


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
    cells: Mapping[Cell, Placement],
    current: Cell | None,
    placed: int,
    backtracks: int,
    steps: int,
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
    stats = f"placed {placed}/12 · backtracks {backtracks} · steps {steps}"
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
        return render(
            self._cells, self._current, self.placed, self.backtracks, self.steps
        )

    def __enter__(self) -> ProgressObserver:
        self._live.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self._current = None
        self._live.stop()
        self._console.print(self.__rich__())

    def on_placement(self, x: int, y: int, placement: Placement) -> None:
        self._cells[(x, y)] = placement
        self.placed += 1
        self._tick((x, y))

    def on_backtrack(self, x: int, y: int) -> None:
        self._cells.pop((x, y), None)
        self.placed -= 1
        self.backtracks += 1
        self._tick((x, y))

    def _tick(self, current: Cell) -> None:
        self.steps += 1
        self._current = current
        if self._delay:
            self._sleep(self._delay)
