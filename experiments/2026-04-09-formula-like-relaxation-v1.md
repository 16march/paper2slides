# Experiment Record

## Metadata
- Experiment ID: `2026-04-09-formula-like-relaxation-v1`
- Date: `2026-04-09`
- Author: `Tongyan CONG`

## Question
- Can reading-order recovery improve further if long narrative paragraphs with inline equations or set notation stop being forced into `formula_like` blocks?

## Motivation
- After `v21`, many remaining paragraph misses were not true ordering failures.
- Failure analysis showed that several missed anchors already existed in the text stream, but those blocks had been typed as `formula_like` only because they contained `=` or set notation.
- This was especially visible in `2024.findings-acl.662`, `2024.findings-acl.164`, and `2024.findings-acl.536`.

## Baseline
- Baseline commit or prior result:
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v21-caption-reference-cleanup/`
- Why is this the correct baseline?
  - `v21` is the latest reading-order baseline before revisiting `formula_like` classification.

## Changed Module
- Which module or tightly related idea was changed?
  - block-type classification in `src/pdf2slides/stages.py`
- What was intentionally not changed?
  - extraction mode
  - title heuristics
  - abstract heuristics
  - heading heuristics
  - caption classification
  - reading-order evaluation protocol

## Input Set
- Which PDFs or documents were used?
  - smoke test on `2024.findings-acl.662`, `2024.findings-acl.164`, and `2024.findings-acl.536`
  - full rerun on all 8 PDFs in `data/eval/findings-acl-2024-v1/`
- Why were these inputs chosen?
  - the three-paper smoke test covers the clearest inline-formula failures,
  - the full rerun keeps the comparison directly comparable to `v21`.

## Procedure
- What command or workflow was used?
  - inspect `v21` paragraph misses and identify anchors that were landing inside `formula_like` blocks
  - relax `classify_paragraph()` so `=` only opens `formula_like` when the block still looks equation-heavy
  - keep obvious equation-only lines and `Algorithm ...` blocks as `formula_like`
  - add regression tests for:
    - narrative prose with inline equations,
    - budget-formulation prose with inline variables,
    - pure equation blocks
  - run a three-paper smoke test into `outputs/findings-acl-2024-v1-reading-order-smoke-v22-formula-like/`
  - rerun all 8 eval PDFs into `outputs/findings-acl-2024-v1-full-placeholder-baseline-v22-formula-like-relaxation/`
  - rerun `scripts/eval_dev_headings.py` and `scripts/eval_reading_order.py`
- Where are the outputs stored?
  - `outputs/findings-acl-2024-v1-reading-order-smoke-v22-formula-like/`
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v22-formula-like-relaxation/`

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
  - The relaxed `formula_like` rule improved paragraph recovery again without changing heading metrics.
- What worked?
  - Smoke test results improved on all three target papers:
    - `2024.findings-acl.662`: paragraph match `33/44 -> 37/44`
    - `2024.findings-acl.164`: paragraph match `21/25 -> 25/25`
    - `2024.findings-acl.536`: paragraph match `30/40 -> 35/40`
  - Full frozen-set heading metrics stayed unchanged:
    - `title 8/8`
    - `abstract 8/8`
    - `sections 70/71`
    - `subsections 91/91`
  - Full frozen-set reading-order metrics improved over `v21`:
    - paragraph match `306/355 -> 322/355`
    - paragraph order `266/306 -> 279/322`
  - Caption metrics held steady:
    - figure caption match `20/23`
    - figure caption order `19/20`
    - table caption match `31/36`
    - table caption order `29/31`
- What failed or remained unclear?
  - `formula_like` block count dropped from `74` to `41`, but the project still lacks a true formula-recovery evaluation, so the tradeoff is not yet directly measured.
  - Many remaining paragraph misses now look more like citation-interrupted anchors or OCR surface mismatch than block-type classification.

## Result
- Better than baseline

## Decision
- Keep

## Next Action
- Use `v22` as the current reading-order baseline.
- Analyze remaining paragraph misses with an emphasis on:
  - citation-interrupted anchor text,
  - OCR variation inside theorem/definition-style prose,
  - longer caption truncation.

## Links
- Related baseline: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v21-caption-reference-cleanup/`
- Related smoke test: `outputs/findings-acl-2024-v1-reading-order-smoke-v22-formula-like/`
- Related output directory: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v22-formula-like-relaxation/`
- Related protocol: `docs/reading-order-evaluation.md`
