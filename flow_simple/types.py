from typing import Callable, Optional, Tuple, Union

import requests

StepTuple = Tuple[dict, Union[dict, Callable[[requests.Response], Optional["StepTuple"]]]]
