from __future__ import annotations
import csv
from pathlib import Path
from .exceptions import EvaluationError

class CsvDataSource:
    def __init__(self, csv_path: str | Path) -> None:
        self.csv_path = Path(csv_path)
        self._cache: dict[str, list[float]] | None = None

    def _load(self) -> dict[str, list[float]]:
        if not self.csv_path.exists():
            raise EvaluationError(f"Fetch data file not found: {self.csv_path}")
        data: dict[str, list[float]] = {}
        with self.csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            for row_number, row in enumerate(reader, start=1):
                if not row:
                    continue
                label = row[0].strip()
                if not label:
                    raise EvaluationError(f"Missing datasource label at row {row_number}")
                try:
                    values = [float(cell) for cell in row[1:] if cell.strip() != ""]
                except ValueError as exc:
                    raise EvaluationError(
                        f"Datasource {label!r} contains a non-numeric value."
                    ) from exc
                if not values:
                    raise EvaluationError(f"Datasource {label!r} has no values.")
                data[label] = values
        return data

    @property
    def data(self) -> dict[str, list[float]]:
        if self._cache is None:
            self._cache = self._load()
        return self._cache
    def fetch(self, datasource: str) -> list[float]:
        try:
            return list(self.data[datasource])
        except KeyError as exc:
            known = ", ".join(sorted(self.data))
            raise EvaluationError(
                f"Unknown datasource {datasource!r}. Available datasources: {known}"
            ) from exc