import logging
from typing import Callable, Optional, Union

import requests
from flow_simple.response.validate import validate

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
        response_callback = validate(
            response_settings, await_endpoint, await_params) if response_settings else None
        until_response_callback = validate(retries["until"]["response"], await_endpoint, await_params)
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

    return validate(response_settings, await_endpoint, await_params)


