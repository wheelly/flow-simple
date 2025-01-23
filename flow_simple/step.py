import logging
from types import StepTuple
from typing import Optional

from response import create_response_callback

logger = logging.getLogger(__name__)

class Step():
    def __init__(self, url: str, params: dict, refs: Optional[dict] = None):
        """Initializes the Step object."""
        self.url = url
        self.params = params
        self.refs = refs
        if parameters := params.get("parameters"):
            url += "/" + "/".join(parameters)
        self.request = {
            "method": params["method"],
            "url": url,
            "params": params.get("query"),
            "json": params.get("body")
        }

    def parse(self) -> StepTuple:
        """Parses the step configuration."""
        info = []

        if awaits := self.params.get("awaits"):
            info.append(f"Awaits: {awaits}")
            await_endpoint_or_ref, await_params_or_ref_name = next(iter(awaits.items()))
            if await_endpoint_or_ref == "ref" and isinstance(await_params_or_ref_name, str):
                assert await_params_or_ref_name in self.refs, f"Reference '{await_params_or_ref_name}' not found"
                await_ref_endpoint, await_ref_params = next(iter(self.refs[await_params_or_ref_name].items()))
                info.append(f"ref resolved: {await_ref_endpoint} -> {await_ref_params}")
                response = create_response_callback(self.params, await_ref_endpoint, copy.deepcopy(await_ref_params))
            else:
                response = create_response_callback(self.params, await_endpoint_or_ref, await_params_or_ref_name)
        else:
            response = create_response_callback(self.params)

        logger.debug(f"Step: {self.request} -> {response} {info}")
        return self.request, response
