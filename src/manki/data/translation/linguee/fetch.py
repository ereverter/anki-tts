import argparse
import json
import os
from typing import List

from manki.data.translation.fetcher import URLFetcher


def extract_words_from_errors(file_path: str) -> List[str]:
    with open(file_path, "r", encoding="utf-8") as file:
        error_paths = json.load(file)
    words = [path.split("/")[-1].replace(".html", "") for path in error_paths]
    return words


def get_fetched_words(
    fetched_files_dir: str, src_lang: str, dst_lang: str
) -> List[str]:
    fetched_files = os.listdir(fetched_files_dir)
    fetched_words = [
        file.replace(
            "https___linguee_api_fly_dev_api_v2_translations_query_", ""
        ).replace(f"_src_{src_lang}_dst_{dst_lang}.html", "")
        for file in fetched_files
        if file.endswith(".html")
    ]
    return fetched_words


def main(
    src_lang, dst_lang, error_word_file, output_dir, user_agents_file, fetched_files_dir
):
    words_to_translate = extract_words_from_errors(error_word_file)
    fetched_words = get_fetched_words(fetched_files_dir, src_lang, dst_lang)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    base_url = "https://linguee-api.fly.dev/api/v2/translations"
    urls = []
    skipped_words = []

    for word in words_to_translate:
        if word not in fetched_words:
            urls.append(f"{base_url}?query={word}&src={src_lang}&dst={dst_lang}")
        else:
            skipped_words.append(word)

    if skipped_words:
        print(f"Skipped already fetched words: {', '.join(skipped_words)}")

    if not urls:
        print("No new words to fetch.")
        return

    with open(user_agents_file, "r", encoding="utf-8") as file:
        user_agents = [entry["ua"] for entry in json.load(file)]

    fetcher = URLFetcher(
        urls, None, user_agents, output_dir, mean_sleep=30.0, noise_stddev=10.0
    )
    fetcher.fetch()

    for url, path in fetcher.url_index.items():
        print(f"{url}: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch translations for error words")
    parser.add_argument("--src_lang", type=str, required=True, help="Source language")
    parser.add_argument(
        "--dst_lang", type=str, required=True, help="Destination language"
    )
    parser.add_argument(
        "--error_word_file",
        type=str,
        required=True,
        help="Path to the JSON file with error words",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Directory to save the fetched translations",
    )
    parser.add_argument(
        "--user_agents_file",
        type=str,
        required=True,
        help="Path to the user agents JSON file",
    )
    parser.add_argument(
        "--fetched_files_dir",
        type=str,
        required=True,
        help="Directory containing the fetched files",
    )

    args = parser.parse_args()
    main(
        args.src_lang,
        args.dst_lang,
        args.error_word_file,
        args.output_dir,
        args.user_agents_file,
        args.fetched_files_dir,
    )
