from collections.abc import Callable
from typing import Any

import hy

from .lexer import read
from .library import evaluate, evaluate2


def parse(input: str, use_hy: bool = True) -> Callable[[Any], Any]:
    """Parse an S-expression string into a callable function.

    Args:
        input: The S-expression string to parse
        use_hy: If True, use Hy's reader (default). If False, use our custom reader.

    Returns:
        A callable function that takes a context argument

    Raises:
        ValueError: If the input cannot be parsed
        AssertionError: If the result is not callable
    """
    if use_hy:
        result = evaluate(hy.read(input))
    else:
        result = evaluate2(read(input))

    assert callable(result)
    return result