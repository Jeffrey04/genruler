from collections.abc import Callable
from typing import Any

from .lexer import read
from .library import evaluate
from .exceptions import NonCallableResultError


def parse(input: str) -> Callable[[Any], Any]:
    """Parse an S-expression string into a callable function.

    Args:
        input: The S-expression string to parse

    Returns:
        A callable function that takes a context argument

    Raises:
        ValueError: If the input cannot be parsed
        NonCallableResultError: If the result is not callable
    """
    result = evaluate(read(input))

    if not callable(result):
        raise NonCallableResultError(type(result).__name__)
    return result