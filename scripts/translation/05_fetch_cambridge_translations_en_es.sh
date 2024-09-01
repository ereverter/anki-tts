#!/bin/bash

BASE_URL="https://dictionary.cambridge.org/dictionary/english-spanish/"
WORDS_FILE="data/processed/common_words/words.json"
USER_AGENTS_FILE="data/raw/scrapping/user_agents.json"
OUTPUT_DIR="data/raw/dictionaries/cambridge/en_es"
# PROXIES=""

python src/manki/data/translation/cambdrige/fetch.py --base_url $BASE_URL --words_file $WORDS_FILE --user_agents_file $USER_AGENTS_FILE --output_dir $OUTPUT_DIR