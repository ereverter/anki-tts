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
        base_url: str,
        words: List[str],
        proxies: Optional[List[str]] = None,
        user_agents_file: str = "data/raw/scrapping/user_agents.json",
        output_dir: str = "fetched_pages",
        min_sleep: float = 1.0,
        max_sleep: float = 3.0,
        index_file: str = "index.json",
        force_index: bool = True,
    ):
        self.base_url = base_url
        self.words = words
        self.proxies = cycle(proxies) if proxies else None
        self.user_agents = cycle(self.load_user_agents(user_agents_file))
        self.output_dir = output_dir
        self.min_sleep = min_sleep
        self.max_sleep = max_sleep
        os.makedirs(output_dir, exist_ok=True)
        self.index_path = os.path.join(output_dir, index_file)
        self.force_index = force_index
        self.word_index: Dict[str, str] = self.load_index(self.index_path)

    @staticmethod
    def load_user_agents(file_path: str) -> List[str]:
        with open(file_path, "r", encoding="utf-8") as file:
            user_agents_data = json.load(file)
        return [entry["ua"] for entry in user_agents_data]

    @staticmethod
    def load_words(file_path: str) -> List[str]:
        with open(file_path, "r", encoding="utf-8") as file:
            words_data = json.load(file)
        return [entry["word"] for entry in words_data]

    def load_index(self, index_path: str) -> Dict[str, str]:
        if os.path.exists(index_path) and not self.force_index:
            with open(index_path, "r", encoding="utf-8") as file:
                return json.load(file)
        return self.build_index_from_files()

    def build_index_from_files(self) -> Dict[str, str]:
        index = {}
        for file_name in os.listdir(self.output_dir):
            if file_name.endswith(".html"):
                word = file_name.rsplit(".", 1)[0].replace("_", " ")
                file_path = os.path.join(self.output_dir, file_name)
                index[word] = file_path
        self.save_index(index)
        return index

    def save_index(self, index: Optional[Dict[str, str]] = None):
        if index is None:
            index = self.word_index
        with open(self.index_path, "w", encoding="utf-8") as file:
            json.dump(index, file, ensure_ascii=False, indent=4)

    def fetch(self):
        progress_bar = tqdm(self.words, desc="Fetching words")
        for word in progress_bar:
            if word in self.word_index:
                continue

            progress_bar.set_description(f"Fetching {word}")

            url = f"{self.base_url}{word}"
            user_agent = next(self.user_agents)
            headers = {"User-Agent": user_agent}

            with Session() as session:
                if self.proxies:
                    proxy = next(self.proxies)
                    session.proxies.update({"http": proxy, "https": proxy})
                session.headers.update(headers)

                response = session.get(url)

                if response.status_code == 200:
                    file_path = self._store_result(word, response.text)
                    self.word_index[word] = file_path

            sleep_time = uniform(self.min_sleep, self.max_sleep)
            time.sleep(sleep_time)

    def _store_result(self, word: str, content: str) -> str:
        file_name = self._sanitize_filename(word)
        file_path = os.path.join(self.output_dir, f"{file_name}.html")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        return file_path

    @staticmethod
    def _sanitize_filename(url: str) -> str:
        return "".join([c if c.isalnum() else "_" for c in url])


# Example usage:
if __name__ == "__main__":
    base_url = "https://dictionary.cambridge.org/dictionary/english-catalan/"
    words_file = "data/processed/common_words/words.json"
    proxies = None
    user_agents_file = "data/raw/scrapping/user_agents.json"
    output_dir = "data/raw/dictionaries/cambridge_en_ca"

    words = URLFetcher.load_words(words_file)
    fetcher = URLFetcher(base_url, words, proxies, user_agents_file, output_dir)
    fetcher.fetch()

    # Print the word index
    for word, path in fetcher.word_index.items():
        print(f"{word}: {path}")
