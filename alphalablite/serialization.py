from __future__ import annotations
import math
from typing import Any

def encode_series(series: list[float]) -> list[float | None]:
    return [None if isinstance(value, float) and math.isnan(value) else value for value in series]

def decode_series(series: list[Any]) -> list[float]:
    # json values badn yrja3o floats
    return [float("nan") if value is None else float(value) for value in series]

def encode_variables(variables: dict[str, list[float]]) -> dict[str, list[float | None]]:
    return {name: encode_series(values) for name, values in variables.items()}

def decode_variables(variables: dict[str, list[Any]]) -> dict[str, list[float]]:
    return {name: decode_series(values) for name, values in variables.items()}