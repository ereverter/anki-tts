import logging
import re
from typing import List

import fitz  # PyMuPDF
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WordEntry(BaseModel):
    word: str
    part_of_speech: List[str]
    definitions: List[str]
    level: str


class Oxford3000Parser:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    def _extract_text(self) -> List[str]:
        document = fitz.open(self.pdf_path)
        text = []
        for page_num in range(document.page_count):
            page = document.load_page(page_num)
            text.append(page.get_text())
        return text

    def _parse_text(self, text: List[str]) -> List[WordEntry]:
        entries = []
        level = None
        word_entry_pattern = re.compile(
            r"^([a-zA-Z1-9() ]+)\s+((?:[a-z]+\.,?\s*)+)(.*)$"
        )
        pos_pattern = re.compile(r"([a-z]+\.,?)")

        current_entry = None

        for line in text:
            line = line.strip()
            logger.debug(f"Processing line: {line}")
            if line in ["A1", "A2", "B1", "B2"]:
                level = line
                logger.info(f"Current level set to: {level}")
            elif level:
                match = word_entry_pattern.match(line)
                if match:
                    word = match.group(1).strip()
                    pos_list = [
                        pos.strip() for pos in pos_pattern.findall(match.group(2))
                    ]
                    definition = match.group(3).strip() if match.group(3) else ""

                    logger.debug(
                        f"Matched word: {word}, POS: {pos_list}, Definition: {definition}"
                    )

                    current_entry = WordEntry(
                        word=word,
                        part_of_speech=pos_list,
                        definitions=[definition] if definition else [],
                        level=level,
                    )
                    entries.append(current_entry)
                else:
                    if current_entry and current_entry.definitions:
                        if (
                            line.isdigit()
                            or "©" in line
                            or "The Oxford 3000™ by CEFR level" in line
                        ):
                            continue
                        if re.match(r".+[,.;]", line):
                            current_entry.definitions[-1] += f" {line}"
                        else:
                            logger.warning(f"Unhandled line: {line}")
                    else:
                        logger.warning(f"No match found for line: {line}")

        return entries

    def parse(self) -> List[WordEntry]:
        text = self._extract_text()
        flattened_text = "\n".join(text).split("\n")
        return self._parse_text(flattened_text)


if __name__ == "__main__":
    pdf_path = "data/raw/common_words/The_Oxford_3000_by_CEFR_level.pdf"
    parser = Oxford3000Parser(pdf_path)
    word_entries = parser.parse()

    for entry in word_entries:  # Print first 10 entries as a sample
        print(entry.model_dump())
