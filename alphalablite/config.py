from __future__ import annotations
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "alphalablite.sqlite"
DEFAULT_FETCH_CSV_PATH = PROJECT_ROOT / "data" / "fetch_transformation_data.csv"

def database_path() -> Path:
    return Path(os.getenv("ALPHALABLITE_DB", DEFAULT_DB_PATH))

def fetch_csv_path() -> Path:
    return Path(os.getenv("ALPHALABLITE_FETCH_CSV", DEFAULT_FETCH_CSV_PATH))