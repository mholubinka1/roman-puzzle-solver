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

    if not isinstance(raw, dict):
        raise CardConfigError(
            f"expected an object mapping card number to card, got {type(raw).__name__}"
        )
    if len(raw) != EXPECTED_CARD_COUNT:
        raise CardConfigError(f"expected {EXPECTED_CARD_COUNT} cards, found {len(raw)}")

    cards = []
    for key, spec in raw.items():
        try:
            number = int(key)
        except (TypeError, ValueError):
            raise CardConfigError(f"card key {key!r} is not a number") from None
        cards.append(_build_card(number, spec))
    return cards


def _build_card(number: int, spec: Any) -> Card:
    if not isinstance(spec, dict):
        raise CardConfigError(f"card {number}: expected an object, got {spec!r}")

    sides = spec.get("sides")
    if not isinstance(sides, list):
        raise CardConfigError(f"card {number}: 'sides' must be a list")

    side_ids = [s.get("id") if isinstance(s, dict) else None for s in sides]
    if sorted(str(side_id) for side_id in side_ids) != sorted(_REQUIRED_SIDE_IDS):
        raise CardConfigError(
            f"card {number} must have exactly the sides "
            f"{sorted(_REQUIRED_SIDE_IDS)}, got {side_ids}"
        )

    symbols = {}
    for side in sides:
        side_id = side["id"]
        if "symbol" not in side or "half" not in side:
            raise CardConfigError(
                f"card {number} side {side_id}: needs both 'symbol' and 'half'"
            )
        try:
            symbol_type = to_symbol_type(side["symbol"])
        except KeyError:
            raise CardConfigError(
                f"card {number} side {side_id}: unknown symbol {side['symbol']!r}"
            ) from None
        try:
            half = int(side["half"])
        except (TypeError, ValueError):
            raise CardConfigError(
                f"card {number} side {side_id}: half must be 1 or -1, got {side['half']!r}"
            ) from None
        try:
            symbols[to_side(side_id)] = Symbol(symbol_type, half)
        except ValueError as error:
            raise CardConfigError(f"card {number} side {side_id}: {error}") from error

    return Card.from_sides(number, symbols)
