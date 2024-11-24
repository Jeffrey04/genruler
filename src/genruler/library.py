import importlib
from collections.abc import Callable
from typing import Any, List

from hy.models import Expression, Float, Integer, Object, String, Symbol

from .lexer import Symbol as genSymbol


def compute[T, U, V](argument: Callable[[T], U] | V, context: T) -> U | V:
    """Compute the value of an argument, which can be either a callable or a value.

    Args:
        argument: Either a callable that takes a context and returns a value, or a direct value.
            If it's a callable, it will be called with the context.
            If it's a value, it will be returned as is.
        context: The context to pass to the callable if argument is a callable.

    Returns:
        If argument is a callable, returns the result of calling it with context.
        If argument is a value, returns the value directly.

    Example:
        >>> compute(lambda x: x + 1, 5)  # Callable case
        6
        >>> compute(42, None)  # Direct value case
        42
    """
    return (
        argument(context)  # type: ignore
        if callable(argument)
        else argument  # type: ignore
    )


def evaluate(
    sequence: Expression | List[Any], result=None
) -> tuple[Any] | Callable[[Any], Any]:
    """Evaluate an S-expression sequence into a callable or value.

    This function recursively evaluates S-expressions, handling several forms:
    1. Symbol-based function calls: (module.function arg1 arg2)
    2. Hy-style function calls: (. module function arg1 arg2)
    3. Nested expressions: (module.function (other.function arg1) arg2)

    The sequence must be wrapped in parentheses - bare literals or symbols are not accepted.

    Args:
        sequence: The S-expression to evaluate. Must be either:
            - A Hy Expression object
            - A Python list from the custom parser
            The first item in the sequence must be either:
            - A Symbol (module.function)
            - A nested Expression/List starting with '.'
            Subsequent items can be:
            - Nested expressions
            - Literal values (strings, integers, floats)
        result: Internal parameter for recursive evaluation.
            Accumulates the evaluated parts of the expression.
            Users should not pass this parameter.

    Returns:
        - If evaluating a complete expression: A callable that takes a context
        - If evaluating a partial expression: A tuple of evaluated values

    Raises:
        ValueError: If the sequence is not properly wrapped in parentheses
        AssertionError: If a Symbol doesn't contain a module.function name
        TypeError: If sequence is not a list or Expression

    Examples:
        >>> evaluate(parse("(boolean.and True False)"))({})  # Function call
        False
        >>> evaluate(parse("(. boolean not True)"))({})      # Hy-style call
        False
        >>> evaluate(parse("(math.add (math.mul 2 3) 4)"))({})  # Nested call
        10

        # These will raise errors:
        >>> evaluate(parse("True"))  # ValueError: not wrapped in parentheses
        >>> evaluate(parse("(invalid_symbol)"))  # AssertionError: no module.function
        >>> evaluate("not a sequence")  # TypeError: must be list or Expression
    """
    assert isinstance(sequence, (list, Expression)), "sequence must be a list or Expression"
    result = result or tuple()
    to_return = None

    if len(sequence) > 0:
        if isinstance(sequence[0], genSymbol):
            assert "." in sequence[0].name
            module, function = sequence[0].name.split(".")
            to_return = evaluate(
                sequence[1:],  # type: ignore
                result + (get_function(f"genruler.modules.{module}", function),),
            )

        elif isinstance(sequence[0], Expression) and sequence[0][0] == Symbol("."):
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

        elif isinstance(sequence[0], list):
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
    match argument.__class__.__name__:
        case String.__name__:
            return str(argument)
        case Integer.__name__:
            return int(argument)
        case Float.__name__:
            return float(argument)
        case _:
            return argument


def get_function(module_name: str, function_name: str) -> Callable[[Any], Any]:
    """Get a function from a module by name."""
    module = importlib.import_module(module_name)

    try:
        function = getattr(module, function_name)
    except AttributeError:
        function = getattr(module, f"{function_name}_")

    assert callable(function)

    return function