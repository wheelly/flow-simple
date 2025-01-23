from typing import Callable, Tuple

import requests

StepTuple = Tuple[dict, Callable[[requests.Response], None]]
