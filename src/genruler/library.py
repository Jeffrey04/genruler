import importlib
from collections.abc import Callable
from typing import Any, List

from .exceptions import InvalidFunctionNameError
from .lexer import Symbol as genSymbol


def compute[T, U, V](argument: Callable[[T], U] | V, context: T) -> U | V:
    """Compute the value of an argument, which can be either a callable or a value.

    This function handles two cases:
    1. If the argument is callable, it calls it with the context
    2. If the argument is a value, it returns it as is

    Args:
        argument: Either a callable function or a value
        context: The context to pass to the callable

    Returns:
        Either the result of calling the function with context,
        or the original value if not callable

    Examples:
        >>> compute(lambda x: x + 1, 1)
        2
        >>> compute("not callable", None)
        'not callable'
    """
    return (
        argument(context)  # type: ignore
        if callable(argument)
        else argument  # type: ignore
    )


def evaluate(sequence: List[Any], result=None) -> tuple[Any] | Callable[[Any], Any]:
    """Evaluate an S-expression sequence into a callable or value.

    This function recursively evaluates S-expressions, handling function calls
    in the form: (module.function arg1 arg2)

    Args:
        sequence: A list representing an S-expression
        result: Internal accumulator for recursive evaluation

    Returns:
        Either a callable function or a tuple of values

    Raises:
        TypeError: If sequence is not a list
        InvalidFunctionNameError: If function reference is invalid
        TypeError: If function arguments are invalid
    """
    if not isinstance(sequence, list):
        raise TypeError("sequence must be a list")

    result = result or tuple()
    to_return = None

    if len(sequence) > 0:
        if isinstance(sequence[0], genSymbol):
            if "." not in sequence[0].name:
                raise InvalidFunctionNameError(sequence[0].name)
            module, function = sequence[0].name.split(".")
            to_return = evaluate(
                sequence[1:],  # type: ignore
                result + (get_function(f"genruler.modules.{module}", function),),
            )

        elif isinstance(sequence[0], list):
            to_return = evaluate(
                sequence[1:],  # type: ignore
                result + (evaluate(sequence[0]),),
            )

        else:
            to_return = evaluate(
                sequence[1:],  # type: ignore
                result + (sequence[0],),
            )

    else:
        if callable(result[0]):
            to_return = result[0](*result[1:])
        else:
            to_return = result

    return to_return


def get_function(module_name: str, function_name: str) -> Callable[[Any], Any]:
    """Get a function from a module by name."""
    module = importlib.import_module(module_name)

    try:
        function = getattr(module, function_name)
    except AttributeError:
        function = getattr(module, f"{function_name}_")

    assert callable(function)

    return function