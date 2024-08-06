#!/bin/bash

DEFAULT_URL_3000="https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/The_Oxford_3000_by_CEFR_level.pdf"
DEFAULT_URL_5000="https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/The_Oxford_5000_by_CEFR_level.pdf"

DOWNLOAD_DIR="data/raw/common_words"

mkdir -p $DOWNLOAD_DIR

python src/manki/data/common_words/download.py --pdf_url $DEFAULT_URL_3000 --download_dir $DOWNLOAD_DIR
python src/manki/data/common_words/download.py --pdf_url $DEFAULT_URL_5000 --download_dir $DOWNLOAD_DIR
