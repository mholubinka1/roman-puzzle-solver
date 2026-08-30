import pytest

from arranger import Arranger, NoArrangementError
from card.card import Card, Symbol
from card.loader import load_cards
from card.side import Side
from card.symbol_type import SymbolType


def assert_internally_consistent(arrangement):
    numbers = []
    for x, y, placement in arrangement.placements():
        numbers.append(placement.card.number)
        if x > 0:
            left = arrangement.placement_at(x - 1, y)
            assert placement.symbol_at(Side.LEFT).is_match(left.symbol_at(Side.RIGHT))
        if y > 0:
            above = arrangement.placement_at(x, y - 1)
            assert placement.symbol_at(Side.TOP).is_match(above.symbol_at(Side.BOTTOM))
    assert sorted(numbers) == list(range(1, 13))


def unmatchable_deck():
    return [
        Card.from_sides(number, {side: Symbol(SymbolType.CHARIOT, 1) for side in Side})
        for number in range(1, 13)
    ]


def test_solves_the_real_puzzle(real_config):
    arrangement = Arranger().solve(load_cards(real_config))

    assert arrangement.is_complete()
    assert_internally_consistent(arrangement)


def test_raises_when_no_arrangement_exists():
    with pytest.raises(NoArrangementError):
        Arranger().solve(unmatchable_deck())


def test_reports_placements_and_backtracks_to_an_observer(real_config):
    class SpyObserver:
        def __init__(self):
            self.events = []

        def on_placement(self, x, y, placement):
            self.events.append(("place", x, y))

        def on_backtrack(self, x, y):
            self.events.append(("backtrack", x, y))

    spy = SpyObserver()
    Arranger().solve(load_cards(real_config), observer=spy)

    kinds = {kind for kind, _, _ in spy.events}
    assert kinds == {"place", "backtrack"}
