#!/bin/bash

DOMAIN="translations"
INPUT_FILE="data/processed/dictionaries/semi_curated/en_ca.json"
OUTPUT_FILE="data/processed/dictionaries/curated/requests/ca_translation"
CLEANED_WORDS_FILE="data/curated/words.json"
TARGET_LANGUAGE="Catalan"

mkdir -p "$(dirname "$OUTPUT_FILE")"

python src/manki/data/translation/curater.py --domain $DOMAIN --input_file $INPUT_FILE --output_file $OUTPUT_FILE --cleaned_words_file $CLEANED_WORDS_FILE --target_language $TARGET_LANGUAGE

DOMAIN="translations"
INPUT_FILE="data/processed/dictionaries/semi_curated/en_es.json"
OUTPUT_FILE="data/processed/dictionaries/curated/requests/es_translation"
CLEANED_WORDS_FILE="data/curated/words.json"
TARGET_LANGUAGE="Spanish"

mkdir -p "$(dirname "$OUTPUT_FILE")"

python src/manki/data/translation/curater.py --domain $DOMAIN --input_file $INPUT_FILE --output_file $OUTPUT_FILE --cleaned_words_file $CLEANED_WORDS_FILE --target_language $TARGET_LANGUAGE


#!/bin/bash

DOMAIN="translations"
INPUT_FILE="data/processed/dictionaries/semi_curated/en_fr.json"
OUTPUT_FILE="data/processed/dictionaries/curated/requests/fr_translation"
CLEANED_WORDS_FILE="data/curated/words.json"
TARGET_LANGUAGE="French"

mkdir -p "$(dirname "$OUTPUT_FILE")"

python src/manki/data/translation/curater.py --domain $DOMAIN --input_file $INPUT_FILE --output_file $OUTPUT_FILE --cleaned_words_file $CLEANED_WORDS_FILE --target_language $TARGET_LANGUAGE
