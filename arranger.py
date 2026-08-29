from arrangement import COLS, ROWS, Arrangement, Placement
from card.card import Card
from card.side import Side

_ORIENTATIONS = (0, 90, 180, 270)
_CELLS = [(x, y) for y in range(ROWS) for x in range(COLS)]


class NoArrangementError(Exception):
    """Raised when no arrangement satisfies the given cards."""


class SearchObserver:
    """No-op sink for search progress. Slice 3 formalises and renders this."""

    def on_placement(self, x: int, y: int, placement: Placement) -> None:
        """A candidate was accepted into cell (x, y)."""

    def on_reject(self, x: int, y: int, placement: Placement) -> None:
        """A candidate was rejected from cell (x, y)."""

    def on_backtrack(self, x: int, y: int) -> None:
        """Cell (x, y) was vacated and the search stepped back."""


class Arranger:
    """Finds the puzzle's arrangement by depth-first backtracking search."""

    def solve(
        self, cards: list[Card], observer: SearchObserver | None = None
    ) -> Arrangement:
        observer = observer or SearchObserver()
        ordered = sorted(cards, key=lambda card: card.number)
        result = self._search(Arrangement(), 0, ordered, observer)
        if result is None:
            raise NoArrangementError(
                "no arrangement exists for this card configuration"
            )
        return result

    def _search(
        self,
        arrangement: Arrangement,
        cell_index: int,
        remaining: list[Card],
        observer: SearchObserver,
    ) -> Arrangement | None:
        if cell_index == len(_CELLS):
            return arrangement

        x, y = _CELLS[cell_index]
        for card in remaining:
            for orientation in _ORIENTATIONS:
                placement = Placement(card, orientation)
                if not self._fits(arrangement, x, y, placement):
                    observer.on_reject(x, y, placement)
                    continue

                observer.on_placement(x, y, placement)
                filled = arrangement.with_placement(x, y, placement)
                rest = [other for other in remaining if other is not card]
                solved = self._search(filled, cell_index + 1, rest, observer)
                if solved is not None:
                    return solved
                observer.on_backtrack(x, y)

        return None

    def _fits(
        self, arrangement: Arrangement, x: int, y: int, placement: Placement
    ) -> bool:
        left = arrangement.placement_at(x - 1, y) if x > 0 else None
        above = arrangement.placement_at(x, y - 1) if y > 0 else None
        left_neighbour = left.symbol_at(Side.RIGHT) if left else None
        above_neighbour = above.symbol_at(Side.BOTTOM) if above else None

        fits_left = placement.symbol_at(Side.LEFT).is_match(left_neighbour)
        fits_above = placement.symbol_at(Side.TOP).is_match(above_neighbour)
        return fits_left and fits_above
