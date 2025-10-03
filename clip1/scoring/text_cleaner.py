from alternative_words import AlternativeWords
from spellings import CheckSpellings

import inflect
import jiwer
import re

p = inflect.engine()

class NormalizeNumbers(jiwer.AbstractTransform):
    def process_string(self, s: str):
        def replace_decimal(match):
            num_str = match.group(0)
            whole, decimal = num_str.split(".")
            whole_spoken = p.number_to_words(whole, andword="").replace("-", " ")
            decimal_spoken = " ".join(p.number_to_words(d) for d in decimal)
            return f"{whole_spoken} point {decimal_spoken}"

        def replace_integer(match):
            num_str = match.group(0)
            return p.number_to_words(num_str, andword="").replace("-", " ")

        # Replace decimals first (to avoid partial integer matches)
        text = re.sub(r"\d+\.\d+", replace_decimal, s)

        # Then replace remaining integers
        text = re.sub(r"\b\d+\b", replace_integer, text)
        return text.lower()

class MyRemovePunctuation(jiwer.AbstractTransform):
    """Replacement fo%pip listr jiwer's remove punctuation that allows more control."""

    def __init__(self, symbols):
        self.substitutions = f"[{symbols}]"

    def process_string(self, s):
        return re.sub(self.substitutions, "", s)

class TextCleaner:
    def __init__(self, contractions_file: str = None, spellings_file: str = None, alternative_words_file: str = None):
        """
        Initialize the TextCleaner with optional files for contractions and spellings.

        Args:
            contractions_file (str): Path to the contractions file.
            spellings_file (str): Path to the spellings file.
            alternative_words_file (str): Path to the alternative words file (not used in this implementation).

        """
        self.numbers = NormalizeNumbers()
        self.punctuation = MyRemovePunctuation(";!*#,.′’‘_()")

        self.contraction = None
        if contractions_file:
            self.contraction = AlternativeWords(contractions_file)

        self.spelling = None
        if spellings_file:
            self.spelling = CheckSpellings(spellings_file)

        self.alternative_words = None
        if alternative_words_file:
            self.alternative_words = AlternativeWords(alternative_words_file)

    def __call__(self, text: str, descending: bool = False) -> list[str]:
        """
        Clean the text by removing punctuation and applying contractions.
        """

        # Correct spellings
        if self.spelling:
            text = self.spelling.fix_misspellings(text)

        # Number to text
        text = self.numbers.process_string(text)

        # Remove punctuation
        text = self.punctuation.process_string(text)

        # Correct spellings again to recover some errors with contractions
        if self.spelling:
            text = self.spelling.fix_misspellings(text)

        # Handle alternative words
        if self.alternative_words:
            text = self.alternative_words.make_sentence_forms(text)

        # Expand Contractions
        if self.contraction:
            text = self.contraction.make_sentence_forms(text)
        else:
            text = [text]

        # return sorted
        return sorted(text, key=lambda s: len(s.split()), reverse=descending)
