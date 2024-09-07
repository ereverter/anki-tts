import json
from pathlib import Path

import pytest

from manki.anki.sources import MarkdownAnkiFileParser


class TestMarkdownAnkiFileParser:
    @pytest.fixture
    def parser(self):
        return MarkdownAnkiFileParser(deck_name="Default", model_name="Basic")

    def test_parse_valid_md_file(self, parser, samples_path, snapshot):
        # arrange
        sample_md_path = Path(samples_path) / "md.md"

        # act
        result = parser.parse([str(sample_md_path)])

        # assert
        assert len(result) == 1

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
            "md_file_snapshot",
        )

    def test_malformed_md_file(self, parser, samples_path, snapshot):
        # arrange
        malformed_file = Path(samples_path) / "malformed.md"

        # act
        result = parser.parse([str(malformed_file)])

        # assert
        assert len(result) == 0

        snapshot.assert_match(
            json.dumps(result, indent=4),
            "malformed_md_file_snapshot",
        )
