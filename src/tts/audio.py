"""
Script for generating audio files from text using Google Text-to-Speech (gTTS).
"""
import os
import re
from gtts import gTTS
from tqdm import tqdm
from dotenv import load_dotenv
from pathlib import Path
from ..utils import setup_logger

# Configure logging
logger = setup_logger(name=__name__)

# Load environment variables
load_dotenv()
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE")
ANKI_MEDIA_FOLDER = os.getenv("ANKI_MEDIA_FOLDER")


class AudioGenerator:
    """
    A class that generates audio files from given text using Google's Text-to-Speech (gTTS) service.

    This class is particularly useful for creating language learning materials, such as generating pronunciations
    for words or phrases in a foreign language. It can also automatically generate an import file for Anki, a popular
    spaced repetition software, linking the text to its corresponding audio file.

    Attributes:
        lang (str): The language in which the text is to be spoken, e.g., 'en' for English, 'fr' for French.
        anki_media_folder (str): Path to the Anki media folder where audio files will be stored.
        replace_duplicates (bool): If True, existing audio files with the same name will be replaced.

    Methods:
        sanitize_filename(filename): Sanitizes the filename to remove any invalid characters.
        text_to_audio(text, filename): Converts the given text to audio and saves it as a file.
        generate_audio_files_from_text(input_file, output_file): Generates audio files from the text in the input file
            and creates an Anki import file with links to these audio files.
        generate_from_dataframe(df, text_column, output_file): Same as above but takes a Pandas DataFrame as input.
    """

    def __init__(
        self,
        lang=DEFAULT_LANGUAGE,
        anki_media_folder=ANKI_MEDIA_FOLDER,
        replace_duplicates=True,
    ):
        self.lang = lang
        self.anki_media_folder = anki_media_folder
        self.replace_duplicates = replace_duplicates

    @staticmethod
    def sanitize_filename(filename):
        return re.sub(r'[\\/*?:"<>|]', "_", filename)

    def text_to_audio(self, text, filename):
        try:
            tts = gTTS(text=text, lang=self.lang, slow=False)
            tts.save(filename)
        except Exception as e:
            logger.error(f"Audio generation failed for text: {text}, error: {e}")
            raise

    def generate_audio_files_from_text(self, input_file, output_file):
        with open(input_file, "r", encoding="utf-8") as file:
            lines = [line for line in file if not line.startswith("#") and "\t" in line]

        anki_lines = []  # Collect lines for Anki import file
        c = 0

        for line in tqdm(lines, desc="Generating audio files", total=len(lines)):
            text = line.split("\t")[1].strip()
            sanitized_text = self.sanitize_filename(text)
            filename = os.path.join(self.anki_media_folder, f"{sanitized_text}.mp3")
            if not os.path.exists(filename) or self.replace_duplicates:
                self.text_to_audio(text, filename)
                c += 1

            # Prepare line for Anki import file
            audio_filename = f"{sanitized_text}.mp3"
            anki_line = self._prepare_anki_line(line, audio_filename)
            anki_lines.append(anki_line)

        logger.info(f"{c} audio files generated")

        # Generate Anki import file
        self._generate_anki_import_file(anki_lines, output_file)

    def generate_from_dataframe(self, df, text_column, output_file):
        anki_lines = []
        c = 0

        for index, row in tqdm(
            df.iterrows(), desc="Generating audio files", total=len(df)
        ):
            text = row[text_column]
            sanitized_text = self.sanitize_filename(text)
            filename = os.path.join(self.anki_media_folder, f"{sanitized_text}.mp3")
            if not os.path.exists(filename) or self.replace_duplicates:
                self.text_to_audio(text, filename)
                c += 1

            audio_filename = f"{sanitized_text}.mp3"
            audio_tag = f"[sound:{audio_filename}]"

            # Assuming the DataFrame has 'french' and 'spanish' columns
            anki_line = f"{row['spanish']}\t{row['french']}\t{audio_tag}"
            anki_lines.append(anki_line)

        logger.info(f"{c} audio files generated")

        # Generate Anki import file
        self._generate_anki_import_file(anki_lines, output_file)

    @staticmethod
    def _prepare_anki_line(line, audio_filename):
        fields = line.strip().split("\t")
        audio_tag = f"[sound:{audio_filename}]"
        if len(fields) < 3 or not fields[2].startswith("[sound:"):
            fields.append(
                audio_tag
            )  # Append audio tag as third field only if it doesn't already exist
        return "\t".join(fields)

    @staticmethod
    def _generate_anki_import_file(lines, output_file):
        # Ensure output folder exists
        output_folder = Path(output_file).parent
        if not output_folder.exists():
            output_folder.mkdir(parents=True)
        with open(output_file, "w", encoding="utf-8") as outfile:
            for line in lines:
                outfile.write(line + "\n")
