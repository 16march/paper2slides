from __future__ import annotations

import unittest

from scripts.eval_reading_order import first_match_indices, normalize_text, strip_citation_spans


class ReadingOrderEvalTest(unittest.TestCase):
    def test_normalize_text_collapses_unicode_quotes_hyphens_and_diacritics(self) -> None:
        normalized = normalize_text("English-Japanese text’s role in Lučić-style evaluation")
        self.assertEqual(normalized, "english japanese text s role in lucic style evaluation")

    def test_first_match_indices_uses_normalized_contains_matching(self) -> None:
        matches = first_match_indices(
            ["Text simplification aims to reduce a text's difficulty"],
            [
                {
                    "text": "Text simplification aims to reduce a text’s difficulty for readers.",
                    "reading_order_index": 1,
                }
            ],
            contains=True,
        )
        self.assertEqual(matches, [0])

    def test_strip_citation_spans_removes_parenthetical_author_year_citations(self) -> None:
        stripped = strip_citation_spans(
            "Dense retrieval (Lee et al., 2019; Karpukhin et al., 2020) is currently the de facto implementation."
        )
        self.assertEqual(
            stripped,
            "Dense retrieval is currently the de facto implementation.",
        )

    def test_first_match_indices_ignores_inline_citation_spans_for_paragraph_matching(self) -> None:
        matches = first_match_indices(
            ["We present MINDER, an advanced generative retrieval system"],
            [
                {
                    "text": "We present MINDER (Li et al., 2023c), an advanced generative retrieval system, as the base model.",
                    "reading_order_index": 1,
                }
            ],
            contains=True,
        )
        self.assertEqual(matches, [0])
