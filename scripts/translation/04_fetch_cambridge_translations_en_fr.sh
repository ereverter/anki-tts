#!/bin/bash

BASE_URL="https://dictionary.cambridge.org/dictionary/english-french/"
WORDS_FILE="data/processed/test/words.json"
USER_AGENTS_FILE="data/raw/scrapping/user_agents.json"
OUTPUT_DIR="data/raw/dictionaries/cambridge/en_fr"
# PROXIES=""

python src/manki/data/translation/cambdrige/fetch.py --base_url $BASE_URL --words_file $WORDS_FILE --user_agents_file $USER_AGENTS_FILE --output_dir $OUTPUT_DIR