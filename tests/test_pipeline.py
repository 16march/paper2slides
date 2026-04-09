from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pdf2slides.pipeline import run_pipeline
from pdf2slides.stages import (
    clean_caption_text,
    classify_paragraph,
    detect_layout_blocks,
    infer_abstract,
    infer_title,
    looks_like_section_header,
    normalize_heading,
    parse_structure,
    reconstruct_column_order_page,
    starts_new_section,
    split_into_pages,
    split_into_paragraphs,
)


SAMPLE_TEXT = """Test Paper Title

Abstract

This is the first abstract sentence. This is the second abstract sentence.

1 Introduction

This is the introduction paragraph. It has enough content to become bullets.

2 Method

2.1 Details

This is the subsection paragraph. It should be captured under Method.

Figure 1: Sample figure caption.

We define x = y + z for the placeholder formula example.
"""


class PipelineSmokeTest(unittest.TestCase):
    def test_split_into_paragraphs_joins_blank_split_numbered_heading(self) -> None:
        paragraphs = split_into_paragraphs(
            "3\n\nMethodology\n\nThis section describes the method in enough detail for parsing."
        )
        self.assertEqual(paragraphs[0], "3 Methodology")
        self.assertEqual(
            paragraphs[1],
            "This section describes the method in enough detail for parsing.",
        )

    def test_split_into_paragraphs_joins_parent_heading_before_subsection(self) -> None:
        paragraphs = split_into_paragraphs(
            "3\n\nMethod\n\n3.1 Overview\n\nThis section starts immediately with a subsection."
        )
        self.assertEqual(paragraphs[0], "3 Method")
        self.assertEqual(paragraphs[1], "3.1 Overview")

    def test_split_into_paragraphs_joins_short_heading_continuation_fragment(self) -> None:
        paragraphs = split_into_paragraphs(
            "5.1 In-context learning with noisy ASR\ntranscriptions\n\nThis subsection starts here."
        )
        self.assertEqual(paragraphs[0], "5.1 In-context learning with noisy ASR transcriptions")
        self.assertTrue(looks_like_section_header(paragraphs[0]))

    def test_split_into_paragraphs_joins_blank_split_nested_heading_before_child_heading(self) -> None:
        paragraphs = split_into_paragraphs(
            "4.2\n\nResults\n\n4.2.1 Overall Results\n\nThis subsection starts here."
        )
        self.assertEqual(paragraphs[0], "4.2 Results")
        self.assertEqual(paragraphs[1], "4.2.1 Overall Results")

    def test_split_into_paragraphs_breaks_inline_paragraph_at_discourse_start(self) -> None:
        paragraphs = split_into_paragraphs(
            "Text simplification helps users understand difficult content.\n"
            "Different groups of people require different simplification strategies.\n"
            "This second paragraph continues with more detail."
        )
        self.assertEqual(
            paragraphs,
            [
                "Text simplification helps users understand difficult content.",
                "Different groups of people require different simplification strategies. This second paragraph continues with more detail.",
            ],
        )

    def test_split_into_paragraphs_breaks_after_short_previous_line(self) -> None:
        paragraphs = split_into_paragraphs(
            "The first paragraph ends here.\n"
            "We propose a new benchmark for evaluation.\n"
            "This paragraph continues with more detail."
        )
        self.assertEqual(
            paragraphs,
            [
                "The first paragraph ends here.",
                "We propose a new benchmark for evaluation. This paragraph continues with more detail.",
            ],
        )

    def test_split_into_paragraphs_splits_inline_labels_inside_long_paragraph(self) -> None:
        paragraphs = split_into_paragraphs(
            "We present a retrieval system with strong performance.\n"
            "Identifiers. The model uses title and query views.\n"
            "Training. The model is optimized with sequence loss."
        )
        self.assertEqual(
            paragraphs,
            [
                "We present a retrieval system with strong performance.",
                "Identifiers. The model uses title and query views.",
                "Training. The model is optimized with sequence loss.",
            ],
        )

    def test_split_into_paragraphs_splits_multi_caption_block(self) -> None:
        paragraphs = split_into_paragraphs(
            "Figure 2: Accuracy by setting.\n"
            "Table 4: Main results with prompts."
        )
        self.assertEqual(
            paragraphs,
            [
                "Figure 2: Accuracy by setting.",
                "Table 4: Main results with prompts.",
            ],
        )

    def test_detect_layout_blocks_keeps_table_reference_sentence_as_paragraph(self) -> None:
        pages = detect_layout_blocks(split_into_pages("Dummy Title\n\nTable 2 gives the overall results on the test set."))
        self.assertEqual(pages[0].blocks[1].block_type, "paragraph")

    def test_clean_caption_text_drops_short_trailing_table_header_noise(self) -> None:
        self.assertEqual(
            clean_caption_text("Table 3: Analysis on DGR with different teacher models. Methods"),
            "Table 3: Analysis on DGR with different teacher models.",
        )

    def test_classify_paragraph_keeps_narrative_text_with_inline_equation_as_paragraph(self) -> None:
        paragraph = (
            "Inference. During the inference process, given a query text, the trained autoregressive "
            "language model AM could generate several predicted identifiers via beam search. "
            "The rank list is denoted as Rstu = (p1, ..., pN)."
        )
        self.assertEqual(classify_paragraph(paragraph, index=3), "paragraph")

    def test_classify_paragraph_keeps_budget_formulation_with_prose_as_paragraph(self) -> None:
        paragraph = (
            "To conduct budget-constrained tool learning, we first propose a simplified formulation. "
            "For any integer i in [1, n], we use ci to represent the cost of using the tool ti once."
        )
        self.assertEqual(classify_paragraph(paragraph, index=4), "paragraph")

    def test_classify_paragraph_keeps_equation_only_block_as_formula_like(self) -> None:
        paragraph = "F F N (x) = ReLU (xW1 + b1 )W2 + b2"
        self.assertEqual(classify_paragraph(paragraph, index=5), "formula_like")

    def test_reconstruct_column_order_page_flattens_left_then_right_columns(self) -> None:
        page = "\n".join(
            [
                "Centered Title",
                "",
                "Left intro line one                          Right intro line one",
                "Left intro line two                          Right intro line two",
                "Left second para                             Right second para",
            ]
        )
        rebuilt = reconstruct_column_order_page(page)
        self.assertEqual(
            rebuilt,
            "\n".join(
                [
                    "Centered Title",
                    "",
                    "Left intro line one",
                    "Left intro line two",
                    "Left second para",
                    "",
                    "Right intro line one",
                    "Right intro line two",
                    "Right second para",
                ]
            ),
        )

    def test_section_header_filter_rejects_front_matter_and_formula_noise(self) -> None:
        self.assertFalse(looks_like_section_header("3 Key Laboratory of Archival Intelligent Development and Service, NAAC"))
        self.assertFalse(looks_like_section_header("2 KSL ="))
        self.assertFalse(looks_like_section_header("Method"))
        self.assertFalse(looks_like_section_header("claim"))
        self.assertFalse(looks_like_section_header("1.50 Case Study"))
        self.assertTrue(looks_like_section_header("Data"))
        self.assertTrue(looks_like_section_header("Sentence Filtering"))
        self.assertTrue(looks_like_section_header("4.1 Datasets, Pruning, BATS Vectors"))
        self.assertTrue(starts_new_section("2.2 Related Work"))

    def test_normalize_heading_cleans_number_noise_and_formatting(self) -> None:
        self.assertEqual(normalize_heading("3.2.2 3.2 Selective Prefix Tuning"), "Selective Prefix Tuning")
        self.assertEqual(normalize_heading("0.0 3.3 Planned v.s. Actual Tool Usage"), "Planned v.s. Actual Tool Usage")
        self.assertEqual(normalize_heading("RQ1 : From Literature to Practice"), "RQ1: From Literature to Practice")
        self.assertEqual(normalize_heading("Effect of Threshold τ"), "Effect of Threshold T")
        self.assertEqual(normalize_heading("② Essay Generation"), "Essay Generation")
        self.assertEqual(
            normalize_heading("4.3.1 Difference Between Machine Translation and Semantic Parsing"),
            "Translation and Semantic Parsing",
        )

    def test_parse_structure_keeps_empty_grouping_subsections(self) -> None:
        raw_text = """Sample Title

4 Experiments

4.1

Settings

4.1.1 Models

We evaluate a baseline model here.

4.2

Results

4.2.1 Overall Results

The model performs well on the benchmark.
"""
        pages = detect_layout_blocks(split_into_pages(raw_text))
        document = parse_structure(Path("sample.pdf"), pages)
        experiments = next(section for section in document.sections if section.heading == "Experiments")
        self.assertEqual(
            [subsection.heading for subsection in experiments.subsections],
            ["Settings", "Models", "Results", "Overall Results"],
        )

    def test_infer_title_joins_multiline_title(self) -> None:
        raw_text = """Decomposing Argumentative Essay Generation via
Dialectical Planning of Complex Reasoning
Yuhang He1,5 , Jianzhu Bao1,5

Abstract
"""
        pages = split_into_pages(raw_text)
        title = infer_title(Path("sample.pdf"), pages)
        self.assertEqual(
            title,
            "Decomposing Argumentative Essay Generation via Dialectical Planning of Complex Reasoning",
        )

    def test_infer_abstract_skips_short_noise_after_abstract_heading(self) -> None:
        raw_text = """Sample Title

Abstract

Add & Norm

The prevalent approach for optimizing pretrained language models in downstream tasks
is fine-tuning. However, it is both time-consuming and memory-inefficient.

1 Introduction
"""
        pages = split_into_pages(raw_text)
        abstract = infer_abstract(pages)
        self.assertTrue(abstract.startswith("The prevalent approach for optimizing pretrained language models"))
        self.assertNotIn("Add & Norm", abstract)

    def test_infer_abstract_skips_multiple_short_noise_lines_before_body(self) -> None:
        raw_text = """Sample Title

Abstract

Budget Constraint
Method

Despite intensive efforts devoted to tool learning, the problem of budget-constrained tool
learning has been widely overlooked.

1 Introduction
"""
        pages = split_into_pages(raw_text)
        abstract = infer_abstract(pages)
        self.assertTrue(abstract.startswith("Despite intensive efforts devoted to tool learning"))
        self.assertNotIn("Budget Constraint", abstract)
        self.assertNotIn("Method", abstract)

    def test_run_pipeline_writes_expected_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            input_pdf = tmp_path / "sample.pdf"
            input_pdf.write_bytes(b"%PDF-1.4\n% placeholder test file\n")

            def fake_extract_text_from_pdf(_pdf_path: Path, output_txt: Path, pdftotext_mode: str = "default") -> str:
                self.assertEqual(pdftotext_mode, "default")
                output_txt.write_text(SAMPLE_TEXT, encoding="utf-8")
                return SAMPLE_TEXT

            with patch("pdf2slides.pipeline.extract_text_from_pdf", side_effect=fake_extract_text_from_pdf):
                with patch("pdf2slides.pipeline.run_pdftotext", return_value=SAMPLE_TEXT):
                    run = run_pipeline(input_pdf, tmp_path / "outputs", pdftotext_mode="hybrid")

            self.assertTrue(run.run_dir.exists())

            expected_files = [
                run.raw_text_path,
                run.pages_path,
                run.blocks_path,
                run.structured_doc_path,
                run.slide_deck_path,
                run.latex_path,
                run.metadata_path,
                run.run_dir / "RUN_SUMMARY.md",
            ]
            for path in expected_files:
                self.assertTrue(path.exists(), f"missing expected artifact: {path}")

            structured_document = json.loads(run.structured_doc_path.read_text(encoding="utf-8"))
            self.assertEqual(structured_document["paper_id"], "sample")
            self.assertEqual(structured_document["title"], "Test Paper Title")
            self.assertEqual(structured_document["page_count"], 1)
            self.assertEqual(structured_document["metadata"]["ir_version"], "structured-document-v0")
            self.assertIn("blocks", structured_document)
            self.assertIn("assets", structured_document)
            self.assertGreaterEqual(len(structured_document["blocks"]), 1)
            first_block = structured_document["blocks"][0]
            self.assertIn("reading_order_index", first_block)
            self.assertEqual(first_block["reading_order_index"], 1)
            first_page = structured_document["pages"][0]
            self.assertEqual(first_page["width"], 612.0)
            self.assertEqual(first_page["height"], 792.0)
            self.assertEqual(first_page["block_ids"][0], first_block["block_id"])
            sections = structured_document["sections"]
            section_headings = [section["heading"] for section in sections]
            self.assertIn("Introduction", section_headings)
            self.assertIn("Method", section_headings)
            method_section = next(section for section in sections if section["heading"] == "Method")
            self.assertTrue(method_section["section_id"].startswith("sec_"))
            self.assertIn("page_start", method_section)
            self.assertIn("page_end", method_section)
            self.assertIn("content_block_ids", method_section)
            subsection_headings = [subsection["heading"] for subsection in method_section["subsections"]]
            self.assertIn("Details", subsection_headings)
            details_subsection = next(subsection for subsection in method_section["subsections"] if subsection["heading"] == "Details")
            self.assertTrue(details_subsection["subsection_id"].startswith("subsec_"))
            self.assertIn("content_block_ids", details_subsection)

            slide_deck = json.loads(run.slide_deck_path.read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(slide_deck["slides"]), 3)
            self.assertEqual(slide_deck["slides"][0]["title"], "Test Paper Title")
            self.assertIn("Abstract", [slide["title"] for slide in slide_deck["slides"]])

            metadata = json.loads(run.metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(metadata["input_pdf"], str(input_pdf.resolve()))
            self.assertEqual(metadata["run_dir"], str(run.run_dir))
            self.assertEqual(metadata["pdftotext_mode"], "hybrid")
            self.assertIn("extract_text_from_pdf", metadata["stages"])


if __name__ == "__main__":
    unittest.main()
