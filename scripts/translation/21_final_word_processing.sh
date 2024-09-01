#!/bin/bash

python3 src/manki/data/translation/curater.py \
    --domain curate \
    --words_file data/curated/words.json \
    --translation_dirs data/processed/dictionaries/curated/output/ca_translation \
                      data/processed/dictionaries/curated/output/es_translation \
                      data/processed/dictionaries/curated/output/fr_translation \
    --output_dir data/curated
