from typing import Any, Callable

from genruler.library import compute
from genruler.modules import basic


def field(key: str, *args) -> Callable[[dict[Any, Any] | list[Any]], Any]:
    def inner(context: dict[Any, Any] | list[Any]) -> Any:
        return str(compute(basic.field(compute(key, context), *args), context))

    return inner


def concat(link: Any, *arguments: Any) -> Callable[[dict[Any, Any]], str]:
    def inner(context: dict[Any, Any]) -> str:
        return compute(link, context).join(
            compute(argument, context) for argument in arguments
        )

    return inner


def concat_fields(link: Any, *arguments: Any) -> Callable[[dict[Any, Any]], str]:
    def inner(context: dict[Any, Any]) -> str:
        print(arguments)
        return concat(
            link,
            *[field(compute(argument, context))(context) for argument in arguments],
        )(context)

    return inner


def lower(argument: Any) -> Callable[[dict[Any, Any]], str]:
    def inner(context: dict[Any, Any]) -> str:
        return compute(argument, context).lower()

    return inner
