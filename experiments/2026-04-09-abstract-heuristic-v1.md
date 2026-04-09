# Experiment Record

## Metadata
- Experiment ID: `2026-04-09-abstract-heuristic-v1`
- Date: `2026-04-09`
- Author: `Tongyan CONG`

## Question
- Can a small abstract-start heuristic remove short figure or layout noise after the `Abstract` heading on the full `findings-acl-2024-v1` set?

## Motivation
- The first full 8-paper evaluation showed that abstract isolation was the weakest stable parser metric after title recovery.
- Several failures were clearly caused by short non-abstract lines immediately after `Abstract`, so this was a good low-cost parser fix before touching OCR or reading order.

## Baseline
- Baseline commit or prior result: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v5/`
- Why is this the correct baseline?
  - It is the first frozen full-set baseline after all 8 papers were labeled.
  - Its failures were already recorded in `experiments/2026-04-08-full-v5-heading-eval.md`.

## Changed Module
- Which module or tightly related idea was changed?
  - `infer_abstract()` in `src/pdf2slides/stages.py`
- What was intentionally not changed?
  - title extraction
  - heading detection
  - section parsing
  - OCR backend
  - evaluation script

## Input Set
- Which PDFs or documents were used?
  - all 8 PDFs in `data/eval/findings-acl-2024-v1/`
- Why were these inputs chosen?
  - The heuristic should be judged against the frozen full set, not only against the dev papers.

## Procedure
- What command or workflow was used?
  - update `infer_abstract()` so it skips short non-body lines before the first abstract sentence
  - add targeted tests in `tests/test_pipeline.py`
  - run `PYTHONPATH=src python3 -m unittest discover -s tests`
  - run `PYTHONPATH=src python3 -m pdf2slides <pdf> --output-root outputs/findings-acl-2024-v1-full-placeholder-baseline-v7` for each eval PDF
  - run `PYTHONPATH=src python3 scripts/eval_dev_headings.py outputs/findings-acl-2024-v1-full-placeholder-baseline-v7 --paper-ids ...`
- Where are the outputs stored?
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v7/`

## Metrics Or Review Criteria
- Abstract prefix match against gold
- Regression check on title recovery
- Regression check on section and subsection overlap

## Main Observations
- What happened?
  - The heuristic removed the short leading noise from all four previously failing abstracts.
- What worked?
  - Abstract recovery improved from `4/8` to `8/8`.
  - The fixed failures were:
    - `2024.findings-acl.244`: removed formula-like noise before the real abstract
    - `2024.findings-acl.536`: skipped `Budget Constraint` / `Method` before the abstract body
    - `2024.findings-acl.731`: skipped `Descriptive analysis`
    - `2024.findings-acl.164`: skipped `Add & Norm`
  - Title, section, and subsection scores were unchanged relative to `v5`.
- What failed or remained unclear?
  - `2024.findings-acl.731` title recovery is still wrong because the title spans two lines and the current title heuristic only selects one line.
  - Heading recovery remains the next structural bottleneck after abstract extraction is fixed.

## Result
- Better than baseline

## Decision
- Keep

## Next Action
- Prioritize title recovery for multi-line titles, starting with `2024.findings-acl.731`.
- Then return to section and subsection under-recovery on `379`, `731`, and `164`.

## Links
- Related eval set: `eval-sets/findings-acl-2024-v1.md`
- Related gold spec: `eval-sets/findings-acl-2024-v1-gold-fields.md`
- Related baseline record: `experiments/2026-04-08-full-v5-heading-eval.md`
- Related output directory: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v7/`
