from collections.abc import Callable, Mapping

import pytest

from card.card import Card, Symbol
from card.side import Side
from card.symbol_type import SymbolType

REAL_CONFIG = "card_config.json"


@pytest.fixture
def real_config() -> str:
    """Path to the real 12-card puzzle configuration."""
    return REAL_CONFIG


@pytest.fixture
def canonical_symbols() -> dict[Side, Symbol]:
    """Four distinct symbols, one per side, so rotation is observable."""
    return {
        Side.TOP: Symbol(SymbolType.CHARIOT, 1),
        Side.RIGHT: Symbol(SymbolType.BANNER, 1),
        Side.BOTTOM: Symbol(SymbolType.SPEARMAN, 1),
        Side.LEFT: Symbol(SymbolType.SWORDSMAN, 1),
    }


@pytest.fixture
def make_card(
    canonical_symbols: dict[Side, Symbol],
) -> Callable[..., Card]:
    """Factory for a Card; defaults to the canonical distinct-symbol layout."""

    def _make(number: int = 1, symbols: Mapping[Side, Symbol] | None = None) -> Card:
        return Card.from_sides(number, symbols or canonical_symbols)

    return _make
