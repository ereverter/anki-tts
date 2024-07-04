from typing import List, Optional, Tuple

import fitz
from tqdm import tqdm

from manki.data.domain import WordEntry, WordParser


class OxfordCommonWordParser(WordParser):
    def __init__(self, file_path: str):
        self.font_mapping = {
            "MyriadPro-Light": "metadata",
            "UtopiaStd-Regular": "title",
            "MyriadPro-LightIt": "pos",
            "UtopiaStd-Italic": "comma",
            "UtopiaStd-Bold": "level",
            "MyriadPro-Regular": "word",
            "UtopiaStd-Semibold": "subheading",
        }

        self.file_path = file_path

    def parse_information(self) -> List[WordEntry]:
        doc = fitz.open(self.file_path)
        extracted_data = []
        current_word = None
        current_level = None

        for page_num in tqdm(range(len(doc))):
            page = doc.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                lines = block.get("lines", [])
                for line in lines:
                    spans = line["spans"]
                    extracted_data, current_word, current_level = self._process_spans(
                        spans, current_word, current_level, extracted_data
                    )

        if current_word:
            extracted_data.append(current_word)

        return extracted_data

    def _process_spans(
        self,
        spans: List[dict],
        current_word: Optional[WordEntry],
        current_level: Optional[str],
        extracted_data: List[WordEntry],
    ) -> Tuple[List[WordEntry], Optional[WordEntry], Optional[str]]:
        for span in spans:
            text, font, element_type = self._process_span(span)

            if self._is_level_indicator(text, element_type):
                current_level = text
                continue

            if element_type == "word":
                if current_word:
                    extracted_data.append(current_word)
                current_word = WordEntry(
                    word=self._remove_numeric_elements(text),
                    part_of_speech=[],
                    definitions=[],
                    level=current_level,
                )
            elif current_word:
                if element_type == "pos":
                    current_word.part_of_speech.append(text)
                elif element_type == "metadata" and "(" in text:
                    current_word.definitions.append(text)
                elif element_type == "explanation" and current_word.definitions:
                    current_word.definitions[-1] += f" {text}"

        return extracted_data, current_word, current_level

    def _process_span(self, span: dict) -> Tuple[str, str, str]:
        text = span["text"].strip()
        font = span["font"]
        element_type = self.font_mapping.get(font, "unknown")
        return text, font, element_type

    def _is_level_indicator(self, text: str, element_type: str) -> bool:
        return element_type == "level" and text.isalnum() and len(text) == 2

    def _remove_numeric_elements(self, input_string: str) -> str:
        return "".join(filter(str.isalpha, input_string))


if __name__ == "__main__":
    import argparse
    import json
    import os

    parser = argparse.ArgumentParser(
        description="Extract information from an Oxford CW PDF and save it as JSON."
    )
    parser.add_argument(
        "--pdf_path",
        type=str,
        required=True,
        help="The path to the PDF file to process.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="The directory to save the extracted JSON data.",
    )

    parser.add_argument(
        "--file_name",
        type=str,
        required=True,
        help="The file name of the JSON.",
    )

    args = parser.parse_args()

    parser = OxfordCommonWordParser(file_path=args.pdf_path)
    extracted_data = parser.parse_information()

    output_path = os.path.join(args.output_dir, f"{args.file_name}.json")
    os.makedirs(args.output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(
            [entry.model_dump() for entry in extracted_data],
            json_file,
            ensure_ascii=False,
            indent=4,
        )

    print(f"Extracted data saved to: {output_path}")
    print(f"Number of entries extracted: {len(extracted_data)}")
