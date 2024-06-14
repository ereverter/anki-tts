import json
from pathlib import Path

import pytest
import requests_mock
from tqdm import tqdm

from manki.anki.connection import AnkiConnection
from manki.anki.port import AnkiImporterExporter


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
                    "fields": {
                        "Front": {"value": "Front1"},
                        "Back": {"value": "Back1"},
                    }
                },
                {
                    "fields": {
                        "Front": {"value": "Front2"},
                        "Back": {"value": "Back2"},
                    }
                },
            ],
            "error": None,
        },
    )


@pytest.fixture
def mock_add_notes_response(requests_mocker):
    requests_mocker.post(
        "http://localhost:8765",
        additional_matcher=lambda request: json.loads(request.text)["action"]
        == "findNotes",
        json={"result": [1, 2, 3], "error": None},
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
                "Front1\tBack1\n",
                "Front2\tBack2\n",
            ]

    def test_add_anki_notes(self):
        pass

    def test_update_anki_notes(self):
        pass
