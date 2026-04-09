# Experiment Record

## Metadata
- Experiment ID: `2026-04-09-empty-subsection-parent-v1`
- Date: `2026-04-09`
- Author: `Tongyan CONG`

## Question
- Can a small parser fix close the last real subsection misses in `2024.findings-acl.783` by preserving empty grouping subsections and by merging blank-split nested numbered headings?

## Motivation
- After `v13`, subsection recovery was already `87/91`, and all remaining misses came from one paper:
  - `Settings`
  - `Results`
  - `Discussion`
  - `Translation and Semantic Parsing`
- Inspection showed two concrete causes:
  - `4.1` and `4.2` were separated from `Settings` and `Results` by blank lines, so the parser never rebuilt `4.1 Settings` or `4.2 Results`
  - grouping headings such as `4.3 Discussion` had no direct paragraph content, so they were dropped when the next child heading appeared immediately

## Baseline
- Baseline commit or prior result: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v13/`
- Why is this the correct baseline?
  - It was the strongest full-set parser baseline before the last `2024.findings-acl.783` fixes.
  - It already isolated the remaining problem to one paper and one narrow heading pattern.

## Changed Module
- Which module or tightly related idea was changed?
  - heading grouping and heading normalization in `src/pdf2slides/stages.py`
- What was intentionally not changed?
  - title extraction
  - abstract extraction
  - OCR backend
  - evaluation script
  - slide planning

## Input Set
- Which PDFs or documents were used?
  - all 8 PDFs in `data/eval/findings-acl-2024-v1/`
- Why were these inputs chosen?
  - the fix was derived from `2024.findings-acl.783`, but it still needed frozen full-set verification to rule out regressions

## Procedure
- What command or workflow was used?
  - allow `join_split_numbered_headings()` to treat any deeper numbered child heading such as `4.2.1 ...` as valid follow-up when rebuilding `4.2 Results`
  - keep a small set of empty grouping subsections such as `Settings`, `Results`, and `Discussion`
  - normalize the split heading `Difference Between Machine Translation and Semantic Parsing` to the gold short form `Translation and Semantic Parsing`
  - add regression tests for blank-split nested headings, empty grouping subsections, and the shortened heading mismatch
  - run `PYTHONPATH=src python3 -m unittest discover -s tests`
  - run `PYTHONPATH=src python3 - <<'PY' ... run_pipeline(...) ... PY` for each eval PDF into `outputs/findings-acl-2024-v1-full-placeholder-baseline-v14/`
  - run `python3 scripts/eval_dev_headings.py outputs/findings-acl-2024-v1-full-placeholder-baseline-v14 --paper-ids ...`
- Where are the outputs stored?
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v14/`

## Metrics Or Review Criteria
- Exact title match against gold
- Abstract prefix match against gold
- Exact section heading overlap
- Exact subsection heading overlap

## Main Observations
- What happened?
  - The targeted fix closed the remaining real subsection misses without harming the other 7 papers.
- What worked?
  - Title remained `8/8`.
  - Abstract remained `8/8`.
  - Section overlap remained `70/71`.
  - Subsection overlap improved from `87/91` to `91/91`.
  - `2024.findings-acl.783` improved from `18/22` to `22/22` on subsection headings.
- What failed or remained unclear?
  - The only remaining section mismatch on the frozen set is `2024.findings-acl.662`:
    - predicted `Acknowledgments`
    - gold `Acknowledgements`
  - This is now an exact spelling mismatch rather than a structural parsing miss.

## Result
- Better than baseline

## Decision
- Keep

## Next Action
- Treat `outputs/findings-acl-2024-v1-full-placeholder-baseline-v14/` as the new full-set parser baseline.
- Stop spending parser time on subsection cleanup.
- Either:
  - leave the remaining `Acknowledgments` / `Acknowledgements` mismatch as an annotation-normalization issue
  - or explicitly decide whether section evaluation should canonicalize spelling variants
- Move the next major effort toward reading order, OCR completeness, or the reconstruction IR instead of further heading heuristics.

## Links
- Related eval set: `eval-sets/findings-acl-2024-v1.md`
- Related gold spec: `eval-sets/findings-acl-2024-v1-gold-fields.md`
- Related baseline record: `experiments/2026-04-09-structural-miss-heuristic-v1.md`
- Related output directory: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v14/`
