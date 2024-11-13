import importlib
from collections.abc import Callable
from typing import Any

from hy.models import Expression, Symbol


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
                    getattr(
                        importlib.import_module(f"genruler.modules.{sequence[0][1]}"),
                        str(sequence[0][2]),
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
                result + (sequence[0],),
            )

    else:
        assert callable(result[0])

        return result[0](*result[1:])

    return to_return
