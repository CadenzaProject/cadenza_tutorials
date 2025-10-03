from __future__ import annotations

from collections import defaultdict
from itertools import product
from pathlib import Path
import re
import logging

logger = logging.getLogger(__name__)


class PronDictionary:
    def __init__(self, filename: str | Path | list | None = None):
        if isinstance(filename, str):
            filename = [Path(filename)]
        elif isinstance(filename, Path):
            filename = [filename]
        elif filename is None:
            filename = []

        self.pron_dict = defaultdict(set)
        for file in filename:
            self.load_from_file(file)

    def add_dict(self, filename):
        self.load_from_file(filename)

    def load_from_file(self, filename: str | Path):
        """Load pronunciations from a file."""
        if isinstance(filename, str):
            filename = Path(filename)
        if not filename.exists():
            raise FileNotFoundError(f"File {filename} does not exist.")

        with open(filename, "r") as file:
            for line in file:
                if line.strip() == "" or line.startswith("#"):
                    continue
                word, *phones = line.strip().split()
                pron = "-".join(phones)
                self.add_pronunciation(word.upper(), pron)

    def add_pronunciation(self, word, pronunciation):
        """Add a word and its pronunciation to the dictionary."""
        self.pron_dict[word].add(pronunciation)

    def lookup(self, word):
        """Get the pronunciation of a word."""
        word = word.upper()
        if self.pron_dict.get(word, None):
            return list(self.pron_dict[word])
        else:
            # Optionally return the word itself as a fallback
            self.add_pronunciation(word, f"<{word}>")

        return [f"<{word}>"]

    def get_pronunciations(self, phrase: str, sep=" ", ref=True):
        """Return all pronunciations in the dictionary."""
        words = phrase.upper().split()

        # Get list of pronunciation options for each word
        options = []
        for word in words:
            if self.lookup(word):
                if not ref:
                    options.append(self.lookup(word))
                else:
                    # If not all, just take the first pronunciation
                    options.append([self.lookup(word)[0]])
            else:
                # Optionally use the word itself as fallback
                options.append([f"<{word}>"])

        # Cartesian product of all word pronunciations
        combinations = product(*options)

        # Join each combination into a transcription string
        return [sep.join(comb) for comb in combinations]