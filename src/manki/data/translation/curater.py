"""
Generate set of jsonl files to be curated by an LLM, in this case OpenAI using its structured output and batch processing capabilities for lower cost.
"""

import argparse
import json
import os


def load_json_data(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def generate_jsonl_for_words_cleaning(words_data: list, output_file: str):
    jsonl_lines = []
    custom_id_counter = 1

    for word_entry in words_data:
        word = word_entry["word"]
        part_of_speech_list = word_entry.get("part_of_speech", [])
        definitions = word_entry.get("definitions", [])

        user_content = json.dumps(
            {
                "word": word,
                "part_of_speech": part_of_speech_list,
                "definitions": definitions,
            },
            ensure_ascii=False,
            indent=2,
        )

        jsonl_entry = {
            "custom_id": f"request-{custom_id_counter}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": 'You are a language processing system. Your task is to correct the given word entity by transforming it into a structured format. You will receive a word entity containing a word, part of speech, and other optional fields. Your response should return a corrected word entity that includes the original word, a clean word (if applicable), and the part of speech from the provided enum. If the word has multiple parts of speech, include a separate entry for each one.\n\nPlease note how some words might be written in weird ways from an automatic parsing process. Those need to be rewritten in a clear standard. As an example, "hisher" would become "his, her", and "semisupervised" would become "semi-supervised". Use always the simplest option for the clean word (e.g. "mymine" -> "my").',
                    },
                    {"role": "user", "content": user_content},
                ],
                "max_tokens": 1000,
                "response_format": {  # Corrected this section
                    "type": "json_schema",
                    "json_schema": {
                        "name": "WordEntity",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "entries": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "original_word": {"type": "string"},
                                            "clean_word": {"type": "string"},
                                            "part_of_speech": {
                                                "type": "string",
                                                "enum": [
                                                    "noun",
                                                    "verb",
                                                    "adjective",
                                                    "adverb",
                                                    "determiner",
                                                    "pronoun",
                                                    "conjunction",
                                                    "preposition",
                                                    "article",
                                                    "exclamation",
                                                    "other",
                                                ],
                                            },
                                        },
                                        "required": [
                                            "original_word",
                                            "clean_word",
                                            "part_of_speech",
                                        ],
                                        "additionalProperties": False,
                                    },
                                }
                            },
                            "required": ["entries"],
                            "additionalProperties": False,
                        },
                        "strict": True,
                    },
                },
            },
        }
        jsonl_lines.append(json.dumps(jsonl_entry))
        custom_id_counter += 1

    with open(output_file, "w", encoding="utf-8") as file:
        for line in jsonl_lines:
            file.write(line + "\n")


def generate_jsonl_for_translation_cleaning(
    curated_words: dict,
    translation_dictionary: dict,
    output_directory: str,
    target_language: str,
):
    jsonl_entries = []
    custom_id_counter = 1
    file_counter = 1

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Iterate over the curated words
    for clean_word, entries in curated_words.items():
        # Collect all relevant data for the word
        word_entries = []
        plausible_translations = []

        for entry in entries:
            part_of_speech = entry["part_of_speech"]
            level = entry.get("level", None)

            # Add the part of speech and level to word_entries
            word_entries.append({"part_of_speech": part_of_speech, "level": level})

            # Check if there are existing translations for this word
            if clean_word in translation_dictionary:
                for trans_entry in translation_dictionary[clean_word]:
                    plausible_translations.append(
                        {
                            "part_of_speech": trans_entry["part_of_speech"],
                            "translations": trans_entry.get("translations", []),
                        }
                    )

        # Construct the user content with all entries for the same word
        user_content = json.dumps(
            {
                "word": clean_word,
                "entries": word_entries,
                "plausible_translations": plausible_translations,
            },
            ensure_ascii=False,
            indent=2,
        )

        # Create the JSONL entry
        jsonl_entry = {
            "custom_id": f"request-{custom_id_counter}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a language processing system. Your task is to translate "
                            "the given word entity into the target language. The word entity contains a word, "
                            "multiple entries with part of speech and level, and plausible translations. "
                            "Your response should include the original word, the translation for each part of speech, "
                            "and the part of speech from the provided enum. If the word has multiple parts of speech, include a separate "
                            f"entry for each one. The target language is {target_language}. The translation should ideally be a single word if possible."
                        ),
                    },
                    {"role": "user", "content": user_content},
                ],
                "max_tokens": 1000,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "TranslatedWordEntity",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "entries": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "original_word": {"type": "string"},
                                            "translation": {"type": "string"},
                                            "part_of_speech": {
                                                "type": "string",
                                                "enum": [
                                                    "noun",
                                                    "verb",
                                                    "adjective",
                                                    "adverb",
                                                    "determiner",
                                                    "pronoun",
                                                    "conjunction",
                                                    "preposition",
                                                    "article",
                                                    "exclamation",
                                                    "other",
                                                ],
                                            },
                                        },
                                        "required": [
                                            "original_word",
                                            "translation",
                                            "part_of_speech",
                                        ],
                                        "additionalProperties": False,
                                    },
                                }
                            },
                            "required": ["entries"],
                            "additionalProperties": False,
                        },
                        "strict": True,
                    },
                },
            },
        }
        jsonl_entries.append(json.dumps(jsonl_entry))
        custom_id_counter += 1

        # Write to a new file every 1000 entries
        if custom_id_counter % 1000 == 1 and custom_id_counter != 1:
            output_jsonl_file = os.path.join(
                output_directory, f"translation_prompts_{file_counter}.jsonl"
            )
            with open(output_jsonl_file, "w", encoding="utf-8") as outfile:
                outfile.write("\n".join(jsonl_entries) + "\n")
            print(f"Translation prompts JSONL file created at: {output_jsonl_file}")
            jsonl_entries = []
            file_counter += 1

    # Write remaining entries to a file
    if jsonl_entries:
        output_jsonl_file = os.path.join(
            output_directory, f"translation_prompts_{file_counter}.jsonl"
        )
        with open(output_jsonl_file, "w", encoding="utf-8") as outfile:
            outfile.write("\n".join(jsonl_entries) + "\n")
        print(f"Translation prompts JSONL file created at: {output_jsonl_file}")


