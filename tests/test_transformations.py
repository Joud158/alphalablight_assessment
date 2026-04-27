import math
from alphalablite.data_sources import CsvDataSource
from alphalablite.transformations import TransformationRegistry

class DummyDataSource:
    def fetch(self, datasource):
        return [1.0, 2.0, 3.0, 4.0]

def registry():
    return TransformationRegistry(DummyDataSource()).mapping()

def test_simple_moving_average():
    sma = registry()["SimpleMovingAverage"]
    result = sma(("3",), [[1.0, 2.0, 3.0, 4.0]], ("price",))
    assert math.isnan(result[0])
    assert math.isnan(result[1])
    assert result[2:] == [2.0, 3.0]

def test_exponential_moving_average():
    ema = registry()["ExponentialMovingAverage"]
    result = ema(("0.5",), [[10.0, 20.0, 30.0]], ("price",))
    assert result == [10.0, 15.0, 22.5]

def test_rate_of_change():
    roc = registry()["RateOfChange"]
    result = roc(("2",), [[10.0, 12.0, 15.0, 18.0]], ("price",))
    assert math.isnan(result[0])
    assert math.isnan(result[1])
    assert result[2:] == [0.5, 0.5]

def test_cross_above():
    cross = registry()["CrossAbove"]
    result = cross((), [[1.0, 3.0, 2.0], [2.0, 2.0, 2.0]], ("fast", "slow"))
    assert result == [0.0, 1.0, 0.0]

def test_constant_series():
    constant = registry()["ConstantSeries"]
    assert constant(("7",), [[1.0, 2.0, 3.0]], ("price",)) == [7.0, 7.0, 7.0]

def test_portfolio_simulation_examples_order():
    portfolio = registry()["PortfolioSimulation"]
    entry = [1.0, 0.0, 0.0, 0.0]
    exit_ = [0.0, 0.0, 1.0, 0.0]
    price = [10.0, 12.0, 15.0, 20.0]
    result = portfolio(("100",), [entry, exit_, price], ("entry", "exit", "price"))
    assert result == [100.0, 102.0, 105.0, 105.0]

def test_portfolio_simulation_spec_order_is_supported_when_names_are_clear():
    portfolio = registry()["PortfolioSimulation"]
    price = [10.0, 12.0, 15.0, 20.0]
    entry = [1.0, 0.0, 0.0, 0.0]
    exit_ = [0.0, 0.0, 1.0, 0.0]
    result = portfolio(("100",), [price, entry, exit_], ("price", "entry", "exit"))
    assert result == [100.0, 102.0, 105.0, 105.0]