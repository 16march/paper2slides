# Minimal Architecture

## Objective
Build a minimal end-to-end system that can take a PDF as input and produce:
- extracted raw text,
- page-level and block-level intermediate representations,
- a structured document JSON,
- a structured slide deck JSON,
- a placeholder Beamer `.tex` file.

The current target is architectural completeness, not accuracy.

## Pipeline Stages
1. `PDF extraction`
   Uses `pdftotext` to convert the source PDF into raw text.

2. `Layout detection`
   Placeholder heuristic that splits page text into paragraph-like blocks and assigns block types.

3. `OCR`
   Placeholder stage that keeps block text as-is and marks the source as placeholder OCR.

4. `Structure parsing`
   Converts detected blocks into a `StructuredDocument` with title, abstract, sections, and page content.

5. `Slide planning`
   Converts the structured document into a `SlideDeck` with slide titles, bullets, section links, and layout hints.

6. `Rendering`
   Produces a minimal Beamer `.tex` file.

## Why This Shape
- Every stage has explicit input and output artifacts.
- Every stage can later be replaced independently with a real model or parser.
- The intermediate JSON files provide debugging visibility.
- The architecture already matches the intended long-term project decomposition.

## Current Replacement Points
- `extract_text_from_pdf`: replace with hybrid PDF parsing or page image extraction.
- `detect_layout_blocks`: replace with layout detector or document parser.
- `run_placeholder_ocr`: replace with OCR or multimodal transcription.
- `parse_structure`: replace with stronger document understanding and reading-order logic.
- `generate_slide_deck`: replace with planning and layout modules.
- `render_beamer`: replace with richer slide templates or direct presentation rendering.

## Command
```bash
PYTHONPATH=src python3 -m pdf2slides path/to/input.pdf --output-root outputs
```

## Output Layout
Each run writes into:

```text
outputs/<pdf-stem>/
  01_raw_text.txt
  02_pages.json
  03_blocks.json
  04_structured_document.json
  05_slide_deck.json
  06_slides.tex
  RUN_SUMMARY.md
```
