import json

import pytest

import main


def _unsolvable_config_file(tmp_path):
    same_side = {"symbol": "chariot", "half": "1"}
    card = {
        "sides": [
            {"id": "top", **same_side},
            {"id": "right", **same_side},
            {"id": "bottom", **same_side},
            {"id": "left", **same_side},
        ]
    }
    path = tmp_path / "unsolvable.json"
    path.write_text(json.dumps({str(n): card for n in range(1, 13)}))
    return str(path)


def test_main_writes_the_solution_file_and_reports_where(tmp_path, capsys, real_config):
    out_dir = tmp_path / "out"

    exit_code = main.main(
        ["--no-animate", "--config", real_config, "--out", str(out_dir)]
    )

    assert exit_code == 0
    solution = json.loads((out_dir / "solution.json").read_text())
    assert len(solution) == 12
    assert "solution.json" in capsys.readouterr().out


def test_main_exits_nonzero_and_writes_nothing_when_unsolvable(tmp_path):
    out_dir = tmp_path / "out"

    exit_code = main.main(
        [
            "--no-animate",
            "--config",
            _unsolvable_config_file(tmp_path),
            "--out",
            str(out_dir),
        ]
    )

    assert exit_code == 1
    assert not out_dir.exists()


def test_no_animate_solves_without_drawing_a_grid(tmp_path, capsys, real_config):
    out_dir = tmp_path / "out"

    exit_code = main.main(
        ["--no-animate", "--config", real_config, "--out", str(out_dir)]
    )

    assert exit_code == 0
    assert (out_dir / "solution.json").exists()
    out = capsys.readouterr().out
    assert "Chariot" not in out  # no legend, no grid


def test_the_animated_run_draws_the_grid(tmp_path, capsys, real_config):
    out_dir = tmp_path / "out"

    exit_code = main.main(
        ["--config", real_config, "--out", str(out_dir), "--delay", "0"]
    )

    assert exit_code == 0
    assert (out_dir / "solution.json").exists()
    assert "Chariot" in capsys.readouterr().out  # legend rendered


def test_a_negative_delay_is_rejected(tmp_path, real_config):
    with pytest.raises(SystemExit):
        main.main(["--config", real_config, "--out", str(tmp_path), "--delay", "-5"])
