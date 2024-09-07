import re
from typing import List

from manki.anki.domain import AnkiNote
from manki.anki.sources.domain import AnkiFileParser


class MarkdownAnkiFileParser(AnkiFileParser):
    def __init__(self, deck_name: str = "Default", model_name: str = "Basic"):
        self.deck_name = deck_name
        self.model_name = model_name

    def parse(self, files: List[str]) -> List[AnkiNote]:
        anki_notes = []
        for file_path in files:
            try:
                content = self._read_file(file_path)
                labels = self._extract_labels(content)
                front = self._extract_content(content, "front")
                back = self._extract_content(content, "back")
                anki_notes.append(self._create_anki_note(front, back, labels))
            except ValueError as e:
                print(f"Error parsing '{file_path}': {e}")
        return anki_notes

    def _read_file(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _extract_labels(self, content: str) -> List[str]:
        labels = re.findall(r"#(\w+)", content)
        if not labels:
            raise ValueError("No labels (tags) found in the file.")
        return labels

    def _extract_content(self, content: str, label: str) -> str:
        match = re.search(
            rf"(?i)^###\s*{label}\n(.+?)(?=^###|\Z)", content, re.DOTALL | re.MULTILINE
        )
        if not match:
            raise ValueError(f"'{label}' content not found.")
        return match.group(1).strip()

    def _create_anki_note(self, front: str, back: str, tags: List[str]) -> AnkiNote:
        return AnkiNote(
            deckName=self.deck_name,
            modelName=self.model_name,
            front=front,
            back=back,
            tags=tags,
        )
