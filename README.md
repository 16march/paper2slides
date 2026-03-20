# My Master Project

This directory is the working root for the master's thesis project on academic paper to slide generation.

## Project Focus
The project studies how to convert academic PDFs into structured LaTeX Beamer slides.

Current understanding:
- this is not only a summarization problem,
- this is a multimodal document understanding problem,
- high-quality slide generation depends on layout parsing, OCR, reading order recovery, structural representation, and generation.

## Research Evolution
The project idea has evolved through several stages:

1. Initial proposal:
   LLM-based automatic generation of academic slides from structured documents.

2. Revised pre-semester proposal:
   Reframed as multimodal machine translation from paper language to presentation language.

3. Fall 2025 progress reports:
   Practical work showed that document parsing and structure recovery are core bottlenecks.
   Detection is strong enough to stop being the default top priority.

## Directory Guide
- `proposals/`: early-stage research proposals and supervisor-approved research descriptions
- `reports/`: dated progress reports prepared for professor meetings
- `references/`: key reference materials such as prior thesis and templates
- `archives/`: older codebases or copied project assets kept for reference

## Important Files
- `AGENTS.md`: project operating instructions and persistent context for Codex
- `PROJECT_LOG.md`: dated project history and high-level decisions
- `TASKS.md`: active task tracking

## Minimal Pipeline
A runnable placeholder system now exists under `src/pdf2slides/`.

It currently supports:
- PDF to raw text extraction via `pdftotext`
- placeholder layout block detection
- placeholder OCR stage
- structured document JSON generation
- structured slide deck JSON generation
- minimal Beamer `.tex` rendering

Run it with:

```bash
PYTHONPATH=src python3 -m pdf2slides proposals/2025-04-20-initial-research-proposal.pdf --output-root outputs
```

Architecture note:
- `docs/architecture.md`

## Immediate Next Use
This folder should become the single organized workspace for:
- collecting previous materials,
- defining thesis scope,
- designing the system architecture,
- building the first end-to-end prototype.
