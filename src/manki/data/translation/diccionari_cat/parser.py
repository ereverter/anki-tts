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


# Load the HTML content
file_path = "/mnt/data/output.html"
with open(file_path, "r", encoding="utf-8") as file:
    content = file.read()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(content, "html.parser")


# Function to extract word entries
def extract_word_entries(soup) -> List[CambridgeWordEntry]:
    word_entries = []

    # Extract the word from the <span class="field--name-title">
    word_tag = soup.find("span", class_="field--name-title")
    word = (
        word_tag.get_text(strip=True)
        .replace('<title type="display">', "")
        .replace("</title>", "")
        .strip()
        if word_tag
        else "Unknown"
    )

    # Extract pronunciation
    pronunciation_tag = soup.find("span", class_="accessory_heading")
    pronunciation = (
        pronunciation_tag.next_sibling.strip() if pronunciation_tag else None
    )

    # Extract part of speech
    pos_tags = soup.find_all("span", class_="grammar")
    parts_of_speech = [pos.get_text(separator=" ", strip=True) for pos in pos_tags]

    # Extract and filter definitions and translations
    list_items = soup.find("div", class_="div1").find_all("li")
    definitions = [
        item.get_text(separator=" ", strip=True)
        .replace("\t", "")
        .replace("\n", " ")
        .strip()
        for item in list_items
    ]
    translations = [
        item.get_text(separator=" ", strip=True)
        .replace("\t", "")
        .replace("\n", " ")
        .strip()
        for item in list_items
    ]

    # Create CambridgeWordEntry instances for each part of speech
    for pos in parts_of_speech:
        word_entry = CambridgeWordEntry(
            word=word,
            part_of_speech=[pos],
            pronunciation=pronunciation,
            definitions=definitions if definitions else None,
            translations=translations if translations else None,
            examples=None,
            synonyms=None,
            antonyms=None,
            metadata=None,
        )
        word_entries.append(word_entry)

    return word_entries


# Extract word entries
word_entries = extract_word_entries(soup)

# Output the parsed CambridgeWordEntry instances
word_entries
