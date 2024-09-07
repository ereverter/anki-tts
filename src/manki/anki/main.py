import argparse
import random
from pathlib import Path

from manki.anki.connection import AnkiConnection
from manki.anki.sources import MarkdownAnkiFileParser, VocabularyAnkiFileParser
from manki.anki.xport import AnkiImporterExporter


def parse_args():
    parser = argparse.ArgumentParser(
        description="Parse and import flashcards into an Anki deck."
    )
    parser.add_argument(
        "input_path",
        help="Path to the input file or directory.",
    )
    parser.add_argument(
        "deck_name", help="Name of the Anki deck to import the cards into."
    )
    parser.add_argument(
        "--source-lang",
        help="Iff vocabulary, source language for vocabulary (e.g., 'fr').",
        choices=["en", "es", "fr", "ca"],
        default=None,
    )
    parser.add_argument(
        "--target-lang",
        help="Iff vocabulary, target language for vocabulary (e.g., 'ca').",
        choices=["en", "es", "fr", "ca"],
        default=None,
    )
    parser.add_argument(
        "--model-name",
        help="Name of the Anki model.",
        default="basic",
    )
    parser.add_argument(
        "--reference-fields",
        nargs="+",
        help="Fields to use as reference.",
        default=["front", "back"],
    )
    parser.add_argument(
        "--changing-fields",
        nargs="+",
        help="Fields to update in existing notes.",
        default=None,
    )
    return parser.parse_args()


def main():
    args = parse_args()

    input_path = Path(args.input_path)
    deck_name = args.deck_name
    model_name = args.model_name
    source_lang = args.source_lang
    target_lang = args.target_lang
    reference_fields = args.reference_fields
    changing_fields = args.changing_fields

    anki_connection = AnkiConnection()
    importer_exporter = AnkiImporterExporter(anki_connection=anki_connection)

    anki_notes = []

    if input_path.is_dir():
        print(f"Processing markdown files in directory: {input_path}")
        parser = MarkdownAnkiFileParser(deck_name=deck_name, model_name=model_name)

        files_to_parse = []
        for md_file in input_path.glob("*.md"):
            files_to_parse.append(str(md_file))
        anki_notes.extend(parser.parse(files_to_parse))

    elif input_path.is_file():
        if input_path.suffix == ".md":
            print(f"Parsing markdown file: {input_path}")
            parser = MarkdownAnkiFileParser(deck_name=deck_name, model_name=model_name)
            anki_notes = parser.parse([str(input_path)])

        elif input_path.suffix == ".json" and source_lang and target_lang:
            print(f"Parsing vocabulary file: {input_path}")
            parser = VocabularyAnkiFileParser(
                deck_name=deck_name, model_name=model_name
            )
            anki_notes = parser.parse([str(input_path)], source_lang, target_lang)

        else:
            raise ValueError(
                "Invalid file format or missing source/target language for vocabulary files."
            )
    else:
        raise ValueError("The provided path is neither a file nor a directory.")

    print(f"Updating and adding notes in deck '{deck_name}'...")
    random.shuffle(anki_notes)
    importer_exporter.import_and_update_notes(
        input_file="",
        anki_notes=anki_notes,
        deck_name=deck_name,
        model_name=model_name,
        reference_fields=reference_fields,
        changing_fields=changing_fields,
        allow_duplicates=False,
    )


if __name__ == "__main__":
    main()
