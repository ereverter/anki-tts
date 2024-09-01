#!/bin/bash

export $(grep -v '^#' .env | xargs)

DIRECTORIES=(
#   "data/processed/dictionaries/curated/requests/ca_translation"
#   "data/processed/dictionaries/curated/requests/es_translation"
  "data/processed/dictionaries/curated/requests/fr_translation"
)

for DIR in "${DIRECTORIES[@]}"; do
  for FILE in "$DIR"/*.jsonl; do
    echo "Uploading $FILE..."
    
    RESPONSE=$(curl -s https://api.openai.com/v1/files \
      -H "Authorization: Bearer $OPENAI_API_KEY" \
      -F purpose="batch" \
      -F file="@$FILE")
    
    FILE_ID=$(echo $RESPONSE | jq -r '.id')
    
    if [ "$FILE_ID" != "null" ]; then
      echo "Uploaded $FILE successfully. File ID: $FILE_ID"
    else
      echo "Failed to upload $FILE. Response: $RESPONSE"
    fi
  done
done

echo "All files uploaded. Use the returned file IDs for your batch API calls."
