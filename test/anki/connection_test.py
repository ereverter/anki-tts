import json
from unittest.mock import Mock, patch

import pytest

from manki.anki.port import AnkiConnection


@pytest.fixture
def anki_connection():
    return AnkiConnection(url="http://localhost:8765", api_version="6")


@patch("requests.post")
def test_invoke_success(mock_post, anki_connection):
    # Mock the response from requests.post
    mock_response = Mock()
    mock_response.json.return_value = {"result": ["Default"], "error": None}
    mock_post.return_value = mock_response

    result = anki_connection.invoke("deckNames")

    assert result == ["Default"]
    mock_post.assert_called_once_with(
        "http://localhost:8765",
        json.dumps({"action": "deckNames", "params": {}, "version": 6}).encode("utf-8"),
        timeout=10,
    )


@patch("requests.post")
def test_invoke_failure(mock_post, anki_connection):
    # Mock the response from requests.post
    mock_response = Mock()
    mock_response.json.return_value = {"result": None, "error": "An error occurred"}
    mock_post.return_value = mock_response

    with pytest.raises(Exception) as excinfo:
        anki_connection.invoke("deckNames")

    assert "An error occurred" in str(excinfo.value)
    mock_post.assert_called_once_with(
        "http://localhost:8765",
        json.dumps({"action": "deckNames", "params": {}, "version": 6}).encode("utf-8"),
        timeout=10,
    )


@patch("requests.post")
def test_list_decks(mock_post, anki_connection):
    # Mock the response from requests.post
    mock_response = Mock()
    mock_response.json.return_value = {"result": ["Default", "MyDeck"], "error": None}
    mock_post.return_value = mock_response

    result = anki_connection.list_decks()

    assert result == ["Default", "MyDeck"]
    mock_post.assert_called_once_with(
        "http://localhost:8765",
        json.dumps({"action": "deckNames", "params": {}, "version": 6}).encode("utf-8"),
        timeout=10,
    )
