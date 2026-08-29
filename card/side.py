from enum import IntEnum, unique


@unique
class Side(IntEnum):
    """An edge of a card. Ordered clockwise so a rotation is a shift of the index."""

    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3


def to_side(name: str) -> Side:
    return Side[name.upper()]
