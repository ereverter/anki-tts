"""
Script to import and export data from Anki.
"""

import csv
import json
from typing import Dict, List

from tqdm import tqdm

from ..utils import setup_logger
from .connection import AnkiConnection
from .domain import AnkiNote, NoteType, NoteTypeFields

# Configure logging
logger = setup_logger(name=__name__)


class AnkiImporterExporter:
    """
    A class to facilitate the import and export of Anki flashcards using the AnkiConnect API.

    This class provides methods to export Anki flashcards to a text file and import flashcards from a file into Anki,
    while handling different card types. It interacts with Anki through AnkiConnect, allowing the automation of flashcard
    management tasks.

    Attributes:
        anki_connection (AnkiConnection): An instance of the AnkiConnection class to interact with AnkiConnect.

    Methods:
        load_card_types(json_file_path): Load card type configurations from a JSON file.
        export_to_txt(deck_name, output_file): Export flashcards from a specified Anki deck to a text file.
        import_and_update_notes(input_file, deck_name, model_name): Import flashcards from a file into Anki and update existing notes.
        _add_new_notes(input_file, deck_name, model_name): Add new flashcards to Anki from a file. Fast and efficient.
        _update_existing_notes(input_file, deck_name): Update existing flashcards in Anki from a file. Slow and inefficient.
        _build_note(deck_name, model_name, front, back, audio_path): Helper method to construct a flashcard note.
        _update_note_audio(note_id, audio_path): Helper method to update the audio path of a flashcard note.
    """

    def __init__(self, anki_connection: AnkiConnection = None) -> None:
        if anki_connection is None:
            self.anki_connection = AnkiConnection()
        else:
            self.anki_connection = anki_connection

    # Export
    def export_to_txt(self, deck_name: str, output_file: str) -> None:
        note_ids = self.anki_connection("findNotes", query=f"deck:{deck_name}")
        notes = self.anki_connection("notesInfo", notes=note_ids)

        logger.info(f"Exporting {len(notes)} notes to {output_file}")

        output_folder = output_file.parent
        if not output_folder.exists():
            output_folder.mkdir(parents=True)

        with open(output_file, "w", encoding="utf-8") as file:
            for note in tqdm(notes, total=len(notes), desc="Exporting notes"):
                fields = note["fields"]
                line_elements = [fields[field]["value"] for field in fields]
                line = "\t".join(line_elements) + "\n"
                file.write(line)

    # Import
    def import_and_update_notes(
        self, input_file: str, deck_name: str, model_name: str = "Base"
    ) -> None:
        note_type = NoteType(model_name)
        note_fields = NoteTypeFields.get_fields(note_type)

        if input_file.endswith(".csv"):
            anki_notes = self._get_anki_notes_from_csv(input_file, deck_name, note_type)
        else:
            raise Exception("Only .csv input files are accepted")

        self._update_anki_notes(anki_notes)
        self._add_anki_notes(anki_notes)

    def _add_anki_notes(self, anki_notes: List[AnkiNote]) -> None:
        anki_notes_dict = [note.to_anki_dict() for note in anki_notes]
        self.anki_connection("addNotes", notes=anki_notes_dict)
        logger.info(f"{len(anki_notes_dict)} new notes added")

    def _get_anki_notes_from_csv(
        self, input_file: str, deck_name: str, note_type: NoteType
    ) -> List[AnkiNote]:
        logger.info(f"Fetching notes from {input_file}")

        fields = NoteTypeFields.get_fields(note_type)

        anki_notes = []
        with open(input_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file, fieldnames=fields)
            for row in tqdm(reader, desc="Adding new notes"):
                note_data = {field: row[field] for field in fields if field in row}
                anki_note = AnkiNote(
                    deckName=deck_name, modelName=note_type.value, **note_data
                )

                anki_notes.append(anki_note)

        return anki_notes

    def _build_query_find_note(self, anki_note: AnkiNote) -> str:
        query_components = [
            f'{field}:"{getattr(anki_note, field)}"'
            for field in anki_note.__fields__.keys()
            if getattr(anki_note, field) and field not in {"audio", "image", "do_write"}
        ]
        return f"deck:{anki_note.deckName} " + " ".join(query_components)

    def _fetch_note_ids(self, query: str) -> List[int]:
        return self.anki_connection("findNotes", query=query)

    def _fetch_existing_note(self, note_id: int) -> Dict:
        notes = self.anki_connection("notesInfo", notes=[note_id])
        return notes[0] if notes else {}

    def _check_for_changes(self, anki_note: AnkiNote, existing_note: Dict) -> bool:
        changes = False
        for field in existing_note["fields"]:
            new_value = getattr(anki_note, field, None)
            if (
                new_value is not None
                and new_value != existing_note["fields"][field]["value"]
            ):
                changes = True
                break
        return changes

    def _prepare_updated_fields(self, anki_note: AnkiNote, existing_note: Dict) -> Dict:
        updated_fields = {}
        for field in existing_note["fields"]:
            updated_fields[field] = getattr(
                anki_note, field, existing_note["fields"][field]["value"]
            )

        if anki_note.audio:
            updated_fields["audio"] = anki_note.audio
        if anki_note.image:
            updated_fields["image"] = anki_note.image
        return updated_fields

    def _update_anki_notes(self, anki_notes: List[AnkiNoteModel]) -> None:
        updated_count = 0

        for anki_note in tqdm(anki_notes, desc="Updating notes"):
            query = self._build_query(anki_note)
            note_ids = self._fetch_note_ids(query)

            if note_ids:
                note_id = note_ids[0]
                existing_note = self._fetch_existing_note(note_id)

                changes = self._check_for_changes(anki_note, existing_note)

                if changes or anki_note.do_write:
                    updated_fields = self._prepare_updated_fields(
                        anki_note, existing_note
                    )
                    updated_note = {"id": note_id, "fields": updated_fields}
                    self.anki_connection("updateNoteFields", note=updated_note)
                    updated_count += 1

        logger.info(f"{updated_count} notes updated")
