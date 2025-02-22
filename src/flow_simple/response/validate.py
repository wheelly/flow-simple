import logging
from collections.abc import Callable
from typing import Any, Optional, cast

import requests
from flow_simple.response.import_function import import_function
from flow_simple.types import StepTuple
from flow_simple.validator import check_data
from flow_simple.variables import resolve_variables

logger = logging.getLogger(__name__)


def validate(
    response_settings: dict,
    new_step_callback: Optional[Callable[[str, dict], StepTuple]] = None,
    await_endpoint: Optional[str] = None,
    await_params: Optional[dict] = None
) -> Callable[[requests.Response], Optional[StepTuple]]:
    """Prepares the response check."""
    def check_response(
        response: requests.Response
    ) -> Optional[StepTuple]:
        """Checks if the response is correct."""
        if status := response_settings.get("status"):
            check_data({"status": status}, {"status": response.status_code})

        if expected_body := response_settings.get("body"):
            is_json = response.headers.get("content-type", "").startswith("application/json")
            if is_json:
                try:
                    data = response.json()
                except ValueError as e:
                    logger.error(response.content)
                    # assertion error here will be caught in retries else test will fail
                    assert False, f"Response is not a valid JSON: {e}"
            else:
                data = response.text
            if function := response_settings.get("function"):
                custom_validator = import_function(function)
                return custom_validator(response, expected_body)
            check_data(expected_body, data)
            if new_step_callback and await_endpoint and await_params:
                if is_json:
                    resolve_variables(await_params, cast(dict[str, Any], data))
                    logger.debug(f"Resolved await_params: {await_params}")
                return new_step_callback(await_endpoint, await_params)
        return None

    return check_response
