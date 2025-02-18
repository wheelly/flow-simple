import copy
import logging
from typing import Callable, Optional

import requests
from flow_simple.request_retry import request_retry
from flow_simple.response.callback import create_response_callback
from flow_simple.types import ExternalChecker, StepTuple

logger = logging.getLogger(__name__)


class Step():
    def __init__(self, url: str, params: dict, refs: Optional[dict] = None, base_url: Optional[str] = None):
        """Initializes the Step object."""
        self.url = url
        self.base_url = base_url
        self.params = params
        self.refs = refs
        if parameters := params.get("parameters"):
            self.url += "/" + "/".join(parameters)
        self.request = {
            "method": params["method"],
            "url": compile_url(self.base_url, self.url),
            "params": params.get("query"),
            "json": params.get("body")
        }

    def parse(self) -> StepTuple:
        """Parses the step configuration."""
        info = []

        def new_step_callback(await_endpoint: str, await_params: dict) -> StepTuple:
            """Creates a new step with await parameters and recursively calls Step.parse."""
            return Step(await_endpoint, await_params, self.refs, self.base_url).parse()

        if awaits := self.params.get("awaits"):
            info.append(f"Awaits: {awaits}")
            await_endpoint_or_ref, await_params_or_ref_name = next(iter(awaits.items()))
            if await_endpoint_or_ref == "ref" and isinstance(
                    await_params_or_ref_name, str) and isinstance(
                    self.refs, dict):
                assert await_params_or_ref_name in self.refs, f"Reference '{await_params_or_ref_name}' not found"
                await_ref_endpoint, await_ref_params = next(iter(self.refs[await_params_or_ref_name].items()))
                info.append(f"ref resolved: {await_ref_endpoint} -> {await_ref_params}")
                response = create_response_callback(self.params, new_step_callback,
                                                    await_ref_endpoint, copy.deepcopy(await_ref_params))
            else:
                response = create_response_callback(self.params, new_step_callback,
                                                    await_endpoint_or_ref, await_params_or_ref_name)
        else:
            response = create_response_callback(self.params)

        logger.debug(f"Step: {self.request} -> {response} {info}")
        return self.request, response

    def run(self, checkers_map: dict[str, ExternalChecker], request_callback: Callable[..., requests.Response]):
        """Runs the step."""
        request_params, response_callback = self.parse()

        # awaits logic with child endpoint
        while True:
            if isinstance(response_callback, dict):
                # retrying if response is dict and has retries settings
                additional_step = request_retry(checkers_map, request_callback,
                                                request_params, response_callback)
            else:
                # child endpoint (no special use for it now - the same as the next endpoint in the flow)
                additional_step = response_callback(checkers_map, request_callback(**request_params))
            if not additional_step:
                break
            request_params, response_callback = additional_step


def compile_url(base_url: Optional[str], url: str) -> str:
    """Compiles the base url and the url."""
    return (base_url.rstrip("/") if base_url else "") + "/" + url.lstrip("/")
