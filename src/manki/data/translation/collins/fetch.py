import json
import os

from ..fetcher import URLFetcher, load_words


def main():
    base_url = "https://www.collinsdictionary.com/us/dictionary/english-french/"
    words_file = "data/processed/common_words/words.json"
    user_agents_file = "data/raw/scrapping/user_agents.json"
    output_dir = "data/raw/dictionaries/collins_en_fr"

    words = load_words(words_file)
    urls = [f"{base_url}{word}" for word in words]

    with open(user_agents_file, "r", encoding="utf-8") as file:
        user_agents = [entry["ua"] for entry in json.load(file)]

    fetcher = URLFetcher(urls, None, user_agents, output_dir)
    fetcher.fetch()

    for url, path in fetcher.url_index.items():
        print(f"{url}: {path}")


if __name__ == "__main__":
    main()
