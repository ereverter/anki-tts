"""
Script to integrate text to audio using Google TTS with Anki or export Anki decks.
"""

import argparse
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from src.anki.connection import AnkiConnection
from src.anki.port import AnkiImporterExporter
from src.tts.audio import AudioGenerator
from src.utils import setup_logger

# Setup logging
logger = setup_logger(name=__name__)

# Load environment variables
load_dotenv()
ANKI_CONNECT_URL = os.getenv("ANKI_CONNECT_URL")
API_VERSION = int(os.getenv("API_VERSION", "default_version_number"))
EXPORT_OUTPUT_FOLDER = os.getenv("EXPORT_OUTPUT_FOLDER")
IMPORT_OUTPUT_FOLDER = os.getenv("IMPORT_OUTPUT_FOLDER")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE")
ANKI_MEDIA_FOLDER = os.getenv("ANKI_MEDIA_FOLDER")


# Export deck
def process_anki_export(args):
    output_file = os.path.join(args.export_folder, f"deck_{args.deck}.txt")
    anki_port = AnkiImporterExporter(
        AnkiConnection(args.anki_connect_url, args.api_version)
    )
    logger.info(f"Current decks: {anki_port.anki_connection.list_decks()}")
    logger.info(f"Card types: {anki_port.anki_connection('modelNames')}")
    anki_port.export_to_txt(args.deck, Path(output_file))


# Generate audio files
def process_audio_generation(args):
    audio_generator = AudioGenerator(
        args.lang, args.media_folder, args.replace_duplicates
    )
    import_file = os.path.join(
        args.import_folder, f"{Path(args.file).stem}_anki_import.txt"
    )

    if args.input_type == "txt":
        # Process as a text file
        audio_generator.generate_audio_files_from_text(args.file, import_file)
    elif args.input_type == "csv":
        # Process as a DataFrame
        df = pd.read_csv(args.file)
        text_column = "french"  # Adjust this to the name of your text column
        audio_generator.generate_from_dataframe(df, text_column, import_file)


# Import deck
def process_anki_import(args):
    anki_port = AnkiImporterExporter(
        AnkiConnection(args.anki_connect_url, args.api_version)
    )
    if args.update_notes:
        anki_port.import_and_update_notes(args.file, args.deck)
    else:
        card_types = anki_port.load_card_types("card_types.json")

        anki_port._add_new_notes(
            args.file,
            args.deck,
            args.card_type,
            card_types[args.card_type.lower()]["fields"],
        )


def main():
    parser = argparse.ArgumentParser(
        description="Integrate text to audio using Google TTS with Anki or export Anki decks."
    )
    subparsers = parser.add_subparsers(
        title="commands", dest="command", help="Available commands"
    )

    # AnkiConnect parser
    parser.add_argument(
        "-a",
        "--anki-connect-url",
        default=ANKI_CONNECT_URL,
        help="The URL for AnkiConnect (default: config.ANKI_CONNECT_URL).",
    )
    parser.add_argument(
        "-v",
        "--api-version",
        default=API_VERSION,
        help="The API version for AnkiConnect (default: config.API_VERSION).",
    )

    # Subparser for Anki export
    parser_export = subparsers.add_parser(
        "export", help="Export Anki deck to a text file."
    )
    parser_export.add_argument(
        "-d", "--deck", required=True, help="The name of the deck to export."
    )
    parser_export.add_argument(
        "-e",
        "--export_folder",
        default=Path(EXPORT_OUTPUT_FOLDER),
        help="The output folder for the exported Anki file (default: config.EXPORT_OUTPUT_FOLDER).",
    )

    # Subparser for audio generation
    parser_generate = subparsers.add_parser(
        "generate", help="Generate audio files from a text file."
    )
    parser_generate.add_argument(
        "-f", "--file", required=True, help="The path to the input text file."
    )
    parser_generate.add_argument(
        "-t",
        "--input_type",
        choices=["txt", "csv"],
        default="txt",
        help="The type of the input file ('txt' for plain text file, 'csv' for CSV file).",
    )
    parser_generate.add_argument(
        "-l",
        "--lang",
        default=DEFAULT_LANGUAGE,
        help="The language code for TTS (default: config.DEFAULT_LANGUAGE).",
    )
    parser_generate.add_argument(
        "-m",
        "--media_folder",
        default=ANKI_MEDIA_FOLDER,
        help="The output folder for mp3 files (default: config.ANKI_MEDIA_FOLDER).",
    )
    parser_generate.add_argument(
        "-i",
        "--import_folder",
        default=(IMPORT_OUTPUT_FOLDER),
        help="The output folder for mp3 files and Anki import file (default: config.IMPORT_OUTPUT_FOLDER).",
    )
    parser_generate.add_argument(
        "-r",
        "--replace_duplicates",
        action="store_true",
        help="Replace existing audio files with the same name.",
    )

    # Subparser for Anki import
    parser_import = subparsers.add_parser(
        "import",
        help="Generate audio files, create Anki import file, and import to Anki.",
    )
    parser_import.add_argument(
        "-f", "--file", required=True, help="The path to the input text file."
    )
    parser_import.add_argument(
        "-d", "--deck", required=True, help="The name of the Anki deck to import to."
    )
    parser_import.add_argument(
        "-c", "--card_type", default="Advanced", help="The card type to use."
    )
    parser_import.add_argument(
        "-u",
        "--update_notes",
        action="store_true",
        help="Update existing notes in Anki.",
    )

    args = parser.parse_args()

    if args.command == "generate":
        process_audio_generation(args)
    elif args.command == "import":
        process_anki_import(args)
    elif args.command == "export":
        process_anki_export(args)


if __name__ == "__main__":
    main()
