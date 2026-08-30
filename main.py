import argparse
import json
import sys
from pathlib import Path

from arrangement import Arrangement, to_solution_dict
from arranger import Arranger, NoArrangementError
from card.card import Card
from card.loader import CardConfigError, load_cards
from progress import ProgressObserver

DEFAULT_CONFIG = "card_config.json"
DEFAULT_OUT_DIR = "out"
DEFAULT_DELAY_MS = 10


def _non_negative_int(value: str) -> int:
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError(f"must be zero or greater, got {number}")
    return number


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Solve the Romans Mindbender puzzle.")
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG,
        help=f"card config file (default: {DEFAULT_CONFIG})",
    )
    parser.add_argument(
        "--out",
        default=DEFAULT_OUT_DIR,
        help=f"directory for solution.json (default: {DEFAULT_OUT_DIR})",
    )
    parser.add_argument(
        "--delay",
        type=_non_negative_int,
        default=DEFAULT_DELAY_MS,
        metavar="MS",
        help=f"ms paused between search steps, 0 for full speed (default: {DEFAULT_DELAY_MS})",
    )
    parser.add_argument(
        "--no-animate",
        action="store_true",
        help="solve without the live grid",
    )
    return parser.parse_args(argv)


def _search(cards: list[Card], *, animate: bool, delay_ms: int) -> Arrangement:
    if not animate:
        return Arranger().solve(cards)
    with ProgressObserver(delay_ms=delay_ms) as observer:
        return Arranger().solve(cards, observer=observer)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    try:
        cards = load_cards(args.config)
    except (CardConfigError, OSError) as error:
        print(f"could not load {args.config}: {error}", file=sys.stderr)
        return 1

    try:
        arrangement = _search(cards, animate=not args.no_animate, delay_ms=args.delay)
    except NoArrangementError as error:
        print(error, file=sys.stderr)
        return 1

    out_dir = Path(args.out)
    solution_path = out_dir / "solution.json"
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        solution_path.write_text(
            json.dumps(to_solution_dict(arrangement), indent=2) + "\n", encoding="utf-8"
        )
    except OSError as error:
        print(f"could not write {solution_path}: {error}", file=sys.stderr)
        return 1

    print(f"Solved. Arrangement written to {solution_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
