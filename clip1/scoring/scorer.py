from pprint import pprint

import jiwer
import logging
import inflect

from itertools import product
from jiwer import process_words

p = inflect.engine()
logger = logging.getLogger(__name__)


class SentenceScorer:
    def __init__(self, pron_dict=None):
        self.transformation = jiwer.Compose(
            [
                jiwer.RemoveKaldiNonWords(),
                jiwer.Strip(),
                jiwer.ToUpperCase(),
                jiwer.RemoveMultipleSpaces(),
                jiwer.RemoveWhiteSpace(replace_by_space=True),
                jiwer.ReduceToSingleSentence(),
            ]
        )
        self.transformation_towords = jiwer.Compose(
            [jiwer.ReduceToListOfListOfWords(word_delimiter=" ")]
        )

        self.pron_dict = pron_dict

    def get_word_sequence(self, sentence):
        return self.transformation(sentence)

    def lcs_length(self, ref, hyp):
        ref = ref.lower().split()
        hyp = hyp.lower().split()
        n, m = len(ref), len(hyp)
        dp = [[0] * (m + 1) for _ in range(n + 1)]

        for i in range(n):
            for j in range(m):
                if ref[i] == hyp[j]:
                    dp[i + 1][j + 1] = dp[i][j] + 1
                else:
                    dp[i + 1][j + 1] = max(dp[i][j + 1], dp[i + 1][j])
        return dp[n][m]

    def score(self, ref, hyp, show_alignment=False):
        if isinstance(ref, str):
            _ref_form = [ref]
        else:
            _ref_form = ref.copy()

        if isinstance(hyp, str):
            _hyp_forms = [hyp]
        else:
            _hyp_forms = hyp.copy()

        hyp_forms, ref_forms = [], []
        hyp_match_pron_ori= {}
        for hyp_form in _hyp_forms:
            hyp_form = self.transformation(hyp_form)
            hyp_forms.extend(self.pron_dict.get_pronunciations(hyp_form, ref=False))
            for pron in hyp_forms:
                hyp_match_pron_ori[pron] = hyp_form

        for ref_form in _ref_form:
            ref_form = self.transformation(ref_form)
            ref_forms.extend(self.pron_dict.get_pronunciations(ref_form, ref=True))

        alternatives = [(x, y) for x, y in product(hyp_forms, ref_forms)]

        measures = [
            process_words(
                ref,
                hyp,
                reference_transform=self.transformation_towords,
                hypothesis_transform=self.transformation_towords,
            )
            for hyp, ref in alternatives
        ]

        hits = [m.hits for m in measures]
        best_index = hits.index(max(hits))

        if show_alignment:
            print("Alignment:")
            print(jiwer.visualize_alignment(measures[best_index], show_measures=False))



        return {
            "prompt": ref.lower(),
            "response": hyp_match_pron_ori[alternatives[best_index][0]].lower(),
            "total_words": len(measures[best_index].references[0]),
            "hits": measures[best_index].hits,
            "correctness": measures[best_index].hits
            / len(measures[best_index].references[0]),
        }
