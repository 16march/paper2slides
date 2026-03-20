# Project: PDF to Slides Generation

## Goal
Convert academic PDFs into structured LaTeX Beamer slides.

The long-term objective is to build a master's thesis project that can:
- understand the structure and content of academic papers,
- recover document layout and reading order,
- transform the paper into a structured intermediate representation,
- generate usable presentation slides with controllable layout quality.

## Current Status
The project idea is already grounded in prior lab progress reports from the 2025 fall semester.

Confirmed findings from previous work:
- YOLOv8-based layout detection is already strong on the synthetic ACL-style dataset.
- Detection performance is no longer the main bottleneck of the whole system.
- Formula detection remains weaker than other classes, especially for inline formulas.
- OCR quality and document reading order recovery have greater impact on downstream generation quality.
- Two-column document parsing is currently a major unresolved issue.
- Layout generation should likely be separated into:
  - content understanding by LLM/VLM modules,
  - spatial layout prediction by a dedicated layout model or structured heuristic module.

Practical implication:
- Do not treat "improve detection accuracy" as the default top priority unless new experiments show otherwise.
- Current research emphasis should move toward OCR, structure parsing, reading order, intermediate representation design, and slide layout generation.

## Working Research Direction
Current high-level pipeline:
1. PDF to page images or parsed page objects
2. Layout detection
3. OCR and text extraction
4. Structure parsing
5. Reading order recovery
6. Intermediate representation for slide generation
7. LaTeX Beamer generation
8. Layout refinement and evaluation

Expected system design principle:
- Detection, OCR, parsing, and generation should remain modular.
- The project should prefer explicit intermediate outputs over opaque end-to-end generation.
- Every module should be testable independently.

## Key Metrics
Primary metrics:
- detection accuracy such as mAP
- OCR accuracy and text completeness
- structure recovery quality
- reading order correctness
- slide content completeness
- slide layout quality

Secondary metrics:
- reproducibility of outputs
- ease of debugging intermediate results
- robustness across different paper formats

## Project Rules
- Keep modules decoupled.
- Prefer Python scripts unless another language is clearly better for a module.
- Output reproducible results.
- Save important assumptions in project documents instead of leaving them only in chat history.
- Favor explicit experiment records over ad hoc one-off trials.
- Do not overwrite raw inputs or experimental outputs without a clear reason.

## Collaboration Rules For Codex
When working in this directory, Codex should:
- treat this folder as the default root for the master's project,
- read this file first before making major changes,
- preserve existing project context and avoid inventing a new direction without evidence,
- update project documentation when a meaningful decision or milestone is reached.

If present, Codex should also check these files before substantial work:
- `README.md`
- `PROJECT_LOG.md`
- `TASKS.md`
- `reports/`
- `notes/`

After important work, Codex should update at least one of:
- `PROJECT_LOG.md` for dated progress,
- `TASKS.md` for next actions and status,
- `README.md` for major structural or scope changes.

## Suggested Directory Structure
Recommended organization for this project:
- `src/` for source code
- `experiments/` for experiment configs, outputs, and comparisons
- `data/` for local datasets or dataset instructions
- `reports/` for progress reports and professor meeting materials
- `notes/` for literature notes and ideas
- `thesis/` for thesis writing materials
- `slides/` for generated slide outputs and templates
- `docs/` for architecture notes and design decisions

If these folders do not exist yet, they can be created gradually when needed.

## Priorities
Current priority candidates:
- define the target system architecture for PDF-to-slides generation,
- decide the intermediate representation between parsing and slide generation,
- evaluate OCR and reading order recovery strategies,
- identify whether two-column parsing needs a dedicated module,
- design a practical first end-to-end prototype.

Lower priority unless new evidence suggests otherwise:
- chasing small additional gains in detection mAP on the existing synthetic dataset.

## Task List
Now:
- clarify the thesis scope and expected final deliverable,
- formalize the project architecture,
- organize previous reports and findings into this project directory.

Next:
- build a minimal reproducible pipeline,
- compare OCR and reading order approaches,
- define evaluation criteria for generated slides.

Later:
- improve layout generation quality,
- support multiple layout candidates,
- expand from synthetic or ACL-style papers to more diverse paper formats.
