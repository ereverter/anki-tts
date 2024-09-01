#!/bin/bash

JSON_FILE_3000="data/processed/common_words/oxford_3000.json"
JSON_FILE_5000="data/processed/common_words/oxford_5000.json"

OUTPUT_FILE="data/processed/common_words/words.json"

python src/manki/data/common_words/merge.py --input_files $JSON_FILE_3000 $JSON_FILE_5000 --output_file $OUTPUT_FILE
