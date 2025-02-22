"""
To run this from the command line, use the following command:
PYTHONPATH="./src" pytest -v -p flow_simple.pytest_plugin ./examples/plugin/test_example.py
"""
import os

import yaml


def get_flow() -> dict:
    """Returns a flow configuration - this method required by plugin."""
    path_to_yaml = os.path.join(os.path.dirname(__file__), "httpbins.yaml")
    return read_yaml(path_to_yaml)


def read_yaml(file_path: str) -> dict:
    """Reads a YAML file and returns its content as a dictionary."""
    with open(file_path, "r") as file:
        return yaml.safe_load(file)
