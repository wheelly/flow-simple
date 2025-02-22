from typing import Any, Callable, Dict, Optional, Tuple, Union

import requests

StepTuple = Tuple[dict, Union[dict, Callable[[requests.Response], Optional["StepTuple"]]]]
