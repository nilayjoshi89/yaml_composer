from abc import ABC, abstractmethod


class YamlGeneratorBase(ABC):
    @abstractmethod
    def start(self, file_path: str) -> str:
        pass  # pragma: no cover
