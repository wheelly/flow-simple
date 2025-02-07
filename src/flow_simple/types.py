from typing import Any, Callable, Optional, Tuple, Union

import requests

StepTuple = Tuple[dict, Union[dict, Callable[[requests.Response], Optional["StepTuple"]]]]
ExternalChecker = Callable[[Any, Any], None]
