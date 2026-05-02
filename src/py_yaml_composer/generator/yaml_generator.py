from typing import Any

from py_yaml_composer.actions.action_base import YamlActionBase
from py_yaml_composer.actions.action_context import ActionContext
from py_yaml_composer.actions.function_action import YamlFunctionAction
from py_yaml_composer.actions.xref_action import YamlXRefAction
from py_yaml_composer.generator.base import YamlGeneratorBase
from py_yaml_composer.traverser.base import YamlTraverseBase
from py_yaml_composer.utility.files.base import YamlFileHelperBase


class YamlGenerator(YamlGeneratorBase):
    def __init__(
        self,
        file_helper: YamlFileHelperBase,
        traverser: YamlTraverseBase,
        multistage_actions: list[YamlActionBase],
    ) -> None:
        self.fileHelper: YamlFileHelperBase = file_helper
        self.traverser: YamlTraverseBase = traverser
        self.multistage_actions: list[YamlActionBase] = multistage_actions

    def start(self, file_path: str) -> str:
        template_data: dict[Any, Any] = self.fileHelper.load(file_path)

        output_file_path = self.get_output_file_path(template_data)
        ref_data = self.get_ref_data(template_data)
        context: ActionContext = ActionContext(ref_data=ref_data)

        YamlFunctionAction().apply(template_data, ref_data)

        for action in self.multistage_actions:
            self.traverser.traverse(template_data, action, context)

        self.fileHelper.save(template_data, output_file_path)
        return output_file_path

    def get_ref_data(self, app_template: dict[Any, Any]) -> dict[Any, Any]:
        ref_data_file_path = app_template.pop("X-INCLUDE", [])

        ref_data = {}
        for file in ref_data_file_path:
            if not self.fileHelper.exists(file):
                raise ValueError(f"File does not exist - {file}")
            ref_data.update(self.fileHelper.load(file))

        # local overrides
        local_override = app_template.pop("X-OVERRIDE", {})
        for key in list(local_override.keys()):
            if YamlXRefAction.is_ref_node(key):
                ref_data[key] = local_override.pop(key)
        return ref_data

    def get_output_file_path(self, app_template: dict[Any, Any]) -> str:
        output_file_path = app_template.pop("X-OUTPUT", None)
        if not output_file_path:
            raise ValueError("Output file path not specified in the template")
        return str(output_file_path)
