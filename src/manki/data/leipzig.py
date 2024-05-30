import argparse
import json
import os
import re
import time
from typing import Dict, List, Tuple, Union

import requests
from bs4 import BeautifulSoup

# Constants
DATA_PATH = "data"  # Update to your actual data path
RAW_DATA_PATH = os.path.join(DATA_PATH, "raw")


def get_available_languages(url: str) -> Dict[str, str]:
    """Retrieve available languages and their URLs from the Leipzig corpus site."""
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"Error": str(e)}

    soup = BeautifulSoup(response.text, "html.parser")
    modal = soup.find("div", {"id": "corpusSelectionModal"})
    language_links = modal.find_all("a", {"class": "btn-modal"})

    return {link.text.strip(): link["href"] for link in language_links}


def extract_metadata_from_filename(file_name: str) -> Tuple[str, str, str, str, str]:
    """Extract metadata from a given filename."""
    pattern1 = r"(\w+)_([a-z]+)_(\d{4})_(\d+K|\d+M)"
    pattern2 = r"(\w+)_([a-z]+)_(\d{4})"

    for pattern in [pattern1, pattern2]:
        match = re.match(pattern, file_name)
        if match:
            return (*match.groups(), file_name)

    return "Unknown", "Unknown", "Unknown", "Unknown", file_name


def get_corpus_metadata(url: str) -> List[Tuple[str, str, str, str, str]]:
    """Fetch and parse corpus metadata from a given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        return [("Error", str(e), "", "", "")]

    soup = BeautifulSoup(response.text, "html.parser")
    download_links = soup.find_all("a", {"class": "link_corpora_download"})

    return [
        extract_metadata_from_filename(link.get("data-corpora-file", ""))
        for link in download_links
    ]


def process_languages(file_path: str):
    """Process languages from a file and save their metadata."""
    os.makedirs(RAW_DATA_PATH, exist_ok=True)

    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split(": ")
            if len(parts) != 2:
                continue
            language, url = parts

            json_file_path = os.path.join(RAW_DATA_PATH, f"{language}.json")
            if os.path.exists(json_file_path):
                print(f"Metadata for {language} already exists. Skipping...")
                continue

            print(f"Processing {language}...")
            metadata = get_corpus_metadata(url)
            with open(json_file_path, "w") as json_file:
                json.dump(metadata, json_file, indent=4)

            time.sleep(10)  # Sleep to prevent server overload


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(
        description="Scrape corpus metadata from Leipzig website"
    )
    parser.add_argument(
        "leipzig_download_page",
        type=str,
        help="URL of the Leipzig corpus download page",
        default="https://wortschatz.uni-leipzig.de/en/download",
        nargs="?",
    )
    parser.add_argument(
        "available_languages_path",
        type=str,
        help="Path to the file containing language URLs",
    )
    parser.add_argument(
        "--get_languages",
        action="store_true",
        help="Flag to get available languages from Leipzig website",
    )
    parser.add_argument(
        "--process_languages",
        action="store_true",
        help="Flag to process languages and scrape metadata",
    )
    args = parser.parse_args()

    if args.get_languages:
        languages = get_available_languages(args.leipzig_download_page)
        with open(args.available_languages_path, "w") as file:
            for language, url in languages.items():
                file.write(f"{language}: {url}\n")

    if args.process_languages:
        process_languages(args.available_languages_path)


if __name__ == "__main__":
    main()
