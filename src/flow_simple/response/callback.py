import logging
from typing import Callable, Optional, Tuple, Union, cast

import requests
from flow_simple.response.validate import validate
from flow_simple.types import StepTuple

logger = logging.getLogger(__name__)


def create_response_callback(
    settings: dict,
    new_step_callback: Optional[Callable[[str, dict], StepTuple]] = None,
    await_endpoint: Optional[str] = None,
    await_params: Optional[dict] = None
) -> Union[dict, Callable[[requests.Response], Optional[StepTuple]]]:
    """Parses the response configuration and create callback to outer code."""
    response_settings: Optional[dict] = settings.get("response")
    retries = settings.get("retries")
    if not response_settings and not retries:
        raise ValueError("Response or retries that must have until response missing")

    if retries:
        response_callback = validate(
            response_settings, new_step_callback, await_endpoint, await_params) if response_settings else None
        until_response_callback = validate(retries["until"]["response"], new_step_callback, await_endpoint, await_params)
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

    return validate(cast(dict, response_settings), new_step_callback, await_endpoint, await_params)


