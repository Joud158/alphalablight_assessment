# AlphaLabLite

AlphaLabLite is a small time-series transformation engine developed for the Edgebot internship assessment. It allows users to submit a mini script, execute financial and time-series transformations, persist the results in SQLite, and view selected output series through either a command-line interface or a REST API.

## Features

- Custom AlphaLabLite script parser
- Transformation engine with dependency-based execution
- CSV-backed `Fetch` transformation
- SQLite persistence for executed scripts and generated variables
- FastAPI REST API
- Command-line interface
- Unit and integration tests

## Supported Transformations

| Transformation | Purpose |
|---|---|
| `Fetch{Datasource}{}` | Loads a price/data series from `data/fetch_transformation_data.csv` |
| `SimpleMovingAverage{window}{series}` | Calculates a rolling simple moving average |
| `ExponentialMovingAverage{alpha}{series}` | Calculates an exponential moving average |
| `RateOfChange{period}{series}` | Calculates the rate of change over a lookback period |
| `CrossAbove{}{seriesA, seriesB}` | Returns `1` when `seriesA` crosses above `seriesB`; otherwise returns `0` |
| `ConstantSeries{value}{series}` | Creates a constant series with the same length as the input series |
| `PortfolioSimulation{cash}{entry, exit, price}` | Simulates portfolio value using entry/exit signals and price data |

## Project Structure

```text
alphalablite/
  api.py              FastAPI REST endpoints
  cli.py              Command-line interface
  config.py           Default paths and environment-variable overrides
  data_sources.py     CSV loading for Fetch
  engine.py           Script execution engine
  exceptions.py       Domain-specific exceptions
  models.py           Assignment data model
  parser.py           AlphaLabLite script parser
  repository.py       SQLite persistence layer
  serialization.py    JSON-safe output encoding
  service.py          Application service layer
  transformations.py  Transformation implementations

data/
  fetch_transformation_data.csv

scripts/
  sample_strategy.txt
  sample_momentum.txt

tests/
  test_parser.py
  test_transformations.py
  test_engine_repository.py
  test_api.py
  test_cli_e2e.py

solution-cli
solution-cli.bat
pyproject.toml
README.md
```

## Requirements

- Python 3.10 or newer
- pip

## Setup

Create and activate a virtual environment.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project and test dependencies:

```bash
python -m pip install -e ".[dev]"
```

If you prefer using `requirements.txt`, run:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Run Tests

Run the full test suite:

```bash
python -m pytest
```

Expected result:

```text
15 passed
```

## Script Syntax

Each assignment follows this format:

```text
variable = Transformation{configuration}{input_series}
```

Example:

```text
price = Fetch{OneMinuteGoldPrices}{}
fast = ExponentialMovingAverage{0.3}{price}
slow = SimpleMovingAverage{20}{price}
entry = CrossAbove{}{fast, slow}
exit = CrossAbove{}{slow, fast}
result = PortfolioSimulation{10000}{entry, exit, price}
```

## Run the CLI

The CLI reads scripts from standard input.

### Using Python Directly

Execute a script:

```bash
python -m alphalablite.cli execute < scripts/sample_strategy.txt
```

On Windows, use:

```bat
python -m alphalablite.cli execute < scripts\sample_strategy.txt
```

The output will look like:

```text
Script successfully executed: <script_id>
```

Use the returned script ID to view selected variables:

```bash
python -m alphalablite.cli view --id <script_id> price fast slow entry exit result
```

Example:

```bash
python -m alphalablite.cli view --id 76b71ad0-ebc7-453a-bd52-2b8f0e0b4cb7 price fast slow entry exit result
```

### Using the Helper Script on macOS/Linux

Execute a script:

```bash
./solution-cli execute < scripts/sample_strategy.txt
```

View selected variables:

```bash
./solution-cli view --id <script_id> price fast slow entry exit result
```

If the helper script is not executable, run:

```bash
chmod +x solution-cli
```

Then run the command again.

### Using the Helper Script on Windows

Execute a script:

```bat
solution-cli.bat execute < scripts\sample_strategy.txt
```

View selected variables:

```bat
solution-cli.bat view --id <script_id> price fast slow entry exit result
```

## Run the REST API

Start the API server:

```bash
python -m uvicorn alphalablite.api:app --reload
```

Open the interactive API documentation in your browser:

```text
http://127.0.0.1:8000/docs
```

### Health Check

Endpoint:

```text
GET /health
```

Expected response:

```json
{
  "status": "ok"
}
```

### Execute a Script

Endpoint:

```text
POST /execute
```

Request body:

```json
{
  "script": "price = Fetch{OneMinuteGoldPrices}{}\nsma = SimpleMovingAverage{5}{price}"
}
```

Example response:

```json
{
  "message": "Script successfully executed",
  "result": "<script_id>"
}
```

Copy the value of `result`. This is the script ID.

### View Variables

Endpoint:

```text
GET /view/<script_id>?items=price&items=sma
```

Example:

```text
GET /view/76b71ad0-ebc7-453a-bd52-2b8f0e0b4cb7?items=price&items=sma
```

Example response:

```json
{
  "price": [1900.0, 1901.5, 1902.0],
  "sma": [null, null, 1901.1666666667]
}
```

Some values may be `null`. This is expected when a transformation does not have enough previous data points yet, such as the first values of a moving average.

## Data Source

`Fetch{OneMinuteGoldPrices}{}` reads from:

```text
data/fetch_transformation_data.csv
```

The CSV format is:

```text
DatasourceName,value1,value2,value3,...
```

Example:

```text
OneMinuteGoldPrices,1900.0,1901.5,1902.0,1904.2
```

## Environment Variables

You can override the default database and CSV paths.

| Variable | Purpose |
|---|---|
| `ALPHALABLITE_DB` | SQLite database path |
| `ALPHALABLITE_FETCH_CSV` | CSV data source path |

### macOS/Linux Example

```bash
ALPHALABLITE_DB=/tmp/alphalablite.sqlite python -m alphalablite.cli execute < scripts/sample_strategy.txt
```

### Windows PowerShell Example

```powershell
$env:ALPHALABLITE_DB="C:\Temp\alphalablite.sqlite"
python -m alphalablite.cli execute < scripts\sample_strategy.txt
```

## Credits

This project was completed by Joud Senan for the Edgebot internship assessment.