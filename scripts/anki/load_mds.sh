#!/bin/bash

md_directory="/mnt/g/My Drive/obsidian/anki" 
deck_name="General Learning" 
model_name="basic"

if [ ! -d "$md_directory" ]; then
    echo "Directory $md_directory does not exist."
    exit 1
fi

manki anki "$md_directory" "$deck_name" --model-name "$model_name" --reference-fields "front"
