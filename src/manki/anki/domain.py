from typing import Optional

from pydantic import BaseModel


class AnkiNote(BaseModel):
    front: str
    back: str
    do_write: bool = False
    audio: Optional[str] = None
    image: Optional[str] = None
