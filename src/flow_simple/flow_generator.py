import logging
from typing import Generator

from flow_simple.step import Step
from flow_simple.types import StepTuple

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

def flow_generator(config: dict) -> Generator[StepTuple, None, None]:
    """Starts parsing the flow configuration and returns Generator."""
    flow = config["flow"]
    base_url = config.get("base_url", "")
    refs = config.get("refs") or {}
    for step in flow:
        url, params = next(iter(step.items()))
        yield Step(base_url + url, params, refs).parse()
