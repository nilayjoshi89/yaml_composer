from typing import Any

import pytest

from py_yaml_composer.actions.default_actions import DefaultActions
from py_yaml_composer.generator.yaml_generator import YamlGenerator
from py_yaml_composer.traverser.basic_dfs import YamlTraverser
from tests.py_yaml_composer_tests.mock_file_helper import MockFileHelper


class TestYamlReferences:
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

    def test_simple_yaml_generation(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "Node1": "Value1",
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_file_ref_resolution(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-INCLUDE": ["RefFile.yaml"],
            "X-OUTPUT": MockFileHelper.output_file,
            "Node1": "Value1",
            "X-REF-Node2": None,
        }
        ref_file_data: dict[str, Any] = {
            "X-REF-Node2": {
                "Node2": "Value2",
            }
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
            "Node2": "Value2",
        }
        self.create_generator(input_data)
        self.mock_file_helper.setup_ref_file("RefFile.yaml", ref_file_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_missing_file_ref_raises_error(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-INCLUDE": ["RefFile.yaml", "MissingFile.yaml"],
            "X-OUTPUT": MockFileHelper.output_file,
            "Node1": "Value1",
            "X-REF-Node2": None,
        }
        ref_file_data: dict[str, Any] = {
            "X-REF-Node2": {
                "Node2": "Value2",
            }
        }
        self.create_generator(input_data)
        self.mock_file_helper.setup_ref_file("RefFile.yaml", ref_file_data)

        # act
        with pytest.raises(ValueError) as exc_info:
            self.generator.start(MockFileHelper.input_file)

        # assert
        assert exc_info.type is ValueError
        assert str(exc_info.value) == "File does not exist - MissingFile.yaml"

    def test_missing_output_value_raises_error(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {
                "X-REF-Node2": {
                    "Node2": "Value2",
                }
            },
            "Node1": "Value1",
            "X-REF-Node2": None,
        }

        self.mock_file_helper = MockFileHelper(
            {MockFileHelper.input_file: input_data}
        )

        self.generator = YamlGenerator(
            file_helper=self.mock_file_helper,
            traverser=YamlTraverser(),
            multistage_actions=DefaultActions.get(),
        )

        # act
        with pytest.raises(ValueError) as exc_info:
            self.generator.start(MockFileHelper.input_file)

        # assert
        assert exc_info.type is ValueError
        assert (
            str(exc_info.value) == "Output file path not specified in the template"
        )

    def test_local_ref_resolution(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {"X-REF-Node2": {"Node2": "Value2"}},
            "Node1": "Value1",
            "X-REF-Node2": None,
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

    def test_local_ref_deep_resolution(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {"X-REF-Val": ["1", "2", "3"]},
            "Node1": "Value1",
            "Node2": {"Node2.1": "X-REF-Val"},
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
            "Node2": {"Node2.1": ["1", "2", "3"]},
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_ref_with_tag_replacement(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {
                "X-REF-Node2": {"Node2": "Value2"},
                "X-REF-TAG-VALUE": ["Tag1", "Tag2"],
            },
            "Node1": "Value1",
            "X-REF-Node2": None,
            "Tags": "X-REF-TAG-VALUE",
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
            "Node2": "Value2",
            "Tags": ["Tag1", "Tag2"],
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_nested_ref_in_list(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {
                "X-REF-TAG-0": "Tag2",
                "X-REF-TAG-VALUE": ["Tag1", "X-REF-TAG-0"],
            },
            "Node1": "Value1",
            "Tags": "X-REF-TAG-VALUE",
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
            "Tags": ["Tag1", "Tag2"],
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_nested_ref_in_dict_key_val(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {
                "X-REF-A2": "A2",
                "X-REF-A": {"A1": "X-REF-A2"},
                "X-REF-B": {"B1": "B2"},
            },
            "Back-Ref": {"X-REF-A": None, "X-REF-B": None},
        }
        expected_output: dict[str, Any] = {
            "Back-Ref": {"A1": "A2", "B1": "B2"},
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_local_override_takes_precedence_over_file(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-INCLUDE": ["RefFile.yaml"],
            "X-OVERRIDE": {"X-REF-Node2": {"Node3": "Value3"}},
            "Node1": "Value1",
            "X-REF-Node2": None,
        }
        ref_file_data: dict[str, Any] = {
            "X-REF-Node2": {
                "Node2": "Value2",
            }
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
            "Node3": "Value3",
        }

        self.create_generator(input_data)
        self.mock_file_helper.setup_ref_file(
            "RefFile.yaml", file_content=ref_file_data
        )

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_local_override_with_none_removes_ref(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-INCLUDE": ["RefFile.yaml"],
            "X-OVERRIDE": {"X-REF-Node2": None},
            "Node1": "Value1",
            "X-REF-Node2": None,
        }
        ref_file_data: dict[str, Any] = {
            "X-REF-Node2": {
                "Node2": "Value2",
            }
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
        }

        self.create_generator(input_data)
        self.mock_file_helper.setup_ref_file(
            "RefFile.yaml", file_content=ref_file_data
        )

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_ref_hierarchy(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-INCLUDE": ["RefFile.yaml", "RefFile2.yaml"],
            "X-OVERRIDE": {"X-REF-Node2": {"Node2": "LocalValue"}},
            "Node1": "Value1",
            "X-REF-Node2": None,
        }
        ref_file_data: dict[str, Any] = {
            "X-REF-Node2": {
                "Node2": "RefFileValue",
            }
        }
        ref_file_data2: dict[str, Any] = {
            "X-REF-Node2": {
                "Node2": "RefFileValue2",
            }
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
            "Node2": "LocalValue",
        }
        self.create_generator(input_data)
        self.mock_file_helper.setup_ref_file(
            "RefFile.yaml", file_content=ref_file_data
        )
        self.mock_file_helper.setup_ref_file(
            "RefFile2.yaml", file_content=ref_file_data2
        )

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_dict_key_replacement(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {"X-REF-Node": {"Node2": "Value2"}},
            "Node1": "Value1",
            "X-REF-Node": None,
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

    def test_ref_dict_merges_to_parent(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {"X-REF-Node": {"Node2": "Value2"}},
            "Node1": "Value1",
            "Node2": "This will be replaced",
            "X-REF-Node": 5,
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

    def test_ref_replacement_in_dict_value(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {
                "X-REF-VAL2": "Value2",
                "X-REF-Node2": {
                    "Node2": "X-REF-VAL2",
                },
            },
            "Node1": "Value1",
            "X-REF-Node2": None,
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

    def test_ref_dict_replacement_in_dict_value(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {
                "X-REF-VAL2": {"1": "2", "3": "4"},
                "X-REF-Node2": {
                    "Node2": "X-REF-VAL2",
                },
            },
            "Node1": "Value1",
            "X-REF-Node2": None,
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
            "Node2": {"1": "2", "3": "4"},
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_ref_list_replacement_in_dict_value(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {
                "X-REF-VAL2": ["1", "2", "3", "4"],
                "X-REF-Node2": {
                    "Node2": "X-REF-VAL2",
                },
            },
            "Node1": "Value1",
            "X-REF-Node2": None,
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
            "Node2": ["1", "2", "3", "4"],
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_ref_list_merge_in_dict_value(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {
                "X-REF-Node2": {
                    "Node2": ["1", "2", "3", "4"],
                }
            },
            "Node1": "Value1",
            "Node2": ["0"],
            "X-REF-Node2": None,
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
            "Node2": ["0", "1", "2", "3", "4"],
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_ref_dict_merge_in_dict_value(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {
                "X-REF-Node2": {
                    "Node2": {
                        "1": "One",
                        "2": "Two",
                        "3": "Three",
                        "4": "Four",
                    },
                },
            },
            "Node1": "Value1",
            "Node2": {"0": "Zero", "1": "ShouldBeOverwritten"},
            "X-REF-Node2": None,
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
            "Node2": {
                "0": "Zero",
                "1": "One",
                "2": "Two",
                "3": "Three",
                "4": "Four",
            },
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_ref_in_dict_key_raises_error(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {
                "X-REF-KEY": "Node2",
                "X-REF-Node2": {
                    "X-REF-KEY": "Value2",
                },
            },
            "Node1": "Value1",
            "X-REF-Node2": None,
        }
        self.create_generator(input_data)

        # act
        with pytest.raises(ValueError) as exc_info:
            self.generator.start(MockFileHelper.input_file)

        # assert
        assert exc_info.type is ValueError
        assert str(exc_info.value) == "Value must be dict - Node2"

    def test_ref_list_merge_in_list(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {
                "X-REF-Val2": ["1", "2", "3", "4"],
            },
            "Node1": "Value1",
            "Node2": ["0", "X-REF-Val2"],
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
            "Node2": ["0", "1", "2", "3", "4"],
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)

    def test_undefined_dict_value_ref_raises_error(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "Node1": "X-REF-Undefined",
        }
        self.create_generator(input_data)

        # act
        with pytest.raises(ValueError) as exc_info:
            self.generator.start(MockFileHelper.input_file)

        # assert
        assert exc_info.type is ValueError
        assert str(exc_info.value) == "Reference not found - X-REF-Undefined"

    def test_undefined_list_ref_raises_error(self) -> None:
        # arrange
        input_data: dict[str, Any] = {
            "Node1": ["X-REF-Undefined"],
        }
        self.create_generator(input_data)

        # act
        with pytest.raises(ValueError) as exc_info:
            self.generator.start(MockFileHelper.input_file)

        # assert
        assert exc_info.type is ValueError
        assert str(exc_info.value) == "Reference not found - X-REF-Undefined"

    def test_ref_dict_replacement_in_list_value(self) -> None:
        # arrange - dict reference in a single-element list should replace list with dict
        input_data: dict[str, Any] = {
            "X-OVERRIDE": {
                "X-REF-ENV-CONFIG": {
                    "DB": "mydb",
                    "USER": "admin",
                    "PASSWORD": "secret",
                },
            },
            "Node1": "Value1",
            "Node2": ["X-REF-ENV-CONFIG"],
        }
        expected_output: dict[str, Any] = {
            "Node1": "Value1",
            "Node2": {
                "DB": "mydb",
                "USER": "admin",
                "PASSWORD": "secret",
            },
        }
        self.create_generator(input_data)

        # act
        self.generator.start(MockFileHelper.input_file)

        # assert
        self.verify_no_diff(expected_output)
