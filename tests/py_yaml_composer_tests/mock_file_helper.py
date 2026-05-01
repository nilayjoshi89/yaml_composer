import typing
from copy import deepcopy

from deepdiff import DeepDiff

from py_yaml_composer.utility.files.base import YamlFileHelperBase


class MockFileHelper(YamlFileHelperBase):
    input_file: str = "input.yaml"
    output_file: str = "output.yaml"

    def __init__(
        self,
        file_data: dict[str, dict[typing.Any, typing.Any]],
    ):
        self.file_data = file_data

    def load(self, file_path: str) -> dict[typing.Any, typing.Any]:
        return deepcopy(self.file_data.get(file_path, {}))

    def save(self, data: dict[typing.Any, typing.Any], file_path: str) -> None:
        self.file_data[file_path] = data

    def exists(self, file_path: str) -> bool:
        return file_path in self.file_data

    def get_output(self) -> dict[typing.Any, typing.Any] | None:
        return self.file_data.get(MockFileHelper.output_file)

    def setup_ref_file(
        self, file_name: str, file_content: dict[typing.Any, typing.Any]
    ) -> None:
        self.file_data[file_name] = deepcopy(file_content)

    def diff_output(
        self, expected_data: dict[typing.Any, typing.Any]
    ) -> dict[typing.Any, typing.Any]:
        return DeepDiff(
            self.get_output(),
            expected_data,
            ignore_order=True,
        )
