from collections.abc import Callable
from typing import Generator

import requests
from flow_simple.request_retry import request_retry
from flow_simple.types import StepTuple


class FlowRunner:
    """Runs every step of the flow."""
    def __init__(
        self,
        flow_iterator: Generator[StepTuple, None, None],
        request_callback: Callable[..., requests.Response] = requests.request
    ):
        self.flow_iterator = flow_iterator
        self.request_callback = request_callback

    def run(self):
        """Test the flow by default on resourses/flow/github.yaml."""
        for step in self.flow_iterator:
            request_params, response_callback = step

            # awaits logic with child endpoint
            while True:
                if isinstance(response_callback, dict):
                    # retrying if response is dict and has retries settings
                    additional_step = request_retry(self.request_callback, request_params, response_callback)
                else:
                    # child endpoint (no special use for it now - the same as the next endpoint in the flow)
                    additional_step = response_callback(self.request_callback(**request_params))
                if not additional_step:
                    break
                request_params, response_callback = additional_step
