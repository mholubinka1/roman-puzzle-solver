import io

from rich.console import Console

from arrangement import Placement
from arranger import Arranger
from card.card import Card, Symbol
from card.loader import load_cards
from card.side import Side
from card.symbol_type import SymbolType
from progress import ProgressObserver, format_cell, symbol_label

CANONICAL = {
    Side.TOP: Symbol(SymbolType.CHARIOT, 1),
    Side.RIGHT: Symbol(SymbolType.BANNER, 1),
    Side.BOTTOM: Symbol(SymbolType.SPEARMAN, 1),
    Side.LEFT: Symbol(SymbolType.SWORDSMAN, 1),
}


def a_card(number: int = 4) -> Card:
    return Card.from_sides(number, CANONICAL)


def test_symbol_label_pairs_a_two_letter_code_with_the_half_sign():
    assert symbol_label(Symbol(SymbolType.CHARIOT, 1)) == "Ch+"
    assert symbol_label(Symbol(SymbolType.LIGHTCOIN, -1)) == "Lt-"


def test_format_cell_shows_the_number_and_the_oriented_edge_labels():
    cell = format_cell(Placement(a_card(4), 90))

    assert "4" in cell
    # rotated 90 clockwise: the canonical TOP symbol now sits on the right edge
    assert "Ch+" in cell
    assert symbol_label(CANONICAL[Side.LEFT]) in cell


def _silent_observer(**kwargs):
    console = Console(file=io.StringIO(), force_terminal=False)
    return ProgressObserver(console=console, sleep=lambda _seconds: None, **kwargs)


def test_progress_observer_counts_placements_backtracks_and_steps():
    placement = Placement(a_card(), 0)

    with _silent_observer(delay_ms=0) as observer:
        observer.on_placement(0, 0, placement)
        observer.on_placement(1, 0, placement)
        observer.on_backtrack(1, 0)

    assert observer.placed == 1
    assert observer.backtracks == 1
    assert observer.steps == 3


def test_progress_observer_throttles_by_the_configured_delay():
    slept = []
    console = Console(file=io.StringIO(), force_terminal=False)
    placement = Placement(a_card(), 0)

    with ProgressObserver(delay_ms=50, console=console, sleep=slept.append) as observer:
        observer.on_placement(0, 0, placement)

    assert slept == [0.05]


def test_progress_observer_does_not_sleep_when_delay_is_zero():
    slept = []
    console = Console(file=io.StringIO(), force_terminal=False)
    placement = Placement(a_card(), 0)

    with ProgressObserver(delay_ms=0, console=console, sleep=slept.append) as observer:
        observer.on_placement(0, 0, placement)
        observer.on_backtrack(0, 0)

    assert slept == []


def test_a_real_solve_renders_the_legend_grid_and_stats_and_leaves_the_result():
    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=False, width=120)

    with ProgressObserver(
        delay_ms=0, console=console, sleep=lambda _s: None
    ) as observer:
        Arranger().solve(load_cards("card_config.json"), observer=observer)

    output = buffer.getvalue()
    assert "Chariot" in output  # legend
    assert "placed 12/12" in output  # final stats, grid fully populated
    assert "steps" in output
