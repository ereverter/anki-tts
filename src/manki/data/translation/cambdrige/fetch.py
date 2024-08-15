import argparse
import json

from manki.data.translation.fetcher import URLFetcher, load_words


def main(base_url, words_file, user_agents_file, output_dir, proxies):
    words = load_words(words_file)
    urls = [f"{base_url}{word}" for word in words]

    with open(user_agents_file, "r", encoding="utf-8") as file:
        user_agents = [entry["ua"] for entry in json.load(file)]

    fetcher = URLFetcher(urls, proxies, user_agents, output_dir)
    fetcher.fetch()

    for url, path in fetcher.url_index.items():
        print(f"{url}: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch translations from Cambridge Dictionary"
    )
    parser.add_argument(
        "--base_url",
        type=str,
        required=True,
        help="The base URL for the Cambridge Dictionary.",
    )
    parser.add_argument(
        "--words_file",
        type=str,
        required=True,
        help="The file containing the list of words to translate.",
    )
    parser.add_argument(
        "--user_agents_file",
        type=str,
        required=True,
        help="The file containing the list of user agents.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="The directory to save the fetched translations.",
    )
    parser.add_argument(
        "--proxies",
        type=str,
        default=None,
        help="Optional proxy settings.",
    )

    args = parser.parse_args()
    main(
        args.base_url,
        args.words_file,
        args.user_agents_file,
        args.output_dir,
        args.proxies,
    )
