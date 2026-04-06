from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pdf2slides.pipeline import run_pipeline


SAMPLE_TEXT = """Test Paper Title

Abstract

This is the first abstract sentence. This is the second abstract sentence.

1 Introduction

This is the introduction paragraph. It has enough content to become bullets.

2 Method

Figure 1: Sample figure caption.

We define x = y + z for the placeholder formula example.
"""


class PipelineSmokeTest(unittest.TestCase):
    def test_run_pipeline_writes_expected_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            input_pdf = tmp_path / "sample.pdf"
            input_pdf.write_bytes(b"%PDF-1.4\n% placeholder test file\n")

            def fake_extract_text_from_pdf(_pdf_path: Path, output_txt: Path) -> str:
                output_txt.write_text(SAMPLE_TEXT, encoding="utf-8")
                return SAMPLE_TEXT

            with patch("pdf2slides.pipeline.extract_text_from_pdf", side_effect=fake_extract_text_from_pdf):
                run = run_pipeline(input_pdf, tmp_path / "outputs")

            self.assertTrue(run.run_dir.exists())

            expected_files = [
                run.raw_text_path,
                run.pages_path,
                run.blocks_path,
                run.structured_doc_path,
                run.slide_deck_path,
                run.latex_path,
                run.run_dir / "RUN_SUMMARY.md",
            ]
            for path in expected_files:
                self.assertTrue(path.exists(), f"missing expected artifact: {path}")

            structured_document = json.loads(run.structured_doc_path.read_text(encoding="utf-8"))
            self.assertEqual(structured_document["title"], "Test Paper Title")
            section_headings = [section["heading"] for section in structured_document["sections"]]
            self.assertIn("Introduction", section_headings)
            self.assertIn("Method", section_headings)

            slide_deck = json.loads(run.slide_deck_path.read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(slide_deck["slides"]), 3)
            self.assertEqual(slide_deck["slides"][0]["title"], "Test Paper Title")
            self.assertIn("Abstract", [slide["title"] for slide in slide_deck["slides"]])


if __name__ == "__main__":
    unittest.main()
