import importlib
from collections.abc import Callable
from types import ModuleType
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


def evaluate(
    sequence: List[Any], env: ModuleType | None, result=None
) -> tuple[Any] | Callable[[Any], Any]:
    """Evaluate an S-expression sequence into a callable or value.

    This function recursively evaluates S-expressions into either a callable function
    or a tuple of values. It supports three types of expressions:
    1. Function calls: (module.function arg1 arg2)
    2. Nested expressions: ((inner_expr) arg1 arg2)
    3. Value sequences: (1 2 3 4)

    Function calls can use either:
    - Built-in genruler functions (e.g., "number.add")
    - Custom functions from the provided env module (e.g., "custom_func")

    Args:
        sequence: A list representing an S-expression to evaluate
        env: Optional module containing custom functions that can be referenced
            by name without a module prefix
        result: Internal accumulator for recursive evaluation, should not be
            provided by external callers

    Returns:
        - If the first element is a function: the result of calling that function
          with the evaluated remaining elements
        - Otherwise: a tuple containing all evaluated elements

    Raises:
        TypeError: If sequence is not a list
        InvalidFunctionNameError: If a function reference is invalid or not found
            in either genruler's modules or the provided env
        TypeError: If function arguments are invalid for the called function
    """
    if not isinstance(sequence, list):
        raise TypeError("sequence must be a list")

    result = result or tuple()
    to_return = None

    if len(sequence) > 0:
        if isinstance(sequence[0], genSymbol):
            closure = (
                get_function(sequence[0].name, env)
                if "." not in sequence[0].name
                else get_genruler_function(*sequence[0].name.split("."))
            )

            to_return = evaluate(
                sequence[1:],  # type: ignore
                env,
                result + (closure,),
            )

        elif isinstance(sequence[0], list):
            to_return = evaluate(
                sequence[1:],  # type: ignore
                env,
                result + (evaluate(sequence[0], env),),
            )

        else:
            to_return = evaluate(
                sequence[1:],  # type: ignore
                env,
                result + (sequence[0],),
            )

    else:
        if callable(result[0]):
            to_return = result[0](*result[1:])
        else:
            to_return = result

    return to_return


def get_function(function_name: str, env: ModuleType | None):
    try:
        assert env

        return getattr(env, function_name)
    except (AttributeError, AssertionError) as e:
        raise InvalidFunctionNameError(function_name) from e


def get_genruler_function(module_name: str, function_name: str) -> Callable[[Any], Any]:
    """Get a function from a module by name."""
    module = importlib.import_module(f"genruler.modules.{module_name}")

    try:
        function = getattr(module, function_name)
    except AttributeError:
        function = getattr(module, f"{function_name}_")

    assert callable(function)

    return function