def curate_words_and_translations(words_file, translation_dirs, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Process English words and save to words.json (without original_word)
    with open(words_file, "r") as file:
        words_data = json.load(file)

    # Remove the "original_word" field from words_data
    processed_words_data = {
        word: [
            {"part_of_speech": entry["part_of_speech"], "level": entry.get("level", "")}
            for entry in entries
        ]
        for word, entries in words_data.items()
    }

    with open(os.path.join(output_dir, "words.json"), "w") as file:
        json.dump(processed_words_data, file, indent=4)

    # Step 2: Process translations from JSONL files
    translations = {}

    for lang, translation_dir in translation_dirs.items():
        for i in range(1, 6):  # Assuming 5 files per language
            with open(f"{translation_dir}/translation_{i}.jsonl", "r") as file:
                for line in file:
                    data = json.loads(line)
                    entries = json.loads(
                        data["response"]["body"]["choices"][0]["message"]["content"]
                    )["entries"]

                    for entry in entries:
                        english_word = entry.get("original_word")
                        translated_word = entry.get("translation")
                        part_of_speech = entry.get("part_of_speech")

                        if english_word and translated_word and part_of_speech:
                            # Initialize the word entry if not already present
                            if english_word not in translations:
                                translations[english_word] = {}

                            # Check if the part of speech has been encountered before for this word
                            if lang not in translations[english_word]:
                                translations[english_word][lang] = {}

                            if part_of_speech not in translations[english_word][lang]:
                                translations[english_word][lang][
                                    part_of_speech
                                ] = translated_word

    # Step 3: Save language-specific translations
    for lang in translation_dirs.keys():
        lang_translations = {}
        for word, data in translations.items():
            if lang in data:
                for part_of_speech, translation in data[lang].items():
                    if word not in lang_translations:
                        lang_translations[word] = []
                    lang_translations[word].append(
                        {"translation": translation, "part_of_speech": part_of_speech}
                    )

        with open(os.path.join(output_dir, f"words_{lang}.json"), "w") as file:
            json.dump(lang_translations, file, indent=4)

    # Step 4: Save combined translations across languages
    combined_translations = {}
    for english_word, lang_data in translations.items():
        combined_translations[english_word] = []
        for part_of_speech in processed_words_data[english_word]:
            part_of_speech_key = part_of_speech["part_of_speech"]
            combined_entry = {
                "part_of_speech": part_of_speech_key,
                "translations": {
                    lang: lang_data[lang][part_of_speech_key]
                    for lang in lang_data
                    if part_of_speech_key in lang_data[lang]
                },
            }
            combined_translations[english_word].append(combined_entry)

    with open(os.path.join(output_dir, "translations_ca_es_fr.json"), "w") as file:
        json.dump(combined_translations, file, indent=4)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--domain", type=str, required=True, choices=["words", "translations", "curate"]
    )
    parser.add_argument("--input_file", type=str, required=False)
    parser.add_argument("--output_file", type=str, required=False)
    parser.add_argument("--cleaned_words_file", type=str, required=False)
    parser.add_argument("--target_language", type=str, required=False)

    # Arguments for the curate functionality
    parser.add_argument("--words_file", type=str, required=False)
    parser.add_argument(
        "--translation_dirs",
        type=str,
        nargs=3,
        required=False,
        help="Provide the paths for 'ca', 'es', and 'fr' translation directories in that order.",
    )
    parser.add_argument("--output_dir", type=str, required=False)

    args = parser.parse_args()

    if args.domain == "words":
        words_data = load_json_data(args.input_file)
        generate_jsonl_for_words_cleaning(words_data, args.output_file)
    elif args.domain == "translations":
        curated_words = load_json_data(args.cleaned_words_file)
        translation_dictionary = load_json_data(args.input_file)
        generate_jsonl_for_translation_cleaning(
            curated_words,
            translation_dictionary,
            args.output_file,
            args.target_language,
        )
    elif args.domain == "curate":
        if args.translation_dirs is None or len(args.translation_dirs) != 3:
            raise ValueError(
                "Please provide three translation directories for 'ca', 'es', and 'fr' in that order."
            )

        translation_dirs = {
            "ca": args.translation_dirs[0],
            "es": args.translation_dirs[1],
            "fr": args.translation_dirs[2],
        }

        curate_words_and_translations(
            args.words_file, translation_dirs, args.output_dir
        )


if __name__ == "__main__":
    main()
