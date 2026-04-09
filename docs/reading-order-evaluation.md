# Reading-Order Evaluation

## Decision
The project should evaluate reading order through `StructuredDocument v0`, not as a separate output format.

The first protocol should therefore score the IR fields that reading order directly affects:
- paragraph sequence,
- caption sequence,
- section-content continuity,
- subsection-content continuity.

## What Can Be Scored Now
The current eval set already provides:
- `paragraph_sequence`
- `figure_caption_texts`
- `table_caption_texts`
- `caption_to_asset_link`

The current system output now provides:
- top-level `blocks`
- block-level `reading_order_index`
- page-level ordered `block_ids`
- section and subsection `content_block_ids`

That is enough for a first reading-order evaluation pass, even though true asset grounding is not yet implemented.

## Protocol v1
Use `scripts/eval_reading_order.py`.

This protocol has two parts:

1. Gold-backed proxy metrics using existing annotations
2. IR-internal continuity metrics using ordered block IDs

## Gold-Backed Proxy Metrics

### 1. Paragraph Match
Definition:
- For each gold `paragraph_sequence` anchor, check whether any predicted `paragraph` block contains that anchor text after normalization.

Normalization:
- fold Unicode diacritics to ASCII,
- normalize curly quotes and dash variants,
- drop punctuation differences before matching.
- ignore inline citation spans such as `(Lee et al., 2019)` during paragraph-anchor matching.

Why it matters:
- If reading order is badly wrong, the extracted paragraph units often become merged, truncated, or misplaced, and anchor recall drops.

Current interpretation:
- low score can reflect paragraph segmentation problems,
- low score can reflect reading-order failure,
- low score can also reflect OCR extraction damage.

This is therefore a mixed but useful downstream-sensitive proxy.

### 2. Paragraph Order
Definition:
- For matched paragraph anchors, compare the sequence of predicted `reading_order_index` values against the gold paragraph order.
- Score with longest increasing subsequence over the matched anchors.

Why it matters:
- This is the closest current proxy to true reading-order correctness in main-body prose.

### 3. Figure Caption Match
Definition:
- Compare gold `figure_caption_texts` against predicted caption blocks whose text starts with `Figure`.

Why it matters:
- Wrong ordering and wrong block grouping often hide or distort captions.

### 4. Figure Caption Order
Definition:
- For matched figure captions, compare predicted caption order against the gold visual order.

### 5. Table Caption Match
Definition:
- Compare gold `table_caption_texts` against predicted caption blocks whose text starts with `Table`.

### 6. Table Caption Order
Definition:
- For matched table captions, compare predicted caption order against the gold visual order.

## IR-Internal Continuity Metrics

### 7. Section Contiguous Spans
Definition:
- For each section, check whether its `content_block_ids` form one contiguous span in `reading_order_index`.

Why it matters:
- If a section is internally fragmented in reading order, downstream summarization and slide planning become unstable even when the heading itself is correct.

### 8. Subsection Contiguous Spans
Definition:
- Same as above, but at subsection level.

Why it matters:
- This measures whether local content grouping is consistent after parsing.

## What Protocol v1 Does Not Score Yet

### Caption-to-Asset Grounding
Although the gold set has `caption_to_asset_link`, the current outputs do not yet populate:
- first-class `assets`
- `caption_block_ids`
- asset IDs such as `figure_1` or `table_3`

So protocol v1 cannot yet measure true caption grounding.

That should become protocol v2 once `assets` are implemented.

### True Block-Level Reading-Order Gold
The current annotations do not include:
- explicit block IDs,
- page-local block order labels,
- paragraph-to-page coordinates.

So protocol v1 is still a proxy-based evaluation, not full block-order supervision.

## Recommended Use
For the current project stage:
- keep using heading recovery as the structure baseline,
- use protocol v1 to compare reading-order changes,
- do not over-interpret a single score in isolation.

Read the metrics in this order:
1. paragraph match
2. paragraph order
3. figure/table caption match
4. section/subsection contiguous spans

The continuity metrics tell you whether the parsed IR is internally coherent.
The paragraph and caption metrics tell you whether the upstream ordering is actually recovering the intended content sequence.

## Current Reference Run
The current reading-order reference run is:
- system output root: `outputs/findings-acl-2024-v1-full-placeholder-baseline-v22-formula-like-relaxation/`

Headline results on the frozen 8-paper set:
- paragraph match: `330/355`
- paragraph order: `286/330`
- figure caption match: `20/23`
- figure caption order: `19/20`
- table caption match: `31/36`
- table caption order: `29/31`
- section contiguous spans: `56/56`
- subsection contiguous spans: `87/87`

Interpretation:
- the protocol previously undercounted matches when gold and prediction differed only by quote style, dash style, or diacritics,
- the current local paragraph-boundary repair plus inline caption/label splitting improves paragraph order materially without regressing heading recovery,
- tightening caption classification so body references like `Table 2 gives ...` stay in paragraphs, and trimming short trailing header noise from real captions, improves both paragraph and table-caption recovery,
- relaxing `formula_like` classification for long narrative paragraphs with inline equations or set notation improves paragraph recovery again without changing heading metrics,
- ignoring author-year citation spans during paragraph-anchor matching removes another source of false negatives in reading-order evaluation,
- current structure grouping is already internally contiguous,
- the main remaining weakness is paragraph-level and caption-level ordering/completeness,
- this supports the project claim that OCR and reading order are now more important bottlenecks than heading recovery.

## Next Step
The next implementation round should not expand the IR again.

It should analyze the remaining paragraph misses after `v22`, especially:
- OCR surface variation inside definition-style or theorem-style prose,
- longer caption truncation that still prevents exact caption recovery.
