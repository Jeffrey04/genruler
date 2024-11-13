from collections.abc import Callable
from functools import reduce
from typing import Any

from .library import compute


def binary[T](
    operation: Callable[[Any, Any], T], arguments: tuple[Any]
) -> Callable[[Any], T]:
    def inner(context: dict[Any, Any]) -> T:
        return reduce(operation, (compute(argument, context) for argument in arguments))

    return inner
