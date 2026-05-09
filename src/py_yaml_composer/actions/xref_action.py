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
                items_to_iterate = []
                for key, val in data.items():
                    if YamlXRefAction.is_ref_node(key):
                        items_to_iterate.append((key, val, "key"))
                    elif isinstance(val, str) and YamlXRefAction.is_ref_node(val):
                        items_to_iterate.append((key, val, "value"))
                    elif (
                        isinstance(val, list)
                        and len(val) == 1
                        and YamlXRefAction.is_ref_node(val[0])
                    ):
                        # Only handle list->dict replacement at dict level
                        ref_val = context.ref_data.get(val[0])
                        if isinstance(ref_val, dict):
                            items_to_iterate.append((key, val, "list_value"))

                if not items_to_iterate:
                    break

                for key, val, item_type in items_to_iterate:
                    if item_type == "key":
                        data.pop(key)
                        self.__replace_dict_key(data, key, context)
                    elif item_type == "list_value":
                        self.__replace_list_value(data, key, context)
                    else:  # value
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

    def __replace_list_value(
        self, parent: dict[Any, Any], key: str, context: ActionContext
    ) -> None:
        """Replace a list containing a single ref with the ref's value if it's a dict."""
        list_val = parent[key]
        if not isinstance(list_val, list) or len(list_val) != 1:
            return

        ref_node = list_val[0]
        if not YamlXRefAction.is_ref_node(ref_node):
            return

        new_val = context.ref_data.get(ref_node)
        if new_val is None:
            raise ValueError(f"Reference not found - {ref_node}")

        # Only replace with dict values - keep lists and scalars as-is
        if isinstance(new_val, dict):
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

    @staticmethod
    def _is_list_with_single_ref(val: Any) -> bool:
        """Check if a value is a list with exactly one ref node."""
        return (
            isinstance(val, list)
            and len(val) == 1
            and YamlXRefAction.is_ref_node(val[0])
        )
