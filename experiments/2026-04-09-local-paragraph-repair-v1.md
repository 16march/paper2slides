# Experiment Record

## Metadata
- Experiment ID: `2026-04-09-local-paragraph-repair-v1`
- Date: `2026-04-09`
- Author: `Tongyan CONG`

## Question
- Can a local inline paragraph-boundary repair improve reading-order quality without changing extraction mode or hurting heading recovery?

## Motivation
- `v18-hybrid` showed that global body-slot replacement was too coarse.
- Failure analysis on `v15` showed many paragraph-order errors came from long merged body blocks, not from section grouping.
- The next step should therefore repair local paragraph boundaries inside the default `pdftotext` stream instead of replacing the whole page order.

## Baseline
- Baseline commit or prior result:
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v15/`
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v18-hybrid/`
- Why is this the correct baseline?
  - `v15` is the stable normalized reading-order baseline.
  - `v18-hybrid` is the latest negative result showing that coarse reordering is not sufficient.

## Changed Module
- Which module or tightly related idea was changed?
  - local paragraph splitting heuristic in `src/pdf2slides/stages.py`
- What was intentionally not changed?
  - `pdftotext` extraction mode
  - title heuristics
  - abstract heuristics
  - heading heuristics
  - reading-order evaluation protocol

## Input Set
- Which PDFs or documents were used?
  - all 8 PDFs in `data/eval/findings-acl-2024-v1/`
- Why were these inputs chosen?
  - the comparison should stay on the frozen reconstruction set and remain directly comparable to `v15` and `v18`

## Procedure
- What command or workflow was used?
  - inspect merged paragraph failures in `v15`
  - add a conservative inline paragraph break rule:
    - only inside normal body text,
    - only after sentence-ending punctuation,
    - prefer discourse-style paragraph starts such as `In this paper`, `We`, `Our`, `Different`, `Historically`, and similar local cues,
    - otherwise allow a break after a very short completed previous line
  - add regression tests for the new inline paragraph splitting behavior
  - rerun all 8 eval PDFs into `outputs/findings-acl-2024-v1-full-placeholder-baseline-v19-local-paragraph-repair/`
  - rerun `scripts/eval_dev_headings.py` and `scripts/eval_reading_order.py`
- Where are the outputs stored?
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v19-local-paragraph-repair/`

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
  - The local repair improved reading-order metrics materially while preserving the strong heading baseline.
- What worked?
  - Heading-side metrics stayed unchanged:
    - `title 8/8`
    - `abstract 8/8`
    - `sections 70/71`
    - `subsections 91/91`
  - Paragraph metrics improved over `v15`:
    - paragraph match `289/355 -> 299/355`
    - paragraph order `184/289 -> 257/299`
  - Figure caption recovery also improved slightly:
    - figure caption match `17/23 -> 18/23`
    - figure caption order `16/17 -> 17/18`
  - The biggest order gains appeared in papers that previously had visibly merged body blocks:
    - `2024.findings-acl.712`: `24/49 -> 45/49`
    - `2024.findings-acl.783`: `28/51 -> 43/50`
    - `2024.findings-acl.662`: `21/31 -> 27/33`
    - `2024.findings-acl.731`: `30/41 -> 36/41`
- What failed or remained unclear?
  - Table caption recovery did not move.
  - The heuristic is still text-surface based and cannot distinguish true paragraph boundaries from all author-intended stylistic line breaks.
  - Some remaining misses still come from inline citations, figure references, or OCR surface differences rather than pure ordering.

## Result
- Better than baseline

## Decision
- Keep

## Next Action
- Use `v19` as the current reading-order comparison baseline.
- Analyze the remaining misses before adding another heuristic.
- Prioritize caption-sensitive and citation-sensitive failures rather than another global reordering attempt.

## Links
- Related baseline: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v15/`
- Related hybrid negative control: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v18-hybrid/`
- Related output directory: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v19-local-paragraph-repair/`
- Related protocol: `docs/reading-order-evaluation.md`
