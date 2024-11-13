import operator
from collections.abc import Callable
from numbers import Number
from typing import Any

from genruler.common import binary


def add(*arguments: Any) -> Callable[[dict[Any, Any]], Number]:
    return binary(operator.add, arguments)


def subtract(*arguments: Any) -> Callable[[dict[Any, Any]], Number]:
    return binary(operator.sub, arguments)


def multiply(*arguments: Any) -> Callable[[dict[Any, Any]], Number]:
    return binary(operator.mul, arguments)


def divide(*arguments: Any) -> Callable[[dict[Any, Any]], Number]:
    return binary(operator.truediv, arguments)


def modulo(*arguments: Any) -> Callable[[dict[Any, Any]], Number]:
    return binary(operator.mod, arguments)
