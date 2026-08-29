# roman-puzzle

## Romans Mindbender

The game consists of 12 squares each showing one half of a picture on each of its sides. These should be combined to form one large 4x3 rectangle, whilst matching all of the pictures on the complementary sides.

At first it appears easy, but there is only one solution which can only be found by trial and error. Good luck!

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```sh
uv sync                     # create .venv and install the dev dependency group
uv run pre-commit install   # enable the pre-commit hooks
```

Run the full hook suite manually with `uv run pre-commit run --all-files`.

The solver itself (`main.py`) is a work in progress and does not yet run.
