#!/bin/bash

DICTIONARY_NAME="linguee"
LANG="es"
INPUT_DIR="data/raw/dictionaries/${DICTIONARY_NAME}/en_es"
OUTPUT_FILE="data/processed/dictionaries/${DICTIONARY_NAME}/en_es.json"
ERROR_FILE="data/processed/dictionaries/${DICTIONARY_NAME}/en_es_errors.json"

mkdir -p "$(dirname "$INPUT_DIR")"
mkdir -p "$(dirname "$OUTPUT_FILE")"
mkdir -p "$(dirname "$ERROR_FILE")"

python src/manki/data/translation/parser.py --dictionary_name $DICTIONARY_NAME --lang $LANG --input_dir $INPUT_DIR --output_file $OUTPUT_FILE --error_file $ERROR_FILE
