"""
Clean the processed data by combining the dictionaries and removing words with no entries.
"""

import argparse
import json
import os
from collections import defaultdict
from typing import Dict, List

from tqdm import tqdm


def process_common_words(directory: str) -> List[str]:
    words_set = set()
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    words_set.update(data)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    return list(words_set)


def process_cambridge_json(file_path: str) -> Dict[str, List[Dict]]:
    grouped_words = defaultdict(list)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            for entry in data:
                word = entry["word"]
                grouped_words[word].append(
                    {
                        "part_of_speech": entry.get("part_of_speech", []),
                        "definitions": entry.get("definitions", []),
                        "translations": entry.get("translations", []),
                        "examples": entry.get("examples", None),
                    }
                )
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return grouped_words


def process_diccionari_cat_json(file_path: str) -> Dict[str, List[Dict]]:
    grouped_words = defaultdict(list)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            for entry in data:
                word = entry["word"]
                grouped_words[word].append(
                    {
                        "part_of_speech": [entry.get("part_of_speech")],
                        "definitions": [entry.get("definition_or_translation")],
                        "translations": [entry.get("definition_or_translation")],
                        "examples": None,
                    }
                )
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return grouped_words


def process_linguee_json(file_path: str) -> Dict[str, List[Dict]]:
    grouped_words = defaultdict(list)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            for entry in data:
                word = entry["word"]
                grouped_words[word].append(
                    {
                        "part_of_speech": entry.get("part_of_speech", []),
                        "definitions": entry.get("definitions", []),
                        "translations": entry.get("translations", []),
                        "examples": entry.get("examples", []),
                    }
                )
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return grouped_words


def process_extra_json(file_path: str) -> Dict[str, List[Dict]]:
    grouped_words = defaultdict(list)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            for entry in data:
                word = entry["word"]
                grouped_words[word].append(
                    {
                        "part_of_speech": entry.get("part_of_speech", []),
                        "definitions": entry.get("definitions", []),
                        "translations": entry.get("translations", []),
                    }
                )
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return grouped_words


def main():
    parser = argparse.ArgumentParser(
        description="Process and combine JSON files into en_fr, en_es, and en_ca."
    )
    parser.add_argument(
        "--base_dir",
        type=str,
        required=True,
        help="Base directory containing the processed data.",
    )
    args = parser.parse_args()

    base_dir = args.base_dir
    common_words_dir = os.path.join(base_dir, "common_words")
    dictionaries_dir = os.path.join(base_dir, "dictionaries")
    cambridge_dir = os.path.join(dictionaries_dir, "cambridge")
    diccionari_cat_dir = os.path.join(dictionaries_dir, "diccionari_cat")
    linguee_dir = os.path.join(dictionaries_dir, "linguee")
    extra_dir = os.path.join(dictionaries_dir, "extra")
    semi_curated_dir = os.path.join(dictionaries_dir, "semi_curated")

    os.makedirs(semi_curated_dir, exist_ok=True)

    # Initialize dictionaries for each language pair
    en_fr = defaultdict(list)
    en_es = defaultdict(list)
    en_ca = defaultdict(list)

    # Process common words
    common_words = process_common_words(common_words_dir)
    for word in common_words:
        en_fr[word] = []
        en_es[word] = []
        en_ca[word] = []

    # Process Cambridge files
    cambridge_files = {
        "en_fr": os.path.join(cambridge_dir, "en_fr.json"),
        "en_es": os.path.join(cambridge_dir, "en_es.json"),
        "en_ca": os.path.join(cambridge_dir, "en_ca.json"),
    }

    for lang_pair, file_path in cambridge_files.items():
        if os.path.exists(file_path):
            data = process_cambridge_json(file_path)
            if lang_pair == "en_fr":
                for word, entries in data.items():
                    en_fr[word].extend(entries)
            elif lang_pair == "en_es":
                for word, entries in data.items():
                    en_es[word].extend(entries)
            elif lang_pair == "en_ca":
                for word, entries in data.items():
                    en_ca[word].extend(entries)

    # Process Diccionari Catala files
    diccionari_cat_file = os.path.join(diccionari_cat_dir, "en_ca.json")
    if os.path.exists(diccionari_cat_file):
        data = process_diccionari_cat_json(diccionari_cat_file)
        for word, entries in data.items():
            en_ca[word].extend(entries)

    # Process Linguee files
    linguee_files = {
        "en_fr": os.path.join(linguee_dir, "en_fr.json"),
        "en_es": os.path.join(linguee_dir, "en_es.json"),
    }

    for lang_pair, file_path in linguee_files.items():
        if os.path.exists(file_path):
            data = process_linguee_json(file_path)
            if lang_pair == "en_fr":
                for word, entries in data.items():
                    en_fr[word].extend(entries)
            elif lang_pair == "en_es":
                for word, entries in data.items():
                    en_es[word].extend(entries)

    # Process Extra files
    extra_file = os.path.join(extra_dir, "en_ca.json")
    if os.path.exists(extra_file):
        data = process_extra_json(extra_file)
        for word, entries in data.items():
            en_ca[word].extend(entries)

    # Remove words with no entries
    en_fr = {word: entries for word, entries in en_fr.items() if entries}
    en_es = {word: entries for word, entries in en_es.items() if entries}
    en_ca = {word: entries for word, entries in en_ca.items() if entries}

    # Save the combined data
    with open(os.path.join(semi_curated_dir, "en_fr.json"), "w", encoding="utf-8") as f:
        json.dump(en_fr, f, ensure_ascii=False, indent=4)

    with open(os.path.join(semi_curated_dir, "en_es.json"), "w", encoding="utf-8") as f:
        json.dump(en_es, f, ensure_ascii=False, indent=4)

    with open(os.path.join(semi_curated_dir, "en_ca.json"), "w", encoding="utf-8") as f:
        json.dump(en_ca, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
