# Experiment Record

## Metadata
- Experiment ID: `2026-04-09-structured-document-v0-schema-v1`
- Date: `2026-04-09`
- Author: `Tongyan CONG`

## Question
- Can the current `StructuredDocument` output be migrated toward `StructuredDocument v0` without changing the already-frozen heading recovery behavior?

## Motivation
- The project decided to move to an IR-first mainline, but the current `04_structured_document.json` was still too thin for reading-order evaluation.
- The next step needed a minimal schema migration that adds reconstruction-IR fields while preserving current parser behavior and current heading evaluation.

## Baseline
- Baseline commit or prior result: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v14/`
- Why is this the correct baseline?
  - It is the frozen full-set parser baseline before the IR schema migration.
  - It already stabilized title, abstract, section, and subsection recovery on the 8-paper evaluation set.

## Changed Module
- Which module or tightly related idea was changed?
  - `src/pdf2slides/schema.py`
  - `src/pdf2slides/stages.py`
- What was intentionally not changed?
  - heading heuristics
  - title extraction
  - abstract extraction
  - slide planning behavior
  - evaluation script

## Input Set
- Which PDFs or documents were used?
  - all 8 PDFs in `data/eval/findings-acl-2024-v1/`
- Why were these inputs chosen?
  - the schema migration should be checked against the same frozen full set as the parser baseline

## Procedure
- What command or workflow was used?
  - add `paper_id`, `page_count`, top-level `blocks`, `assets`, and `metadata.ir_version` to `StructuredDocument`
  - add `reading_order_index` to every block
  - add page-level `width`, `height`, and ordered `block_ids`
  - add stable `section_id` and `subsection_id`
  - add ordered `content_block_ids` plus page ranges on sections and subsections
  - keep existing nested `content_blocks` and nested `subsections` so current consumers still work
  - add regression assertions in `tests/test_pipeline.py`
  - run `PYTHONPATH=src python3 -m unittest discover -s tests`
  - run `PYTHONPATH=src python3 - <<'PY' ... run_pipeline(...) ... PY` for each eval PDF into `outputs/findings-acl-2024-v1-full-placeholder-baseline-v15/`
  - run `python3 scripts/eval_dev_headings.py outputs/findings-acl-2024-v1-full-placeholder-baseline-v15 --paper-ids ...`
- Where are the outputs stored?
  - `outputs/findings-acl-2024-v1-full-placeholder-baseline-v15/`

## Metrics Or Review Criteria
- Exact title match against gold
- Abstract prefix match against gold
- Exact section heading overlap
- Exact subsection heading overlap
- Presence of the new `StructuredDocument v0` fields in `04_structured_document.json`

## Main Observations
- What happened?
  - The structured document JSON was successfully migrated toward `StructuredDocument v0` without changing the heading recovery results.
- What worked?
  - Title remained `8/8`.
  - Abstract remained `8/8`.
  - Section overlap remained `70/71`.
  - Subsection overlap remained `91/91`.
  - The output now includes:
    - `paper_id`
    - `page_count`
    - top-level `blocks`
    - `assets`
    - `metadata.ir_version`
    - page-level `block_ids`
    - block-level `reading_order_index`
    - `section_id` and `subsection_id`
    - ordered `content_block_ids`
- What failed or remained unclear?
  - `assets` still remain empty placeholders because figures, tables, and equations are not yet promoted to first-class assets.
  - The only remaining heading mismatch is still the spelling variant in `2024.findings-acl.662`.

## Result
- Better than baseline

## Decision
- Keep

## Next Action
- Treat `outputs/findings-acl-2024-v1-full-placeholder-baseline-v15/` as the current IR-migrated structured-output snapshot.
- Keep `v14` as the frozen parser comparison baseline.
- Use the new block-level ordering fields to define a reading-order evaluation protocol next.

## Links
- Related IR decision: `docs/intermediate-representation.md`
- Related parser baseline freeze: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v14/FREEZE.md`
- Related output directory: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v15/`
