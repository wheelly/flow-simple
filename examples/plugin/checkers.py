from typing import Any

from requests import Response


def contains(response: Response, expected: Any):
    """Checks if the response contains the expected value."""
    got = response.text
    assert isinstance(expected, str), f"Expected a string, got {type(expected)}"
    assert got.find(expected) != -1, f"Expected {expected} in {got}"
