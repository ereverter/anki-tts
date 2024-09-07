import json
from unittest.mock import Mock, patch

import pytest

from manki.anki.xport import AnkiConnection


@pytest.fixture(scope="session")
def anki_connection():
    return AnkiConnection(url="http://localhost:8765", api_version=6, api_key="apikey")


class TestAnkiConnection:
    @patch("requests.post")
    def test_invoke_success(self, mock_post, anki_connection):
        # arrange
        mock_response = Mock()
        mock_response.json.return_value = {"result": ["Default"], "error": None}
        mock_post.return_value = mock_response

        # act
        result = anki_connection.invoke("deckNames")
        call_args, _ = mock_post.call_args
        request_url, request_data = call_args
        request_json = json.loads(request_data)

        # assert
        assert result == ["Default"]
        mock_post.assert_called_once()
        assert request_url == "http://localhost:8765"
        assert request_json["action"] == "deckNames"
        assert request_json["params"] == {}
        assert request_json["version"] == 6
        assert request_json["key"] == "apikey"
