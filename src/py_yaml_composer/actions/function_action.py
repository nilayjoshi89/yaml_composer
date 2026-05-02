import copy
from typing import Any

from py_yaml_composer.utility.regex_helper import RegexHelper


class YamlFunctionAction:
    pattern_func_call = r"^(?:X-REF-)(.+?)\((.+?)\)$"
    pattern_funct_arg = r"^(.*?)\{\s?(?:X-ARG-)(.+?)\s?\}(.*?)$"

    def __init__(self) -> None:
        self.ref_data: dict[Any, Any]

    def apply(
        self, data: dict[Any, Any] | list[Any] | Any, ref_data: dict[Any, Any]
    ) -> None:
        self.ref_data = ref_data
        self.__apply_internal(data, [])

    def __apply_internal(
        self, data: dict[Any, Any] | list[Any] | Any, funct_arguments: list[str]
    ) -> None:
        # dict
        if isinstance(data, dict):
            self.__handle_dict(data, funct_arguments)
            return

        # list
        if isinstance(data, list):
            items_to_iterate = data[:]
            for item in items_to_iterate:
                if YamlFunctionAction.is_funct_arg(item):
                    item_value = YamlFunctionAction.get_funct_arg_val(
                        item, funct_arguments
                    )
                    data.remove(item)
                    data.append(item_value)
                    continue
                self.__apply_internal(item, funct_arguments)
            return

    def __handle_dict(
        self, data: dict[Any, Any], funct_arguments: list[str]
    ) -> None:
        items_to_iterate: list[tuple[Any, Any]] = list(data.items())
        for key, val in items_to_iterate:
            if YamlFunctionAction.is_function_node(key):
                data.pop(key)
                new_args: list[str] = YamlFunctionAction.get_function_arguments(
                    key
                )
                modified_values = self.__replace_dict_key(data, key, new_args)
                for key in modified_values:
                    self.__apply_internal(data[key], new_args)
                continue

            if YamlFunctionAction.is_function_node(val):
                new_args = YamlFunctionAction.get_function_arguments(val)
                modified_values = self.__replace_dict_value(
                    val, data, key, funct_arguments
                )
                for key in modified_values:
                    self.__apply_internal(data[key], new_args)
                continue

            if YamlFunctionAction.is_funct_arg(key):
                funct_arg_val = YamlFunctionAction.get_funct_arg_val(
                    key, funct_arguments
                )
                old_val = data.pop(key)
                data[funct_arg_val] = old_val
                key = funct_arg_val

            if YamlFunctionAction.is_funct_arg(val):
                funct_arg_val = YamlFunctionAction.get_funct_arg_val(
                    val, funct_arguments
                )
                data[key] = funct_arg_val

            self.__apply_internal(val, funct_arguments)

    def __replace_dict_key(
        self, parent: Any, key: str, funct_param: list[str]
    ) -> list[str]:
        added_items: list[str] = []
        function_name = f"X-REF-{YamlFunctionAction.get_function_name(key)}"
        new_val = self.ref_data.get(function_name)
        if new_val is None:  # overriden value is None
            return added_items

        if not isinstance(new_val, dict):
            raise ValueError(f"Value must be dict - {new_val}")

        for k, v in new_val.items():
            if YamlFunctionAction.is_funct_arg(k):
                k = YamlFunctionAction.get_funct_arg_val(k, funct_param)
            if YamlFunctionAction.is_funct_arg(v):
                v = YamlFunctionAction.get_funct_arg_val(v, funct_param)

            cloned_val = copy.deepcopy(v)
            added_items.append(str(k))

            existing_value = parent.get(k, None)
            if existing_value is None or isinstance(v, str):
                parent[k] = cloned_val
                continue

            if isinstance(existing_value, dict) and isinstance(cloned_val, dict):
                existing_value.update(cloned_val)
                continue
            if isinstance(existing_value, list):
                existing_value.extend(cloned_val)
                continue

            parent[k] = copy.deepcopy(cloned_val)

        return added_items

    def __replace_dict_value(
        self, node: Any, parent: Any, key: str, funct_param: list[str]
    ) -> list[str]:
        function_name = f"X-REF-{YamlFunctionAction.get_function_name(node)}"
        new_val = self.ref_data.get(function_name)

        if new_val is None:
            raise ValueError(f"Reference not found - {node}")

        if YamlFunctionAction.is_funct_arg(new_val):
            new_val = YamlFunctionAction.get_funct_arg_val(new_val, funct_param)

        cloned_val = copy.deepcopy(new_val)
        parent[key] = cloned_val
        return [key]

    @staticmethod
    def get_function_name(function: str) -> str:
        return RegexHelper.match(YamlFunctionAction.pattern_func_call, function)[0]

    @staticmethod
    def is_function_node(function: Any) -> bool:
        if function is None or not isinstance(function, str):
            return False

        return (
            function is not None
            and len(
                RegexHelper.match(YamlFunctionAction.pattern_func_call, function)
            )
            == 2
        )

    @staticmethod
    def get_function_arguments(function: str) -> list[str]:
        return (
            RegexHelper.match(YamlFunctionAction.pattern_func_call, function)[1]
            .replace("'", "")
            .replace('"', "")
            .split(",")
        )

    @staticmethod
    def is_funct_arg(argument: str) -> bool:
        if argument is None or not isinstance(argument, str):
            return False
        return (
            argument is not None
            and len(
                RegexHelper.match(YamlFunctionAction.pattern_funct_arg, argument)
            )
            == 3
        )

    @staticmethod
    def get_funct_arg_val(key: str, funct_arg: list[str]) -> str:
        matches: list[str] = RegexHelper.match(
            YamlFunctionAction.pattern_funct_arg, key
        )
        index = int(matches[1])
        if index > len(funct_arg) or index < 1:
            raise ValueError(f"Invalid Function argument index: {key}")

        return f"{matches[0]}{funct_arg[index - 1]}{matches[2]}"
