#!/bin/bash

SRC_LANG="en"
DST_LANG="es"
ERROR_WORD_FILE="data/processed/dictionaries/cambridge/${SRC_LANG}_${DST_LANG}_errors.json"
OUTPUT_DIR="data/raw/dictionaries/linguee/${SRC_LANG}_${DST_LANG}"
USER_AGENTS_FILE="data/raw/scrapping/user_agents.json"
FETCHED_FILES_DIR="data/raw/dictionaries/linguee/${SRC_LANG}_${DST_LANG}"

mkdir -p "$(dirname "$OUTPUT_DIR")"

python src/manki/data/translation/linguee/fetch.py --src_lang $SRC_LANG --dst_lang $DST_LANG --error_word_file $ERROR_WORD_FILE --output_dir $OUTPUT_DIR --user_agents_file $USER_AGENTS_FILE --fetched_files_dir $FETCHED_FILES_DIR
