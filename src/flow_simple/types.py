from typing import Any, Callable, Dict, Optional, Tuple, Union

import requests

ExternalChecker = Callable[[Any, Any], None]
StepTuple = Tuple[dict, Union[dict, Callable[[Dict[str, ExternalChecker], requests.Response], Optional["StepTuple"]]]]
