import dataclasses

import pytest

from card.card import Card, Symbol
from card.side import Side
from card.symbol_type import SymbolType

CANONICAL = {
    Side.TOP: Symbol(SymbolType.CHARIOT, 1),
    Side.RIGHT: Symbol(SymbolType.BANNER, 1),
    Side.BOTTOM: Symbol(SymbolType.SPEARMAN, 1),
    Side.LEFT: Symbol(SymbolType.SWORDSMAN, 1),
}


def a_card(number: int = 1) -> Card:
    return Card.from_sides(number, CANONICAL)


def test_symbol_at_returns_the_canonical_symbols_when_not_rotated():
    card = a_card()

    for side, symbol in CANONICAL.items():
        assert card.symbol_at(side, 0) == symbol


def test_rotating_a_card_ninety_degrees_moves_each_symbol_one_side_clockwise():
    card = a_card()

    assert card.symbol_at(Side.RIGHT, 90) == CANONICAL[Side.TOP]
    assert card.symbol_at(Side.BOTTOM, 90) == CANONICAL[Side.RIGHT]
    assert card.symbol_at(Side.LEFT, 90) == CANONICAL[Side.BOTTOM]
    assert card.symbol_at(Side.TOP, 90) == CANONICAL[Side.LEFT]


def test_rotating_a_card_one_eighty_and_two_seventy():
    card = a_card()

    assert card.symbol_at(Side.BOTTOM, 180) == CANONICAL[Side.TOP]
    assert card.symbol_at(Side.LEFT, 180) == CANONICAL[Side.RIGHT]
    assert card.symbol_at(Side.LEFT, 270) == CANONICAL[Side.TOP]
    assert card.symbol_at(Side.TOP, 270) == CANONICAL[Side.RIGHT]


def test_a_card_needs_a_symbol_on_every_side():
    three_sides = {
        side: CANONICAL[side] for side in (Side.TOP, Side.RIGHT, Side.BOTTOM)
    }

    with pytest.raises(ValueError):
        Card.from_sides(1, three_sides)


def test_a_card_always_has_four_symbols():
    with pytest.raises(ValueError):
        Card(1, (CANONICAL[Side.TOP], CANONICAL[Side.RIGHT]))


def test_a_card_cannot_be_rotated_or_mutated():
    card = a_card()

    assert not hasattr(card, "rotate")
    with pytest.raises(dataclasses.FrozenInstanceError):
        card.number = 2  # type: ignore[misc]


@pytest.mark.parametrize("bad_orientation", [45, 1, 360, -90])
def test_symbol_at_rejects_orientations_that_are_not_quarter_turns(bad_orientation):
    with pytest.raises(ValueError):
        a_card().symbol_at(Side.TOP, bad_orientation)
