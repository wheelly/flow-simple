import logging
from collections.abc import Callable
from typing import Any, List, Optional

import requests
from flow_simple.flow_generator import flow_generator

logger = logging.getLogger(__name__)


class FlowRunner:
    """Runs every step of the flow."""

    def __init__(
        self,
        config: dict,
        request_callback: Callable[..., requests.Response] = requests.request
    ):
        """Initializes the FlowRunner."""

        self.flow_iterator = flow_generator(config)
        self.request_callback = request_callback

    def run(self):
        """Test the flow by default on resourses/flow/github.yaml."""
        for step in self.flow_iterator:
            step.run(self.request_callback)
