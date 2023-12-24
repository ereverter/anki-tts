"""
Script (ad-hoc) to scrap the specfic list of common French words from the specified website below.
"""
import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from pathlib import Path

try:
    from ..utils import setup_logger

    # Configure logging
    logger = setup_logger(name=__name__)

except ImportError:
    import logging

    logger = logging.getLogger(__name__)


def clean_text(text):
    text = text.strip()  # Remove leading/trailing spaces
    text = " ".join(text.split())  # Replace line breaks and tabs with a single space
    text = text.replace("\n", " ").replace(
        "\r", ""
    )  # Remove newline and carriage return characters
    return text


def scrape_french_words(base_url, num_pages, table_id):
    all_words = []
    with requests.Session() as session:
        for page in tqdm(range(1, num_pages + 1), desc="Scraping pages"):
            url = f"{base_url}-{page}.asp"
            response = session.get(url)
            if response.status_code != 200:
                logger.warning(f"Failed to retrieve page {page}")
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            table = soup.find("table", {"id": table_id})
            if not table:
                logger.warning(f"No table found on page {page}")
                continue

            for row in table.find_all("tr"):
                columns = row.find_all("td")
                if len(columns) == 3:  # Ensure there are exactly three columns
                    french_word = clean_text(columns[1].text)
                    spanish_translation = clean_text(columns[2].text)
                    all_words.append((french_word, spanish_translation))

    return pd.DataFrame(all_words, columns=["french", "spanish"])


def main(args):
    base_url = "..."
    num_pages = -1
    table_id = "..."
    french_words_df = scrape_french_words(base_url, num_pages, table_id)

    print(french_words_df.head())

    # Check folder exists
    output_folder = Path(args.output_file).parent
    if not output_folder.exists():
        output_folder.mkdir(parents=True)
    french_words_df.to_csv(
        args.output_file,
        index=False,
        encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrap the specfic list of common French words from the specified website below."
    )
    parser.add_argument(
        "-o",
        "--output_file",
        type=str,
        default="data/raw/french_words_1000.csv",
        help="Output file",
    )
    args = parser.parse_args()

    main(args)
