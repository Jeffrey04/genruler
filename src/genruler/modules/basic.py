from functools import reduce
from operator import itemgetter
from typing import Any, TypeVar

from genruler.library import compute

T = TypeVar("T")


class coalesce:
    """Return the first non-empty value from a sequence of values.

    Similar to SQL's COALESCE function, returns the first value that is truthy
    when evaluated in the given context.

    Attributes:
        value: The first value to try
        arguments: Additional values to try in sequence
    """

    value: Any
    arguments: Any

    def __init__(self, value: Any, *arguments: Any) -> None:
        """Initialize with a sequence of values to try.

        Args:
            value: The first value to try
            *arguments: Additional values to try in sequence
        """
        self.value = value
        self.arguments = arguments

    def __call__(self, context: dict[Any, Any]) -> Any:
        """Evaluate values in sequence until a truthy value is found.

        Args:
            context: The context for evaluating callable values

        Returns:
            The first truthy value found, or the last value if all are falsy
        """
        return reduce(
            lambda current, incoming: current or compute(incoming, context),
            self.arguments,
            compute(self.value, context),
        )

    # TODO: may be beneficial if reversible
    # Incomplete implementation
    # def __repr__(self) -> str:
    #     import json
    #     return (
    #         f"({str(__name__).split('.')[-1]}.{self.__class__.__name__} "
    #         f"{str(self.value)} "
    #         f"{' '.join(str(argument) if callable(argument) else json.dumps(argument) for argument in self.arguments)})"
    #     )


class context:
    """Access nested context values using a sub-context and argument.

    Allows accessing values from a nested context by first evaluating a sub-context
    expression and then evaluating an argument within that sub-context.

    Attributes:
        context_sub: Expression to evaluate to get the sub-context
        argument: Expression to evaluate within the sub-context
    """

    context_sub: Any
    argument: Any

    def __init__(self, context_sub: Any, argument: Any) -> None:
        """Initialize with sub-context and argument expressions.

        Args:
            context_sub: Expression to evaluate to get the sub-context
            argument: Expression to evaluate within the sub-context
        """
        self.context_sub = context_sub
        self.argument = argument

    def __call__(self, context: dict[Any, Any]) -> Any:
        """Evaluate the argument in the sub-context.

        First evaluates context_sub in the given context to get a sub-context,
        then evaluates argument in that sub-context.

        Args:
            context: The root context for evaluation

        Returns:
            The result of evaluating argument in the sub-context
        """
        return compute(self.argument, compute(self.context_sub, context))


class field:
    """Access field values from a dictionary or list context.

    For dictionaries, supports optional default values for missing keys.
    For lists, uses operator.itemgetter for direct index access.

    Attributes:
        key: The key or index to access
        args: Optional default value for dictionary access
    """

    key: str
    args: tuple[Any, ...]

    def __init__(self, key: str, *args: Any) -> None:
        """Initialize with key/index and optional default value.

        Args:
            key: The key or index to access
            *args: Optional default value for dictionary access
        """
        self.key = key
        self.args = args

    def __call__(self, context: dict[Any, Any] | list[Any]) -> Any:
        """Access a value from the context.

        For dictionaries:
        - If args is provided, uses dict.get with the first arg as default
        - If no args, uses direct key access
        For lists:
        - Uses itemgetter with computed key value

        Args:
            context: The dictionary or list to access

        Returns:
            The value at the specified key/index, or the default value
        """
        if isinstance(context, dict):
            return (
                context.get(self.key, compute(self.args[0], context))
                if self.args
                else context[self.key]
            )
        else:
            return itemgetter(compute(self.key, context))(context)


class value:
    """Hold a constant value that ignores context.

    A simple wrapper that returns the same value regardless of context.
    Useful for injecting constant values into expressions.

    Attributes:
        value: The constant value to return

    Raises:
        ValueError: If the value is a sub-rule
    """

    def __init__(self, value: T) -> None:
        """Initialize with a constant value.

        Args:
            value: The value to return on every call

        Raises:
            ValueError: If the value is a sub-rule
        """
        if callable(value):
            raise ValueError("basic.value cannot accept sub-rules")
        self.value = value

    def __call__(self, _: Any) -> T:
        """Return the constant value, ignoring context.

        Args:
            _: Ignored context parameter

        Returns:
            The constant value provided at initialization
        """
        return self.value
