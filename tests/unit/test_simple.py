from typing import Any, List, Optional, Union

import pytest
import responses
from flow_simple.flow_generator import flow_generator
from flow_simple.runner import FlowRunner
from flow_simple.step import compile_url
from responses.registries import OrderedRegistry

FLOW: dict[str, Union[List[dict[str, Any]], str]] = {
    "base_url": "http://localhost/api/v1/",
    "flow": [],
    "refs": {
        "check-status": {
            "actions": {
                "method": "GET",
                "parameters": [
                    "${action_id}"
                ],
                "response": {
                    "body": {
                        "action_id": "${action_id}",
                        "status": {
                            "&in": [
                                "pending",
                                "processing"
                            ]
                        }
                    }
                },
                "retries": {
                    "max": 3,  # we need 3 retries to test 3 different responses
                    "delay": {
                        "min": 1,
                        "max": 1
                    },
                    "until": {
                        "response": {
                            "body": {
                                "action_id": "${action_id}",
                                "status": "completed"
                            }
                        }
                    }
                }
            }
        }
    }
}


def get_await_response(status: str) -> dict:
    """Returns the await response."""
    return {
        "url": compile_url(FLOW["base_url"], "actions/123"),
        "method": "GET",
        "body": {
            "action_id": "123",
            "status": status
        }
    }


@pytest.mark.parametrize(
    "steps, mock_responses, await_request_response",
    [
        (
            [
                {
                    "status": {
                        "method": "GET",
                        "response": {
                            # interested in status equal to ready
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
            ],
            [
                {
                    # mocked response
                    "body": {
                        "components": {
                            "collector-source": {
                                "status": "ready",
                                "some_other_property": "some_other_value"
                            }
                        }
                    }
                }
            ],
            None
        ),
        # awaits logic
        (
            [
                {
                    "providers": {
                        "method": "PUT",
                        "parameters": [
                            "local-vault"
                        ],
                        "body": {
                            "type": "vault",
                            "parameters": {
                                "vaultAddress": "http://vault.default:8200",
                                "roleName": "database",
                                "objects": [
                                    {
                                        "objectName": "credentials",
                                        "secretPath": "secret/data/db-credentials",
                                        "secretKey": "credentials"
                                    }
                                ]
                            }
                        },
                        "response": {
                            "body": {
                                "action_id": "${action_id}"
                            }
                        },
                        "awaits": {
                            "ref": "check-status"
                        }
                    }
                }
            ],
            [
                # mocked responses
                {
                    "body": {
                        "action_id": "123"
                    }
                }
            ],
            [
                get_await_response("pending"),
                get_await_response("processing"),
                get_await_response("completed"),
            ]
        )
    ]
)
def test_flow(steps: list[dict], mock_responses: list[dict], await_request_response: Optional[list[dict]]):
    FLOW["flow"] = steps

    with responses.RequestsMock(registry=OrderedRegistry) as rsps:
        for i, step in enumerate(steps):
            endpoint, props = next(iter(step.items()))
            url = compile_url(FLOW["base_url"], endpoint)
            # TODO: copypast from step - remove next to lines
            if parameters := props.get("parameters"):
                url += "/" + "/".join(parameters)
            rsps.add(
                url=url,
                method=props["method"],
                json=mock_responses[i].get("body"),
                status=mock_responses[i].get("status", 200)
            )
        if await_request_response:
            for i, response in enumerate(await_request_response):
                rsps.add(
                    url=response["url"],
                    method=response["method"],
                    json=response.get("body"),
                    status=response.get("status", 200)
                )
        FlowRunner(flow_generator(FLOW)).run()
