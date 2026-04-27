from __future__ import annotations
from .data_sources import CsvDataSource
from .exceptions import EvaluationError, UnknownTransformationError
from .parser import parse_script
from .transformations import TransformationRegistry

class Engine:
    def __init__(self, data_source: CsvDataSource) -> None:
        self.registry = TransformationRegistry(data_source).mapping()

    def execute(self, script: str) -> dict[str, list[float]]:
        variables: dict[str, list[float]] = {}
        for assignment in parse_script(script):
            try:
                transformation = self.registry[assignment.transformation]
            except KeyError as exc:
                raise UnknownTransformationError(
                    f"Unknown transformation {assignment.transformation!r}."
                ) from exc
            missing = [name for name in assignment.series_args if name not in variables]
            if missing:
                raise EvaluationError(
                    f"{assignment.target} references undefined series: {', '.join(missing)}"
                )
            input_series = [variables[name] for name in assignment.series_args]
            variables[assignment.target] = transformation(
                assignment.config_args,
                input_series,
                assignment.series_args,
            )
        return variables