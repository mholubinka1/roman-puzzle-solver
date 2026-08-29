import json

import pytest

from card.card import Symbol
from card.loader import CardConfigError, load_cards
from card.side import Side
from card.symbol_type import SymbolType

REAL_CONFIG = "card_config.json"


def _sides(top="chariot", right="banner", bottom="spearMan", left="swordsMan"):
    return [
        {"id": "top", "symbol": top, "half": "1"},
        {"id": "right", "symbol": right, "half": "1"},
        {"id": "bottom", "symbol": bottom, "half": "1"},
        {"id": "left", "symbol": left, "half": "1"},
    ]


def _config_file(tmp_path, cards):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(cards))
    return str(path)


def _twelve_valid_cards():
    return {str(number): {"sides": _sides()} for number in range(1, 13)}


def test_loads_all_twelve_cards_from_the_real_config():
    cards = load_cards(REAL_CONFIG)

    assert [card.number for card in cards] == list(range(1, 13))


def test_a_loaded_card_carries_the_symbols_from_the_config():
    card_one = load_cards(REAL_CONFIG)[0]

    assert card_one.symbol_at(Side.TOP) == Symbol(SymbolType.LIGHTCOIN, -1)
    assert card_one.symbol_at(Side.RIGHT) == Symbol(SymbolType.SPEARMAN, -1)
    assert card_one.symbol_at(Side.BOTTOM) == Symbol(SymbolType.SWORDSMAN, 1)
    assert card_one.symbol_at(Side.LEFT) == Symbol(SymbolType.CHARIOT, 1)


def test_a_valid_generated_config_loads(tmp_path):
    cards = load_cards(_config_file(tmp_path, _twelve_valid_cards()))

    assert len(cards) == 12


def test_rejects_a_config_without_exactly_twelve_cards(tmp_path):
    eleven = _twelve_valid_cards()
    del eleven["12"]

    with pytest.raises(CardConfigError):
        load_cards(_config_file(tmp_path, eleven))


def test_rejects_a_card_that_is_missing_a_side(tmp_path):
    config = _twelve_valid_cards()
    config["5"]["sides"] = config["5"]["sides"][:3]

    with pytest.raises(CardConfigError):
        load_cards(_config_file(tmp_path, config))


def test_rejects_a_card_with_a_duplicated_side(tmp_path):
    config = _twelve_valid_cards()
    config["5"]["sides"][3]["id"] = "top"

    with pytest.raises(CardConfigError):
        load_cards(_config_file(tmp_path, config))


def test_rejects_an_unknown_symbol_name(tmp_path):
    config = _twelve_valid_cards()
    config["5"]["sides"][0]["symbol"] = "catapult"

    with pytest.raises(CardConfigError):
        load_cards(_config_file(tmp_path, config))


def test_rejects_a_half_that_is_not_plus_or_minus_one(tmp_path):
    config = _twelve_valid_cards()
    config["5"]["sides"][0]["half"] = "0"

    with pytest.raises(CardConfigError):
        load_cards(_config_file(tmp_path, config))
