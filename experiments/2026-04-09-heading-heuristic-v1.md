# Experiment Record

## Metadata
- Experiment ID: `2026-04-09-heading-heuristic-v1`
- Date: `2026-04-09`
- Author: `Tongyan CONG`

## Question
- Can a small heading heuristic improve section and subsection recovery on the frozen `findings-acl-2024-v1` set by fixing blank-split numbered headings and filtering obvious table or front-matter noise?

## Motivation
- After abstract and title recovery reached `8/8`, heading recovery became the main parser bottleneck.
- Many misses were caused by the same local pattern: the section number and heading text were split across blank lines, while several false positives came from affiliations, formulas, and table labels.

## Baseline
- Baseline commit or prior result: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v8/`
- Why is this the correct baseline?
  - It is the latest full-set baseline with front-matter extraction stabilized.
  - It isolates heading recovery as the next parser task.

## Changed Module
- Which module or tightly related idea was changed?
  - heading detection and paragraph splitting in `src/pdf2slides/stages.py`
- What was intentionally not changed?
  - title extraction
  - abstract extraction
  - OCR backend
  - slide planning
  - evaluation script

## Input Set
- Which PDFs or documents were used?
  - all 8 PDFs in `data/eval/findings-acl-2024-v1/`
- Why were these inputs chosen?
  - The effect needed to be measured on the frozen full set rather than only on the dev papers.

## Procedure
- What command or workflow was used?
  - preprocess page text so blank-split numbered headings such as `3` + `Methodology` are merged before paragraph splitting
  - extend the exact heading lexicon with missing ACL-style headings such as `Methodology`, `Experimental Setup`, `Related Works`, `Results and Analysis`, and `Ethics Statement`
  - reject obvious false heading phrases containing affiliation or table-label cues such as commas, `=`, `laboratory`, `cost`, or `value`
  - stop treating isolated unnumbered `Method` / `Methods` labels as headings
  - keep a small set of empty back-matter sections such as `Conclusions` and `Limitations`
  - add regression tests for blank-split numbered headings and known false positives
  - run `PYTHONPATH=src python3 -m unittest discover -s tests`
  - run `PYTHONPATH=src python3 -m pdf2slides <pdf> --output-root outputs/findings-acl-2024-v1-full-placeholder-baseline-v10` for each eval PDF
  - run `PYTHONPATH=src python3 scripts/eval_dev_headings.py outputs/findings-acl-2024-v1-full-placeholder-baseline-v10 --paper-ids ...`
- Where are the outputs stored?
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v10/`

## Metrics Or Review Criteria
- Exact title match against gold
- Abstract prefix match against gold
- Exact section heading overlap
- Exact subsection heading overlap

## Main Observations
- What happened?
  - The heading heuristic produced a large gain on both section and subsection recovery while preserving the already-fixed title and abstract metrics.
- What worked?
  - Title remained `8/8`.
  - Abstract remained `8/8`.
  - Section overlap improved from `44/71` to `69/71`.
  - Subsection overlap improved from `47/91` to `70/91`.
  - Strongest section gains:
    - `2024.findings-acl.379`: `5/10 -> 9/10`
    - `2024.findings-acl.712`: `5/7 -> 7/7`
    - `2024.findings-acl.731`: `5/11 -> 11/11`
    - `2024.findings-acl.244`: `5/10 -> 10/10`
    - `2024.findings-acl.164`: `4/7 -> 7/7`
  - The heuristic also removed many false sections caused by affiliations and table labels, especially in `2024.findings-acl.536`, `2024.findings-acl.662`, and `2024.findings-acl.731`.
- What failed or remained unclear?
  - Some subsection noise remains, e.g. `claim`, `1.50 Case Study`, and a few shortened headings.
  - `2024.findings-acl.379` and `2024.findings-acl.662` still each miss one top-level section.
  - The heuristic is tuned to the current ACL-style set and may need revision before moving to more diverse formats.

## Result
- Better than baseline

## Decision
- Keep

## Next Action
- Treat `outputs/findings-acl-2024-v1-full-placeholder-baseline-v10/` as the new frozen full-set parser baseline.
- Next parser work should focus on subsection cleanup and remaining reading-order errors rather than front-matter extraction.

## Links
- Related eval set: `eval-sets/findings-acl-2024-v1.md`
- Related gold spec: `eval-sets/findings-acl-2024-v1-gold-fields.md`
- Related baseline record: `experiments/2026-04-09-title-heuristic-v1.md`
- Related output directory: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v10/`
