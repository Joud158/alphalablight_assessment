from __future__ import annotations
import json
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from .exceptions import NotFoundError
from .serialization import decode_variables, encode_variables

class SQLiteScriptRepository:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS scripts (
                    id TEXT PRIMARY KEY,
                    script TEXT NOT NULL,
                    variables_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def save(self, script: str, variables: dict[str, list[float]]) -> str:
        script_id = str(uuid.uuid4())
        created_at = datetime.now(UTC).isoformat()
        variables_json = json.dumps(encode_variables(variables), separators=(",", ":"))
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO scripts (id, script, variables_json, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (script_id, script, variables_json, created_at),
            )
        return script_id

    def get_variables(self, script_id: str) -> dict[str, list[float]]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT variables_json FROM scripts WHERE id = ?",
                (script_id,),
            ).fetchone()
        if row is None:
            raise NotFoundError(f"No script found with id {script_id!r}.")
        return decode_variables(json.loads(row[0]))