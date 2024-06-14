from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel


class AnkiNote(BaseModel):
    deckName: str
    modelName: str
    tags: Optional[List[str]] = []
    front: str
    back: str
    audio: Optional[Dict[str, str]] = None
    image: Optional[Dict[str, str]] = None
    video: Optional[Dict[str, str]] = None
    do_write: Optional[bool] = False
    id: Optional[int] = None

    def to_anki_dict(self) -> Dict:
        anki_note_dict = {
            "deckName": self.deckName,
            "modelName": self.modelName,
            "tags": [],
            "fields": {
                "front": self.front,
                "back": self.back,
            },
            "audio": self.audio,
            "image": self.image,
            "video": self.video,
            "options": {"allowDuplicate": False},
        }

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
