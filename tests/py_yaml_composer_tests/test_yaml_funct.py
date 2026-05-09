from typing import Any

import pytest

from py_yaml_composer.actions.default_actions import DefaultActions
from py_yaml_composer.generator.yaml_generator import YamlGenerator
from py_yaml_composer.traverser.basic_dfs import YamlTraverser
from tests.py_yaml_composer_tests.mock_file_helper import MockFileHelper


class TestYamlFunctions:
    def create_generator(self, input_yaml_data: dict[str, Any]) -> None:
        input_data: dict[str, Any] = {
            "X-OUTPUT": MockFileHelper.output_file
        } | input_yaml_data

        self.mock_file_helper: MockFileHelper = MockFileHelper(
            {MockFileHelper.input_file: input_data}
        )

        self.generator: YamlGenerator = YamlGenerator(
            file_helper=self.mock_file_helper,
            traverser=YamlTraverser(),
            multistage_actions=DefaultActions.get(),
        )

    def verify_no_diff(self, expected_output: dict[str, Any]) -> None:
        diff = self.mock_file_helper.diff_output(expected_output)
        assert diff == {}

    def test_function_with_dict_value(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {"X-REF-Node2": {"{X-ARG-1}": "{X-ARG-2}"}},
            "Node1": "Value1",
            "X-REF-Node2('Node2','Value2')": None,
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
            "Node2": "Value2",
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_function_with_list_value(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {"X-REF-Node2": ["{X-ARG-1}", "{X-ARG-2}"]},
            "Node1": "Value1",
            "Node2": "X-REF-Node2('Value2.1','Value2.2')",
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
            "Node2": ["Value2.1", "Value2.2"],
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_function_with_deep_arguments(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {"X-REF-Node2": {"Node2.1": {"{X-ARG-1}": "{X-ARG-2}"}}},
            "Node1": "Value1",
            "X-REF-Node2('Node2','Value2')": None,
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
            "Node2.1": {"Node2": "Value2"},
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_function_with_dict_value_composite_argument(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {"X-REF-Node2": {"Nod{X-ARG-1}": "Val{X-ARG-2}"}},
            "Node1": "Value1",
            "X-REF-Node2('e2','ue2')": None,
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
            "Node2": "Value2",
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_function_with_list_value_composite_argument(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {"X-REF-Node2": ["Value{X-ARG-1}", "Value{X-ARG-2}"]},
            "Node1": "Value1",
            "Node2": "X-REF-Node2('2.1','2.2')",
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
            "Node2": ["Value2.1", "Value2.2"],
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_function_with_deep_composite_argument(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {
                "X-REF-Node2": {"Node2.1": {"Node{X-ARG-1}a": "Value{X-ARG-2}a"}}
            },
            "Node1": "Value1",
            "X-REF-Node2('2','2')": None,
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
            "Node2.1": {"Node2a": "Value2a"},
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_function_with_deep_composite_argument2(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {
                "X-REF-GENERIC-COMPONENT": {
                    "type": "{X-ARG-1}",
                    "name": "{X-ARG-2}",
                    "config": {"timeout": "{X-ARG-3}"},
                }
            },
            "components": {
                "api-handler": {
                    "X-REF-GENERIC-COMPONENT('handler', 'api-processor', '30')": None
                }
            },
        }
        expected_output: dict[str, Any] = {
            "components": {
                "api-handler": {
                    "type": "handler",
                    "name": "api-processor",
                    "config": {"timeout": "30"},
                }
            }
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_function_key_with_undefined_ref_is_ignored(self) -> None:
        # arrange — function call key whose underlying X-REF does not exist;
        # __replace_dict_key returns early (line 89), key is silently dropped
        input_data: dict[str, Any] = {
            "Node1": "Value1",
            "X-REF-Undefined('arg1', 'arg2')": None,
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_function_key_with_non_dict_ref_raises_error(self) -> None:
        # arrange — X-REF resolves to a scalar, not a dict; raises ValueError (line 92)
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {"X-REF-Node2": "not_a_dict"},
            "Node1": "Value1",
            "X-REF-Node2('arg1')": None,
        }
        self.create_generator(input_data)

        # act
        with pytest.raises(ValueError) as exc_info:
            self.generator.start(MockFileHelper.input_file)

        # assert
        assert str(exc_info.value) == "Value must be dict - not_a_dict"

    def test_function_key_merges_existing_dict(self) -> None:
        # arrange — function key result has a key already present in parent as a dict;
        # existing dict is updated in-place (lines 108-110)
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {"X-REF-Node": {"Node2": {"key1": "val1"}}},
            "Node2": {"existing_key": "existing_val"},
            "X-REF-Node('arg')": None,
        }
        expected_output: dict[str, Any] = {
            "Node2": {"existing_key": "existing_val", "key1": "val1"},
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_function_key_extends_existing_list(self) -> None:
        # arrange — function key result has a key already present in parent as a list;
        # existing list is extended (lines 111-113)
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {"X-REF-Node": {"Node2": ["new1", "new2"]}},
            "Node2": ["existing"],
            "X-REF-Node('arg')": None,
        }
        expected_output: dict[str, Any] = {
            "Node2": ["existing", "new1", "new2"],
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_function_key_replaces_incompatible_existing_value(self) -> None:
        # arrange — function key result has a key already present in parent as a dict,
        # but the incoming value is a list (not dict-dict merge); parent key is replaced (line 115)
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {"X-REF-Node": {"Node2": ["new1", "new2"]}},
            "Node2": {"existing_key": "existing_val"},
            "X-REF-Node('arg')": None,
        }
        expected_output: dict[str, Any] = {
            "Node2": ["new1", "new2"],
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_function_value_with_undefined_ref_raises_error(self) -> None:
        # arrange — function call used as a dict VALUE whose X-REF is not defined;
        # raises ValueError (line 126)
        input_data: dict[str, Any] = {
            "Node1": "X-REF-Undefined('arg1')",
        }
        self.create_generator(input_data)

        # act
        with pytest.raises(ValueError) as exc_info:
            self.generator.start(MockFileHelper.input_file)

        # assert
        assert str(exc_info.value) == "Reference not found - X-REF-Undefined('arg1')"

    def test_function_invalid_arg_index_raises_error(self) -> None:
        # arrange — function VALUE call where the ref resolves to a funct-arg placeholder
        # (line 129) but the placeholder index exceeds the supplied arg count (line 183)
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {"X-REF-Node2": "{X-ARG-2}"},
            "Node2": "X-REF-Node2('only_one')",
        }
        self.create_generator(input_data)

        # act
        with pytest.raises(ValueError) as exc_info:
            self.generator.start(MockFileHelper.input_file)

        # assert
        assert str(exc_info.value) == "Invalid Function argument index: {X-ARG-2}"
