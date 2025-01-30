import time

import pytest
from pytest_mock import MockerFixture


@pytest.fixture(scope="function", autouse=True)
def do_something(mocker: MockerFixture, request):
    """Fixture to do something before and after the test session."""
    mocker.patch.object(time, "sleep", return_value=None)
