#!/bin/bash

DOMAIN="words"
INPUT_FILE="data/processed/dictionaries/semi_curated/words.json"
OUTPUT_FILE="data/processed/dictionaries/curated/requests/word_requests.jsonl"

mkdir -p "$(dirname "$OUTPUT_FILE")"

python src/manki/data/translation/curater.py --domain $DOMAIN --input_file $INPUT_FILE --output_file $OUTPUT_FILE
