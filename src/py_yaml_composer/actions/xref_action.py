import copy
from typing import Any

from py_yaml_composer.actions.action_base import YamlActionBase
from py_yaml_composer.actions.action_context import ActionContext


class YamlXRefAction(YamlActionBase):
    def apply(
        self, data: dict[Any, Any] | list[Any] | Any, context: ActionContext
    ) -> None:
        if isinstance(data, dict):
            while True:
                items_to_iterate = [
                    (key, val)
                    for (key, val) in data.items()
                    if YamlXRefAction.is_ref_node(key)
                    or YamlXRefAction.is_ref_node(val)
                ]

                if not items_to_iterate:
                    break

                for key, val in items_to_iterate:
                    if YamlXRefAction.is_ref_node(key):
                        data.pop(key)
                        self.__replace_dict_key(data, key, context)
                    else:
                        self.__replace_dict_value(val, data, key, context)
            return

        if isinstance(data, list):
            while True:
                items_to_iterate = [
                    val for val in data if YamlXRefAction.is_ref_node(val)
                ]
                if not items_to_iterate:
                    break
                for val in items_to_iterate:
                    self.__replace_list(val, data, context)

    def __replace_dict_key(
        self, parent: Any, key: str, context: ActionContext
    ) -> None:
        new_val = context.ref_data.get(key)
        if new_val is None:  # overriden value is None
            return

        if not isinstance(new_val, dict):
            raise ValueError(f"Value must be dict - {new_val}")

        for k, v in new_val.items():
            existing_value = parent.get(k, None)

            if existing_value is None:
                parent[k] = copy.deepcopy(v)
                continue

            if isinstance(existing_value, dict):
                existing_value.update(copy.deepcopy(v))
                continue
            if isinstance(existing_value, list):
                existing_value.extend(copy.deepcopy(v))
                continue

            parent[k] = copy.deepcopy(v)

    def __replace_dict_value(
        self, node: Any, parent: Any, key: str, context: ActionContext
    ) -> None:
        new_val = context.ref_data.get(node)
        if new_val is None:
            raise ValueError(f"Reference not found - {node}")

        parent[key] = copy.deepcopy(new_val)

    def __replace_list(
        self, node: Any, parent: Any, context: ActionContext
    ) -> None:
        new_val = context.ref_data.get(node)
        if new_val is None:
            raise ValueError(f"Reference not found - {node}")

        parent.remove(node)

        if not isinstance(new_val, list) and not isinstance(new_val, dict):
            parent.append(new_val)
            return

        for item in new_val:
            parent.append(copy.deepcopy(item))

    @staticmethod
    def is_ref_node(key: str) -> bool:
        return key is not None and str(key).startswith("X-REF")
