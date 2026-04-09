# Experiment Record

## Metadata
- Experiment ID: `2026-04-09-column-aware-layout-flattening-v1`
- Date: `2026-04-09`
- Author: `Tongyan CONG`

## Question
- Can a simple column-aware flattening heuristic recover useful reading-order improvements from `pdftotext -layout` without fully breaking the current parser?

## Motivation
- Pure `pdftotext -layout` was clearly unusable as a direct replacement.
- But it still exposed visible column structure.
- The next cheap baseline was therefore to use `-layout` only as a page-level column source and flatten each page as:
  - top full-width region
  - left column
  - right column

## Baseline
- Baseline commit or prior result:
  - default reference: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v15/`
  - failed direct layout variant: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v16-layout/`
- Why is this the correct baseline?
  - `v15` is the current default extraction reference.
  - `v16-layout` is the immediate prior failed attempt using raw `-layout`.

## Changed Module
- Which module or tightly related idea was changed?
  - extraction-time column reconstruction heuristic in `src/pdf2slides/stages.py`
- What was intentionally not changed?
  - heading rules
  - section assignment logic
  - reading-order evaluation protocol
  - slide planning logic

## Input Set
- Which PDFs or documents were used?
  - all 8 PDFs in `data/eval/findings-acl-2024-v1/`
- Why were these inputs chosen?
  - the comparison should remain on the frozen reconstruction set and be directly comparable to `v15` and `v16-layout`

## Procedure
- What command or workflow was used?
  - add a new `pdftotext_mode='columns'`
  - call `pdftotext -layout`
  - infer a page-local column split from repeated right-column start positions
  - flatten each page as preamble, then left-column lines, then right-column lines
  - only split a line when a real gutter exists around the inferred split position
  - rerun all 8 eval PDFs into `outputs/findings-acl-2024-v1-full-placeholder-baseline-v17-columns/`
  - run both `scripts/eval_dev_headings.py` and `scripts/eval_reading_order.py`
  - save `heading_eval.md` and `reading_order_eval.md` under the output root
- Where are the outputs stored?
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v17-columns/`

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
  - The column-aware flattening heuristic recovered a lot of the catastrophic damage seen in raw `-layout`, but it still did not beat the default extraction baseline.
- What worked?
  - Relative to `v16-layout`, the heuristic recovered heading quality substantially:
    - `title 7/8 -> 8/8`
    - `abstract 0/8 -> 3/8`
    - `sections 10/71 -> 59/71`
    - `subsections 15/91 -> 86/91`
  - Relative to `v16-layout`, paragraph recovery also recovered strongly:
    - paragraph match `23/355 -> 256/355`
    - paragraph order `19/23 -> 159/256`
  - On `2024.findings-acl.783`, title returned to correct and structure almost fully recovered.
- What failed or remained unclear?
  - The heuristic is still worse than `v15` default extraction:
    - `v15`: `title 8/8`, `abstract 8/8`, `sections 70/71`, `subsections 91/91`
    - `v17-columns`: `title 8/8`, `abstract 3/8`, `sections 59/71`, `subsections 86/91`
  - Caption recovery is still poor:
    - figure caption match `0/23`
    - table caption match `3/36`
  - The main weakness is that line-level column flattening still merges or distorts captions and some paragraph boundaries.

## Result
- Better than `v16-layout`, worse than `v15`

## Decision
- Keep as exploratory baseline, not as current default

## Next Action
- Keep `v15` as the main extraction baseline.
- Do not replace the current default pipeline with `columns`.
- If continuing reading-order work, do it as a hybrid strategy on top of default extracted text, not as a full switch to reconstructed layout text.
- In particular, preserve default title/abstract/caption text while experimenting with column-aware body ordering only.

## Links
- Related default baseline: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v15/`
- Related raw layout variant: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v16-layout/`
- Related columns variant: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v17-columns/`
- Related reading-order protocol: `docs/reading-order-evaluation.md`
