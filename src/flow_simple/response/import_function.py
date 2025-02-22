import importlib
from typing import Any, Callable

from requests import Response


def import_function(dotted_module_function: str) -> Callable[[Response, Any], None]:
    """Imports a function from a module.

    Args:
        dotted_module_function (str): Dotted module function path.

    Returns:
        Callable: Imported function.
    """
    tokens = dotted_module_function.split(".")
    module = importlib.import_module(".".join(tokens[:-1]))
    assert hasattr(module, tokens[-1]), f"Function {tokens[-1]} not found in module {module}"
    function = getattr(module, tokens[-1])
    assert isinstance(function, Callable), f"Function {tokens[-1]} is not callable"
    return function
