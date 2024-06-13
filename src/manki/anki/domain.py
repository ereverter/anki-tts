from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel


class AnkiNote(BaseModel):
    deckName: str
    modelName: str
    front: str
    back: str
    audio: Optional[str] = None
    image: Optional[str] = None
    do_write: bool = False
    tags: List[str] = []

    def to_anki_dict(self) -> Dict:
        anki_note_dict = {
            "deckName": self.deckName,
            "modelName": self.modelName,
            "fields": {"front": self.front, "back": self.back},
            "options": {"allowDuplicate": False},
            "tags": [],
        }

        if self.image is not None:
            anki_note_dict["fields"].update({"image": self.image})

        if self.audio is not None:
            anki_note_dict["fields"].update({"audio": self.audio})

        return anki_note_dict


class NoteType(Enum):
    BASIC = "basic"
    ADVANCED = "advanced"


class NoteTypeFields:
    _fields = {
        NoteType.BASIC: ["front", "back"],
        NoteType.ADVANCED: ["front", "back", "audio"],
    }

    @classmethod
    def get_fields(cls, card_type: NoteType) -> List[str]:
        return cls._fields[card_type]
