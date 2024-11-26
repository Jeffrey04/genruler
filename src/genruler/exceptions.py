class GenRulerException(Exception):
    """Base exception for all genruler exceptions."""

    pass


class NonCallableResultError(GenRulerException):
    """Raised when parse result is not callable."""

    def __init__(self, result_type: str):
        self.result_type = result_type
        super().__init__(f"Parse result must be callable, got {result_type}")


class InvalidFunctionNameError(GenRulerException):
    """Raised when a function name is invalid."""

    def __init__(self, name: str):
        self.name = name
        super().__init__(
            f"Invalid function name '{name}'. Function names must be in format 'module.function'"
        )
