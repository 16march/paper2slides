# Findings ACL 2024 Eval Set v1

## Purpose
This file defines the first small reconstruction-oriented evaluation set for `paper2slides`.

The goal of this set is not broad benchmark coverage. The goal is to provide a stable, high-quality, format-consistent starting point for:
- reconstruction baseline definition,
- reading-order evaluation,
- structure parsing comparison,
- OCR and caption-grounding analysis.

## Scope
This set intentionally uses papers from a single source:
- `Findings of the Association for Computational Linguistics: ACL 2024`

Reason:
- the venue format is relatively consistent,
- the papers are high-quality and publicly accessible,
- the set matches the current constrained-document thesis framing better than a mixed-format collection.

## Public Repo Policy
To keep the public repository lightweight, the PDF files are **not** checked into this repository.

This repository stores only:
- the paper list,
- source URLs,
- split assignments,
- evaluation intent.

PDFs should be downloaded locally in a private workspace when running experiments.

Recommended private local layout:

```text
data/eval/findings-acl-2024-v1/
```

## Split Design
The set is divided into:
- `dev`: for sanity checks, debugging, and fast iteration
- `frozen`: for comparison after a method is fixed

Initial target size:
- `3` dev papers
- `5` frozen papers

## Paper List

| Split | Anthology ID | Title | Source URL | Main Use |
| --- | --- | --- | --- | --- |
| dev | `2024.findings-acl.379` | Speech-based Slot Filling using Large Language Models | https://aclanthology.org/2024.findings-acl.379/ | sanity check, standard two-column layout |
| dev | `2024.findings-acl.712` | BATS: BenchmArking Text Simplicity | https://aclanthology.org/2024.findings-acl.712/ | table-heavy paper, caption handling |
| dev | `2024.findings-acl.783` | Evaluating Structural Generalization in Neural Machine Translation | https://aclanthology.org/2024.findings-acl.783/ | section structure, paragraph order |
| frozen | `2024.findings-acl.662` | Distillation Enhanced Generative Retrieval | https://aclanthology.org/2024.findings-acl.662/ | method + experiment structure |
| frozen | `2024.findings-acl.244` | On Efficiently Representing Regular Languages as RNNs | https://aclanthology.org/2024.findings-acl.244/ | equation presence, dense technical prose |
| frozen | `2024.findings-acl.536` | Budget-Constrained Tool Learning with Planning | https://aclanthology.org/2024.findings-acl.536/ | mixed figures, tables, method blocks |
| frozen | `2024.findings-acl.731` | Decomposing Argumentative Essay Generation via Dialectical Planning of Complex Reasoning | https://aclanthology.org/2024.findings-acl.731/ | longer section structure, complex content grouping |
| frozen | `2024.findings-acl.164` | Selective Prefix Tuning for Pre-trained Language Models | https://aclanthology.org/2024.findings-acl.164/ | standard NLP method paper for stable comparison |

## What This Set Should Support
This set is intended to support at least the following first-pass checks:
- title and abstract recovery,
- ordered section heading recovery,
- paragraph ordering in two-column pages,
- figure/table caption extraction,
- figure/table to caption linking,
- display equation presence recovery,
- simple reconstruction-oriented output review.

## What This Set Does Not Yet Guarantee
This v1 set does not guarantee balanced coverage of:
- heavy footnote usage,
- very formula-dense papers,
- unusual layouts outside standard ACL-style formatting,
- appendices and supplementary material.

Those can be added in a later eval-set revision if they become important for the thesis claims.

## Near-Term Next Step
After the PDFs are downloaded privately, the next step is to create first-pass gold annotations for this set.

The initial gold field definition is documented separately in:

```text
eval-sets/findings-acl-2024-v1-gold-fields.md
```

## Sources
- ACL Anthology volume page: https://aclanthology.org/2024.findings-acl.0/
- Individual paper pages:
  - https://aclanthology.org/2024.findings-acl.379/
  - https://aclanthology.org/2024.findings-acl.712/
  - https://aclanthology.org/2024.findings-acl.783/
  - https://aclanthology.org/2024.findings-acl.662/
  - https://aclanthology.org/2024.findings-acl.244/
  - https://aclanthology.org/2024.findings-acl.536/
  - https://aclanthology.org/2024.findings-acl.731/
  - https://aclanthology.org/2024.findings-acl.164/
