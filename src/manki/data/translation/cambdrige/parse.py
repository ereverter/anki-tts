import json
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from pydantic import BaseModel


class CambridgeWordEntry(BaseModel):
    word: str
    part_of_speech: Optional[List[str]] = None
    pronunciation: Optional[str] = None
    definitions: Optional[List[str]] = None
    translations: Optional[List[str]] = None
    examples: Optional[List[str]] = None
    synonyms: Optional[List[str]] = None
    antonyms: Optional[List[str]] = None
    metadata: Optional[Dict[str, str]] = None


class CambridgeDictionaryParser:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse(self) -> List[CambridgeWordEntry]:
        with open(self.file_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, "html.parser")
        entry_body = soup.find("div", class_="entry-body")
        if not entry_body:
            raise ValueError("The entry-body element is not found.")

        entries = entry_body.find_all("div", class_="pr dictionary")
        parsed_entries = []

        for entry in entries:
            word = entry.find("h2", class_="di-title").get_text(strip=True)
            pos_sections = entry.find_all("div", class_="dpos-h di-head normal-entry")

            for pos_section in pos_sections:
                pos_elem = pos_section.find("span", class_="pos dpos")
                pos = pos_elem.get_text(strip=True) if pos_elem else ""

                pronunciation_span = pos_section.find("span", class_="ipa dipa")
                pronunciation = (
                    pronunciation_span.get_text(strip=True)
                    if pronunciation_span
                    else ""
                )

                di_body = pos_section.find_next_sibling(
                    "div", class_="di-body normal-entry-body"
                )
                if not di_body:
                    continue

                sense_blocks = di_body.find_all(
                    "div", class_="sense-block pr dsense dsense-noh"
                )

                definitions, translations, examples, synonyms, antonyms = (
                    [],
                    [],
                    [],
                    [],
                    [],
                )

                for sense_block in sense_blocks:
                    definition_elem = sense_block.find("div", class_="def ddef_d db")
                    definition = (
                        definition_elem.get_text(" ", strip=True)
                        if definition_elem
                        else ""
                    )
                    translation_elem = sense_block.find("span", class_="trans dtrans")
                    translation = (
                        translation_elem.get_text(strip=True)
                        if translation_elem
                        else ""
                    )
                    example_elem = sense_block.find("div", class_="examp dexamp")
                    example = (
                        example_elem.get_text(" ", strip=True) if example_elem else ""
                    )
                    synonym_elem = sense_block.find(
                        "div", class_="xref synonym hax dxref-w"
                    )
                    synonym = (
                        synonym_elem.get_text(" ", strip=True) if synonym_elem else ""
                    )
                    antonym_elem = sense_block.find(
                        "div", class_="xref antonym hax dxref-w"
                    )
                    antonym = (
                        antonym_elem.get_text(" ", strip=True) if antonym_elem else ""
                    )

                    if definition:
                        definitions.append(definition)
                    if translation:
                        translations.append(translation)
                    if example:
                        examples.append(example)
                    if synonym:
                        synonyms.append(synonym)
                    if antonym:
                        antonyms.append(antonym)

                parsed_entry = CambridgeWordEntry(
                    word=word,
                    part_of_speech=[pos],
                    pronunciation=pronunciation,
                    definitions=definitions if definitions else None,
                    translations=translations if translations else None,
                    examples=examples if examples else None,
                    synonyms=synonyms if synonyms else None,
                    antonyms=antonyms if antonyms else None,
                )

                parsed_entries.append(parsed_entry)

        return parsed_entries
