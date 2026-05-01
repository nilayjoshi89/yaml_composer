from typing import Any

from py_yaml_composer.actions.action_base import YamlActionBase
from py_yaml_composer.actions.action_context import ActionContext


class YamlSortDockerComposeNodeAction(YamlActionBase):
    def apply(
        self, data: dict[Any, Any] | list[Any] | Any, context: ActionContext
    ) -> None:
        node_order = [
            "services",
            "profiles",
            "image",
            "container_name",
            "command",
            "restart",
            "environment",
            "ports",
            "volumes",
            "depends_on",
            "networks",
            "healthcheck",
            "labels",
        ]

        if isinstance(data, dict):
            copy_dict: dict[Any, Any] = dict(
                sorted(
                    data.items(),
                    key=lambda item: (
                        node_order.index(item[0])
                        if item[0] in node_order
                        else len(node_order) + 1
                    ),
                )
            )
            data.clear()
            data.update(copy_dict)
            return

        if isinstance(data, list):
            copy_list: list[Any] = [
                *sorted(
                    data,
                    key=lambda item: (
                        node_order.index(item[0])
                        if item[0] in node_order
                        else len(node_order) + 1
                    ),
                )
            ]
            data.clear()
            data.extend(copy_list)
            return
