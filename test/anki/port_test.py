# """
# Script to import and export data from Anki.
# """
# from tqdm import tqdm
# import json
# from .connection_test import AnkiConnection
# from ..utils import setup_logger

# # Configure logging
# logger = setup_logger(name=__name__)


# class AnkiImporterExporter:
#     """
#     A class to facilitate the import and export of Anki flashcards using the AnkiConnect API.

#     This class provides methods to export Anki flashcards to a text file and import flashcards from a file into Anki,
#     while handling different card types. It interacts with Anki through AnkiConnect, allowing the automation of flashcard
#     management tasks.

#     Attributes:
#         anki_connection (AnkiConnection): An instance of the AnkiConnection class to interact with AnkiConnect.

#     Methods:
#         load_card_types(json_file_path): Load card type configurations from a JSON file.
#         export_to_txt(deck_name, output_file): Export flashcards from a specified Anki deck to a text file.
#         import_and_update_notes(input_file, deck_name, model_name): Import flashcards from a file into Anki and update existing notes.
#         _add_new_notes(input_file, deck_name, model_name): Add new flashcards to Anki from a file. Fast and efficient.
#         _update_existing_notes(input_file, deck_name): Update existing flashcards in Anki from a file. Slow and inefficient.
#         _build_note(deck_name, model_name, front, back, audio_path): Helper method to construct a flashcard note.
#         _update_note_audio(note_id, audio_path): Helper method to update the audio path of a flashcard note.
#     """

#     def __init__(self, anki_connection=None):
#         if anki_connection is None:
#             self.anki_connection = AnkiConnection()
#         else:
#             self.anki_connection = anki_connection

#     def load_card_types(self, json_file_path):
#         with open(json_file_path, "r") as file:
#             return json.load(file)

#     # Export
#     def export_to_txt(self, deck_name, output_file):
#         note_ids = self.anki_connection("findNotes", query=f"deck:{deck_name}")
#         notes = self.anki_connection("notesInfo", notes=note_ids)

#         logger.info(f"Exporting {len(notes)} notes to {output_file}")

#         # Check if the output folder exists
#         output_folder = output_file.parent
#         if not output_folder.exists():
#             output_folder.mkdir(parents=True)

#         with open(output_file, "w", encoding="utf-8") as file:
#             for note in tqdm(notes, total=len(notes), desc="Exporting notes"):
#                 fields = note["fields"]
#                 line_elements = [fields[field]["value"] for field in fields]
#                 line = "\t".join(line_elements) + "\n"
#                 file.write(line)

#     # Import
#     def import_and_update_notes(self, input_file, deck_name, model_name="Advanced"):
#         card_types = self.load_card_types("card_types.json")
#         self._update_existing_notes(
#             input_file, deck_name, card_types[model_name.lower()]["fields"]
#         )
#         self._add_new_notes(
#             input_file, deck_name, model_name, card_types[model_name.lower()]["fields"]
#         )

#     def _add_new_notes(self, input_file, deck_name, model_name, fields):
#         logger.info(f"Adding new notes to {deck_name} from {input_file}")
#         with open(input_file, "r", encoding="utf-8") as file:
#             lines = file.readlines()

#         new_notes = []
#         for line in tqdm(lines, total=len(lines), desc="Adding new notes"):
#             note_data = line.strip().split("\t")
#             note_fields = dict(zip(fields, note_data))

#             # Only build the new note without querying
#             new_note = self._build_note(deck_name, model_name, **note_fields)
#             new_notes.append(new_note)

#         # Add all new notes in one request
#         if new_notes:
#             self.anki_connection("addNotes", notes=new_notes)
#             logger.info(f"{len(new_notes)} new notes added to {deck_name}")

#     def _update_existing_notes(self, input_file, deck_name, fields):
#         logger.info(f"Updating {deck_name} with {input_file}")
#         with open(input_file, "r", encoding="utf-8") as file:
#             lines = file.readlines()

#         updated_count = 0
#         for line in tqdm(lines, total=len(lines), desc="Updating notes"):
#             note_data = line.strip().split("\t")
#             note_fields = dict(zip(fields, note_data))
#             query_components = [
#                 f'{field}:"{value}"'
#                 for field, value in note_fields.items()
#                 if value and field != "audio"
#             ]
#             query = f"deck:{deck_name} " + " ".join(query_components)
#             note_ids = self.anki_connection("findNotes", query=query)

#             if note_ids:
#                 self._update_note_fields(note_ids[0], **note_fields)
#                 updated_count += 1

#         logger.info(f"{updated_count} existing notes updated in {deck_name}")

#     def _build_note(self, deck_name, model_name, **fields):
#         return {
#             "deckName": deck_name,
#             "modelName": model_name,
#             "fields": fields,
#             "options": {"allowDuplicate": False},
#             "tags": [],
#         }

#     def _update_note_fields(self, note_id, **fields):
#         note = self.anki_connection("notesInfo", notes=[note_id])[0]
#         updated_fields = {
#             field: fields.get(field, note["fields"][field]["value"])
#             for field in note["fields"]
#         }
#         updated_note = {"id": note_id, "fields": updated_fields}
#         self.anki_connection("updateNoteFields", note=updated_note)
