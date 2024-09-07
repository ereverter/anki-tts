import json
from pathlib import Path

import pytest
import requests_mock
from tqdm import tqdm

from manki.anki.connection import AnkiConnection
from manki.anki.domain import AnkiNote
from manki.anki.xport import AnkiImporterExporter


@pytest.fixture(scope="session")
def anki_connection():
    return AnkiConnection(url="http://localhost:8765", api_version=6, api_key="apikey")


@pytest.fixture(scope="session")
def anki_importer_exporter(anki_connection):
    return AnkiImporterExporter(anki_connection)


@pytest.fixture
def requests_mocker():
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def mock_find_notes_response(requests_mocker):
    requests_mocker.post(
        "http://localhost:8765",
        additional_matcher=lambda request: json.loads(request.text)["action"]
        == "findNotes",
        json={"result": [1, 2, 3], "error": None},
    )


@pytest.fixture
def mock_notes_info_response(requests_mocker):
    requests_mocker.post(
        "http://localhost:8765",
        additional_matcher=lambda request: json.loads(request.text)["action"]
        == "notesInfo",
        json={
            "result": [
                {
                    "noteID": 1,
                    "modelName": "Basic",
                    "tags": ["tag1"],
                    "fields": {
                        "Front": {"value": "front1"},
                        "Back": {"value": "back1"},
                    },
                },
                {
                    "noteID": 2,
                    "modelName": "Basic",
                    "tags": ["tag1"],
                    "fields": {
                        "Front": {"value": "front2"},
                        "Back": {"value": "back2"},
                    },
                },
            ],
            "error": None,
        },
    )


@pytest.fixture
def mock_add_notes_response(requests_mocker):
    requests_mocker.post(
        "http://localhost:8765",
        json={"result": None, "error": None},
        additional_matcher=lambda request: json.loads(request.text)["action"]
        == "addNotes",
    )


@pytest.fixture
def mock_update_notes_response(requests_mocker):
    requests_mocker.post(
        "http://localhost:8765",
        json={"result": None, "error": None},
        additional_matcher=lambda request: json.loads(request.text)["action"]
        == "updateNoteFields",
    )


class TestAnkiImporterExporter:
    def test_export_to_txt(
        self,
        anki_importer_exporter,
        tmp_path,
        mock_find_notes_response,
        mock_notes_info_response,
    ):
        # arrange
        deck_name = "current"
        output_file = tmp_path / "output.txt"

        # act
        anki_importer_exporter.export_to_txt(deck_name, str(output_file))

        # assert
        assert output_file.exists()
        with open(output_file, "r", encoding="utf-8") as file:
            content = file.readlines()
            assert content == [
                "front1\tback1\n",
                "front2\tback2\n",
            ]

    def test_add_anki_notes(self, anki_importer_exporter, mock_add_notes_response):
        # arrange
        anki_notes = self._create_anki_notes()

        # act
        anki_importer_exporter.add_anki_notes(anki_notes)

        # assert
        assert len(anki_notes) == 2

    def test_update_anki_notes(
        self,
        anki_importer_exporter,
        mock_find_notes_response,
        mock_notes_info_response,
        mock_update_notes_response,
    ):
        # arrange
        anki_notes = self._create_anki_notes()

        # act
        updated_count = anki_importer_exporter.update_anki_notes(
            anki_notes, reference_fields=["front"], changing_fields=["back"]
        )

        # assert
        assert updated_count == 1

    def _create_anki_notes(self):
        return [
            AnkiNote(
                deckName="current",
                modelName="Base",
                front="front1",
                back="back1",
                tags=["tag1"],
            ),
            AnkiNote(
                deckName="current",
                modelName="Base",
                front="front2",
                back="back2",
                tags=["tag1"],
            ),
        ]
