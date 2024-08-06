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


def get_extracted_words(output_dir: str):
    extracted_words = set()
    for file_name in os.listdir(output_dir):
        if file_name.endswith(".html"):
            word = file_name.replace(
                "https___diccionari_cat_angles_catala_", ""
            ).replace(".html", "")
            extracted_words.add(word)
    return extracted_words


def main(
    src_lang,
    dst_lang,
    error_word_file,
    output_dir,
    user_agents_file,
    proxies_file,
    verify,
):
    words_to_translate = extract_words_from_errors(error_word_file)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    base_url = "https://diccionari.cat/angles-catala"
    urls = []
    skipped_words = []
    extracted_words = get_extracted_words(output_dir)

    for word in words_to_translate:
        if word not in extracted_words:
            urls.append(f"{base_url}/{word}")
        else:
            skipped_words.append(word)

    if skipped_words:
        print(f"Skipped already fetched words: {', '.join(skipped_words)}")

    if not urls:
        print("No new words to fetch.")
        return

    with open(user_agents_file, "r", encoding="utf-8") as file:
        user_agents = [entry["ua"] for entry in json.load(file)]

    proxies = []
    if proxies_file:
        with open(proxies_file, "r", encoding="utf-8") as file:
            proxies = [line.strip() for line in file if line.strip()]

    fetcher = URLFetcher(
        urls=urls,
        user_agents=user_agents,
        output_dir=output_dir,
        mean_sleep=20.0,
        noise_stddev=5.0,
        verify=verify,
        proxies=proxies,
    )
    fetcher.fetch()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch HTML content for error words from English to Catalan"
    )
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
        help="Directory to save the fetched HTML content",
    )
    parser.add_argument(
        "--user_agents_file",
        type=str,
        required=True,
        help="Path to the user agents JSON file",
    )
    parser.add_argument(
        "--proxies_file",
        type=str,
        required=False,
        help="Path to the proxies file",
    )
    parser.add_argument(
        "--verify",
        type=str,
        required=False,
        help="Path to the SSL certificate file",
    )

    args = parser.parse_args()
    main(
        args.src_lang,
        args.dst_lang,
        args.error_word_file,
        args.output_dir,
        args.user_agents_file,
        args.proxies_file,
        args.verify,
    )
