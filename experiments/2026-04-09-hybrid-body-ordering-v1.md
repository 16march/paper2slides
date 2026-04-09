# Experiment Record

## Metadata
- Experiment ID: `2026-04-09-hybrid-body-ordering-v1`
- Date: `2026-04-09`
- Author: `Tongyan CONG`

## Question
- Can a hybrid strategy preserve the stable default extraction for title, abstract, and captions while using column-aware paragraph ordering in body pages to improve reading-order quality?

## Motivation
- `v16-layout` was unusable.
- `v17-columns` recovered much of the structure but still damaged abstracts and captions.
- The natural next step was a hybrid baseline:
  - keep default extracted raw text as the main content source,
  - apply column-aware paragraph reordering only as an auxiliary ordering signal for later pages.

## Baseline
- Baseline commit or prior result:
  - main baseline: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v15/`
  - exploratory columns baseline: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v17-columns/`
- Why is this the correct baseline?
  - `v15` is the current stable default extraction baseline.
  - `v17-columns` is the immediate prior exploratory column-aware variant.

## Changed Module
- Which module or tightly related idea was changed?
  - hybrid body-ordering logic in `src/pdf2slides/stages.py`
  - extraction/pipeline mode plumbing in `src/pdf2slides/pipeline.py` and `src/pdf2slides/cli.py`
- What was intentionally not changed?
  - title heuristics
  - abstract heuristics
  - heading heuristics
  - reading-order evaluation protocol

## Input Set
- Which PDFs or documents were used?
  - all 8 PDFs in `data/eval/findings-acl-2024-v1/`
- Why were these inputs chosen?
  - the comparison should remain on the frozen reconstruction set and be directly comparable to `v15`

## Procedure
- What command or workflow was used?
  - add `pdftotext_mode='hybrid'`
  - keep `raw_text` and page text from default `pdftotext`
  - use auxiliary `columns` page text only to reorder paragraph slots on later pages
  - preserve default section headers, captions, title, and abstract extraction
  - rerun all 8 eval PDFs into `outputs/findings-acl-2024-v1-full-placeholder-baseline-v18-hybrid/`
  - run `scripts/eval_dev_headings.py` and `scripts/eval_reading_order.py`
  - save `heading_eval.md` and `reading_order_eval.md` under the output root
- Where are the outputs stored?
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v18-hybrid/`

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
  - The hybrid strategy successfully preserved the stable parser behavior of `v15`.
- What worked?
  - Heading-side metrics stayed unchanged relative to `v15`:
    - `title 8/8`
    - `abstract 8/8`
    - `sections 70/71`
    - `subsections 91/91`
  - `2024.findings-acl.783` remained fully correct on title, abstract, sections, and subsections.
  - Caption metrics were also preserved relative to `v15`:
    - figure caption match `17/23`
    - table caption match `24/36`
- What failed or remained unclear?
  - Reading-order proxy metrics did not improve over `v15`:
    - paragraph match `289/355 -> 274/355`
    - paragraph order `184/289 -> 179/274`
  - So the hybrid ordering was safe, but not beneficial enough to adopt.

## Result
- Safe but not better than baseline

## Decision
- Keep as negative control, do not adopt

## Next Action
- Keep `v15` as the main extraction and reading-order baseline.
- Treat `v18-hybrid` as evidence that naive paragraph-slot reordering is not enough.
- If continuing this line, the next heuristic should target only specific body regions or paragraph boundaries instead of global slot replacement.

## Links
- Related default baseline: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v15/`
- Related columns baseline: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v17-columns/`
- Related hybrid output: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v18-hybrid/`
- Related reading-order protocol: `docs/reading-order-evaluation.md`
