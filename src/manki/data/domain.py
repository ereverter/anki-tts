from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel


class WordEntry(BaseModel):
    word: str
    part_of_speech: Optional[List[str]]
    definitions: Optional[List[str]]
    level: Optional[str]


class WordParser(ABC):
    @abstractmethod
    def parse_information(self) -> List[WordEntry]: ...
