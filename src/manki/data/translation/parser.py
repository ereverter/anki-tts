import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from typing import List

from tqdm import tqdm

from manki.data.translation.cambdrige.parse import (
    CambridgeWordEntry,
    CatalanCambridgeDictionaryParser,
    FrenchCambridgeDictionaryParser,
    SpanishCambridgeDictionaryParser,
)
from manki.data.translation.diccionari_cat.parse import CatalanDictionaryParser
from manki.data.translation.linguee.parse import SimpleWordParser as LingueeParser


def process_file(file_path: str, dictionary_name: str, lang: str):
    if dictionary_name == "cambridge":
        if lang == "fr":
            parser = FrenchCambridgeDictionaryParser(file_path)
        elif lang == "es":
            parser = SpanishCambridgeDictionaryParser(file_path)
        elif lang == "ca":
            parser = CatalanCambridgeDictionaryParser(file_path)
        else:
            raise ValueError(f"Unsupported language: {lang}")
    elif dictionary_name == "diccionari_cat":
        parser = CatalanDictionaryParser(file_path)
    elif dictionary_name == "linguee":
        parser = LingueeParser(file_path)
    else:
        raise ValueError(f"Unsupported dictionary: {dictionary_name}")

    parsed_data = parser.parse()
    return parsed_data


def main(
    dictionary_name: str, lang: str, input_dir: str, output_file: str, error_file: str
):
    all_parsed_data = []
    errors = []

    files_to_process = [
        os.path.join(input_dir, file_name)
        for file_name in os.listdir(input_dir)
        if file_name.endswith(".html")
    ]

    process_function = partial(process_file, dictionary_name=dictionary_name, lang=lang)

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        future_to_file = {
            executor.submit(process_function, file_path): file_path
            for file_path in files_to_process
        }
        for future in tqdm(
            as_completed(future_to_file),
            total=len(future_to_file),
            desc="Processing files",
        ):
            file_path = future_to_file[future]
            try:
                parsed_data = future.result()
                if parsed_data:
                    all_parsed_data.extend(parsed_data)
            except Exception as e:
                errors.append(file_path)

    print(f"Total parsed entries: {len(all_parsed_data)}")
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            [entry.dict() for entry in all_parsed_data],
            file,
            indent=4,
            ensure_ascii=False,
        )

    with open(error_file, "w", encoding="utf-8") as file:
        json.dump(errors, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process dictionary files")
    parser.add_argument(
        "--dictionary_name",
        type=str,
        required=True,
        help="Name of the dictionary (cambridge, diccionari_cat, linguee)",
    )
    parser.add_argument(
        "--lang",
        type=str,
        required=True,
        help="Language of the dictionary (fr, es, ca)",
    )
    parser.add_argument(
        "--input_dir", type=str, required=True, help="Directory with input HTML files"
    )
    parser.add_argument(
        "--output_file", type=str, required=True, help="Path to the output JSON file"
    )
    parser.add_argument(
        "--error_file", type=str, required=True, help="Path to the error JSON file"
    )

    args = parser.parse_args()
    main(
        args.dictionary_name,
        args.lang,
        args.input_dir,
        args.output_file,
        args.error_file,
    )
