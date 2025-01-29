from collections.abc import Callable
from typing import Any, List, Union

import pytest
import requests
import responses
from flow_simple.flow_generator import flow_generator
from flow_simple.runner import FlowRunner

FLOW : dict[str, Union[List[dict[str, Any]], str]] = {
    "base_url": "http://localhost/api/v1/",
    "flow": [],
    "refs":{
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
          "max": 2,
          "delay": {
            "min": 1,
            "max": 2
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

@pytest.mark.parametrize(
    "steps, mock_responses",
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
            ]
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
            ]
        )
    ]
)
def test_flow(steps: list[dict], mock_responses: list[dict]):
    FLOW["flow"] = steps
    FlowRunner(flow_generator(FLOW), create_mock_response(mock_responses)).run()

def create_mock_response(mock_responses: list[dict]) -> Callable[..., requests.Response]:
    """Creates a mock response."""
    @responses.activate
    def mocked_response(**request_args) -> requests.Response:
        for response in mock_responses:
            responses.add(
                method=request_args["method"],
                url=request_args["url"],
                json=response.get("body"),
                status=response.get("status", 200)
            )
        return requests.request(**request_args)
    return mocked_response