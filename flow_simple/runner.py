from typing import Generator

import requests

from flow_simple.request_retry import request_retry
from flow_simple.types import StepTuple


def run_flow(flow_iterator: Generator[StepTuple, None, None]):
    """Test the flow by default on resourses/flow/github.yaml."""
    for step in flow_iterator:
        request_settings, response_settings = step
        while True:
            if isinstance(response_settings, dict):
                additional_step = request_retry(request_settings, response_settings)
            else:
                additional_step = response_settings(requests.request(**request_settings, verify=False))
            if not additional_step:
                break
            request_settings, response_settings = additional_step
