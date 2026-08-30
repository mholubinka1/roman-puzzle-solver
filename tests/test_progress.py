import io

import pytest
from rich.console import Console

from arrangement import Placement
from arranger import Arranger, NoArrangementError
from card.card import Symbol
from card.loader import load_cards
from card.side import Side
from card.symbol_type import SymbolType
from progress import ProgressObserver, format_cell, symbol_label


def test_symbol_label_pairs_a_two_letter_code_with_the_half_sign():
    assert symbol_label(Symbol(SymbolType.CHARIOT, 1)) == "Ch+"
    assert symbol_label(Symbol(SymbolType.LIGHTCOIN, -1)) == "Lt-"


def test_format_cell_shows_the_number_and_the_oriented_edge_labels(
    make_card, canonical_symbols
):
    cell = format_cell(Placement(make_card(4), 90))

    assert "4" in cell
    # rotated 90 clockwise: the canonical TOP symbol now sits on the right edge
    assert symbol_label(canonical_symbols[Side.TOP]) in cell
    assert symbol_label(canonical_symbols[Side.LEFT]) in cell


def _silent_observer(**kwargs):
    console = Console(file=io.StringIO(), force_terminal=False)
    return ProgressObserver(console=console, sleep=lambda _seconds: None, **kwargs)


def test_progress_observer_counts_placements_backtracks_and_steps(make_card):
    placement = Placement(make_card(), 0)

    with _silent_observer(delay_ms=0) as observer:
        observer.on_placement(0, 0, placement)
        observer.on_placement(1, 0, placement)
        observer.on_backtrack(1, 0)

    assert observer.placed == 1
    assert observer.backtracks == 1
    assert observer.steps == 3


def test_a_backtrack_on_an_empty_cell_does_not_drive_placed_negative():
    with _silent_observer(delay_ms=0) as observer:
        observer.on_backtrack(0, 0)

    assert observer.placed == 0
    assert observer.backtracks == 1


def test_a_negative_delay_is_rejected():
    with pytest.raises(ValueError):
        ProgressObserver(delay_ms=-1)


def test_progress_observer_throttles_by_the_configured_delay(make_card):
    slept = []
    console = Console(file=io.StringIO(), force_terminal=False)
    placement = Placement(make_card(), 0)

    with ProgressObserver(delay_ms=50, console=console, sleep=slept.append) as observer:
        observer.on_placement(0, 0, placement)

    assert slept == [0.05]


def test_progress_observer_does_not_sleep_when_delay_is_zero(make_card):
    slept = []
    console = Console(file=io.StringIO(), force_terminal=False)
    placement = Placement(make_card(), 0)

    with ProgressObserver(delay_ms=0, console=console, sleep=slept.append) as observer:
        observer.on_placement(0, 0, placement)
        observer.on_backtrack(0, 0)

    assert slept == []


def test_a_real_solve_renders_the_legend_grid_and_stats_and_leaves_the_result(
    real_config,
):
    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=False, width=120)

    with ProgressObserver(
        delay_ms=0, console=console, sleep=lambda _s: None
    ) as observer:
        Arranger().solve(load_cards(real_config), observer=observer)

    output = buffer.getvalue()
    assert "Dark Coin" in output  # legend uses the glossary spelling
    assert "placed 12/12" in output  # final stats, grid fully populated
    assert "steps" in output


def test_a_failed_search_leaves_no_grid_on_screen(unmatchable_deck):
    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=False, width=120)

    with (
        pytest.raises(NoArrangementError),
        ProgressObserver(
            delay_ms=0, console=console, sleep=lambda _s: None
        ) as observer,
    ):
        Arranger().solve(unmatchable_deck, observer=observer)

    assert "placed" not in buffer.getvalue()
