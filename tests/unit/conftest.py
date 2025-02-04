import logging
import time

import pytest
from pytest_mock import MockerFixture

logger = logging.getLogger(__name__)

@pytest.fixture(scope="function", autouse=True)
def fake_sleep(mocker: MockerFixture, request):
    """Fixture to fake sleep function."""
    def fake_sleep_patched(seconds: int):
        logger.warning(f"Supposed to sleep for {seconds}")
    mocker.patch.object(time, "sleep", side_affect=fake_sleep_patched)
