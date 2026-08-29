from collections.abc import Iterator
from dataclasses import dataclass, field

from card.card import Card, Symbol
from card.side import Side

COLS = 4
ROWS = 3
CELL_COUNT = COLS * ROWS


@dataclass(frozen=True)
class Placement:
    """A card placed in the grid at a chosen orientation."""

    card: Card
    orientation: int

    def symbol_at(self, side: Side) -> Symbol:
        return self.card.symbol_at(side, self.orientation)


@dataclass(frozen=True)
class Arrangement:
    """An immutable 4x3 grid of placements, addressed by (x, y) with (0, 0) top-left."""

    cells: tuple[Placement | None, ...] = field(default=(None,) * CELL_COUNT)

    def placement_at(self, x: int, y: int) -> Placement | None:
        return self.cells[y * COLS + x]

    def with_placement(self, x: int, y: int, placement: Placement) -> "Arrangement":
        updated = list(self.cells)
        updated[y * COLS + x] = placement
        return Arrangement(tuple(updated))

    def is_complete(self) -> bool:
        return all(cell is not None for cell in self.cells)

    def placements(self) -> Iterator[tuple[int, int, Placement]]:
        for y in range(ROWS):
            for x in range(COLS):
                placement = self.placement_at(x, y)
                if placement is not None:
                    yield x, y, placement


def to_solution_dict(arrangement: Arrangement) -> dict[str, dict[str, int]]:
    return {
        f"{x},{y}": {
            "card": placement.card.number,
            "orientation": placement.orientation,
        }
        for x, y, placement in arrangement.placements()
    }
