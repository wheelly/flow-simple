from pathlib import PosixPath

import pytest
from flow_simple.flow_generator import flow_generator
from flow_simple.step import Step


def pytest_pycollect_makemodule(module_path: PosixPath, parent: pytest.Module):
    """Executes get_flow function from the module giving back dict with test configuration."""
    module = pytest.Module.from_parent(parent, path=module_path)
    get_flow = getattr(module.module, "get_flow", None)
    if get_flow is None:
        raise AttributeError(f"Module '{module.name}' does not have a 'get_flow' function!")

    steps = flow_generator(get_flow())
    return FlowCollector.from_parent(name=module.name, parent=parent, steps=steps)


class FlowCollector(pytest.Collector):
    """Collects the test items."""
    def __init__(self, name, parent, steps):
        super().__init__(name, parent)
        self.steps = steps

    def collect(self):
        for step in self.steps:
            yield StepItem.from_parent(parent=self.parent, name=str(step), step=step)


class StepItem(pytest.Item):
    """A single test item."""
    def __init__(self, name, parent: pytest.Module, step: Step):
        super().__init__(name, parent)
        self.step = step

    def runtest(self):
        """Execute the test item."""
        self.step.run()
