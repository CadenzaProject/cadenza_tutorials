import re


class CheckSpellings:
    """
    Class to check and correct common misspellings in text based on a provided dictionary.
    """

    def __init__(self, spellings_file: str):
        """
        Constructor

        Args:
            spellings_file (str): Path to the CSV file with common misspellings.
        """
        self.spellings = {}
        with open(spellings_file, "r") as f:
            for line in f:
                parts = line.strip().split(",", 1)
                if len(parts) == 2:
                    self.spellings[parts[0].lower()] = parts[1].lower()
                else:
                    self.spellings[parts[0].lower()] = ""

    def fix_misspellings(self, text: str) -> str:
        """
        Fix common misspellings in the text based on a provided dictionary.
        Replace whole words, even when surrounded by punctuation.
        Args:
            text (str): Input text to be corrected.
        Returns:
            str: Corrected text.
        """

        def replace_word(match):
            word = match.group(0)
            return self.spellings.get(word.lower(), word)

        # Match word-like tokens including punctuation like (), [], etc.
        # This will match (something), 'hello', etc.
        pattern = r"[^\s]+"
        corrected_text = re.sub(pattern, replace_word, text)
        return corrected_text