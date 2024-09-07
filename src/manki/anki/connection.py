"""
Script to create the Anki connection.
"""

import json
import os

import requests
from dotenv import load_dotenv

from ..utils import setup_logger

# Configure logging
logger = setup_logger(name=__name__)

# Load environment variables
load_dotenv()
ANKI_CONNECT_URL = os.getenv("ANKI_CONNECT_URL")
ANKI_API_VERSION = int(os.getenv("API_VERSION"))
ANKI_API_KEY = os.getenv("ANKI_API_KEY")


class AnkiConnection:
    """
    Class to manage the connection and interactions with Anki through AnkiConnect.

    AnkiConnect is a plugin that allows external applications to communicate with Anki using a JSON-based API.
    This class simplifies the process of sending requests to AnkiConnect and handling responses.

    Attributes:
        url (str): The URL where AnkiConnect is hosted, typically 'http://localhost:8765'.
        api_version (int): The version of the AnkiConnect API being used.

    Methods:
        __call__(action, **params): Shortcut to invoke an AnkiConnect action.
        list_decks(): Retrieves a list of all deck names in the Anki collection.
        request(action, **params): Constructs a request dictionary for AnkiConnect.
        invoke(action, **params): Sends a request to AnkiConnect and handles the response.
    """

    def __init__(
        self, url=ANKI_CONNECT_URL, api_version=ANKI_API_VERSION, api_key=ANKI_API_KEY
    ):
        self.url = url
        self.api_version = api_version
        self.api_key = api_key

    def __call__(self, action, **params):
        return self.invoke(action, **params)

    def list_decks(self):
        return self.invoke("deckNames")

    def request(self, action, **params):
        return {
            "action": action,
            "params": params,
            "version": self.api_version,
            "key": self.api_key,
        }

    def invoke(self, action, **params):
        requestJson = json.dumps(self.request(action, **params)).encode("utf-8")
        try:
            response = requests.post(self.url, requestJson, timeout=60).json()
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

        if "error" in response and response["error"]:
            logger.error(f"Anki connection error: {response['error']}")
            raise Exception(response["error"])
        return response.get("result", {})
