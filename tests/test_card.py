import dataclasses

import pytest

from card.card import Card
from card.side import Side


def test_symbol_at_returns_the_canonical_symbols_when_not_rotated(
    make_card, canonical_symbols
):
    card = make_card()

    for side, symbol in canonical_symbols.items():
        assert card.symbol_at(side, 0) == symbol


def test_rotating_a_card_ninety_degrees_moves_each_symbol_one_side_clockwise(
    make_card, canonical_symbols
):
    card = make_card()

    assert card.symbol_at(Side.RIGHT, 90) == canonical_symbols[Side.TOP]
    assert card.symbol_at(Side.BOTTOM, 90) == canonical_symbols[Side.RIGHT]
    assert card.symbol_at(Side.LEFT, 90) == canonical_symbols[Side.BOTTOM]
    assert card.symbol_at(Side.TOP, 90) == canonical_symbols[Side.LEFT]


def test_rotating_a_card_one_eighty_and_two_seventy(make_card, canonical_symbols):
    card = make_card()

    assert card.symbol_at(Side.BOTTOM, 180) == canonical_symbols[Side.TOP]
    assert card.symbol_at(Side.LEFT, 180) == canonical_symbols[Side.RIGHT]
    assert card.symbol_at(Side.LEFT, 270) == canonical_symbols[Side.TOP]
    assert card.symbol_at(Side.TOP, 270) == canonical_symbols[Side.RIGHT]


def test_a_card_needs_a_symbol_on_every_side(canonical_symbols):
    three_sides = {
        side: canonical_symbols[side] for side in (Side.TOP, Side.RIGHT, Side.BOTTOM)
    }

    with pytest.raises(ValueError):
        Card.from_sides(1, three_sides)


def test_a_card_always_has_four_symbols(canonical_symbols):
    with pytest.raises(ValueError):
        Card(1, (canonical_symbols[Side.TOP], canonical_symbols[Side.RIGHT]))


def test_a_card_cannot_be_rotated_or_mutated(make_card):
    card = make_card()

    assert not hasattr(card, "rotate")
    with pytest.raises(dataclasses.FrozenInstanceError):
        card.number = 2  # type: ignore[misc]


@pytest.mark.parametrize("bad_orientation", [45, 1, 360, -90])
def test_symbol_at_rejects_orientations_that_are_not_quarter_turns(
    make_card, bad_orientation
):
    with pytest.raises(ValueError):
        make_card().symbol_at(Side.TOP, bad_orientation)
