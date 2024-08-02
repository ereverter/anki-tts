import json
import os
from typing import List

from manki.data.translation.fetcher import URLFetcher


def extract_words_from_errors(file_path: str) -> List[str]:
    with open(file_path, "r", encoding="utf-8") as file:
        error_paths = json.load(file)
    words = [path.split("/")[-1].replace(".html", "") for path in error_paths]
    return words


def main():
    src_lang = "en"
    dst_lang = "ca"
    error_word_file = (
        f"data/processed/dictionaries/cambridge/{src_lang}_{dst_lang}_errors.json"
    )
    words_to_translate = extract_words_from_errors(error_word_file)
    output_dir = f"data/raw/dictionaries/diccionari_cat/{src_lang}_{dst_lang}"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    base_url = "https://diccionari.cat/cerca/diccionari-angles-catala?search_api_fulltext_cust={word}&field_faceta_cerca_1=5059&show=title"
    urls = [base_url.format(word=word) for word in words_to_translate]

    user_agents_file = "data/raw/scrapping/user_agents.json"
    with open(user_agents_file, "r", encoding="utf-8") as file:
        user_agents = [entry["ua"] for entry in json.load(file)]

    fetcher = URLFetcher(
        urls, None, user_agents, output_dir, min_sleep=1.0, max_sleep=5.0, verify=False
    )
    fetcher.fetch()

    for url, path in fetcher.url_index.items():
        print(f"{url}: {path}")


if __name__ == "__main__":
    main()
