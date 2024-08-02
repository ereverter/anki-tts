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
from manki.data.translation.collins.parse import (
    CollinsDictionaryParser,
    CollinsWordEntry,
)


def process_cambridge_file(file_path: str, lang: str) -> List[CambridgeWordEntry]:
    if lang == "fr":
        parser = FrenchCambridgeDictionaryParser(file_path)
    elif lang == "es":
        parser = SpanishCambridgeDictionaryParser(file_path)
    elif lang == "ca":
        parser = CatalanCambridgeDictionaryParser(file_path)
    else:
        raise ValueError(f"Unsupported language: {lang}")

    parsed_data = parser.parse()
    return parsed_data


def process_collins_file(file_path: str) -> List[CollinsWordEntry]:
    parser = CollinsDictionaryParser(file_path)
    parsed_data = parser.parse()
    return parsed_data


def main():
    dictionary_name = "cambridge/en_ca"
    lang = "ca"
    input_dir = f"data/raw/dictionaries/{dictionary_name}"
    output_file = f"data/processed/dictionaries/{dictionary_name}.json"
    error_file = f"data/processed/dictionaries/{dictionary_name}_errors.json"

    all_parsed_data = []
    errors = []

    files_to_process = [
        os.path.join(input_dir, file_name)
        for file_name in os.listdir(input_dir)
        if file_name.endswith(".html")
    ]

    process_cambridge_file_lang = partial(process_cambridge_file, lang=lang)
    process_function = (
        process_cambridge_file_lang
        if "cambridge" in dictionary_name
        else process_collins_file
    )

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
    main()
