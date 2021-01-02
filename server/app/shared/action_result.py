from dataclasses import dataclass
from typing import Any


@dataclass
class ActionResult:
    value: Any
    valid: bool