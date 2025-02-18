from typing import Generator

from flow_simple.step import Step


def flow_generator(config: dict) -> Generator[Step, None, None]:
    """Starts parsing the flow configuration and returns Generator."""
    flow = config["flow"]
    base_url = config.get("base_url", "")
    refs = config.get("refs")
    for step in flow:
        url, params = next(iter(step.items()))
        yield Step(url, params, refs, base_url)
