from __future__ import annotations
import math
from collections.abc import Callable
from dataclasses import dataclass
from .data_sources import CsvDataSource
from .exceptions import EvaluationError

Series = list[float]
Transformation = Callable[[tuple[str, ...], list[Series], tuple[str, ...]], Series]

def _require_config_count(name: str, configs: tuple[str, ...], count: int) -> None:
    if len(configs) != count:
        raise EvaluationError(f"{name} expects {count} config argument(s), got {len(configs)}.")

def _require_series_count(name: str, series: list[Series], count: int) -> None:
    if len(series) != count:
        raise EvaluationError(f"{name} expects {count} input series, got {len(series)}.")

def _as_float(value: str, name: str) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise EvaluationError(f"{name} must be numeric, got {value!r}.") from exc

def _as_positive_int(value: str, name: str) -> int:
    parsed = _as_float(value, name)
    if not parsed.is_integer():
        raise EvaluationError(f"{name} must be an integer, got {value!r}.")
    parsed_int = int(parsed)
    if parsed_int <= 0:
        raise EvaluationError(f"{name} must be positive, got {value!r}.")
    return parsed_int

def _ensure_equal_lengths(name: str, series: list[Series]) -> int:
    if not series:
        return 0
    lengths = {len(item) for item in series}
    if len(lengths) != 1:
        raise EvaluationError(f"{name} requires equal-length series, got lengths {sorted(lengths)}.")
    return lengths.pop()

def _is_nan(value: float) -> bool:
    return isinstance(value, float) and math.isnan(value)

@dataclass(frozen=True)
class TransformationRegistry:
    data_source: CsvDataSource
    def mapping(self) -> dict[str, Transformation]:
        return {
            "Fetch": self.fetch,
            "SimpleMovingAverage": self.simple_moving_average,
            "ExponentialMovingAverage": self.exponential_moving_average,
            "RateOfChange": self.rate_of_change,
            "CrossAbove": self.cross_above,
            "ConstantSeries": self.constant_series,
            "PortfolioSimulation": self.portfolio_simulation,
        }

    def fetch(
        self,
        configs: tuple[str, ...],
        series: list[Series],
        series_names: tuple[str, ...],
    ) -> Series:
        _require_config_count("Fetch", configs, 1)
        _require_series_count("Fetch", series, 0)
        return self.data_source.fetch(configs[0])

    def simple_moving_average(
        self,
        configs: tuple[str, ...],
        series: list[Series],
        series_names: tuple[str, ...],
    ) -> Series:
        _require_config_count("SimpleMovingAverage", configs, 1)
        _require_series_count("SimpleMovingAverage", series, 1)
        window = _as_positive_int(configs[0], "window")
        source = series[0]
        output: Series = []
        rolling_sum = 0.0
        nan_count = 0
        for index, value in enumerate(source):
            if _is_nan(value):
                nan_count += 1
            else:
                rolling_sum += value
            if index >= window:
                outgoing = source[index - window]
                if _is_nan(outgoing):
                    nan_count -= 1
                else:
                    rolling_sum -= outgoing
            if index < window - 1 or nan_count:
                output.append(float("nan"))
            else:
                output.append(rolling_sum / window)
        return output

    def exponential_moving_average(
        self,
        configs: tuple[str, ...],
        series: list[Series],
        series_names: tuple[str, ...],
    ) -> Series:
        _require_config_count("ExponentialMovingAverage", configs, 1)
        _require_series_count("ExponentialMovingAverage", series, 1)
        alpha = _as_float(configs[0], "alpha")
        if not 0 <= alpha <= 1:
            raise EvaluationError(f"alpha must be between 0 and 1, got {alpha}.")
        source = series[0]
        if not source:
            return []
        output = [source[0]]
        for value in source[1:]:
            output.append(alpha * value + (1 - alpha) * output[-1])
        return output

    def rate_of_change(
        self,
        configs: tuple[str, ...],
        series: list[Series],
        series_names: tuple[str, ...],
    ) -> Series:
        _require_config_count("RateOfChange", configs, 1)
        _require_series_count("RateOfChange", series, 1)
        period = _as_positive_int(configs[0], "period")
        source = series[0]
        output: Series = []
        for index, value in enumerate(source):
            if index < period:
                output.append(float("nan"))
                continue
            previous = source[index - period]
            if _is_nan(previous) or _is_nan(value) or previous == 0:
                output.append(float("nan"))
            else:
                output.append((value - previous) / previous)
        return output

    def cross_above(
        self,
        configs: tuple[str, ...],
        series: list[Series],
        series_names: tuple[str, ...],
    ) -> Series:
        _require_config_count("CrossAbove", configs, 0)
        _require_series_count("CrossAbove", series, 2)
        n = _ensure_equal_lengths("CrossAbove", series)
        a1, a2 = series
        output: Series = [0.0] * n
        for index in range(1, n):
            values = (a1[index - 1], a2[index - 1], a1[index], a2[index])
            if any(_is_nan(value) for value in values):
                output[index] = 0.0
            elif a1[index - 1] < a2[index - 1] and a1[index] > a2[index]:
                output[index] = 1.0
        return output

    def constant_series(
        self,
        configs: tuple[str, ...],
        series: list[Series],
        series_names: tuple[str, ...],
    ) -> Series:
        _require_config_count("ConstantSeries", configs, 1)
        _require_series_count("ConstantSeries", series, 1)
        constant = _as_float(configs[0], "k")
        return [constant for _ in series[0]]

    def portfolio_simulation(
        self,
        configs: tuple[str, ...],
        series: list[Series],
        series_names: tuple[str, ...],
    ) -> Series:
        _require_config_count("PortfolioSimulation", configs, 1)
        _require_series_count("PortfolioSimulation", series, 3)
        _ensure_equal_lengths("PortfolioSimulation", series)
        balance = _as_float(configs[0], "balance")
        price, entry, exit_ = self._portfolio_argument_order(series, series_names)
        positions_held = 0.0
        portfolio: Series = []
        for price_i, entry_i, exit_i in zip(price, entry, exit_, strict=True):
            if _is_nan(price_i):
                portfolio.append(float("nan"))
                continue
            if exit_i == 1:
                balance += positions_held * price_i
                positions_held = 0.0
            elif entry_i == 1:
                positions_held += 1.0
                balance -= price_i
            portfolio.append(balance + positions_held * price_i)
        return portfolio

    @staticmethod
    def _portfolio_argument_order(
        series: list[Series],
        series_names: tuple[str, ...],
    ) -> tuple[Series, Series, Series]:
        lower_names = tuple(name.lower() for name in series_names)
        entry_index = next((i for i, name in enumerate(lower_names) if "entry" in name), None)
        exit_index = next((i for i, name in enumerate(lower_names) if "exit" in name), None)
        if entry_index is not None and exit_index is not None and entry_index != exit_index:
            price_indices = [i for i in range(3) if i not in {entry_index, exit_index}]
            return series[price_indices[0]], series[entry_index], series[exit_index]
        entry, exit_, price = series
        return price, entry, exit_