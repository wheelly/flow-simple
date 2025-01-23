import logging
from types import StepTuple
from typing import Generator

from step import Step

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


def flow_me(config: dict) -> Generator[StepTuple, None, None]:
    """Parses the flow configuration."""
    flow = config["flow"]
    refs = config.get("refs") or {}
    for step in flow:
        url, params = next(iter(step.items()))
        yield Step(url, params, refs).parse()
