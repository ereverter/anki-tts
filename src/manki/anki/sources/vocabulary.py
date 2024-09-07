import json
from typing import Dict, List

from manki.anki.domain import AnkiNote
from manki.anki.sources.domain import AnkiFileParser


class VocabularyAnkiFileParser(AnkiFileParser):
    def __init__(self, deck_name: str = "Vocabulary", model_name: str = "Basic"):
        self.deck_name = deck_name
        self.model_name = model_name

    def parse(
        self, files: List[str], source_lang: str, target_lang: str
    ) -> List[AnkiNote]:
        anki_notes = []
        for file_path in files:
            try:
                data = self._read_file(file_path)
                anki_notes.extend(
                    self._create_anki_notes(data, source_lang, target_lang)
                )
            except ValueError as e:
                print(f"Error parsing '{file_path}': {e}")
        return anki_notes

    def _read_file(self, file_path: str) -> Dict[str, List[Dict[str, str]]]:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _create_anki_notes(
        self, data: Dict[str, List[Dict]], source_lang: str, target_lang: str
    ) -> List[AnkiNote]:
        notes = []

        for word, definitions in data.items():
            for definition in definitions:
                part_of_speech = definition["part_of_speech"]
                translations = definition["translations"]

                if source_lang in translations and target_lang in translations:
                    source_word = translations.get(source_lang, None) or word
                    target_word = translations.get(target_lang, None) or word

                    front = f"{source_word} ({part_of_speech})"
                    back = f"{target_word}"

                    note = self._create_anki_note(
                        front, back, [source_lang, target_lang]
                    )
                    notes.append(note)

        return notes

    def _create_anki_note(self, front: str, back: str, tags: List[str]) -> AnkiNote:
        return AnkiNote(
            deckName=self.deck_name,
            modelName=self.model_name,
            front=front,
            back=back,
            tags=tags,
        )
