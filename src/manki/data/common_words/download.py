import argparse
import os
from typing import List

import requests


def download_oxford_common_words(pdf_url: str, download_dir: str) -> None:
    response = requests.get(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()

    os.makedirs(download_dir, exist_ok=True)
    filename = os.path.basename(pdf_url)
    file_path = os.path.join(download_dir, filename)

    with open(file_path, "wb") as pdf_file:
        pdf_file.write(response.content)

    print(f"Downloaded file saved to: {file_path}")


if __name__ == "__main__":
    DEFAULT_URL_3000 = "https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/The_Oxford_3000_by_CEFR_level.pdf"
    DEFAULT_URL_5000 = "https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/The_Oxford_5000_by_CEFR_level.pdf"

    parser = argparse.ArgumentParser(
        description="Download a PDF file from a given URL and save it to the specified directory."
    )
    parser.add_argument("--pdf_url", type=str, help="The URL of the PDF to download.")
    parser.add_argument(
        "--download_dir", type=str, help="The directory to save the downloaded PDF."
    )
    parser.add_argument(
        "--default_urls",
        action="store_true",
        help=f"Use default URLs: 3000 words ({DEFAULT_URL_3000}) or 5000 words ({DEFAULT_URL_5000}).",
    )

    args = parser.parse_args()
    download_oxford_common_words(args.pdf_url, args.download_dir)
