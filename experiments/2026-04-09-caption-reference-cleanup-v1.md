# Experiment Record

## Metadata
- Experiment ID: `2026-04-09-caption-reference-cleanup-v1`
- Date: `2026-04-09`
- Author: `Tongyan CONG`

## Question
- After `v20`, can we further improve reading-order recovery by separating true captions from body references such as `Table 2 gives ...`, and by trimming short table-header noise that gets appended to real captions?

## Motivation
- `v20` still left a large fraction of table-caption misses.
- Failure analysis showed two local causes:
  - body paragraphs beginning with `Figure ... shows` or `Table ... gives` were still being misclassified as captions,
  - some true captions had short trailing header fragments such as `Model`, `Method`, `E2E`, or `Length`.

## Baseline
- Baseline commit or prior result:
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v20-caption-label-repair/`
- Why is this the correct baseline?
  - `v20` is the latest reading-order baseline before this caption/reference cleanup pass.

## Changed Module
- Which module or tightly related idea was changed?
  - caption classification and caption text cleanup in `src/pdf2slides/stages.py`
- What was intentionally not changed?
  - extraction mode
  - title heuristics
  - abstract heuristics
  - heading heuristics
  - reading-order evaluation protocol

## Input Set
- Which PDFs or documents were used?
  - all 8 PDFs in `data/eval/findings-acl-2024-v1/`
- Why were these inputs chosen?
  - the comparison should remain on the frozen reconstruction set and stay directly comparable to `v20`

## Procedure
- What command or workflow was used?
  - tighten caption detection so only strings beginning with `Figure N:` / `Fig. N:` / `Table N:` are treated as captions
  - keep body references like `Figure 2 illustrates ...` and `Table 2 gives ...` as ordinary paragraphs
  - trim a caption’s final short suffix when it looks like appended header noise after the last completed sentence
  - add regression tests for these cases
  - rerun all 8 eval PDFs into `outputs/findings-acl-2024-v1-full-placeholder-baseline-v21-caption-reference-cleanup/`
  - rerun `scripts/eval_dev_headings.py` and `scripts/eval_reading_order.py`
- Where are the outputs stored?
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v21-caption-reference-cleanup/`

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
  - The cleanup pass improved paragraph recovery again and produced the biggest table-caption gain so far.
- What worked?
  - Heading-side metrics stayed unchanged:
    - `title 8/8`
    - `abstract 8/8`
    - `sections 70/71`
    - `subsections 91/91`
  - Relative to `v20`, paragraph metrics improved:
    - paragraph match `300/355 -> 306/355`
    - paragraph order `260/300 -> 266/306`
  - Table-caption metrics improved strongly:
    - table caption match `24/36 -> 31/36`
    - table caption order `22/24 -> 29/31`
  - Figure-caption metrics stayed strong:
    - figure caption match `20/23`
    - figure caption order `19/20`
  - The largest targeted wins were:
    - `2024.findings-acl.783`: table caption match `5/7 -> 7/7`
    - `2024.findings-acl.731`: table caption match `5/6 -> 6/6`
    - `2024.findings-acl.536`: table caption match `4/5 -> 5/5`
- What failed or remained unclear?
  - Some table-caption misses remain because OCR/text extraction still merges or truncates longer caption content.
  - Several remaining paragraph misses are definition-style or equation-adjacent text rather than caption/reference confusion.

## Result
- Better than baseline

## Decision
- Keep

## Next Action
- Use `v21` as the current reading-order baseline.
- Focus the next analysis on:
  - remaining long table-caption truncation,
  - definition-style paragraph anchors,
  - equation-adjacent body text and table-header contamination.

## Links
- Related baseline: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v20-caption-label-repair/`
- Related output directory: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v21-caption-reference-cleanup/`
- Related protocol: `docs/reading-order-evaluation.md`
