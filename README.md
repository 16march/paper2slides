# Paper2Slides

> A modular multimodal pipeline for converting academic papers into structured, presentation-ready slides.

---

## Overview

Paper2Slides addresses the problem of transforming academic PDFs into coherent slide presentations.

Unlike traditional approaches that treat this task as text summarization, this project models it as a **multimodal document understanding and structured transformation problem**.

Scientific papers contain complex layouts, figures, tables, and hierarchical structures that must be preserved and reorganized to produce high-quality presentations.

This repository provides a modular, end-to-end pipeline that explicitly represents each transformation stage, enabling systematic analysis, debugging, and improvement.

## Key Idea

Generating slides from research papers is fundamentally different from summarization.

A useful presentation must preserve and reorganize:
- document structure,
- reading order,
- figure and table context,
- formula-related content,
- logical progression across sections.

Paper2Slides therefore treats the task as:

**academic PDF -> structured document representation -> slide plan -> presentation output**

This design makes the system more interpretable, modular, and extensible than a black-box end-to-end generator.

## Pipeline

`PDF -> text/layout extraction -> block detection -> OCR/transcription -> structure parsing -> structured document JSON -> slide planning -> LaTeX Beamer output`

The current implementation already follows this architecture end-to-end, with placeholder components used where research modules are still under development.

## Project Structure

```text
.
├── examples/              # Checked-in example pipeline outputs
├── src/pdf2slides/        # Core pipeline code
├── tests/                 # Minimal smoke tests
└── README.md
```

## Environment / Reproducibility

Minimum environment:
- Python `3.10+`
- a Unix-like shell environment
- `pdftotext` available on `PATH`

Install the Python package in editable mode from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e .
```

Install `pdftotext`:

```bash
# macOS (Homebrew)
brew install poppler

# Ubuntu / Debian
sudo apt-get install poppler-utils
```

The current minimal pipeline calls `pdftotext` directly. If it is missing, the extraction stage will fail with a runtime error.

Sample PDF for reproduction:
- `proposals/2025-04-20-initial-research-proposal.pdf`

## Usage

Run the minimal end-to-end pipeline on a PDF:

```bash
PYTHONPATH=src python3 -m pdf2slides path/to/input.pdf --output-root outputs
```

For example, to reproduce the sample run included in this repository:

```bash
PYTHONPATH=src python3 -m pdf2slides \
  proposals/2025-04-20-initial-research-proposal.pdf \
  --output-root outputs
```

Run the minimal smoke test suite:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

Example outputs:

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

## Demo

The repository already includes a minimal reproducible example run based on the initial research proposal PDF.

Example input:
- source PDF: `proposals/2025-04-20-initial-research-proposal.pdf`

Checked-in example snapshot:
- overview: `examples/2025-04-20-initial-research-proposal/README.md`
- raw text: `examples/2025-04-20-initial-research-proposal/01_raw_text.txt`
- page representation: `examples/2025-04-20-initial-research-proposal/02_pages.json`
- detected blocks: `examples/2025-04-20-initial-research-proposal/03_blocks.json`
- structured document IR: `examples/2025-04-20-initial-research-proposal/04_structured_document.json`
- slide deck plan: `examples/2025-04-20-initial-research-proposal/05_slide_deck.json`
- rendered Beamer output: `examples/2025-04-20-initial-research-proposal/06_slides.tex`
- run summary: `examples/2025-04-20-initial-research-proposal/RUN_SUMMARY.md`

Suggested README demo assets to keep alongside this section:
- one screenshot of the source PDF page,
- one screenshot of the rendered slide output,
- one screenshot of an intermediate JSON artifact such as `04_structured_document.json`.

At the moment, the demo is artifact-first rather than image-first: the repository contains the actual intermediate files and final `.tex` output, but not yet polished screenshots of the pipeline stages.

The corresponding generated run can still be reproduced locally under `outputs/`, but `examples/` is the stable location for browsing a representative result directly in the repository.

## Why This Is Hard

This problem is harder than standard text summarization because the system has to preserve both content and document structure.

Three concrete challenges are:

1. `Reading order recovery`
   Scientific PDFs often use two-column layouts, floating figures, footnotes, and section headers. Even if blocks are detected correctly, a wrong reading order can break paragraph continuity and downstream structure parsing.

2. `Caption grounding`
   A useful slide generator must know which caption belongs to which figure or table, and whether that visual element should appear in the same slide as the surrounding text. This is not recoverable from plain text alone.

3. `Section compression`
   Slides cannot preserve paper sections verbatim. The system has to compress sections into a short presentation narrative while deciding what to keep, what to merge, and what to omit without losing the paper's core logic.

## Current Status

This repository currently provides:
- a runnable end-to-end prototype,
- explicit intermediate representations for each stage,
- a modular architecture designed for future replacement with stronger models.

The present emphasis is **system architecture and research scaffolding**, not benchmark accuracy. Layout detection, OCR, structure parsing, and slide generation are currently implemented with lightweight placeholder logic to validate interfaces and data flow.

## Current Limitations

The current repository is intentionally a research scaffold, not a solved document understanding system.

Current limitations include:
- layout detection in the main pipeline is still placeholder logic rather than a strong document parsing backend,
- OCR is currently a placeholder transcription stage and does not yet represent a serious scientific PDF OCR module,
- structure parsing and reading-order recovery still rely on lightweight heuristics,
- slide planning is a placeholder transformation from document IR to a minimal Beamer-friendly deck plan,
- rendering currently produces a simple Beamer output rather than a layout-aware presentation design system.

The next replacement plan is to swap placeholder stages one by one while preserving the pipeline contract:
- replace placeholder layout analysis with a stronger document parsing or detection module,
- replace placeholder OCR with a reproducible OCR or transcription backend,
- strengthen reading-order and structure parsing for two-column scientific papers,
- improve the intermediate representation for figures, tables, formulas, and captions,
- replace the current slide planner with a module that makes explicit content-selection and layout decisions.

## Future Work / Research Direction

Planned next steps include:
- replacing placeholder layout analysis with document parsing models,
- improving OCR and reading-order recovery for scientific PDFs,
- designing stronger intermediate representations for figures, tables, and formulas,
- developing better slide planning and layout generation modules,
- evaluating the system on paper-slide pairs from academic domains.

The long-term goal is a robust system for converting complex academic papers into coherent, presentation-quality slides while preserving both content fidelity and structural logic.
