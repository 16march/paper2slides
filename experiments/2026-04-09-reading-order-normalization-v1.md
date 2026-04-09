# Experiment Record

## Metadata
- Experiment ID: `2026-04-09-reading-order-normalization-v1`
- Date: `2026-04-09`
- Author: `Tongyan CONG`

## Question
- Is the current reading-order protocol undercounting matches because its text normalization is too strict for PDF extraction artifacts?

## Motivation
- Several apparent paragraph misses were visibly present in the predicted blocks.
- The mismatches were often caused by curly quotes, dash variants, dropped hyphens, or diacritics rather than true ordering failures.
- Before adding another ordering heuristic, the protocol itself needed to stop treating these formatting differences as content misses.

## Baseline
- Baseline commit or prior result:
  - `scripts/eval_reading_order.py`
  - existing reports under `outputs/findings-acl-2024-v1-full-placeholder-baseline-v15/` through `v18-hybrid/`
- Why is this the correct baseline?
  - The issue appeared in the current standard protocol, so the comparison needed to isolate the evaluator rather than the parser.

## Changed Module
- Which module or tightly related idea was changed?
  - text normalization in `scripts/eval_reading_order.py`
  - regression coverage in `tests/test_reading_order_eval.py`
- What was intentionally not changed?
  - parser heuristics
  - OCR extraction
  - `StructuredDocument` schema
  - frozen output JSON artifacts

## Input Set
- Which PDFs or documents were used?
  - all 8 PDFs in `data/eval/findings-acl-2024-v1/`
  - the existing output roots `v15`, `v16-layout`, `v17-columns`, and `v18-hybrid`
- Why were these inputs chosen?
  - the goal was to recompute the already-recorded reading-order comparisons under the corrected protocol.

## Procedure
- What command or workflow was used?
  - update normalization to fold Unicode diacritics to ASCII, normalize curly quotes, and ignore punctuation differences
  - add unit tests for normalized matching
  - rerun `python3 scripts/eval_reading_order.py ...` for `v15`, `v16-layout`, `v17-columns`, and `v18-hybrid`
  - overwrite each output root's `reading_order_eval.md`
- Where are the outputs stored?
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v15/reading_order_eval.md`
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v16-layout/reading_order_eval.md`
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v17-columns/reading_order_eval.md`
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v18-hybrid/reading_order_eval.md`

## Metrics Or Review Criteria
- paragraph match
- paragraph order
- figure caption match
- figure caption order
- table caption match
- table caption order
- whether the relative ranking between `v15`, `v16-layout`, `v17-columns`, and `v18-hybrid` changes

## Main Observations
- What happened?
  - The protocol had been undercounting real matches.
- What worked?
  - `v15` improved from `272/355` to `289/355` on paragraph match and from `177/272` to `184/289` on paragraph order.
  - `v15` caption match also improved from `15/23` to `17/23` for figures and from `20/36` to `24/36` for tables.
  - The main ordering conclusion did not flip:
    - `v16-layout` is still unusable,
    - `v17-columns` is still exploratory and still worse than default,
    - `v18-hybrid` is still safer than `columns` but still not better than `v15`.
- What failed or remained unclear?
  - The corrected protocol still cannot separate OCR damage from paragraph segmentation or reading-order errors.
  - `caption_to_asset_link` is still unscored because current outputs do not yet populate first-class assets.

## Result
- Better than baseline

## Decision
- Keep

## Next Action
- Use the normalized protocol as the default for all future reading-order comparisons.
- Continue with local paragraph-boundary or body-region heuristics instead of another full extraction-mode swap.

## Links
- Related reading-order protocol: `docs/reading-order-evaluation.md`
- Related script: `scripts/eval_reading_order.py`
- Related output directories:
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v15/`
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v16-layout/`
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v17-columns/`
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v18-hybrid/`
