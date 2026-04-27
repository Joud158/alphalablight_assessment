from pathlib import Path
import os
import subprocess
import sys

def test_cli_execute_then_view(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[1]
    csv_path = tmp_path / "data.csv"
    db_path = tmp_path / "alphalablite.sqlite"
    csv_path.write_text("Prices,1,2,3,4\n", encoding="utf-8")
    env = os.environ.copy()
    env["ALPHALABLITE_FETCH_CSV"] = str(csv_path)
    env["ALPHALABLITE_DB"] = str(db_path)
    script = "price = Fetch{Prices}{}\nsma = SimpleMovingAverage{2}{price}\n"
    execute_result = subprocess.run(
        [sys.executable, "-m", "alphalablite.cli", "execute"],
        input=script,
        text=True,
        capture_output=True,
        check=True,
        cwd=project_root,
        env=env,
    )
    assert "Script successfully executed:" in execute_result.stdout
    script_id = execute_result.stdout.strip().split(":", 1)[1].strip()
    view_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "alphalablite.cli",
            "view",
            "--id",
            script_id,
            "price",
            "sma",
        ],
        text=True,
        capture_output=True,
        check=True,
        cwd=project_root,
        env=env,
    )
    assert "price:" in view_result.stdout
    assert "[1.0, 2.0, 3.0, 4.0]" in view_result.stdout
    assert "sma:" in view_result.stdout
    assert "[nan, 1.5, 2.5, 3.5]" in view_result.stdout