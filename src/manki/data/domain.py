from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from pydantic import BaseModel


class WordEntry(BaseModel):
    word: str
    part_of_speech: Optional[List[str]] = None
    definitions: Optional[List[str]] = None
    level: Optional[str] = None
    # synonyms: Optional[List[str]] = None
    # antonyms: Optional[List[str]] = None
    # metadata: Optional[Dict] = None


class WordParser(ABC):
    @abstractmethod
    def parse_information(self) -> List[WordEntry]: ...
