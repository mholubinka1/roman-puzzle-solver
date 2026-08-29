# roman-puzzle

## Romans Mindbender

The game consists of 12 squares each showing one half of a picture on each of its sides. These should be combined to form one large 4x3 rectangle, whilst matching all of the pictures on the complementary sides.

At first it appears easy, but there is only one solution which can only be found by trial and error. Good luck!

## Running the solver

```sh
uv run python main.py
```

The solver reads the 12 cards from `card_config.json`, finds the arrangement by
depth-first backtracking search, and writes it to `out/solution.json` — a JSON object
keyed by `"x,y"` grid coordinate (`x` column 0–3, `y` row 0–2, `(0,0)` top-left), each
value `{"card": <n>, "orientation": <0|90|180|270>}`.

While it searches it draws a live 4×3 grid in the terminal showing cards being placed and
backtracked. Flags:

| Flag | Default | Meaning |
| --- | --- | --- |
| `--delay MS` | `10` | milliseconds paused between placement/backtrack steps; `0` runs at full speed |
| `--no-animate` | off | solve without the live grid |
| `--config PATH` | `card_config.json` | card configuration file |
| `--out DIR` | `out` | directory for `solution.json` |

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```sh
uv sync                     # create .venv and install the dev dependency group
uv run pre-commit install   # enable the pre-commit hooks
```

Run the full hook suite manually with `uv run pre-commit run --all-files`.

Run the tests with `uv run pytest`.
