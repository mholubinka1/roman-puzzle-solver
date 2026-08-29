import json

import main

REAL_CONFIG = "card_config.json"


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


def test_main_writes_the_solution_file_and_reports_where(tmp_path, capsys):
    out_dir = tmp_path / "out"

    exit_code = main.main(["--config", REAL_CONFIG, "--out", str(out_dir)])

    assert exit_code == 0
    solution = json.loads((out_dir / "solution.json").read_text())
    assert len(solution) == 12
    assert "solution.json" in capsys.readouterr().out


def test_main_exits_nonzero_and_writes_nothing_when_unsolvable(tmp_path):
    out_dir = tmp_path / "out"

    exit_code = main.main(
        ["--config", _unsolvable_config_file(tmp_path), "--out", str(out_dir)]
    )

    assert exit_code == 1
    assert not out_dir.exists()
