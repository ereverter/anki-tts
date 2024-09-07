import json
from pathlib import Path

import pytest

from manki.anki.sources import VocabularyAnkiFileParser


class TestVocabularyAnkiFileParser:
    @pytest.fixture
    def parser(self):
        return VocabularyAnkiFileParser(deck_name="Vocabulary", model_name="Basic")

    def test_parse_valid_vocabulary_file(self, parser, samples_path, snapshot):
        # arrange
        vocab_file_path = Path(samples_path) / "translations.json"
        source_lang = "fr"
        target_lang = "ca"

        # act
        result = parser.parse([str(vocab_file_path)], source_lang, target_lang)

        # assert
        assert len(result) > 0

        serialized_result = [
            {
                "deckName": note.deckName,
                "modelName": note.modelName,
                "front": note.front,
                "back": note.back,
                "tags": note.tags,
            }
            for note in result
        ]

        snapshot.assert_match(
            json.dumps(serialized_result, indent=4),
            "vocab_file_snapshot",
        )

    def test_malformed_vocabulary_file(self, parser, samples_path, snapshot):
        # arrange
        malformed_file_path = Path(samples_path) / "malformed_translations.json"
        source_lang = "fr"
        target_lang = "ca"

        # act
        result = parser.parse([str(malformed_file_path)], source_lang, target_lang)

        # assert
        assert len(result) == 0

        snapshot.assert_match(
            json.dumps(result, indent=4),
            "malformed_vocab_file_snapshot",
        )
