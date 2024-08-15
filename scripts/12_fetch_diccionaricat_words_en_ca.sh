#!/bin/bash

SRC_LANG="en"
DST_LANG="ca"
ERROR_WORD_FILE="data/processed/dictionaries/cambridge/${SRC_LANG}_${DST_LANG}_errors.json"
OUTPUT_DIR="data/raw/dictionaries/diccionari_cat/${SRC_LANG}_${DST_LANG}"
USER_AGENTS_FILE="data/raw/scrapping/user_agents.json"
PROXIES_FILE="data/raw/scrapping/proxies.txt" 
SSL_CERT_FILE="diccionari_cat_proxy.crt" 

mkdir -p "$OUTPUT_DIR"

python src/manki/data/translation/diccionari_cat/fetch.py \
    --src_lang $SRC_LANG \
    --dst_lang $DST_LANG \
    --error_word_file $ERROR_WORD_FILE \
    --output_dir $OUTPUT_DIR \
    --user_agents_file $USER_AGENTS_FILE \
    --proxies_file $PROXIES_FILE \
    --verify $SSL_CERT_FILE
