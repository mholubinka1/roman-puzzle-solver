import json
from typing import Any

from card.card import Card, Symbol
from card.side import to_side
from card.symbol_type import to_symbol_type

EXPECTED_CARD_COUNT = 12
_REQUIRED_SIDE_IDS = frozenset({"top", "right", "bottom", "left"})


class CardConfigError(ValueError):
    """Raised when a card config file is structurally invalid."""


def load_cards(config_path: str) -> list[Card]:
    with open(config_path) as config_file:
        raw = json.load(config_file)

    if len(raw) != EXPECTED_CARD_COUNT:
        raise CardConfigError(f"expected {EXPECTED_CARD_COUNT} cards, found {len(raw)}")

    return [_build_card(int(number), spec) for number, spec in raw.items()]


def _build_card(number: int, spec: dict[str, Any]) -> Card:
    sides = spec.get("sides", [])
    ids = [side.get("id") for side in sides]
    if sorted(ids) != sorted(_REQUIRED_SIDE_IDS):
        raise CardConfigError(
            f"card {number} must have exactly the sides "
            f"{sorted(_REQUIRED_SIDE_IDS)}, got {sorted(ids)}"
        )

    symbols = {}
    for side in sides:
        try:
            symbol_type = to_symbol_type(side["symbol"])
        except KeyError:
            raise CardConfigError(
                f"card {number} side {side['id']}: unknown symbol {side['symbol']!r}"
            ) from None
        try:
            symbol = Symbol(symbol_type, int(side["half"]))
        except ValueError as error:
            raise CardConfigError(
                f"card {number} side {side['id']}: {error}"
            ) from error
        symbols[to_side(side["id"])] = symbol

    return Card.from_sides(number, symbols)
