"""
Fetches HTML content from a list of URLs and stores it in a directory.
"""

import json
import os
import time
from itertools import cycle
from typing import Dict, List, Optional

import numpy as np
from requests.sessions import Session
from tqdm import tqdm


class URLFetcher:
    def __init__(
        self,
        urls: List[str],
        proxies: Optional[List[str]] = None,
        user_agents: List[str] = None,
        output_dir: str = "scraping",
        mean_sleep: float = 20.0,
        noise_stddev: float = 5.0,
        create_index: bool = True,
        force_index: bool = True,
        verify: Optional[str] = None,
    ):
        self.urls = urls
        self.proxies = cycle(proxies) if proxies else None
        self.user_agents = cycle(user_agents) if user_agents else None
        self.output_dir = output_dir
        self.mean_sleep = mean_sleep
        self.noise_stddev = noise_stddev
        os.makedirs(output_dir, exist_ok=True)
        self.index_path = os.path.join(output_dir, "index.json")
        self.force_index = force_index
        self.create_index = create_index
        self.url_index: Dict[str, str] = self.load_index(self.index_path)
        self.verify = verify

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

                response = session.get(url, verify=self.verify)

                if response.status_code == 200:
                    file_path = self._store_result(url, response.text)
                    self.url_index[url] = file_path
                elif response.status_code == 429:
                    print("Too many requests")
                    break
                elif response.status_code == 500:
                    print("Internal server error")
                    break
                else:
                    print(f"Something went wrong with {url}")
                    print(response)

            sleep_time = get_sleep_time(self.mean_sleep, self.noise_stddev)
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


def get_sleep_time(mean_sleep: float, stddev_sleep: float, min_sleep: float = 5.0):
    sleep_time = np.random.normal(mean_sleep, stddev_sleep)
    if np.random.random() < 0.1:
        long_pause = np.random.normal(2 * mean_sleep, stddev_sleep)
        sleep_time += long_pause

    if sleep_time <= min_sleep:
        sleep_time = get_sleep_time(mean_sleep, stddev_sleep, min_sleep)

    return sleep_time
