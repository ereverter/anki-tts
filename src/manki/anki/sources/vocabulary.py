import json
from collections import defaultdict
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
        source_word_occurrences = self._track_source_word_occurrences(data, source_lang)

        for word, definitions in data.items():
            for definition in definitions:
                part_of_speech = definition["part_of_speech"]
                translations = definition["translations"]

                source_word = translations.get(source_lang, word)
                target_word = translations.get(target_lang, word)

                source_word = self._disambiguate_source_word(
                    source_word,
                    part_of_speech,
                    word,
                    source_word_occurrences,
                )

                front = f"{source_word} ({part_of_speech})"
                back = f"{target_word}"

                note = self._create_anki_note(front, back, [source_lang, target_lang])
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

    def _track_source_word_occurrences(
        self, data: Dict[str, List[Dict]], source_lang: str
    ) -> Dict[str, List[Dict[str, str]]]:
        occurrences = defaultdict(list)

        for word, definitions in data.items():
            for definition in definitions:
                part_of_speech = definition["part_of_speech"]
                translations = definition["translations"]

                source_word = translations.get(source_lang, None) or word
                occurrences[(source_word, part_of_speech)].append(word)

        return occurrences

    def _disambiguate_source_word(
        self,
        source_word: str,
        part_of_speech: str,
        english_word: str,
        source_word_occurrences: Dict[str, List[Dict[str, str]]],
    ) -> str:
        key = (source_word, part_of_speech)
        if len(source_word_occurrences[key]) > 1:
            source_word = f"{source_word} [{english_word}]"

        return source_word
