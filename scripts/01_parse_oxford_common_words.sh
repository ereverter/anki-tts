#!/bin/bash

PDF_PATH_3000="data/raw/common_words/The_Oxford_3000_by_CEFR_level.pdf"
PDF_PATH_5000="data/raw/common_words/The_Oxford_5000_by_CEFR_level.pdf"

OUTPUT_DIR="data/processed/common_words"

mkdir -p $OUTPUT_DIR

python src/manki/data/common_words/preprocess.py --pdf_path $PDF_PATH_3000 --output_dir $OUTPUT_DIR --file_name oxford_3000
python src/manki/data/common_words/preprocess.py --pdf_path $PDF_PATH_5000 --output_dir $OUTPUT_DIR --file_name oxford_5000