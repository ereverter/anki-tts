# Anki TTS Integration and Deck Export

## Overview
This script facilitates the integration of text-to-speech (TTS) using Google's Text-to-Speech service with Anki flashcards and also provides functionality to export Anki decks. It is particularly useful for language learners who wish to add audio to their Anki cards or for those who need to export their Anki decks for backup or sharing purposes.

**Note**: The code is dirty and not well-organized. It was written for personal use and is not intended to be a polished, production-ready script. However, it is functional and can be used as a starting point for a more robust script.

## Features
- **Deck Export**: Export Anki decks to a text file to then generate audio files.
- **Text-to-Speech Integration**: Generate audio files from text using Google TTS and link them with Anki flashcards.
- **Deck Import**: Process input data from plain text files or CSV files and import them into Anki.

## Set up

Ensure you have the [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on installed.

Clone the repository:
```bash
git clone https://github.com/ereverter/anki-tts
```

Install the required Python packages:
```bash
pip install -r requirements.txt
```

## Configuration
Set up the necessary environment variables in a `.env` file or your environment:
- `ANKI_CONNECT_URL`: The URL for AnkiConnect (default: `http://localhost:8765`).
- `API_VERSION`: The API version for AnkiConnect.
- `EXPORT_OUTPUT_FOLDER`: The output folder for exported Anki files.
- `IMPORT_OUTPUT_FOLDER`: The output folder for audio files and Anki import files.
- `DEFAULT_LANGUAGE`: The language code for TTS (e.g., `fr` for French).
- `ANKI_MEDIA_FOLDER`: The output folder for mp3 files. Should be the same as the Anki media folder.

## Usage

The script can be run from the command line with different subcommands.

To get help on the different subcommands:
```bash
python main.py -h
```

### Export Anki Deck
To get help on exporting decks:
```bash
python main.py export -h
```

To export a specific deck:
```bash
python main.py export --deck DECK_NAME \
    --export_folder FOLDER_PATH
```

### Generate Audio Files
To get help on generating audio files:
```bash
python main.py export -h
```

For text file input:
```bash
python main.py generate --file INPUT_FILE \
    --input_type txt \
    --lang LANGUAGE_CODE \
    --media_folder FOLDER_PATH \
    --import_folder FOLDER_PATH \
    --replace_duplicates
```

For CSV file input:
```bash
python main.py generate --file INPUT_FILE \
    --input_type csv \
    --lang LANGUAGE_CODE \
    --media_folder FOLDER_PATH \
    --import_folder FOLDER_PATH \
    --replace_duplicates
```

### Import to Anki
To get help on importing decks:
```bash
python main.py import -h
```

To import a deck to Anki:
```bash
python main.py import --file INPUT_FILE \
    --deck DECK_NAME \
    --card_type CARD_TYPE \
    --update_notes
```