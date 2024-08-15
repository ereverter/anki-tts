from typing import List, Optional, Tuple

from bs4 import BeautifulSoup
from pydantic import BaseModel


class WordEntry(BaseModel):
    word: str
    pronunciation: Optional[str] = None
    part_of_speech: Optional[str] = None
    definition_or_translation: Optional[str] = None
    example_original: Optional[str] = None
    example_translation: Optional[str] = None


class CatalanDictionaryParser:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse(self) -> List[WordEntry]:
        with open(self.file_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, "html.parser")
        word_entries = self.extract_word_entries(soup)
        cleaned_word_entries = self.postprocess_word_entries(word_entries)
        return cleaned_word_entries

    def extract_word_entries(self, soup: BeautifulSoup) -> List[WordEntry]:
        word_entries = []
        articles = soup.find_all("article")

        for article in articles:
            word = article["about"].split("/")[-1] if article else "Unknown"
            pronunciation = self.extract_pronunciation(article)
            definition_section = article.find("div", class_="div1")

            if definition_section:
                part_of_speech_tags = definition_section.find_all(
                    "span", class_="grammar"
                )

                for pos_tag in part_of_speech_tags:
                    part_of_speech = pos_tag.get_text(separator=" ", strip=True)
                    next_element = pos_tag.find_next_sibling()

                    while next_element and (
                        next_element.name == "li" or next_element.name == "span"
                    ):
                        if next_element.name == "li":
                            text = self.clean_text(
                                next_element.get_text(separator=" ", strip=True)
                            )
                            if next_element.find("b"):
                                original, translation = self.split_example(text)
                                if part_of_speech == "adverb":
                                    word_entries.append(
                                        WordEntry(
                                            word=word,
                                            pronunciation=pronunciation,
                                            part_of_speech=part_of_speech,
                                            example_original=original,
                                            example_translation=translation,
                                        )
                                    )
                            else:
                                if (
                                    "Ecclesiastical" in text
                                    and part_of_speech != "noun"
                                ):
                                    next_element = next_element.find_next_sibling()
                                    continue
                                word_entries.append(
                                    WordEntry(
                                        word=word,
                                        pronunciation=pronunciation,
                                        part_of_speech=part_of_speech,
                                        definition_or_translation=text,
                                    )
                                )

                        next_element = next_element.find_next_sibling()

        return word_entries

    def extract_pronunciation(self, article: BeautifulSoup) -> Optional[str]:
        pronunciation_tag = article.find("span", class_="accessory_heading")
        return (
            pronunciation_tag.find_next_sibling(string=True).strip()
            if pronunciation_tag
            else None
        )

    @staticmethod
    def clean_text(text: str) -> str:
        return text.replace("\n", " ").replace("\t", " ").strip()

    @staticmethod
    def split_example(text: str) -> Tuple[str, str]:
        for indicator in ["abans de", "fins a", "abans d'aquest"]:
            if indicator in text:
                original, translation = text.split(indicator, 1)
                translation = indicator + " " + translation.strip()
                translation = translation.replace(" ,", ",")
                return original.strip(), translation
        return text, None

    @staticmethod
    def postprocess_word_entries(entries: List[WordEntry]) -> List[WordEntry]:
        for entry in entries:
            if entry.definition_or_translation:
                entry.definition_or_translation = " ".join(
                    entry.definition_or_translation.split()
                )
            if entry.example_original:
                entry.example_original = " ".join(entry.example_original.split())
            if entry.example_translation:
                entry.example_translation = " ".join(entry.example_translation.split())
        return entries
