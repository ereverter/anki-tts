#!/bin/bash

BASE_DIR="data/processed"

python3 src/manki/data/translation/cleaner.py --base_dir "$BASE_DIR"
