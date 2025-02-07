import logging
from collections.abc import Callable
from typing import Any, List, Optional

import requests
from flow_simple.flow_generator import flow_generator
from flow_simple.request_retry import request_retry
from flow_simple.types import ExternalChecker

logger = logging.getLogger(__name__)


class FlowRunner:
    """Runs every step of the flow."""

    def __init__(
        self,
        config: dict,
        external_checkers: Optional[List[ExternalChecker]] = None,
        request_callback: Callable[..., requests.Response] = requests.request
    ):
        """Initializes the FlowRunner."""

        self.flow_iterator = flow_generator(config)
        self.checkers_map = {}
        for checker in external_checkers or []:
            self.checkers_map[checker.__name__] = checker
        if self.checkers_map:
            logger.debug(f"Checkers: {','.join(self.checkers_map.keys())}")
        self.request_callback = request_callback

    def run(self):
        """Test the flow by default on resourses/flow/github.yaml."""
        for step in self.flow_iterator:
            request_params, response_callback = step

            # awaits logic with child endpoint
            while True:
                if isinstance(response_callback, dict):
                    # retrying if response is dict and has retries settings
                    additional_step = request_retry(self.checkers_map, self.request_callback,
                                                    request_params, response_callback)
                else:
                    # child endpoint (no special use for it now - the same as the next endpoint in the flow)
                    additional_step = response_callback(self.checkers_map, self.request_callback(**request_params))
                if not additional_step:
                    break
                request_params, response_callback = additional_step
