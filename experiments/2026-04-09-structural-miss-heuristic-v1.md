# Experiment Record

## Metadata
- Experiment ID: `2026-04-09-structural-miss-heuristic-v1`
- Date: `2026-04-09`
- Author: `Tongyan CONG`

## Question
- Can a small structural heuristic close the remaining true heading misses after `v11` by distinguishing top-level versus subsection unnumbered headings and by handling misnumbered top-level headings conservatively?

## Motivation
- After `v11`, most formatting noise was gone, but several real headings were still missing:
  - `2024.findings-acl.379`: `Related Work`, `Slot Filling with Limited Data`, `Data`
  - `2024.findings-acl.712`: `Datasets, Pruning, BATS Vectors`
  - `2024.findings-acl.731`: `Essay Generation`, `Evaluation Metrics`
  - `2024.findings-acl.164`: `Experiments` children were being mis-grouped in intermediate attempts
- The remaining problem was not OCR cleanup anymore; it was heading type assignment.

## Baseline
- Baseline commit or prior result: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v11/`
- Why is this the correct baseline?
  - It is the strongest parser baseline before the final structural grouping fix.
  - It already resolved most formatting artifacts, so later gains can be interpreted as true structural recovery gains.

## Changed Module
- Which module or tightly related idea was changed?
  - heading classification and section/subsection assignment in `src/pdf2slides/stages.py`
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
  - The remaining misses were spread across multiple papers and needed frozen full-set verification.

## Procedure
- What command or workflow was used?
  - separate explicit top-level heading words from explicit subsection heading words
  - allow short heading continuation fragments to join the previous heading
  - allow short numbered headings with commas while still filtering affiliation-like content
  - treat only a small subset of top-level headings as valid even when misnumbered, to recover cases like `2.2 Related Work` without promoting `4.1 Experimental Setup` to a section
  - add regression tests for these cases
  - run `PYTHONPATH=src python3 -m unittest discover -s tests`
  - run `PYTHONPATH=src python3 -m pdf2slides <pdf> --output-root outputs/findings-acl-2024-v1-full-placeholder-baseline-v13` for each eval PDF
  - run `PYTHONPATH=src python3 scripts/eval_dev_headings.py outputs/findings-acl-2024-v1-full-placeholder-baseline-v13 --paper-ids ...`
- Where are the outputs stored?
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v13/`

## Metrics Or Review Criteria
- Exact title match against gold
- Abstract prefix match against gold
- Exact section heading overlap
- Exact subsection heading overlap

## Main Observations
- What happened?
  - The structural grouping heuristic closed most of the remaining true misses while preserving the already-fixed title and abstract behavior.
- What worked?
  - Title remained `8/8`.
  - Abstract remained `8/8`.
  - Section overlap improved from `69/71` to `70/71`.
  - Subsection overlap improved from `77/91` to `87/91`.
  - The following papers now match perfectly on both sections and subsections:
    - `2024.findings-acl.379`
    - `2024.findings-acl.712`
    - `2024.findings-acl.731`
    - `2024.findings-acl.164`
  - `2024.findings-acl.536`, `2024.findings-acl.244`, and `2024.findings-acl.662` stayed stable.
- What failed or remained unclear?
  - The remaining misses are concentrated in `2024.findings-acl.783`.
  - Current misses there are:
    - `Settings`
    - `Results`
    - `Discussion`
    - `Translation and Semantic Parsing`
  - There is still one wording mismatch:
    - predicted `Difference Between Machine Translation and Semantic Parsing`
    - gold `Translation and Semantic Parsing`

## Result
- Better than baseline

## Decision
- Keep

## Next Action
- Treat `outputs/findings-acl-2024-v1-full-placeholder-baseline-v13/` as the new full-set parser baseline.
- Focus next work on the remaining hard case `2024.findings-acl.783`, especially heading shortening and fine-grained grouping inside `Results` / `Discussion`.

## Links
- Related eval set: `eval-sets/findings-acl-2024-v1.md`
- Related gold spec: `eval-sets/findings-acl-2024-v1-gold-fields.md`
- Related baseline record: `experiments/2026-04-09-subsection-cleanup-v1.md`
- Related output directory: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v13/`
