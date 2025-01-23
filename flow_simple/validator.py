import logging
from typing import Any, List, Union

logger = logging.getLogger(__name__)

def check_data(expected: dict, data: Any):
    """Checks if the data is correct."""
    for key, value in expected.items():
        if key.startswith("&"):
            check_operator_expr(key, value, data)
        else:
            if isinstance(value, dict):
                # recursion
                check_data(value, data[key])
            elif isinstance(value, list):
                check_list(value, data[key])
            else:
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    logger.warning(
                        f"Variable '{value}' detected in expected data. Checking property existence in response data")
                    assert key in data and data[key], f"Key for variable {value} not found in response body"
                else:
                    logger.debug(f"{data[key]} == {value}")
                    assert data[key] == value


def check_operator_expr(key: str, expected: Any, data: Union[str, List[Any]]):
    """Evaluates the expression."""

    assert not isinstance(expected, dict), "Dictionary is not supported in operator expression"

    operator = key[1:]
    if operator == "lt":
        logger.debug(f"{data} < {expected}")
        assert data < expected
    elif operator == "lte":
        logger.debug(f"{data} <= {expected}")
        assert data <= expected
    elif operator == "gt":
        logger.debug(f"{data} > {expected}")
        assert data > expected
    elif operator == "gte":
        logger.debug(f"{data} >= {expected}")
        assert data >= expected
    elif operator == "ne":
        logger.debug(f"{data} != {expected}")
        assert data != expected
    elif operator == "in":
        logger.debug(f"{data} in {expected}")
        assert isinstance(expected, list), "Expected should be a list"
        assert data in expected
    elif operator == "nin":
        logger.debug(f"{data} not in {expected}")
        assert isinstance(expected, list), "Expected should be a list"
        assert data not in expected
    elif operator == "has":
        logger.debug(f"{expected} in {data}")
        assert isinstance(data, list), "Data should be a list"
        assert expected in data

    else:
        raise ValueError(f"Unknown operator: {operator}")


def check_list(expected: Union[list, dict], data: list):
    """Checks if the list is correct."""

    if isinstance(expected, dict):
        for key, value in expected.items():
            if key.startswith("&"):
                check_operator_expr(key, value, data)
            else:
                raise ValueError("Expected should be a list or use correct operator definition starting with '&'")
    else:
        assert len(expected) == len(data)
        for i, value in enumerate(expected):
            if isinstance(value, dict):
                check_data(value, data[i])
            elif isinstance(value, list):
                check_list(value, data[i])
            else:
                # Check if the value is in the list so we don't need to sort it
                assert value in data