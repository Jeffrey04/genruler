from collections.abc import Callable
from types import ModuleType
from typing import Any

from .exceptions import NonCallableResultError
from .lexer import read
from .library import evaluate


def parse(input: str, env: ModuleType | None = None) -> Callable[[Any], Any]:
    """Parse an S-expression string into a callable function.

    This function takes an S-expression string (e.g., "(module.function arg1 arg2)") and 
    converts it into a callable function. The S-expression can reference functions from 
    either the provided environment module or from genruler's built-in modules.

    Args:
        input: The S-expression string to parse. Should be in the format "(function arg1 arg2)"
            where function can be either a local function from env or a genruler module function
            in the format "module.function".
        env: Optional module containing local functions that can be referenced in the S-expression.
            If None, only genruler's built-in modules can be used.

    Returns:
        A callable function that takes a context argument. When called with a context,
        the function evaluates the S-expression with that context and returns the result.

    Raises:
        ValueError: If the input string cannot be parsed as a valid S-expression
        NonCallableResultError: If the parsed expression does not evaluate to a callable
        InvalidFunctionNameError: If the referenced function cannot be found

    Examples:
        >>> # Using a genruler module function
        >>> fn = parse("(number.add 1 2)")
        >>> fn({})  # Empty context
        3
    """
    result = evaluate(read(input), env=env)

    if not callable(result):
        raise NonCallableResultError(type(result).__name__)
    return result