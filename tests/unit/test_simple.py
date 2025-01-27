from collections.abc import Callable

import pytest
import requests
import responses
from flow_simple.flow_generator import flow_generator
from flow_simple.runner import FlowRunner

FLOW = {"flow": [], "base_url": "http://localhost/api/v1/"}

@pytest.mark.parametrize(
    "steps, response_data",
    [
        ([
             {
                 "status": {
                     "method": "GET",
                     "response": {
                         "body": {
                             "components": {
                                 "collector-source": {
                                     "status": "ready"
                                 }
                             }
                         }
                     }
                 }
             }
         ]
        , {"components": {"collector-source": {"status": "ready"}}}
        ),
    ]
)
def test_flow(steps: list[dict], response_data: dict):
    FLOW["flow"] = steps
    FlowRunner(flow_generator(FLOW), create_mock_response(json=response_data)).run()



def create_mock_response(**kwargs) -> Callable[[requests.request], requests.Response]:
    """Creates a mock response."""

    @responses.activate
    def mocked_response(**inner_kwargs) -> requests.Response:
        responses.add(method=inner_kwargs["method"], url=inner_kwargs["url"], json=kwargs["json"], status=kwargs.get("status", 200))
        return requests.request(**inner_kwargs)
    return mocked_response