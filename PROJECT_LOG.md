# Project Log

## 2025-04-20
Initial admission-stage research proposal written.

Main idea:
- use LLMs to transform academic documents into LaTeX Beamer slides,
- support audience adaptation,
- provide speaker notes,
- build a parallel dataset from papers and slides.

Limitation in hindsight:
- the proposal assumed relatively structured inputs,
- it did not yet fully account for PDF parsing, OCR, reading order, and formula handling as core bottlenecks.

## 2025-11-07
Supervisor-approved research description form prepared before/around the start of the semester.

Main improvement over the initial proposal:
- the task was redefined as multimodal machine translation,
- the input was treated as a complex academic PDF rather than plain structured text,
- document parsing and visual layout analysis were explicitly introduced into the method.

Key conceptual shift:
- academic paper to slides is not just text summarization,
- formulas, figures, tables, and cross-element relations must be preserved.

## 2025-11-21
Progress report focused on reproducing and improving the lab's previous thesis work based on Sulaeman (2019).

Main outcomes:
- reconstructed the synthetic dataset generation pipeline,
- replaced YOLOv3 with YOLOv8n,
- achieved mAP@50 of 95.5 percent on the synthetic validation set,
- significantly outperformed the previous baseline.

Key insight:
- layout detection is already strong for most structural classes,
- formula detection remains weaker, especially for inline formulas,
- purely visual methods are insufficient for some document elements.

## 2025-12-12
Follow-up progress report clarified evaluation behavior and reported reproduction findings.

Main outcomes:
- clarified the meaning of background in the confusion matrix,
- confirmed that paragraph text extraction is relatively stable,
- identified two-column reading order as a major system bottleneck,
- recognized that OCR and structure recovery matter more for downstream generation quality.

Key conceptual shift:
- detection is no longer the main bottleneck,
- future work should emphasize OCR, reading order, structure parsing, intermediate representation, and layout reasoning.

## 2026-03-20
Created `My Master Project` as the dedicated root directory for the master's thesis project.

Actions taken:
- added persistent project context in `AGENTS.md`,
- copied key historical materials into this directory,
- organized proposals, reports, references, and archived code for future work.

## 2026-03-20
Built the first minimal end-to-end pipeline under `src/pdf2slides/`.

What was implemented:
- a runnable CLI entry point,
- explicit pipeline stages for extraction, placeholder layout detection, placeholder OCR, structure parsing, slide planning, and Beamer rendering,
- intermediate JSON artifacts for pages, blocks, structured documents, and slide decks,
- an architecture note in `docs/architecture.md`.

Validation:
- ran the pipeline successfully on the initial research proposal PDF,
- confirmed generation of all expected intermediate files and a placeholder slide deck.

Interpretation:
- the project now has a concrete system skeleton,
- future research can replace individual placeholder modules without changing the overall pipeline contract.
