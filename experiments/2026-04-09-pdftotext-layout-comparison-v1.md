# Experiment Record

## Metadata
- Experiment ID: `2026-04-09-pdftotext-layout-comparison-v1`
- Date: `2026-04-09`
- Author: `Tongyan CONG`

## Question
- Does replacing the current `pdftotext` extraction mode with `pdftotext -layout` improve reading-order quality on the frozen 8-paper evaluation set?

## Motivation
- The next research step moved to reading order.
- Before implementing a custom ordering heuristic, the project needed to test the cheapest baseline change:
  - keep the parser unchanged,
  - only switch the raw text extractor from default `pdftotext` output to `pdftotext -layout`.

## Baseline
- Baseline commit or prior result: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v15/`
- Why is this the correct baseline?
  - It is the current `StructuredDocument v0` output snapshot using the default `pdftotext` mode.
  - It already has both heading evaluation and reading-order evaluation artifacts.

## Changed Module
- Which module or tightly related idea was changed?
  - extraction mode passed to `pdftotext`
  - pipeline metadata and CLI option for reproducible extraction-mode selection
- What was intentionally not changed?
  - heading heuristics
  - reading-order heuristics
  - section/subsection assignment rules
  - evaluation scripts

## Input Set
- Which PDFs or documents were used?
  - all 8 PDFs in `data/eval/findings-acl-2024-v1/`
- Why were these inputs chosen?
  - the comparison should stay on the same frozen reconstruction set as the current parser baseline

## Procedure
- What command or workflow was used?
  - add `pdftotext_mode` plumbing to `extract_text_from_pdf`, `run_pipeline`, CLI args, and run metadata
  - keep `default` as the normal mode and add `layout` as an explicit alternative
  - rerun all 8 eval PDFs into `outputs/findings-acl-2024-v1-full-placeholder-baseline-v16-layout/` with `pdftotext_mode='layout'`
  - run `scripts/eval_dev_headings.py` on both `v15` and `v16-layout`
  - run `scripts/eval_reading_order.py` on both `v15` and `v16-layout`
  - save `heading_eval.md` and `reading_order_eval.md` under both output roots
- Where are the outputs stored?
  - default reference: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v15/`
  - layout variant: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v16-layout/`

## Metrics Or Review Criteria
- Exact title match against gold
- Abstract prefix match against gold
- Exact section heading overlap
- Exact subsection heading overlap
- paragraph match
- paragraph order
- figure caption match
- table caption match

## Main Observations
- What happened?
  - `pdftotext -layout` made the raw text much worse for the current parser and reading-order pipeline.
- What worked?
  - The experiment itself is now reproducible because the pipeline records `pdftotext_mode`.
- What failed or remained unclear?
  - Heading recovery collapsed badly under `-layout`:
    - `v15` default: `title 8/8`, `abstract 8/8`, `sections 70/71`, `subsections 91/91`
    - `v16-layout`: `title 7/8`, `abstract 0/8`, `sections 10/71`, `subsections 15/91`
  - Reading-order proxy metrics also collapsed:
    - paragraph match: `289/355 -> 23/355`
    - paragraph order: `184/289 -> 19/23`
    - figure caption match: `17/23 -> 3/23`
    - table caption match: `24/36 -> 9/36`
  - The likely reason is that `-layout` preserves visual spacing and column geometry in a way that breaks the current paragraph splitter and heading heuristics.
  - So `-layout` is not a viable direct replacement baseline for this pipeline.

## Result
- Worse than baseline

## Decision
- Discard as direct replacement

## Next Action
- Keep default `pdftotext` output as the extraction baseline.
- Do not pursue `-layout` as a drop-in replacement for the current parser.
- Compare future reading-order ideas on top of default extracted text, especially:
  - column-aware block ordering
  - page-level left-column then right-column traversal
  - section-aware ordering with heading anchors

## Links
- Related parser baseline: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v14/FREEZE.md`
- Related IR snapshot: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v15/`
- Related layout variant: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v16-layout/`
- Related reading-order protocol: `docs/reading-order-evaluation.md`
