import json
from typing import List, Optional

from bs4 import BeautifulSoup
from pydantic import BaseModel


class WordEntry(BaseModel):
    word: str
    part_of_speech: List[str]
    pronunciation: Optional[str] = None
    definitions: List[str]
    translations: List[str]
    examples: Optional[List[str]] = None


class SimpleWordParser:
    def __init__(self, html_file_path: str):
        with open(html_file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            self.data = json.loads(soup.get_text(strip=True))

    def parse(self) -> List[WordEntry]:
        word_entries = []

        for entry in self.data:
            word = entry.get("text")
            part_of_speech = [entry.get("pos")]

            translations = [t.get("text") for t in entry.get("translations", [])]
            definitions = translations  # Treating translations as definitions

            examples = []
            for translation in entry.get("translations", []):
                for example in translation.get("examples", []):
                    examples.append(f"{example.get('src')} -> {example.get('dst')}")

            word_entry = WordEntry(
                word=word,
                part_of_speech=part_of_speech,
                definitions=definitions,
                translations=translations,
                examples=examples if examples else None,
            )
            word_entries.append(word_entry)

        return word_entries
