from collections.abc import Callable
from typing import Any

import hy

from genruler.library import evaluate


def parse(input: str) -> Callable[[Any], Any]:
    result = evaluate(hy.read(input))

    assert callable(result)

    return result
