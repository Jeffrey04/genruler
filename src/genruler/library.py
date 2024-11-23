import importlib
from collections.abc import Callable
from typing import Any, List

from hy.models import Expression, Float, Integer, Object, String, Symbol

from .lexer import Symbol as genSymbol


def compute[T, U, V](argument: Callable[[T], U] | V, context: T) -> U | V:
    return (
        argument(context)  # type: ignore
        if callable(argument)
        else argument  # type: ignore
    )


def evaluate(sequence: Expression, result=None) -> tuple[Any] | Callable[[Any], Any]:
    assert isinstance(sequence, Expression)

    result = result or tuple()
    to_return = None

    if len(sequence) > 0:
        if isinstance(sequence[0], Expression) and sequence[0][0] == Symbol("."):
            to_return = evaluate(
                sequence[1:],  # type: ignore
                result
                + (
                    get_function(
                        f"genruler.modules.{sequence[0][1]}", str(sequence[0][2])
                    ),
                ),
            )

        elif isinstance(sequence[0], Expression):
            to_return = evaluate(
                sequence[1:],  # type: ignore
                result + (evaluate(sequence[0]),),
            )

        else:
            to_return = evaluate(
                sequence[1:],  # type: ignore
                result + (extract(sequence[0]),),
            )

    else:
        if callable(result[0]):
            to_return = result[0](*result[1:])
        else:
            to_return = result

    return to_return


def evaluate2(sequence: List[Any], result=None) -> tuple[Any] | Callable[[Any], Any]:
    """Evaluate a parsed S-expression tree into a callable function.

    Args:
        sequence: The parsed expression tree, where each node is a list:
            - First element is a Symbol object for function names (e.g. Symbol('boolean.tautology'))
            - Remaining elements are arguments, which can be subtrees

    Returns:
        A callable function that takes a context argument and returns a value

    Raises:
        ValueError: If the expression is invalid or empty
        TypeError: If the evaluated expression is not callable
    """
    result = result or tuple()
    to_return = None

    if len(sequence) > 0:
        if isinstance(sequence[0], genSymbol):
            assert "." in sequence[0].name
            module, function = sequence[0].name.split(".")
            to_return = evaluate2(
                sequence[1:],  # type: ignore
                result + (get_function(f"genruler.modules.{module}", function),),
            )

        elif isinstance(sequence[0], list):
            to_return = evaluate2(
                sequence[1:],  # type: ignore
                result + (evaluate2(sequence[0]),),
            )

        else:
            to_return = evaluate2(
                sequence[1:],  # type: ignore
                result + (sequence[0],),
            )

    else:
        if callable(result[0]):
            to_return = result[0](*result[1:])
        else:
            to_return = result

    return to_return


def extract(argument: type[Object]) -> Any:
    match argument.__class__.__name__:
        case String.__name__:
            return str(argument)
        case Integer.__name__:
            return int(argument)
        case Float.__name__:
            return float(argument)
        case _:
            return str(argument)


def get_function(module_name: str, function_name: str) -> Callable[[Any], Any]:
    """Get a function from a module by name."""
    module = importlib.import_module(module_name)

    try:
        function = getattr(module, function_name)
    except AttributeError:
        function = getattr(module, f"{function_name}_")

    assert callable(function)

    return function


def compute(value: Any, context: Any) -> Any:
    """Compute a value in a context."""
    if callable(value):
        return value(context)

    return value
