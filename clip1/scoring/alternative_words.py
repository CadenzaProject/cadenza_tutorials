from __future__ import annotations

import re
from collections import defaultdict
from itertools import product


class AlternativeWords:
    """
    Class to handle alternative spellings. The class takes a CSV file
    with two columns:

    - Column 1: word or phrase to be replaced
    - Column 2: alternative spelling or phrase

    The class can generate all possible sentence forms by replacing words/phrases
    with their alternatives.
    """

    def __init__(self, alternative_file: str):
        """Constructor

        Args:
            alternative_file (str): Path to the CSV file with alternative words.
        """
        self.alternative_dict = defaultdict(list)
        with open(alternative_file, "r") as f:
            for line in f:
                parts = [x.strip() for x in line.strip().split(",", 1)]
                if len(parts) == 1:
                    k, v = parts[0], ""
                else:
                    k, v = parts
                self.alternative_dict[k.lower()].append(v.lower())

        # Create regex pattern
        pattern = "|".join(
            rf"\b{re.escape(k)}\b" if "'" not in k else rf"(?<!\w){re.escape(k)}(?!\w)"
            for k in self.alternative_dict.keys()
        )

        self.contra_re = re.compile(f"({pattern})", re.IGNORECASE)

    def make_sentence_forms(self, sentence: str | list) -> list[str]:
        """ Generate all possible forms of a sentence by expanding using alternatives.

        Args:
            sentence (str or list): Input sentence or list of sentences.
        Returns:
            list: List of all possible sentence forms.
        """
        if isinstance(sentence, str):
            sentence = [sentence]

        APOST = r"['\u2019]"
        token_re = re.compile(
            rf"[a-z]+(?:{APOST}[a-z]+)*(?:{APOST})?|{APOST}[a-z]+|[^\w\s]",
            re.IGNORECASE,
        )

        sentence_forms = []
        for s in sentence:
            parts = token_re.findall(s.lower())

            # For each part, list all possible variants
            options = [
                self.alternative_dict[p] + [p] if p in self.alternative_dict else [p]
                for p in parts
            ]

            sentence_forms += [" ".join(s).strip() for s in product(*options)]
        return list(set(sentence_forms))