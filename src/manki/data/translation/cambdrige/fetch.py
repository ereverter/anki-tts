import json

from ..fetcher import URLFetcher, load_words


def main():
    base_url = "https://dictionary.cambridge.org/dictionary/english-catalan/"
    words_file = "data/processed/common_words/words.json"
    user_agents_file = "data/raw/scrapping/user_agents.json"
    output_dir = "data/raw/dictionaries/cambridge_en_ca"

    words = load_words(words_file)
    urls = [f"{base_url}{word}" for word in words]

    with open(user_agents_file, "r", encoding="utf-8") as file:
        user_agents = [entry["ua"] for entry in json.load(file)]

    proxies = None

    fetcher = URLFetcher(urls, proxies, user_agents, output_dir)
    fetcher.fetch()

    for url, path in fetcher.url_index.items():
        print(f"{url}: {path}")


if __name__ == "__main__":
    main()
