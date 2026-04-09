from __future__ import annotations

import argparse
import json
import re
import unicodedata
from bisect import bisect_left
from pathlib import Path


DEFAULT_PAPER_IDS = [
    "2024.findings-acl.379",
    "2024.findings-acl.712",
    "2024.findings-acl.783",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate reading-order proxies from StructuredDocument outputs.")
    parser.add_argument("system_output_root", type=Path, help="Output root containing per-paper run directories.")
    parser.add_argument(
        "--gold-root",
        type=Path,
        default=Path("eval-sets/findings-acl-2024-v1-annotations"),
        help="Directory containing gold annotation JSON files.",
    )
    parser.add_argument(
        "--paper-ids",
        nargs="+",
        default=DEFAULT_PAPER_IDS,
        help="Paper IDs to evaluate.",
    )
    return parser


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.casefold()


def strip_citation_spans(text: str) -> str:
    text = re.sub(r"\(([^()]*?(?:et al\.|\b(?:19|20)\d{2}\b)[^()]*)\)", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\[([^\[\]]*?(?:et al\.|\b(?:19|20)\d{2}\b)[^\[\]]*)\]", " ", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip()


def first_match_indices(gold_texts: list[str], predicted_blocks: list[dict[str, object]], contains: bool) -> list[int | None]:
    matches: list[int | None] = []
    normalized_predictions = [normalize_text(str(block["text"])) for block in predicted_blocks]
    citation_stripped_predictions = [normalize_text(strip_citation_spans(str(block["text"]))) for block in predicted_blocks]

    for gold_text in gold_texts:
        normalized_gold = normalize_text(gold_text)
        citation_stripped_gold = normalize_text(strip_citation_spans(gold_text))
        matched_index: int | None = None
        for block_index, normalized_prediction in enumerate(normalized_predictions):
            if contains:
                citation_stripped_prediction = citation_stripped_predictions[block_index]
                if normalized_gold in normalized_prediction:
                    matched_index = block_index
                    break
                if citation_stripped_gold and citation_stripped_gold in citation_stripped_prediction:
                    matched_index = block_index
                    break
            elif normalized_gold == normalized_prediction:
                matched_index = block_index
                break
        matches.append(matched_index)
    return matches


def longest_increasing_subsequence_length(values: list[int]) -> int:
    tails: list[int] = []
    for value in values:
        index = bisect_left(tails, value)
        if index == len(tails):
            tails.append(value)
        else:
            tails[index] = value
    return len(tails)


def match_ratio(matches: list[int | None]) -> tuple[int, int]:
    matched = sum(match is not None for match in matches)
    return matched, len(matches)


def order_ratio(matches: list[int | None], predicted_blocks: list[dict[str, object]]) -> tuple[int, int]:
    matched_positions = [
        int(predicted_blocks[match]["reading_order_index"])
        for match in matches
        if match is not None
    ]
    if not matched_positions:
        return 0, 0
    return longest_increasing_subsequence_length(matched_positions), len(matched_positions)


def section_fragmentation(system_doc: dict[str, object], key: str) -> tuple[int, int]:
    block_index_by_id = {
        block["block_id"]: int(block["reading_order_index"])
        for block in system_doc["blocks"]
    }
    unit_count = 0
    contiguous_count = 0

    for section in system_doc["sections"]:
        units = [section] if key == "sections" else section.get("subsections", [])
        for unit in units:
            block_ids = unit.get("content_block_ids", [])
            if not block_ids:
                continue
            indices = sorted(block_index_by_id[block_id] for block_id in block_ids if block_id in block_index_by_id)
            if not indices:
                continue
            spans = 1
            for previous, current in zip(indices, indices[1:]):
                if current != previous + 1:
                    spans += 1
            unit_count += 1
            if spans == 1:
                contiguous_count += 1
    return contiguous_count, unit_count


def format_ratio(hit: int, total: int) -> str:
    return f"{hit}/{total}" if total else "0/0"


def load_gold(gold_root: Path, paper_id: str) -> dict[str, object]:
    return json.loads((gold_root / f"{paper_id}.json").read_text(encoding="utf-8"))


def load_system_doc(system_output_root: Path, paper_id: str) -> dict[str, object]:
    return json.loads((system_output_root / paper_id / "04_structured_document.json").read_text(encoding="utf-8"))


def predicted_paragraph_blocks(system_doc: dict[str, object]) -> list[dict[str, object]]:
    return [block for block in system_doc["blocks"] if block["block_type"] == "paragraph"]


def predicted_caption_blocks(system_doc: dict[str, object], prefix: str) -> list[dict[str, object]]:
    lowered_prefix = prefix.casefold()
    return [
        block
        for block in system_doc["blocks"]
        if block["block_type"] == "figure_caption" and normalize_text(str(block["text"])).startswith(lowered_prefix)
    ]


def main() -> None:
    args = build_parser().parse_args()
    system_output_root = args.system_output_root.expanduser().resolve()
    gold_root = args.gold_root.expanduser().resolve()

    aggregate = {
        "paragraph_match_hit": 0,
        "paragraph_match_total": 0,
        "paragraph_order_hit": 0,
        "paragraph_order_total": 0,
        "figure_match_hit": 0,
        "figure_match_total": 0,
        "figure_order_hit": 0,
        "figure_order_total": 0,
        "table_match_hit": 0,
        "table_match_total": 0,
        "table_order_hit": 0,
        "table_order_total": 0,
        "section_contiguous_hit": 0,
        "section_contiguous_total": 0,
        "subsection_contiguous_hit": 0,
        "subsection_contiguous_total": 0,
    }

    print("# Reading-Order Eval Report\n")
    print(f"- System output root: `{system_output_root}`")
    print(f"- Gold root: `{gold_root}`")
    print("- Note: caption-to-asset grounding is not scored yet because current outputs do not populate `assets` links.")
    print()
    print(
        "| Paper | Paragraph match | Paragraph order | Figure captions | Figure order | Table captions | Table order | Section contiguous | Subsection contiguous |"
    )
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")

    for paper_id in args.paper_ids:
        gold = load_gold(gold_root, paper_id)
        system_doc = load_system_doc(system_output_root, paper_id)
        annotations = gold["annotations"]

        paragraph_gold = [item["anchor_text"] for item in annotations["paragraph_sequence"]]
        paragraph_predictions = predicted_paragraph_blocks(system_doc)
        paragraph_matches = first_match_indices(paragraph_gold, paragraph_predictions, contains=True)
        paragraph_match_hit, paragraph_match_total = match_ratio(paragraph_matches)
        paragraph_order_hit, paragraph_order_total = order_ratio(paragraph_matches, paragraph_predictions)

        figure_gold = annotations["figure_caption_texts"]
        figure_predictions = predicted_caption_blocks(system_doc, "figure")
        figure_matches = first_match_indices(figure_gold, figure_predictions, contains=False)
        figure_match_hit, figure_match_total = match_ratio(figure_matches)
        figure_order_hit, figure_order_total = order_ratio(figure_matches, figure_predictions)

        table_gold = annotations["table_caption_texts"]
        table_predictions = predicted_caption_blocks(system_doc, "table")
        table_matches = first_match_indices(table_gold, table_predictions, contains=False)
        table_match_hit, table_match_total = match_ratio(table_matches)
        table_order_hit, table_order_total = order_ratio(table_matches, table_predictions)

        section_contiguous_hit, section_contiguous_total = section_fragmentation(system_doc, "sections")
        subsection_contiguous_hit, subsection_contiguous_total = section_fragmentation(system_doc, "subsections")

        aggregate["paragraph_match_hit"] += paragraph_match_hit
        aggregate["paragraph_match_total"] += paragraph_match_total
        aggregate["paragraph_order_hit"] += paragraph_order_hit
        aggregate["paragraph_order_total"] += paragraph_order_total
        aggregate["figure_match_hit"] += figure_match_hit
        aggregate["figure_match_total"] += figure_match_total
        aggregate["figure_order_hit"] += figure_order_hit
        aggregate["figure_order_total"] += figure_order_total
        aggregate["table_match_hit"] += table_match_hit
        aggregate["table_match_total"] += table_match_total
        aggregate["table_order_hit"] += table_order_hit
        aggregate["table_order_total"] += table_order_total
        aggregate["section_contiguous_hit"] += section_contiguous_hit
        aggregate["section_contiguous_total"] += section_contiguous_total
        aggregate["subsection_contiguous_hit"] += subsection_contiguous_hit
        aggregate["subsection_contiguous_total"] += subsection_contiguous_total

        print(
            f"| `{paper_id}` | "
            f"{format_ratio(paragraph_match_hit, paragraph_match_total)} | "
            f"{format_ratio(paragraph_order_hit, paragraph_order_total)} | "
            f"{format_ratio(figure_match_hit, figure_match_total)} | "
            f"{format_ratio(figure_order_hit, figure_order_total)} | "
            f"{format_ratio(table_match_hit, table_match_total)} | "
            f"{format_ratio(table_order_hit, table_order_total)} | "
            f"{format_ratio(section_contiguous_hit, section_contiguous_total)} | "
            f"{format_ratio(subsection_contiguous_hit, subsection_contiguous_total)} |"
        )

    print()
    print("## Aggregate")
    print(f"- Paragraph match: `{format_ratio(aggregate['paragraph_match_hit'], aggregate['paragraph_match_total'])}`")
    print(f"- Paragraph order: `{format_ratio(aggregate['paragraph_order_hit'], aggregate['paragraph_order_total'])}`")
    print(f"- Figure caption match: `{format_ratio(aggregate['figure_match_hit'], aggregate['figure_match_total'])}`")
    print(f"- Figure caption order: `{format_ratio(aggregate['figure_order_hit'], aggregate['figure_order_total'])}`")
    print(f"- Table caption match: `{format_ratio(aggregate['table_match_hit'], aggregate['table_match_total'])}`")
    print(f"- Table caption order: `{format_ratio(aggregate['table_order_hit'], aggregate['table_order_total'])}`")
    print(f"- Section contiguous spans: `{format_ratio(aggregate['section_contiguous_hit'], aggregate['section_contiguous_total'])}`")
    print(
        f"- Subsection contiguous spans: `{format_ratio(aggregate['subsection_contiguous_hit'], aggregate['subsection_contiguous_total'])}`"
    )


if __name__ == "__main__":
    main()
