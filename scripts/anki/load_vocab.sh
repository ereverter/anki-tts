#!/bin/bash

vocab_file="data/curated/words/translations.json"
deck_name="Vocabulary: Catalan to French"
model_name="basic"
source_lang="ca"
target_lang="fr"
reference_fields="front" # "front,back"

if [ ! -f "$vocab_file" ]; then
    echo "Vocabulary file $vocab_file does not exist."
    exit 1
fi

manki anki "$vocab_file" "$deck_name" --model-name "$model_name" --source-lang "$source_lang" --target-lang "$target_lang" --reference-fields "$reference_fields"