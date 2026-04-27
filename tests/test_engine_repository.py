from pathlib import Path
from alphalablite.data_sources import CsvDataSource
from alphalablite.engine import Engine
from alphalablite.repository import SQLiteScriptRepository
from alphalablite.service import AlphaLabLiteService

def test_engine_executes_script(tmp_path: Path):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("Prices,1,2,3,4,5\n", encoding="utf-8")
    engine = Engine(CsvDataSource(csv_path))
    variables = engine.execute(
        """
        price = Fetch{Prices}{}
        slow = SimpleMovingAverage{2}{price}
        zero = ConstantSeries{0}{price}
        """
    )
    assert variables["price"] == [1.0, 2.0, 3.0, 4.0, 5.0]
    assert variables["zero"] == [0.0] * 5

def test_service_persists_results(tmp_path: Path):
    csv_path = tmp_path / "data.csv"
    db_path = tmp_path / "alphalablite.sqlite"
    csv_path.write_text("Prices,1,2,3\n", encoding="utf-8")
    engine = Engine(CsvDataSource(csv_path))
    repository = SQLiteScriptRepository(db_path)
    service = AlphaLabLiteService(engine, repository)
    script_id = service.execute("price = Fetch{Prices}{}")
    assert service.view(script_id, ["price"]) == {"price": [1.0, 2.0, 3.0]}
    service_after_restart = AlphaLabLiteService(engine, SQLiteScriptRepository(db_path))
    assert service_after_restart.view(script_id, ["price"]) == {"price": [1.0, 2.0, 3.0]}