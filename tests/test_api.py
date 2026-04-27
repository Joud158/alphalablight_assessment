from pathlib import Path
import pytest
from fastapi import HTTPException
from alphalablite import api
from alphalablite.data_sources import CsvDataSource
from alphalablite.engine import Engine
from alphalablite.repository import SQLiteScriptRepository
from alphalablite.service import AlphaLabLiteService

def make_service(tmp_path: Path) -> AlphaLabLiteService:
    csv_path = tmp_path / "data.csv"
    db_path = tmp_path / "alphalablite.sqlite"
    csv_path.write_text("Prices,1,2,3,4,5\n", encoding="utf-8")
    engine = Engine(CsvDataSource(csv_path))
    repository = SQLiteScriptRepository(db_path)
    return AlphaLabLiteService(engine, repository)

def test_health_endpoint():
    assert api.health() == {"status": "ok"}

def test_execute_and_view_endpoints(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setattr(api, "service", make_service(tmp_path))
    response = api.execute(
        api.ExecuteRequest(
            script="price = Fetch{Prices}{}\nsma = SimpleMovingAverage{2}{price}"
        )
    )
    assert response["message"] == "Script successfully executed"
    script_id = response["result"]
    view_response = api.view(script_id, ["price", "sma"])
    assert view_response["price"] == [1.0, 2.0, 3.0, 4.0, 5.0]
    assert view_response["sma"][0] is None
    assert view_response["sma"][1:] == [1.5, 2.5, 3.5, 4.5]

def test_view_unknown_script_returns_404(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setattr(api, "service", make_service(tmp_path))
    with pytest.raises(HTTPException) as exc_info:
        api.view("missing-id", ["price"])
    assert exc_info.value.status_code == 404