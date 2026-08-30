import json

import pytest

from card.card import Symbol
from card.loader import CardConfigError, load_cards
from card.side import Side
from card.symbol_type import SymbolType


def _sides(top="chariot", right="banner", bottom="spearMan", left="swordsMan"):
    return [
        {"id": "top", "symbol": top, "half": "1"},
        {"id": "right", "symbol": right, "half": "1"},
        {"id": "bottom", "symbol": bottom, "half": "1"},
        {"id": "left", "symbol": left, "half": "1"},
    ]


def _config_file(tmp_path, contents):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(contents))
    return str(path)


def _twelve_valid_cards():
    return {str(number): {"sides": _sides()} for number in range(1, 13)}


def test_loads_all_twelve_cards_from_the_real_config(real_config):
    cards = load_cards(real_config)

    assert [card.number for card in cards] == list(range(1, 13))


def test_a_loaded_card_carries_the_symbols_from_the_config(real_config):
    card_one = load_cards(real_config)[0]

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


@pytest.mark.parametrize("bad_symbol", [None, 7, ["chariot"]])
def test_rejects_a_symbol_that_is_not_a_string(tmp_path, bad_symbol):
    config = _twelve_valid_cards()
    config["5"]["sides"][0]["symbol"] = bad_symbol

    with pytest.raises(CardConfigError):
        load_cards(_config_file(tmp_path, config))


def test_rejects_a_half_that_is_not_plus_or_minus_one(tmp_path):
    config = _twelve_valid_cards()
    config["5"]["sides"][0]["half"] = "0"

    with pytest.raises(CardConfigError):
        load_cards(_config_file(tmp_path, config))


def test_rejects_a_side_with_no_id(tmp_path):
    config = _twelve_valid_cards()
    del config["5"]["sides"][0]["id"]

    with pytest.raises(CardConfigError):
        load_cards(_config_file(tmp_path, config))


def test_rejects_a_side_missing_its_symbol_or_half(tmp_path):
    config = _twelve_valid_cards()
    del config["5"]["sides"][0]["symbol"]

    with pytest.raises(CardConfigError):
        load_cards(_config_file(tmp_path, config))


def test_rejects_a_half_that_is_not_a_number(tmp_path):
    config = _twelve_valid_cards()
    config["5"]["sides"][0]["half"] = "east"

    with pytest.raises(CardConfigError):
        load_cards(_config_file(tmp_path, config))


def test_rejects_a_non_numeric_card_key(tmp_path):
    config = _twelve_valid_cards()
    config["oops"] = config.pop("12")

    with pytest.raises(CardConfigError):
        load_cards(_config_file(tmp_path, config))


def test_rejects_a_top_level_json_array(tmp_path):
    with pytest.raises(CardConfigError):
        load_cards(_config_file(tmp_path, [{"sides": _sides()}]))


def test_rejects_a_card_that_is_not_an_object(tmp_path):
    config = _twelve_valid_cards()
    config["5"] = "not a card"

    with pytest.raises(CardConfigError):
        load_cards(_config_file(tmp_path, config))


def test_rejects_a_card_with_no_sides_list(tmp_path):
    config = _twelve_valid_cards()
    config["5"] = {}

    with pytest.raises(CardConfigError):
        load_cards(_config_file(tmp_path, config))


def test_rejects_a_file_that_is_not_valid_json(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{ not json")

    with pytest.raises(CardConfigError):
        load_cards(str(path))
