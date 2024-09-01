##!/bin/bash
export $(grep -v '^#' .env | xargs)

curl https://api.openai.com/v1/files \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F purpose="batch" \
  -F file="@data/processed/dictionaries/curated/requests/word_requests.jsonl"

echo "Run it with the returned file id"