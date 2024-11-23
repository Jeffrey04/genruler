from collections.abc import Callable
from operator import itemgetter
from typing import Any

from genruler.library import compute


def context(context_sub: Any, argument: Any) -> Callable[[dict[Any, Any]], Any]:
    def inner(context: dict[Any, Any]) -> Any:
        return compute(argument, compute(context_sub, context))

    return inner


def field(key: str, *args) -> Callable[[dict[Any, Any] | list[Any]], Any]:
    def inner(context: dict[Any, Any] | list[Any]) -> Any:
        return (
            context.get(compute(key, context), compute(args[0], context))
            if args
            else itemgetter(compute(key, context))(context)
        )

    return inner


def value[T](value: T) -> Callable[[dict[Any, Any]], T]:
    def inner(_: Any) -> T:
        return value

    return inner
