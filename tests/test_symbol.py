import pytest

from card.card import Symbol
from card.symbol_type import SymbolType


def test_symbols_of_same_type_with_opposite_halves_match():
    top_half = Symbol(SymbolType.CHARIOT, 1)
    bottom_half = Symbol(SymbolType.CHARIOT, -1)

    assert top_half.is_match(bottom_half)


def test_symbol_matches_a_missing_neighbour():
    symbol = Symbol(SymbolType.BANNER, 1)

    assert symbol.is_match(None)


def test_symbols_of_different_types_do_not_match():
    chariot = Symbol(SymbolType.CHARIOT, 1)
    banner = Symbol(SymbolType.BANNER, -1)

    assert not chariot.is_match(banner)


def test_symbols_whose_halves_do_not_cancel_do_not_match():
    one_half = Symbol(SymbolType.SPEARMAN, 1)
    same_half = Symbol(SymbolType.SPEARMAN, 1)

    assert not one_half.is_match(same_half)


@pytest.mark.parametrize("bad_half", [0, 2, -3])
def test_a_symbol_half_must_be_plus_or_minus_one(bad_half):
    with pytest.raises(ValueError):
        Symbol(SymbolType.DARKCOIN, bad_half)
