import logging
from types import StepTuple
from typing import Callable, Optional, Union

import requests

logger = logging.getLogger(__name__)


def create_response_callback(
    settings: dict,
    await_endpoint: Optional[str] = None,
    await_params: Optional[dict] = None
) -> Union[dict, Callable[[requests.Response], None]]:
    """Parses the response configuration and create callback to outer code."""
    response_settings = settings.get("response")
    retries = settings.get("retries")
    if not response_settings and not retries:
        raise ValueError("Response or retries that must have until response missing")

    if retries:
        response_callback = prepare_check_response(
            response_settings, await_endpoint, await_params) if response_settings else None
        until_response_callback = prepare_check_response(retries["until"]["response"], await_endpoint, await_params)
        return {
            # it's intermediate response check which is optional
            "response_callback": response_callback,
            "max": retries.get("max", 10),
            "delay": {
                "min": retries.get("delay", {}).get("min", 1),
                "max": retries.get("delay", {}).get("max", 10)
            },
            "until_response_callback": until_response_callback
        }

    return prepare_check_response(response_settings, await_endpoint, await_params)

def prepare_check_response(
    response_settings: dict,
    await_endpoint: Optional[str] = None,
    await_params: Optional[dict] = None
) -> Callable[[requests.Response], Optional[StepTuple]]:
    """Prepares the response check."""
    def check_response(response: requests.Response) -> Optional[StepTuple]:
        """Checks if the response is correct."""
        if status := response_settings.get("status"):
            check_data({"status": status}, {"status": response.status_code})
        if expected_body := response_settings.get("body"):
            try:
                data = response.json()
            except ValueError as e:
                logger.error(response.content)
                # assertion error here will be caught in retries else test will fail
                assert False, f"Response is not a valid JSON: {e}"
            check_data(expected_body, data)
        if await_params:
            resolve_variables(await_params, data)
            logger.debug(f"Resolved await_params: {await_params}")
            return step_parser(await_endpoint, await_params)

    return check_response

