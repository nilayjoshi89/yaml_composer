"""Tests for xref_action.py to cover missing lines 90, 94, 98, 127."""

from typing import Any

import pytest

from py_yaml_composer.actions.action_context import ActionContext
from py_yaml_composer.actions.xref_action import YamlXRefAction


class TestYamlXRefActionCoverage:
    """Test missing coverage lines in YamlXRefAction."""

    def test_replace_dict_value_missing_reference_raises_error(self) -> None:
        """Test line 90: ValueError when reference not found in dict value."""
        # arrange
        from py_yaml_composer.traverser.basic_dfs import YamlTraverser

        action = YamlXRefAction()
        traverser = YamlTraverser()
        data: dict[Any, Any] = {
            "Node1": "X-REF-Missing",
        }
        context = ActionContext(ref_data={})

        # act & assert - need traverser to reach this code path
        with pytest.raises(ValueError) as exc_info:
            traverser.traverse(data, action, context)
        assert "Reference not found - X-REF-Missing" in str(exc_info.value)

    def test_replace_dict_key_with_non_dict_value_raises_error(self) -> None:
        """Test line 94: ValueError when X-REF key resolves to non-dict."""
        # arrange
        from py_yaml_composer.traverser.basic_dfs import YamlTraverser

        action = YamlXRefAction()
        traverser = YamlTraverser()
        data: dict[Any, Any] = {
            "X-REF-BadRef": None,
        }
        ref_data: dict[Any, Any] = {
            "X-REF-BadRef": "not-a-dict",  # Should be dict
        }
        context = ActionContext(ref_data=ref_data)

        # act & assert
        with pytest.raises(ValueError) as exc_info:
            traverser.traverse(data, action, context)
        assert "Value must be dict" in str(exc_info.value)

    def test_list_value_with_multiple_elements_skipped(self) -> None:
        """Test line 90: Early return when list has more than one element."""
        # arrange - list with multiple elements shouldn't be processed
        action = YamlXRefAction()
        data: dict[Any, Any] = {
            "config": ["X-REF-Config", "extra_item"],
        }
        ref_data: dict[Any, Any] = {
            "X-REF-Config": {"key": "value"},
        }
        context = ActionContext(ref_data=ref_data)

        # act
        action.apply(data, context)

        # assert - list with >1 item is not touched
        assert data == {"config": ["X-REF-Config", "extra_item"]}

    def test_list_value_with_non_ref_element_skipped(self) -> None:
        """Test line 94: Early return when list element is not a ref node."""
        # arrange - list with non-ref element
        action = YamlXRefAction()
        data: dict[Any, Any] = {
            "values": ["not-a-ref"],
        }
        ref_data: dict[Any, Any] = {}
        context = ActionContext(ref_data=ref_data)

        # act
        action.apply(data, context)

        # assert - non-ref single-element lists are not touched
        assert data == {"values": ["not-a-ref"]}

    def test_list_value_with_missing_ref_raises_error(self) -> None:
        """Test line 98: ValueError when single-ref list has missing reference."""
        # arrange
        from py_yaml_composer.traverser.basic_dfs import YamlTraverser

        action = YamlXRefAction()
        traverser = YamlTraverser()
        data: dict[Any, Any] = {
            "config": ["X-REF-Missing"],
        }
        context = ActionContext(ref_data={})

        # act & assert
        with pytest.raises(ValueError) as exc_info:
            traverser.traverse(data, action, context)
        assert "Reference not found - X-REF-Missing" in str(exc_info.value)

    def test_is_list_with_single_ref_static_method(self) -> None:
        """Test the _is_list_with_single_ref static method (line 127)."""
        # arrange & act & assert
        assert YamlXRefAction._is_list_with_single_ref(["X-REF-Node"]) is True
        assert YamlXRefAction._is_list_with_single_ref(["not-a-ref"]) is False
        assert YamlXRefAction._is_list_with_single_ref([]) is False
        assert (
            YamlXRefAction._is_list_with_single_ref(["X-REF-1", "X-REF-2"])
            is False
        )
        assert YamlXRefAction._is_list_with_single_ref("not-a-list") is False
        assert YamlXRefAction._is_list_with_single_ref(None) is False

    def test_list_with_single_ref_dict_replacement(self) -> None:
        """Test replacing list containing single ref with dict value."""
        # arrange
        action = YamlXRefAction()
        data: dict[Any, Any] = {
            "config": ["X-REF-Config"],
        }
        ref_data: dict[Any, Any] = {
            "X-REF-Config": {"key": "value", "timeout": 30},
        }
        context = ActionContext(ref_data=ref_data)

        # act
        action.apply(data, context)

        # assert - single-ref lists with dict values are replaced
        assert data == {"config": {"key": "value", "timeout": 30}}

    def test_list_with_single_ref_scalar_stays_in_list(self) -> None:
        """Test that list with single scalar ref stays unchanged."""
        # arrange - scalar refs in lists don't get replaced at dict value level
        action = YamlXRefAction()
        data: dict[Any, Any] = {
            "value": ["X-REF-Scalar"],
        }
        ref_data: dict[Any, Any] = {
            "X-REF-Scalar": "just-a-string",
        }
        context = ActionContext(ref_data=ref_data)

        # act
        action.apply(data, context)

        # assert - scalar values in single-ref lists are not replaced
        # The list itself isn't replaced because the value isn't a dict
        assert data == {"value": ["X-REF-Scalar"]}

    def test_list_with_single_ref_list_stays_unchanged(self) -> None:
        """Test that list with single list ref stays unchanged at dict value level."""
        # arrange
        action = YamlXRefAction()
        data: dict[Any, Any] = {
            "items": ["X-REF-Items"],
        }
        ref_data: dict[Any, Any] = {
            "X-REF-Items": ["item1", "item2", "item3"],
        }
        context = ActionContext(ref_data=ref_data)

        # act
        action.apply(data, context)

        # assert - list refs at dict value level are not replaced
        # Only dict refs are replaced
        assert data == {"items": ["X-REF-Items"]}

    def test_dict_value_ref_replacement_with_traverser(self) -> None:
        """Test X-REF value replacement in dict using traverser."""
        # arrange - needs traverser to recursively process nested structures
        from py_yaml_composer.traverser.basic_dfs import YamlTraverser

        action = YamlXRefAction()
        traverser = YamlTraverser()
        data: dict[Any, Any] = {
            "parent": {
                "child": "X-REF-Child",
            }
        }
        ref_data: dict[Any, Any] = {
            "X-REF-Child": {"child_key": "child_value"},
        }
        context = ActionContext(ref_data=ref_data)

        # act
        traverser.traverse(data, action, context)

        # assert - refs at nested dict value level get replaced when using traverser
        assert data == {
            "parent": {
                "child": {"child_key": "child_value"},
            }
        }

    def test_ref_data_dict_merge_with_existing_key(self) -> None:
        """Test dict merge when key already exists."""
        # arrange
        action = YamlXRefAction()
        data: dict[Any, Any] = {
            "X-REF-Config": None,
            "existing_key": "should_be_overwritten",
        }
        ref_data: dict[Any, Any] = {
            "X-REF-Config": {
                "existing_key": "new_value",
                "new_key": "added_value",
            },
        }
        context = ActionContext(ref_data=ref_data)

        # act
        action.apply(data, context)

        # assert
        assert data == {
            "existing_key": "new_value",
            "new_key": "added_value",
        }

    def test_ref_data_list_extend_with_existing_list(self) -> None:
        """Test list extend when key already has list value."""
        # arrange
        action = YamlXRefAction()
        data: dict[Any, Any] = {
            "X-REF-Items": None,
            "items": ["existing1"],
        }
        ref_data: dict[Any, Any] = {
            "X-REF-Items": {
                "items": ["new1", "new2"],
            },
        }
        context = ActionContext(ref_data=ref_data)

        # act
        action.apply(data, context)

        # assert
        assert data == {"items": ["existing1", "new1", "new2"]}

    def test_multiple_iterations_for_complex_refs(self) -> None:
        """Test that apply loops multiple times for complex references."""
        # arrange
        action = YamlXRefAction()
        data: dict[Any, Any] = {
            "X-REF-First": None,
            "X-REF-Second": None,
        }
        ref_data: dict[Any, Any] = {
            "X-REF-First": {"first": "value1"},
            "X-REF-Second": {"second": "value2"},
        }
        context = ActionContext(ref_data=ref_data)

        # act
        action.apply(data, context)

        # assert
        assert data == {"first": "value1", "second": "value2"}

    def test_is_ref_node_validation(self) -> None:
        """Test is_ref_node identifies X-REF nodes correctly."""
        # arrange & act & assert
        assert YamlXRefAction.is_ref_node("X-REF-Node") is True
        assert YamlXRefAction.is_ref_node("X-REF-") is True
        assert YamlXRefAction.is_ref_node("X-REF") is True  # Starts with X-REF
        assert YamlXRefAction.is_ref_node("REF-Node") is False
        assert YamlXRefAction.is_ref_node("not-a-ref") is False
