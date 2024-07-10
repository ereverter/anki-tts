import json
import os
import time
from itertools import cycle
from random import uniform
from typing import Dict, List, Optional

from requests.sessions import Session
from tqdm import tqdm


class URLFetcher:
    def __init__(
        self,
        urls: List[str],
        proxies: Optional[List[str]] = None,
        user_agents: List[str] = None,
        output_dir: str = "scrapping",
        min_sleep: float = 1.0,
        max_sleep: float = 3.0,
        create_index: bool = True,
        force_index: bool = True,
    ):
        self.urls = urls
        self.proxies = cycle(proxies) if proxies else None
        self.user_agents = cycle(user_agents) if user_agents else None
        self.output_dir = output_dir
        self.min_sleep = min_sleep
        self.max_sleep = max_sleep
        os.makedirs(output_dir, exist_ok=True)
        self.index_path = os.path.join(output_dir, "index.json")
        self.force_index = force_index
        self.create_index = create_index
        self.url_index: Dict[str, str] = self.load_index(self.index_path)

    def load_index(self, index_path: str) -> Dict[str, str]:
        if os.path.exists(index_path) and not self.force_index:
            with open(index_path, "r", encoding="utf-8") as file:
                return json.load(file)
        return self.build_index_from_files()

    def build_index_from_files(self) -> Dict[str, str]:
        index = {}
        for file_name in os.listdir(self.output_dir):
            if file_name.endswith(".html"):
                url = file_name.rsplit(".", 1)[0].replace("_", "/")
                file_path = os.path.join(self.output_dir, file_name)
                index[url] = file_path
        self.save_index(index)
        return index

    def save_index(self, index: Optional[Dict[str, str]] = None):
        if index is None:
            index = self.url_index
        with open(self.index_path, "w", encoding="utf-8") as file:
            json.dump(index, file, ensure_ascii=False, indent=4)

    def fetch(self):
        progress_bar = tqdm(self.urls, desc="Fetching URLs")
        for url in progress_bar:
            if url in self.url_index:
                continue

            progress_bar.set_description(f"Fetching {url}")

            headers = {"User-Agent": next(self.user_agents)} if self.user_agents else {}

            with Session() as session:
                if self.proxies:
                    proxy = next(self.proxies)
                    session.proxies.update({"http": proxy, "https": proxy})
                session.headers.update(headers)

                response = session.get(url)

                if response.status_code == 200:
                    file_path = self._store_result(url, response.text)
                    self.url_index[url] = file_path

            sleep_time = uniform(self.min_sleep, self.max_sleep)
            time.sleep(sleep_time)

        if self.create_index:
            self.save_index()

    def _store_result(self, url: str, content: str) -> str:
        file_name = self._sanitize_filename(url)
        file_path = os.path.join(self.output_dir, f"{file_name}.html")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        return file_path

    @staticmethod
    def _sanitize_filename(url: str) -> str:
        return "".join([c if c.isalnum() else "_" for c in url])


def load_words(file_path: str) -> List[str]:
    with open(file_path, "r", encoding="utf-8") as file:
        words_data = json.load(file)
    return [entry["word"] for entry in words_data]


def main():
    base_url = "https://dictionary.cambridge.org/dictionary/english-catalan/"
    words_file = "data/processed/common_words/words.json"
    proxies = None
    user_agents_file = "data/raw/scrapping/user_agents.json"
    output_dir = "data/raw/dictionaries/cambridge_test"

    words = load_words(words_file)
    urls = [f"{base_url}{word}" for word in words]

    with open(user_agents_file, "r", encoding="utf-8") as file:
        user_agents = [entry["ua"] for entry in json.load(file)]

    fetcher = URLFetcher(urls, proxies, user_agents, output_dir)
    fetcher.fetch()

    # Print the URL index
    for url, path in fetcher.url_index.items():
        print(f"{url}: {path}")


if __name__ == "__main__":
    main()
