# Experiment Record

## Metadata
- Experiment ID: `2026-04-09-caption-label-repair-v1`
- Date: `2026-04-09`
- Author: `Tongyan CONG`

## Question
- After the local paragraph-boundary repair, can a second local pass that splits merged captions and inline label-style subparagraphs improve reading-order recovery further without hurting heading recovery?

## Motivation
- `v19` still had two visible residual patterns:
  - multiple captions merged into a single block, for example `Figure 2 ... Table 4 ...`
  - long body blocks that still contained inline label markers such as `Identifiers.`, `Training.`, `Inference.`, or `Evaluation.`
- Both errors were local segmentation problems inside already-extracted text, so they could be attacked without changing extraction mode or global ordering.

## Baseline
- Baseline commit or prior result:
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v19-local-paragraph-repair/`
- Why is this the correct baseline?
  - `v19` is the first stable reading-order baseline with improved paragraph boundaries and unchanged heading metrics.

## Changed Module
- Which module or tightly related idea was changed?
  - post-processing paragraph splitting in `src/pdf2slides/stages.py`
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
  - the comparison should remain on the frozen reconstruction set and stay directly comparable to `v19`

## Procedure
- What command or workflow was used?
  - add post-processing that splits a paragraph when:
    - a caption block starting with `Figure X:` or `Table Y:` contains another caption starter later in the same text
    - a long paragraph contains inline label markers such as `Identifiers.`, `Training.`, `Inference.`, `Evaluation.`, `Data Preparation.`, or `Implementation Details.`
  - keep the existing local paragraph-boundary repair
  - add regression tests for inline label splitting and multi-caption splitting
  - rerun all 8 eval PDFs into `outputs/findings-acl-2024-v1-full-placeholder-baseline-v20-caption-label-repair/`
  - rerun `scripts/eval_dev_headings.py` and `scripts/eval_reading_order.py`
- Where are the outputs stored?
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v20-caption-label-repair/`

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
  - The local caption/label pass improved the reading-order metrics again while keeping the parser baseline intact.
- What worked?
  - Heading-side metrics stayed unchanged:
    - `title 8/8`
    - `abstract 8/8`
    - `sections 70/71`
    - `subsections 91/91`
  - Relative to `v19`, paragraph metrics improved slightly:
    - paragraph match `299/355 -> 300/355`
    - paragraph order `257/299 -> 260/300`
  - Figure caption recovery improved more clearly:
    - figure caption match `18/23 -> 20/23`
    - figure caption order `17/18 -> 19/20`
  - The gain came from exactly the targeted failure modes:
    - `2024.findings-acl.379` now separates merged `Figure 2` / `Table 4` and `Figure 3` / `Table 7` blocks
    - `2024.findings-acl.662` now separates more inline label-style subparagraphs such as `Identifiers.`, `Training.`, and `Inference.`
- What failed or remained unclear?
  - Table caption match did not improve; the remaining misses are now more about caption truncation or attached table-header noise than merged caption starters.
  - The residual paragraph misses are increasingly citation-sensitive or footnote-marker-sensitive rather than pure local segmentation errors.

## Result
- Better than baseline

## Decision
- Keep

## Next Action
- Use `v20` as the current reading-order baseline.
- Focus the next analysis on:
  - table-caption cleanup,
  - inline footnote-marker noise such as `SGET1` / `GitHub1`,
  - citation-heavy paragraphs that still fail anchor matching.

## Links
- Related baseline: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v19-local-paragraph-repair/`
- Related output directory: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v20-caption-label-repair/`
- Related protocol: `docs/reading-order-evaluation.md`
