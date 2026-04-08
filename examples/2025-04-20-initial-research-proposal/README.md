# Example Snapshot

This directory is a checked-in snapshot of a real pipeline run.

The original source PDF is not distributed in the public repository, but the generated artifacts are kept here so the current pipeline contract can be inspected without rerunning the system.

Included artifacts:
- `01_raw_text.txt`
- `02_pages.json`
- `03_blocks.json`
- `04_structured_document.json`
- `05_slide_deck.json`
- `06_slides.tex`
- `RUN_SUMMARY.md`

Purpose:
- let readers inspect the current intermediate representations without running the code,
- make the pipeline contract visible from the repository alone,
- provide a stable example while the main system remains under active development.

Note:
- this is a snapshot of the placeholder pipeline,
- some paths recorded inside generated files may reflect the original run environment.
