import operator
from collections.abc import Callable
from typing import Any

from genruler.common import binary
from genruler.library import compute


def equal(*arguments: Any) -> Callable[[dict[Any, Any]], bool]:
    return binary(operator.eq, arguments)


def gt(*arguments: Any) -> Callable[[dict[Any, Any]], bool]:
    return binary(operator.gt, arguments)


def ge(*arguments: Any) -> Callable[[dict[Any, Any]], bool]:
    return binary(operator.ge, arguments)


def in_(*arguments: Any) -> Callable[[dict[Any, Any]], bool]:
    return binary(operator.contains, arguments[::-1])


def is_none(argument: Any) -> Callable[[dict[Any, Any]], bool]:
    def inner(context: dict[Any, Any]) -> bool:
        return compute(argument, context) is None

    return inner

def is_true(argument: Any) -> Callable[[dict[Any, Any]], bool]:
    def inner(context: dict[Any, Any]) -> bool:
        return compute(argument, context) is True

    return inner


def lt(*arguments: Any) -> Callable[[dict[Any, Any]], bool]:
    return binary(operator.lt, arguments)


def le(*arguments: Any) -> Callable[[dict[Any, Any]], bool]:
    return binary(operator.le, arguments)
