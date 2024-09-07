import csv
import os
from pathlib import Path
from typing import Dict, List, Optional

from tqdm import tqdm

from manki.utils import normalize_text, setup_logger

from .connection import AnkiConnection
from .domain import AnkiNote, NoteType, NoteTypeFields

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
        export_to_txt(deck_name, output_file): Export flashcards from a specified Anki deck to a text file.
        import_and_update_notes(input_file, deck_name, model_name): Import flashcards from a file into Anki and update existing notes.
        add_anki_notes(anki_notes): Add new flashcards to Anki.
        update_anki_notes(anki_notes, reference_fields, changing_fields): Update existing flashcards in Anki.
    """

    def __init__(self, anki_connection: Optional[AnkiConnection] = None) -> None:
        if anki_connection is None:
            self.anki_connection = AnkiConnection()
        else:
            self.anki_connection = anki_connection

    # export
    def export_to_txt(self, deck_name: str, output_file: str) -> None:
        notes = self._fetch_all_notes(deck_name)
        output_file = Path(output_file)

        logger.info(f"Exporting {len(notes)} notes to {output_file}")

        output_folder = output_file.parent
        if not output_folder.exists():
            output_folder.mkdir(parents=True)

        if not str(output_file).endswith(".txt"):
            raise Exception("Can only export to .txt")

        with open(output_file, "w", encoding="utf-8") as file:
            for note in tqdm(notes, total=len(notes), desc="Exporting notes"):
                fields = note["fields"]
                line_elements = [fields[field]["value"] for field in fields]
                line = "\t".join(line_elements) + "\n"
                file.write(line)

    def _fetch_all_notes(self, deck_name: str):
        note_ids = self.anki_connection("findNotes", query=f"deck:{deck_name}")
        notes = self.anki_connection("notesInfo", notes=note_ids)

        return notes

    # import
    def import_and_update_notes(
        self,
        input_file: str,
        anki_notes: Optional[List[AnkiNote]],
        deck_name: str,
        model_name: str = "basic",
        reference_fields: Optional[List[str]] = ["front", "back"],
        changing_fields: Optional[List[str]] = None,
        allow_duplicates: bool = False,
    ) -> None:
        self._if_not_exists_create_deck(deck_name)

        note_type = NoteType(model_name)
        note_fields = NoteTypeFields.get_fields(note_type)

        if input_file.endswith(".csv"):
            anki_notes = self._get_anki_notes_from_csv(input_file, deck_name, note_type)
        elif not anki_notes:
            raise Exception("Only .csv files or AnkiNotes objects are supported.")

        new_notes = self.update_anki_notes(
            anki_notes, reference_fields, changing_fields
        )
        self.add_anki_notes(new_notes, allow_duplicates)

    ## add
    def add_anki_notes(
        self, anki_notes: List[AnkiNote], allow_duplicates: bool = False
    ) -> None:
        anki_notes_dict = [note.to_anki_dict(allow_duplicates) for note in anki_notes]
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

    ## update
    def update_anki_notes(
        self,
        anki_notes: List[AnkiNote],
        reference_fields: Optional[List[str]] = ["front", "back"],
        changing_fields: Optional[List[str]] = None,
    ) -> List[AnkiNote]:
        updated_count = 0
        deck_name = anki_notes[0].deckName

        new_notes = []
        for anki_note in tqdm(anki_notes, desc="Updating notes"):
            matching_notes = self._find_notes_like(anki_note, reference_fields)
            if matching_notes:
                note_id = matching_notes[0]
                existing_note = self._get_note(note_id, deck_name)

                if self._update_note(
                    new_note=anki_note,
                    existing_note=existing_note,
                    changing_fields=changing_fields,
                ):
                    updated_count += 1

            else:
                new_notes.append(anki_note)

        logger.info(f"{updated_count} notes updated")
        return new_notes

    def _update_note(
        self,
        new_note: AnkiNote,
        existing_note: AnkiNote,
        changing_fields: Optional[List[str]] = None,
    ) -> bool:
        if changing_fields is None:
            return

        changes_detected = False
        for field in changing_fields:
            new_value = getattr(new_note, field)
            existing_value = getattr(existing_note, field)

            if new_value != existing_value:
                setattr(existing_note, field, new_value)
                changes_detected = True

        updated_fields = existing_note.to_anki_dict()
        if changes_detected:
            updated_note = {"id": existing_note.id, **updated_fields}
            self.anki_connection("updateNoteFields", note=updated_note)
            return True

        return False

    # utils
    def _find_notes_like(
        self, note: AnkiNote, reference_fields: List[str] = ["front", "back"]
    ) -> List[int]:
        filters = []
        for field in reference_fields:
            field_value = normalize_text(getattr(note, field)).replace("\\", "\\\\")
            filters.append(f'{field}:"{field_value}"')

        field_filter = " ".join(filters)
        query = f'deck:"{note.deckName}" {field_filter}'
        return self.anki_connection("findNotes", query=query)

    def _get_note(self, note_id: int, deck_name: str) -> AnkiNote:
        notes = self.anki_connection("notesInfo", notes=[note_id])
        if not notes:
            return None

        note_info = notes[0]
        fields = note_info["fields"]
        return AnkiNote(
            deckName=deck_name,
            modelName=note_info["modelName"],
            front=fields["front"]["value"],
            back=fields["back"]["value"],
            audio=fields.get("audio", {}).get("value", None),
            image=fields.get("image", {}).get("value", None),
            tags=note_info.get("tags", []),
            id=note_id,
        )

    def _if_not_exists_create_deck(self, deck_name: str) -> None:
        existing_decks = self.anki_connection("deckNames")

        if deck_name not in existing_decks:
            logger.info(f"Deck '{deck_name}' does not exist. Creating it...")
            deck_id = self.anki_connection("createDeck", deck=deck_name)
            if deck_id:
                logger.info(
                    f"Deck '{deck_name}' created successfully with ID {deck_id}."
                )
            else:
                raise Exception(f"Failed to create deck '{deck_name}'.")
        else:
            logger.info(f"Deck '{deck_name}' already exists.")
