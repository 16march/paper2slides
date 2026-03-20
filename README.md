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
├── src/pdf2slides/        # Core pipeline code
├── docs/                  # Architecture notes
├── reports/               # Progress reports and research artifacts
├── archives/              # Archived legacy code and reusable components
└── README.md
```

## Usage

Run the minimal end-to-end pipeline on a PDF:

```bash
PYTHONPATH=src python3 -m pdf2slides path/to/input.pdf --output-root outputs
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

## Current Status

This repository currently provides:
- a runnable end-to-end prototype,
- explicit intermediate representations for each stage,
- a modular architecture designed for future replacement with stronger models.

The present emphasis is **system architecture and research scaffolding**, not benchmark accuracy. Layout detection, OCR, structure parsing, and slide generation are currently implemented with lightweight placeholder logic to validate interfaces and data flow.

## Future Work / Research Direction

Planned next steps include:
- replacing placeholder layout analysis with document parsing models,
- improving OCR and reading-order recovery for scientific PDFs,
- designing stronger intermediate representations for figures, tables, and formulas,
- developing better slide planning and layout generation modules,
- evaluating the system on paper-slide pairs from academic domains.

The long-term goal is a robust system for converting complex academic papers into coherent, presentation-quality slides while preserving both content fidelity and structural logic.
