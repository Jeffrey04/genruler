from collections.abc import Callable

from python_ruler.library import compute


def length[T](argument: Callable[[T], list] | list) -> Callable[[T], int]:
    def inner(context: T) -> int:
        return len(compute(argument, context))

    return inner
