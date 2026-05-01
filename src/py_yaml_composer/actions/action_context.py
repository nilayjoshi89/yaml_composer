from dataclasses import dataclass
from typing import Any


@dataclass
class ActionContext:
    ref_data: dict[Any, Any]
