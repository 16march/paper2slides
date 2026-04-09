# Experiment Record

## Metadata
- Experiment ID: `2026-04-09-subsection-cleanup-v1`
- Date: `2026-04-09`
- Author: `Tongyan CONG`

## Question
- Can a small heading-normalization and subsection-cleanup pass improve subsection recovery on top of the `v10` parser baseline without changing section-level behavior?

## Motivation
- After `v10`, the main remaining parser errors were no longer front-matter extraction or top-level section segmentation.
- Most residual subsection misses were formatting artifacts: duplicated leading numbers, colon spacing, `τ` vs `T`, circled digits, and split heading tails such as `In-context learning with noisy ASR` + `transcriptions`.

## Baseline
- Baseline commit or prior result: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v10/`
- Why is this the correct baseline?
  - It is the strongest full-set parser baseline before subsection-specific cleanup.
  - It already fixed the major section-level errors, so any gain can be attributed more cleanly to subsection cleanup.

## Changed Module
- Which module or tightly related idea was changed?
  - heading normalization and subsection detection heuristics in `src/pdf2slides/stages.py`
- What was intentionally not changed?
  - title extraction
  - abstract extraction
  - top-level section heuristics
  - OCR backend
  - evaluation script

## Input Set
- Which PDFs or documents were used?
  - all 8 PDFs in `data/eval/findings-acl-2024-v1/`
- Why were these inputs chosen?
  - The effect needed to be checked against the frozen full set because the remaining misses were spread across several papers.

## Procedure
- What command or workflow was used?
  - normalize heading text more aggressively by removing repeated numeric prefixes and cleaning colon spacing
  - normalize `Threshold τ` to `Threshold T`
  - strip circled-number prefixes such as `②`
  - join short lowercase continuation fragments such as `transcriptions` onto the previous heading line
  - reject large decimal pseudo-numbering such as `1.50 Case Study`
  - add regression tests for these formatting cases
  - run `PYTHONPATH=src python3 -m unittest discover -s tests`
  - run `PYTHONPATH=src python3 -m pdf2slides <pdf> --output-root outputs/findings-acl-2024-v1-full-placeholder-baseline-v11` for each eval PDF
  - run `PYTHONPATH=src python3 scripts/eval_dev_headings.py outputs/findings-acl-2024-v1-full-placeholder-baseline-v11 --paper-ids ...`
- Where are the outputs stored?
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v11/`

## Metrics Or Review Criteria
- Exact title match against gold
- Abstract prefix match against gold
- Exact section heading overlap
- Exact subsection heading overlap

## Main Observations
- What happened?
  - The cleanup pass improved subsection recovery without changing title, abstract, or section-level scores.
- What worked?
  - Title stayed `8/8`.
  - Abstract stayed `8/8`.
  - Section overlap stayed `69/71`.
  - Subsection overlap improved from `70/91` to `77/91`.
  - The cleaned matches included:
    - `2024.findings-acl.379`: `In-context learning with noisy ASR transcriptions`
    - `2024.findings-acl.536`: `Planned v.s. Actual Tool Usage`, `Effect of Threshold T`
    - `2024.findings-acl.712`: `RQ1:`, `RQ2:`, `RQ3:` normalization
    - `2024.findings-acl.164`: `Selective Prefix Tuning`
  - False-positive subsection noise such as `Case Study` disappeared.
- What failed or remained unclear?
  - Remaining misses are now mostly real structural misses rather than formatting artifacts:
    - `2024.findings-acl.379`: `Slot Filling with Limited Data`, `Data`
    - `2024.findings-acl.712`: `Datasets, Pruning, BATS Vectors`
    - `2024.findings-acl.731`: `Essay Generation`, `Evaluation Metrics`
    - `2024.findings-acl.783`: several still-missing method and results subsections

## Result
- Better than baseline

## Decision
- Keep

## Next Action
- Treat `outputs/findings-acl-2024-v1-full-placeholder-baseline-v11/` as the new parser baseline.
- Next work should focus on true structural misses and reading-order-related losses rather than formatting cleanup.

## Links
- Related eval set: `eval-sets/findings-acl-2024-v1.md`
- Related gold spec: `eval-sets/findings-acl-2024-v1-gold-fields.md`
- Related baseline record: `experiments/2026-04-09-heading-heuristic-v1.md`
- Related output directory: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v11/`
