import argparse
import json
from typing import List


def load_json(file_path: str) -> List[dict]:
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data: List[dict], file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def merge_json_files(file_paths: List[str], output_path: str) -> None:
    merged_data = []

    for file_path in file_paths:
        data = load_json(file_path)
        merged_data.extend(data)

    save_json(merged_data, output_path)
    print(f"Merged data saved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge multiple JSON files into one.")
    parser.add_argument(
        "--input_files",
        type=str,
        nargs="+",
        required=True,
        help="List of input JSON files to merge.",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        required=True,
        help="Output file to save the merged JSON data.",
    )

    args = parser.parse_args()

    merge_json_files(args.input_files, args.output_file)
