import operator
from collections.abc import Callable
from typing import Any, Literal

from genruler.common import binary
from genruler.library import compute


def and_(*arguments: Any) -> Callable[[dict[Any, Any]], bool]:
    return binary(operator.and_, arguments)


def contradiction() -> Callable[[dict[Any, Any]], Literal[False]]:
    def inner(_: Any) -> Literal[False]:
        return False

    return inner


def or_(*arguments: Any) -> Callable[[dict[Any, Any]], bool]:
    return binary(operator.or_, arguments)


def not_(argument: Any) -> Callable[[dict[Any, Any]], bool]:
    def inner(context: dict[Any, Any]) -> bool:
        return not compute(argument, context)

    return inner


def tautology() -> Callable[[dict[Any, Any]], Literal[True]]:
    def inner(_: Any) -> Literal[True]:
        return True

    return inner
