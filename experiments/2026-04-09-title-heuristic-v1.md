# Experiment Record

## Metadata
- Experiment ID: `2026-04-09-title-heuristic-v1`
- Date: `2026-04-09`
- Author: `Tongyan CONG`

## Question
- Can a small title-continuation heuristic recover the remaining multi-line title failure on the frozen `findings-acl-2024-v1` set without regressing the already-correct titles?

## Motivation
- After the abstract fix, the only remaining title error on the full set was `2024.findings-acl.731`.
- The failure was local and clearly caused by a title split across two lines on page 1, so it was worth fixing before moving to harder heading recovery work.

## Baseline
- Baseline commit or prior result: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v7/`
- Why is this the correct baseline?
  - It is the latest full-set parser baseline after abstract recovery reached `8/8`.
  - It isolates title recovery as the remaining front-matter extraction issue.

## Changed Module
- Which module or tightly related idea was changed?
  - title recovery in `src/pdf2slides/stages.py`
- What was intentionally not changed?
  - abstract extraction
  - heading detection
  - section parsing
  - OCR backend
  - evaluation script

## Input Set
- Which PDFs or documents were used?
  - all 8 PDFs in `data/eval/findings-acl-2024-v1/`
- Why were these inputs chosen?
  - The title heuristic needed a frozen full-set regression check, not only a single-paper spot check.

## Procedure
- What command or workflow was used?
  - update `infer_title()` so the best first-page title line can absorb following title-like continuation lines
  - reject likely author lines from title continuation by excluding digits, emails, braces, commas, and lines without clear title-function words
  - add a targeted regression test for the `2024.findings-acl.731` pattern
  - run `PYTHONPATH=src python3 -m unittest discover -s tests`
  - run `PYTHONPATH=src python3 -m pdf2slides <pdf> --output-root outputs/findings-acl-2024-v1-full-placeholder-baseline-v8` for each eval PDF
  - run `PYTHONPATH=src python3 scripts/eval_dev_headings.py outputs/findings-acl-2024-v1-full-placeholder-baseline-v8 --paper-ids ...`
- Where are the outputs stored?
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v8/`

## Metrics Or Review Criteria
- Exact title match against gold
- Regression check on abstract recovery
- Regression check on section and subsection overlap

## Main Observations
- What happened?
  - The heuristic fixed the only remaining title failure without changing the already-correct titles.
- What worked?
  - Title recovery improved from `7/8` to `8/8`.
  - `2024.findings-acl.731` now recovers as `Decomposing Argumentative Essay Generation via Dialectical Planning of Complex Reasoning`.
  - Abstract recovery stayed at `8/8`.
  - Section and subsection scores were unchanged relative to `v7`.
- What failed or remained unclear?
  - Heading recovery is now the clearest remaining parser bottleneck on the frozen full set.
  - The continuation rule is still heuristic and has only been checked on the current ACL-style set.

## Result
- Better than baseline

## Decision
- Keep

## Next Action
- Shift parser work to section and subsection recovery on the remaining weak papers.
- Treat `outputs/findings-acl-2024-v1-full-placeholder-baseline-v8/` as the new frozen full-set baseline for future parser comparisons.

## Links
- Related eval set: `eval-sets/findings-acl-2024-v1.md`
- Related gold spec: `eval-sets/findings-acl-2024-v1-gold-fields.md`
- Related baseline record: `experiments/2026-04-09-abstract-heuristic-v1.md`
- Related output directory: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v8/`
