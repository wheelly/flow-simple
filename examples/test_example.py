import http.client as http_client

import yaml
from flow_simple import FlowRunner

http_client.HTTPConnection.debuglevel = 1

def test_example():
    FlowRunner(read_yaml("./httpbins.yaml")).run()

def read_yaml(file_path: str) -> dict:
    """Reads a YAML file and returns its content as a dictionary.

    Args:
        file_path (str): Path to the YAML file.

    Returns:
        dict: Content of the YAML file.
    """
    with open(file_path, "r") as file:
        return yaml.safe_load(file)