from collections.abc import Callable
from typing import Any

from genruler.library import compute


def context(context_sub: Any, argument: Any) -> Callable[[dict[Any, Any]], Any]:
    def inner(context: dict[Any, Any]) -> Any:
        return compute(argument, compute(context_sub, context))

    return inner


def field(key, default=None) -> Callable[[dict[Any, Any]], Any]:
    def inner(context: dict[Any, Any]) -> Any:
        return context.get(compute(key, context), compute(default, context))

    return inner


def value[T](value: T) -> Callable[[dict[Any, Any]], T]:
    def inner(_: Any) -> T:
        return value

    return inner
