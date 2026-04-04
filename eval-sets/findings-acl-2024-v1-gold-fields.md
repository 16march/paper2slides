# Findings ACL 2024 Eval Set v1 Gold Fields

## Purpose
This file defines the first-pass gold annotation fields for:

```text
eval-sets/findings-acl-2024-v1.md
```

The goal is to support a realistic reconstruction baseline without creating a heavy full-layout annotation burden.

This first-pass gold spec is designed to evaluate the current thesis priorities:
- text recovery,
- reading order,
- structure parsing,
- caption grounding,
- reconstruction-oriented usability.

## Annotation Principle
Annotate only the smallest set of fields needed to make reconstruction experiments comparable.

Do **not** start with:
- token-level transcription alignment,
- bounding boxes for every text span,
- page-level pixel-perfect layout targets,
- full slide-level gold outputs.

Those may be added later if a specific experiment truly requires them.

## Annotation Unit
The primary annotation unit is the paper, not the page.

Some fields refer to ordered content spans inside the paper, but the gold target should stay focused on paper-level structure rather than full visual layout.

## Required Gold Fields

### 1. Identity And Core Text
- `paper_id`
- `title`
- `abstract`

Purpose:
- evaluate title and abstract recovery,
- verify basic extraction correctness,
- anchor the rest of the annotation record.

### 2. Section Structure
- `ordered_section_headings`
- `ordered_subsection_headings`

Recommended format:

```json
{
  "ordered_section_headings": [
    "Introduction",
    "Related Work",
    "Method",
    "Experiments",
    "Conclusion"
  ]
}
```

Purpose:
- evaluate section parsing,
- check whether the recovered document skeleton is correct,
- support later slide planning from paper structure.

### 3. Paragraph Sequence
- `paragraph_sequence`

Definition:
- an ordered list of paragraph identifiers or paragraph snippets representing the intended reading order of the main body content.

Recommended annotation rule:
- use stable local paragraph IDs if available,
- otherwise use short distinctive text snippets,
- keep the sequence focused on main-body reading order rather than every tiny fragment.

Purpose:
- evaluate two-column reading order,
- check whether paragraphs are merged or interleaved incorrectly,
- support downstream structure parsing analysis.

### 4. Figure And Table Captions
- `figure_caption_texts`
- `table_caption_texts`

Definition:
- the caption texts that should be recovered for figures and tables.

Purpose:
- evaluate caption extraction,
- support figure/table grounding checks,
- verify that the pipeline preserves non-paragraph content needed for later slide generation.

### 5. Caption Grounding
- `caption_to_asset_link`

Definition:
- the association between a caption and the figure or table it belongs to.

Recommended format:

```json
{
  "caption_to_asset_link": [
    {
      "caption_type": "figure",
      "caption_text": "Figure 1: Overview of the proposed method.",
      "asset_id": "figure_1"
    }
  ]
}
```

Purpose:
- evaluate whether caption text is attached to the correct asset,
- support later figure/table inclusion in slide planning.

### 6. Equation Presence
- `display_equation_presence`

Definition:
- whether the paper contains display-style equations that should appear as explicit structured objects.

First-pass recommendation:
- start with presence or coarse counts,
- do not require full LaTeX transcription in v1.

Purpose:
- capture whether the pipeline preserves equations as first-class content,
- avoid ignoring formula-heavy papers in the reconstruction setup.

### 7. Footnote Presence
- `footnote_presence`

Definition:
- whether the paper includes footnotes that should be recognized as explicit structural elements.

First-pass recommendation:
- annotate boolean presence first,
- defer detailed footnote text annotation unless it becomes necessary.

Purpose:
- keep footnotes visible in the evaluation scope without overloading annotation.

## Optional Fields
These fields are useful, but not required in the first annotation pass:
- `author_names`
- `author_affiliations`
- `keyword_list`
- `display_equation_count`
- `figure_count`
- `table_count`

These can be added later if the baseline becomes stable and annotation cost remains manageable.

## Minimal JSON Shape
One practical first-pass annotation record could look like:

```json
{
  "paper_id": "2024.findings-acl.379",
  "title": "Speech-based Slot Filling using Large Language Models",
  "abstract": "....",
  "ordered_section_headings": [
    "Introduction",
    "Method",
    "Experiments",
    "Conclusion"
  ],
  "ordered_subsection_headings": [],
  "paragraph_sequence": [
    "p01",
    "p02",
    "p03"
  ],
  "figure_caption_texts": [
    "Figure 1: ..."
  ],
  "table_caption_texts": [
    "Table 1: ..."
  ],
  "caption_to_asset_link": [
    {
      "caption_type": "figure",
      "caption_text": "Figure 1: ...",
      "asset_id": "figure_1"
    }
  ],
  "display_equation_presence": true,
  "footnote_presence": false
}
```

## First Evaluation Targets Enabled By This Spec
With this gold spec, the project can already compare systems on:
- title recovery,
- abstract recovery,
- section heading recovery,
- paragraph order correctness,
- figure/table caption recovery,
- caption-to-asset grounding,
- equation preservation,
- footnote awareness.

This is enough for a first reconstruction baseline and is well aligned with the current thesis framing.

## Non-Goals Of This V1 Gold Spec
This spec does not try to solve:
- visual fidelity evaluation,
- token-perfect OCR benchmarking,
- full layout coordinate evaluation,
- slide quality gold labeling.

Those are deliberately deferred so the baseline stays feasible.
