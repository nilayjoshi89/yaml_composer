from abc import ABC, abstractmethod
from typing import Any

from py_yaml_composer.actions.action_context import ActionContext


class YamlActionBase(ABC):
    @abstractmethod
    def apply(
        self, data: dict[Any, Any] | list[Any] | Any, context: ActionContext
    ) -> None:
        pass  # pragma: no cover
