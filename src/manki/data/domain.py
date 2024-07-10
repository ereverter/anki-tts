from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from pydantic import BaseModel


class WordEntry(BaseModel):
    word: str
    part_of_speech: Optional[List[str]]
    definitions: Optional[List[str]]
    level: Optional[str]
    synonyms = Optional[List[str]]
    antonyms = Optional[List[str]]
    metadata = Optional[Dict]


class WordParser(ABC):
    @abstractmethod
    def parse_information(self) -> List[WordEntry]: ...
