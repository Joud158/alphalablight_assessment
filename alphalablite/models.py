from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Assignment:
    target: str
    transformation: str
    config_args: tuple[str, ...]
    series_args: tuple[str, ...]