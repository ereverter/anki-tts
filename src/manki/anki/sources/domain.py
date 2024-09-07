from abc import ABC, abstractmethod
from typing import List

from ..domain import AnkiNote


class AnkiFileParser(ABC):
    @abstractmethod
    def parse(self, files: List[str]) -> List[AnkiNote]:
        pass
