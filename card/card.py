from collections.abc import Mapping
from dataclasses import dataclass

from card.side import Side
from card.symbol_type import SymbolType

_CLOCKWISE = (Side.TOP, Side.RIGHT, Side.BOTTOM, Side.LEFT)
_QUARTER_TURN = 90
_ORIENTATIONS = (0, _QUARTER_TURN, 2 * _QUARTER_TURN, 3 * _QUARTER_TURN)


@dataclass(frozen=True)
class Symbol:
    """One half-picture on a card edge: a symbol type paired with a half (1 or -1)."""

    type: SymbolType
    half: int

    def __post_init__(self) -> None:
        if self.half not in (1, -1):
            raise ValueError(f"a symbol half must be 1 or -1, got {self.half!r}")

    def is_match(self, other: "Symbol | None") -> bool:
        if other is None:
            return True
        return self.type is other.type and self.half + other.half == 0


@dataclass(frozen=True)
class Card:
    """A puzzle card: a number and its four symbols in canonical (unrotated) positions."""

    number: int
    symbols: tuple[Symbol, ...]

    def __post_init__(self) -> None:
        if len(self.symbols) != 4:
            raise ValueError(f"a card has four symbols, got {len(self.symbols)}")

    @classmethod
    def from_sides(cls, number: int, sides: Mapping[Side, Symbol]) -> "Card":
        missing = [side.name for side in _CLOCKWISE if side not in sides]
        if missing:
            raise ValueError(f"card {number} is missing sides: {', '.join(missing)}")
        return cls(number, tuple(sides[side] for side in _CLOCKWISE))

    def symbol_at(self, side: Side, orientation: int = 0) -> Symbol:
        if orientation not in _ORIENTATIONS:
            raise ValueError(
                f"orientation must be one of {_ORIENTATIONS}, got {orientation}"
            )
        steps = orientation // _QUARTER_TURN
        return self.symbols[(side - steps) % len(_CLOCKWISE)]
