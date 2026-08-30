from enum import Enum, unique


@unique
class SymbolType(Enum):
    CHARIOT = 1
    BANNER = 2
    SPEARMAN = 3
    SWORDSMAN = 4
    DARKCOIN = 5
    LIGHTCOIN = 6


def to_symbol_type(symbol_string: str) -> SymbolType:
    return SymbolType[symbol_string.upper()]
