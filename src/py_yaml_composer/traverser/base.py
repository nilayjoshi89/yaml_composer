from abc import ABC, abstractmethod
from typing import Any

from py_yaml_composer.actions.action_base import YamlActionBase
from py_yaml_composer.actions.action_context import ActionContext


class YamlTraverseBase(ABC):
    @abstractmethod
    def traverse(
        self,
        data: dict[Any, Any],
        handler: YamlActionBase,
        context: ActionContext,
    ) -> None:
        pass  # pragma: no cover
