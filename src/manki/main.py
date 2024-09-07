import argparse
import sys

from manki.anki.main import main as anki_main


def main():
    parser = argparse.ArgumentParser(
        description="Manki CLI - Manage Anki decks, TTS, and more."
    )

    subparsers = parser.add_subparsers(dest="module", required=True)

    anki_parser = subparsers.add_parser("anki", help="Manage Anki-related tasks")
    args, unknown_args = parser.parse_known_args()

    if args.module == "anki":
        sys.argv = ["manki anki"] + unknown_args
        anki_main()


if __name__ == "__main__":
    main()
