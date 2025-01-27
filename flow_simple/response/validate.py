import logging
from typing import Callable, Optional

import requests
from flow_simple.types import StepTuple
from flow_simple.validator import check_data
from flow_simple.variables import resolve_variables

logger = logging.getLogger(__name__)

def validate(
    response_settings: dict,
    await_endpoint: Optional[str] = None,
    await_params: Optional[dict] = None
) -> Callable[[requests.Response], Optional[StepTuple]]:
    """Prepares the response check."""
    def check_response(response: requests.Response) -> Optional[StepTuple]:
        """Checks if the response is correct."""
        if status := response_settings.get("status"):
            check_data({"status": status}, {"status": response.status_code})
        data = None
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
            return Step(await_endpoint, await_params).parse()

    return check_response