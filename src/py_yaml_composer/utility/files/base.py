import typing
from abc import ABC, abstractmethod


class YamlFileHelperBase(ABC):
    @abstractmethod
    def load(self, file_path: str) -> dict[typing.Any, typing.Any]:
        pass  # pragma: no cover

    @abstractmethod
    def save(self, data: dict[typing.Any, typing.Any], file_path: str) -> None:
        pass  # pragma: no cover

    @abstractmethod
    def exists(self, file_path: str) -> bool:
        pass  # pragma: no cover
