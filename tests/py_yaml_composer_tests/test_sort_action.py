from typing import Any

from py_yaml_composer.actions.action_context import ActionContext
from py_yaml_composer.actions.sort_action import YamlSortDockerComposeNodeAction


class TestYamlSortDockerComposeNodeAction:
    def test_empty_dict_returns_early(self) -> None:
        # arrange — empty dict hits the early-return guard (line 29)
        action = YamlSortDockerComposeNodeAction()
        data: dict[Any, Any] = {}

        # act
        action.apply(data, ActionContext(ref_data={}))

        # assert
        assert data == {}

    def test_unsortable_list_does_not_raise(self) -> None:
        # arrange — list of integers causes item[0] to raise TypeError inside sorted();
        # the except block swallows it and the list is left unchanged (lines 60-62)
        action = YamlSortDockerComposeNodeAction()
        data: list[Any] = [3, 1, 2]

        # act
        action.apply(data, ActionContext(ref_data={}))

        # assert — list is unchanged after the failed sort
        assert data == [3, 1, 2]
