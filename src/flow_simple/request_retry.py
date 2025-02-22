import logging
import time
from collections.abc import Callable
from typing import Dict, Optional

import requests
from flow_simple.types import StepTuple

logger = logging.getLogger(__name__)


def request_retry(
    request_callback: Callable[..., requests.Response],
    request_params: dict,
    settings: dict
) -> Optional[StepTuple]:
    """Executes HTTP request with retries, raising TimeoutError after max attempts."""
    response_callback = settings.get("response_callback")
    until_response_callback = settings["until_response_callback"]
    delay_min_sec = settings["delay"]["min"]
    delay_max_sec = wait_time = settings["delay"]["max"]
    max_retries = settings["max"]
    response: Optional[requests.Response] = None

    for attempt in range(max_retries):
        try:
            response = request_callback(**request_params)
        except OSError as e:
            logger.warning(f"Got exception: {e}. sleep for {delay_max_sec} seconds")

        if attempt < max_retries - 1:
            wait_time = max(delay_min_sec, delay_max_sec - attempt * max_retries)

        if response is None:
            logger.warning(f"Connection error. Sleeping for {wait_time} seconds")
            time.sleep(wait_time)
            continue

        try:
            return until_response_callback(response)
        except AssertionError:
            if response_callback:
                logger.debug("Checking intermediate response")
                response_callback(response)
            logger.info(f"Sleeping for {wait_time} seconds")
            time.sleep(wait_time)

    raise TimeoutError(
        f"Not ready after {max_retries} attempts: {request_params} got response {response} {response.json() if response else None}")
