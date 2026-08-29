import argparse
import json
import sys
from contextlib import nullcontext
from pathlib import Path

from arrangement import to_solution_dict
from arranger import Arranger, NoArrangementError
from card.loader import load_cards
from progress import ProgressObserver

DEFAULT_CONFIG = "card_config.json"
DEFAULT_OUT_DIR = "out"
DEFAULT_DELAY_MS = 10


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
        type=int,
        default=DEFAULT_DELAY_MS,
        help=f"ms between animation frames, 0 for full speed (default: {DEFAULT_DELAY_MS})",
    )
    parser.add_argument(
        "--no-animate",
        action="store_true",
        help="solve without the live grid",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    cards = load_cards(args.config)

    observer_context = (
        nullcontext(None) if args.no_animate else ProgressObserver(delay_ms=args.delay)
    )
    try:
        with observer_context as observer:
            arrangement = Arranger().solve(cards, observer=observer)
    except NoArrangementError as error:
        print(error, file=sys.stderr)
        return 1

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    solution_path = out_dir / "solution.json"
    solution_path.write_text(json.dumps(to_solution_dict(arrangement), indent=2) + "\n")
    print(f"Solved. Arrangement written to {solution_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
