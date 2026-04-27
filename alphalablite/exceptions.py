class AlphaLabLiteError(Exception):
    """Base exception for expected domain failures."""

class ParseError(AlphaLabLiteError):
    """Raised when a script cannot be parsed."""

class UnknownTransformationError(AlphaLabLiteError):
    """Raised when a script references an unknown transformation."""

class EvaluationError(AlphaLabLiteError):
    """Raised when a script is syntactically valid but cannot be evaluated."""

class NotFoundError(AlphaLabLiteError):
    """Raised when a persisted script id cannot be found."""