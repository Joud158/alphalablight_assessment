from __future__ import annotations
import re
from .exceptions import ParseError
from .models import Assignment

_ASSIGNMENT_RE = re.compile(
    r"""
    ^\s*
    (?P<target>[A-Za-z0-9_]+)
    \s*=\s*
    (?P<transformation>[A-Za-z0-9_]+)
    \s*\{\s*(?P<config>[^{}]*)\s*\}
    \s*\{\s*(?P<series>[^{}]*)\s*\}
    \s*$
    """,
    re.VERBOSE,
)

_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9_]+$")
_ARG_RE = re.compile(r"^[A-Za-z0-9_.+\-]+$")

def _strip_comment(line: str) -> str:
    return line.split("#", 1)[0].strip()

def _parse_args(raw: str, *, kind: str) -> tuple[str, ...]:
    raw = raw.strip()
    if not raw:
        return ()
    args = tuple(part.strip() for part in raw.split(","))
    if any(not arg for arg in args):
        raise ParseError(f"Empty {kind} argument in {{{raw}}}")
    validator = _IDENTIFIER_RE if kind == "series" else _ARG_RE
    invalid = [arg for arg in args if not validator.match(arg)]
    if invalid:
        raise ParseError(
            f"Invalid {kind} argument(s): {', '.join(invalid)}. "
            "Arguments may not contain spaces or braces."
        )
    return args

def parse_script(script: str) -> list[Assignment]:
    assignments: list[Assignment] = []
    buffer = ""
    for line_number, line in enumerate(script.splitlines(), start=1):
        cleaned = _strip_comment(line)
        if not cleaned:
            continue
        buffer = f"{buffer} {cleaned}".strip() if buffer else cleaned
        match = _ASSIGNMENT_RE.match(buffer)
        if match is None:
            continue
        target = match.group("target")
        transformation = match.group("transformation")
        config_args = _parse_args(match.group("config"), kind="config")
        series_args = _parse_args(match.group("series"), kind="series")
        assignments.append(
            Assignment(
                target=target,
                transformation=transformation,
                config_args=config_args,
                series_args=series_args,
            )
        )
        buffer = ""
    if buffer:
        raise ParseError(f"Could not parse assignment near: {buffer!r}")
    if not assignments:
        raise ParseError("The script is empty.")
    seen: set[str] = set()
    duplicates: list[str] = []
    for assignment in assignments:
        if assignment.target in seen:
            duplicates.append(assignment.target)
        seen.add(assignment.target)
    if duplicates:
        raise ParseError(f"Duplicate assignment target(s): {', '.join(duplicates)}")
    return assignments