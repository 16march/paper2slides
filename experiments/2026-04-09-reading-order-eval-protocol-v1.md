# Experiment Record

## Metadata
- Experiment ID: `2026-04-09-reading-order-eval-protocol-v1`
- Date: `2026-04-09`
- Author: `Tongyan CONG`

## Question
- Can the project define and run a first reading-order evaluation protocol on top of `StructuredDocument v0` using the existing frozen annotations?

## Motivation
- After heading recovery stabilized, the next research bottleneck needed to move toward reading order.
- But reading order was still underspecified and had no concrete evaluation script.
- The project needed a minimal protocol that uses the current gold annotations without waiting for a new block-level annotation round.

## Baseline
- Baseline commit or prior result: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v15/`
- Why is this the correct baseline?
  - It is the first full-set output snapshot that already carries the `StructuredDocument v0` ordering fields.

## Changed Module
- Which module or tightly related idea was changed?
  - reading-order evaluation protocol and script
- What was intentionally not changed?
  - parser heuristics
  - OCR extraction
  - slide planning
  - IR schema

## Input Set
- Which PDFs or documents were used?
  - all 8 PDFs in `data/eval/findings-acl-2024-v1/`
  - corresponding JSON annotations in `eval-sets/findings-acl-2024-v1-annotations/`
- Why were these inputs chosen?
  - they are already the project's frozen reconstruction evaluation set

## Procedure
- What command or workflow was used?
  - define protocol v1 in `docs/reading-order-evaluation.md`
  - implement `scripts/eval_reading_order.py`
  - evaluate paragraph-anchor match and order against `paragraph_sequence`
  - evaluate figure/table caption match and order against caption fields
  - evaluate section and subsection contiguity from ordered `content_block_ids`
  - run `python3 scripts/eval_reading_order.py outputs/findings-acl-2024-v1-full-placeholder-baseline-v15 --paper-ids ...`
- Where are the outputs stored?
  - protocol doc: `docs/reading-order-evaluation.md`
  - script: `scripts/eval_reading_order.py`

## Metrics Or Review Criteria
- paragraph match
- paragraph order
- figure caption match
- figure caption order
- table caption match
- table caption order
- section contiguous spans
- subsection contiguous spans

## Main Observations
- What happened?
  - The project now has a runnable reading-order evaluation protocol tied to `StructuredDocument v0`.
- What worked?
  - The script runs on the frozen 8-paper set.
  - It shows that section and subsection content are already contiguous in the current parser output:
    - sections: `56/56`
    - subsections: `87/87`
  - It also exposes the actual remaining weakness at paragraph and caption level:
    - paragraph match: `289/355`
    - paragraph order: `184/289`
    - figure caption match: `17/23`
    - table caption match: `24/36`
- What failed or remained unclear?
  - True caption-to-asset grounding is still not scored because `assets` are not yet populated in current outputs.
  - The current paragraph metrics still mix OCR damage, paragraph segmentation errors, and true reading-order errors.

## Result
- Better than baseline

## Decision
- Keep

## Next Action
- Use protocol v1 as the standard comparison for the next reading-order experiments.
- Compare at least one column-aware ordering baseline against the current simple ordering.
- Add true caption grounding once `assets` and `caption_block_ids` are implemented.

## Links
- Related IR doc: `docs/intermediate-representation.md`
- Related reading-order doc: `docs/reading-order-evaluation.md`
- Related output root: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v15/`
