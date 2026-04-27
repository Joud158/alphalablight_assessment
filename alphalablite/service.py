from __future__ import annotations
from .config import database_path, fetch_csv_path
from .data_sources import CsvDataSource
from .engine import Engine
from .exceptions import EvaluationError
from .repository import SQLiteScriptRepository

class AlphaLabLiteService:
    def __init__(
        self,
        engine: Engine | None = None,
        repository: SQLiteScriptRepository | None = None,
    ) -> None:
        self.engine = engine or Engine(CsvDataSource(fetch_csv_path()))
        self.repository = repository or SQLiteScriptRepository(database_path())

    def execute(self, script: str) -> str:
        variables = self.engine.execute(script)
        return self.repository.save(script, variables)

    def view(self, script_id: str, item_names: list[str]) -> dict[str, list[float]]:
        if not item_names:
            raise EvaluationError("At least one variable name must be requested.")
        variables = self.repository.get_variables(script_id)
        missing = [name for name in item_names if name not in variables]
        if missing:
            available = ", ".join(sorted(variables))
            raise EvaluationError(
                f"Unknown variable(s): {', '.join(missing)}. Available variables: {available}"
            )
        return {name: variables[name] for name in item_names}