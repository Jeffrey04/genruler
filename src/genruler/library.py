import importlib
from collections.abc import Callable
from typing import Any

from hy.models import Expression, Float, Integer, Object, String, Symbol


def compute[T, U, V](argument: Callable[[T], U] | V, context: T) -> U | V:
    return (
        argument(context)  # type: ignore
        if callable(argument)
        else argument
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


def extract(argument: type[Object]) -> Any:
    match type(argument):
        case String.__name__:
            return str(argument)
        case Integer.__name__:
            return int(argument)
        case Float.__name__:
            return float(argument)
        case _:
            return str(argument)


def get_function(module_name: str, function_name: str) -> Callable[..., Any]:
    module = importlib.import_module(module_name)
    try:
        return getattr(module, function_name)
    except AttributeError:
        return getattr(module, f"{function_name}_")
