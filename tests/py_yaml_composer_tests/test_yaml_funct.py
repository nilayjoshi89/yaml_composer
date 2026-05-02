from typing import Any

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
