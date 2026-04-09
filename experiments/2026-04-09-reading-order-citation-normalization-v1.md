# Experiment Record

## Metadata
- Experiment ID: `2026-04-09-reading-order-citation-normalization-v1`
- Date: `2026-04-09`
- Author: `Tongyan CONG`

## Question
- Should paragraph-anchor matching in the reading-order protocol ignore inline author-year citation spans when comparing gold anchors against predicted paragraph blocks?

## Motivation
- After `v22`, many remaining paragraph misses were not caused by paragraph extraction or ordering.
- Failure analysis showed cases such as:
  - `Dense retrieval is currently ...` vs `Dense retrieval (Lee et al., 2019; Karpukhin et al., 2020) is currently ...`
  - `We present MINDER, ...` vs `We present MINDER (Li et al., 2023c), ...`
  - `Tool learning, which uses ...` vs `Tool learning (Schick et al., 2023; ...) which uses ...`
- These should not count as reading-order failures.

## Baseline
- Baseline commit or prior result:
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v22-formula-like-relaxation/reading_order_eval.md`
- Why is this the correct baseline?
  - `v22` is the current reading-order baseline before refining the paragraph proxy.

## Changed Module
- Which module or tightly related idea was changed?
  - paragraph-anchor matching in `scripts/eval_reading_order.py`
- What was intentionally not changed?
  - parser output
  - block typing
  - extraction mode
  - heading evaluation
  - figure-caption matching
  - table-caption matching

## Input Set
- Which PDFs or documents were used?
  - the existing `v22` outputs on all 8 frozen papers
- Why were these inputs chosen?
  - the goal is to refine the evaluation protocol, not rerun a different parser.

## Procedure
- What command or workflow was used?
  - inspect `v22` paragraph misses and identify cases where the only mismatch was an inline author-year citation span
  - add a citation-strip pass for paragraph matching only:
    - remove parenthetical or bracketed spans containing `et al.` or 4-digit years
    - keep caption matching behavior unchanged
  - add regression tests for citation stripping and citation-aware paragraph matching
  - rerun `scripts/eval_reading_order.py` on `outputs/findings-acl-2024-v1-full-placeholder-baseline-v22-formula-like-relaxation/`
- Where are the outputs stored?
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v22-formula-like-relaxation/reading_order_eval.md`

## Metrics Or Review Criteria
- paragraph match
- paragraph order
- figure caption match
- table caption match
- whether the protocol still preserves caption exactness

## Main Observations
- What happened?
  - Citation-aware paragraph matching removed another class of false negatives without changing any system output.
- What worked?
  - Aggregate paragraph metrics improved:
    - paragraph match `322/355 -> 330/355`
    - paragraph order `279/322 -> 286/330`
  - Caption metrics stayed unchanged:
    - figure caption match `20/23`
    - figure caption order `19/20`
    - table caption match `31/36`
    - table caption order `29/31`
  - The main paper-level gains were:
    - `2024.findings-acl.662`: `37/44 -> 40/44`
    - `2024.findings-acl.536`: `35/40 -> 37/40`
    - `2024.findings-acl.783`: `53/58 -> 55/58`
    - `2024.findings-acl.712`: `52/53 -> 53/53`
- What failed or remained unclear?
  - Remaining misses now more clearly reflect OCR surface variation, truncation, or actual paragraph-boundary failures.
  - This pass does not address equation-symbol substitutions such as OCR replacing `=` with other glyphs.

## Result
- Better than baseline

## Decision
- Keep

## Next Action
- Use citation-aware paragraph-anchor matching as the default reading-order protocol.
- Focus the next failure analysis on:
  - OCR surface mismatch in theory-heavy text,
  - truncated paragraph starts,
  - longer caption truncation.

## Links
- Related baseline: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v22-formula-like-relaxation/`
- Related protocol: `docs/reading-order-evaluation.md`
