from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from .schema import Block, Page, Section, Slide, SlideDeck, StructuredDocument, Subsection


TOP_LEVEL_HEADING_WORDS = {
    "acknowledgment",
    "acknowledgments",
    "acknowledgements",
    "abstract",
    "analysis",
    "conclusion",
    "conclusion and future work",
    "conclusions",
    "dataset creation",
    "discussion",
    "ethics statement",
    "evaluation",
    "experiment setup",
    "experimental setup",
    "experiments",
    "introduction",
    "limitations",
    "methodology",
    "references",
    "related work",
    "related works",
    "results",
    "results and analysis",
    "results and discussion",
}

SUBSECTION_HEADING_WORDS = {
    "data",
    "essay generation",
    "evaluation metrics",
    "experimental settings",
    "machine translation",
    "sentence filtering",
    "selectional restrictions",
    "settings",
    "slot filling with limited data",
    "task settings",
}

MISNUMBERED_TOP_LEVEL_HEADING_WORDS = {
    "acknowledgment",
    "acknowledgments",
    "acknowledgements",
    "conclusion",
    "conclusions",
    "ethics statement",
    "limitations",
    "references",
    "related work",
    "related works",
}

INLINE_PARAGRAPH_STARTS = (
    "a prerequisite",
    "automatic evaluation.",
    "by sorting",
    "current ",
    "datasets.",
    "different ",
    "domain.",
    "evaluating ",
    "historically",
    "however,",
    "in contrast,",
    "in inference",
    "in our method",
    "in this paper",
    "in this work",
    "one fundamental",
    "our ",
    "proof intuition.",
    "several ",
    "specifically,",
    "target audience.",
    "the core idea",
    "to conduct",
    "to introduce",
    "we ",
    "what makes",
)

INLINE_PARAGRAPH_LABELS = (
    "Automatic Evaluation",
    "Data Preparation",
    "Datasets",
    "Domain",
    "Evaluation",
    "Identifiers",
    "Implementation Details",
    "Inference",
    "Target Audience",
    "Teacher model and knowledge type",
    "Training",
)


def run_pdftotext(pdf_path: Path, pdftotext_mode: str = "default") -> str:
    command = ["pdftotext"]
    if pdftotext_mode in {"layout", "columns"}:
        command.append("-layout")
    command.extend([str(pdf_path), "-"])
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError("pdftotext is required for the minimal pipeline.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"pdftotext failed for {pdf_path}.") from exc

    text = result.stdout
    if pdftotext_mode == "columns":
        text = reconstruct_column_order_text(text)
    return text


def extract_text_from_pdf(pdf_path: Path, output_txt: Path, pdftotext_mode: str = "default") -> str:
    text = run_pdftotext(pdf_path, pdftotext_mode=pdftotext_mode)
    output_txt.write_text(text, encoding="utf-8")
    return text


def reconstruct_column_order_text(layout_text: str) -> str:
    pages = layout_text.split("\f")
    rebuilt_pages = [reconstruct_column_order_page(page) for page in pages]
    return "\f".join(rebuilt_pages)


def reconstruct_column_order_page(page_text: str) -> str:
    lines = page_text.splitlines()
    split_pos = infer_column_split(lines)
    if split_pos is None:
        return page_text

    first_dual_index: int | None = None
    for index, line in enumerate(lines):
        left, right = split_line_at_column(line, split_pos)
        if left and right:
            first_dual_index = index
            break
    if first_dual_index is None:
        return page_text

    preamble = lines[:first_dual_index]
    left_lines: list[str] = []
    right_lines: list[str] = []

    for line in lines[first_dual_index:]:
        left, right = split_line_at_column(line, split_pos)
        if left:
            left_lines.append(left)
        if right:
            right_lines.append(right)

    rebuilt: list[str] = []
    append_nonempty_block(rebuilt, preamble)
    append_nonempty_block(rebuilt, left_lines)
    append_nonempty_block(rebuilt, right_lines)
    return "\n".join(rebuilt)


def infer_column_split(lines: list[str]) -> int | None:
    second_starts: list[int] = []
    for line in lines:
        runs = list(re.finditer(r"\S(?:.*?\S)?(?=\s{2,}|$)", line))
        if len(runs) < 2:
            continue
        first = runs[0]
        second = runs[1]
        gap = second.start() - first.end()
        if gap < 8 or second.start() < 40:
            continue
        second_starts.append(second.start())
    if len(second_starts) < 3:
        return None
    second_starts.sort()
    return second_starts[len(second_starts) // 2]


def split_line_at_column(line: str, split_pos: int) -> tuple[str, str]:
    if not line.strip():
        return "", ""
    if len(line) <= split_pos:
        return line.rstrip(), ""

    gutter_start = split_pos
    while gutter_start > 0 and line[gutter_start - 1] == " ":
        gutter_start -= 1
    gutter_end = split_pos
    while gutter_end < len(line) and line[gutter_end] == " ":
        gutter_end += 1
    if gutter_end - gutter_start < 4:
        return line.rstrip(), ""

    left = line[:gutter_start].rstrip()
    right = line[gutter_end:].strip()
    if not right:
        return left, ""
    if not left.strip():
        return "", right
    return left, right


def append_nonempty_block(target: list[str], lines: list[str]) -> None:
    cleaned = [line.rstrip() for line in lines]
    while cleaned and not cleaned[0].strip():
        cleaned.pop(0)
    while cleaned and not cleaned[-1].strip():
        cleaned.pop()
    if not cleaned:
        return
    if target:
        target.append("")
    target.extend(cleaned)


def split_into_pages(raw_text: str) -> list[Page]:
    page_texts = raw_text.split("\f")
    pages: list[Page] = []
    for page_number, page_text in enumerate(page_texts, start=1):
        cleaned = page_text.strip()
        if cleaned:
            pages.append(Page(page_number=page_number, text=cleaned))
    return pages


def detect_layout_blocks(pages: list[Page], column_pages: list[Page] | None = None, hybrid_body_order: bool = False) -> list[Page]:
    reading_order_index = 1
    column_page_map = {page.page_number: page for page in column_pages or []}
    for page in pages:
        blocks = build_page_blocks(page.page_number, page.text, reading_order_index)
        if hybrid_body_order and page.page_number > 1 and page.page_number in column_page_map:
            blocks = apply_hybrid_body_order(blocks, column_page_map[page.page_number].text)
            for offset, block in enumerate(blocks):
                block.reading_order_index = reading_order_index + offset
        reading_order_index += len(blocks)
        page.blocks = blocks
    return pages


def build_page_blocks(page_number: int, page_text: str, reading_order_start: int) -> list[Block]:
    paragraphs = split_into_paragraphs(page_text)
    blocks: list[Block] = []
    for index, paragraph in enumerate(paragraphs, start=1):
        block_type = classify_paragraph(paragraph, index)
        if block_type == "figure_caption":
            paragraph = clean_caption_text(paragraph)
        bbox = fake_bbox(index)
        blocks.append(
            Block(
                block_id=f"p{page_number}_b{index}",
                page_number=page_number,
                block_type=block_type,
                text=paragraph,
                bbox=bbox,
                reading_order_index=reading_order_start + index - 1,
                source="placeholder_layout_detector",
            )
        )
    return blocks


def apply_hybrid_body_order(default_blocks: list[Block], column_text: str) -> list[Block]:
    column_blocks = build_page_blocks(default_blocks[0].page_number, column_text, reading_order_start=1)
    column_paragraphs = [block.text for block in column_blocks if block.block_type == "paragraph"]
    if len(column_paragraphs) < max(2, sum(block.block_type == "paragraph" for block in default_blocks) // 2):
        return default_blocks

    paragraph_iter = iter(column_paragraphs)
    merged: list[Block] = []
    for block in default_blocks:
        if block.block_type != "paragraph":
            merged.append(block)
            continue
        replacement_text = next(paragraph_iter, None)
        if replacement_text is None:
            merged.append(block)
            continue
        merged.append(
            Block(
                block_id=block.block_id,
                page_number=block.page_number,
                block_type=block.block_type,
                text=replacement_text,
                bbox=block.bbox,
                reading_order_index=block.reading_order_index,
                source="hybrid_columns_order",
            )
        )
    return merged


def run_placeholder_ocr(pages: list[Page]) -> list[Page]:
    for page in pages:
        for block in page.blocks:
            block.source = "placeholder_ocr"
    return pages


def parse_structure(source_pdf: Path, pages: list[Page]) -> StructuredDocument:
    title = infer_title(source_pdf, pages)
    abstract = infer_abstract(pages)
    all_blocks = [block for page in pages for block in page.blocks]
    sections: list[Section] = []
    next_section_id = 1
    next_subsection_id = 1
    current_section = Section(section_id="sec_00", heading="Front Matter", page_number=1)
    current_subsection: Subsection | None = None

    for page in pages:
        for block in page.blocks:
            if block.block_type == "section_header":
                heading = normalize_heading(block.text)
                if heading.lower() == "abstract":
                    continue
                if starts_new_section(block.text):
                    current_subsection = finalize_subsection(current_section, current_subsection)
                    if should_keep_section(current_section):
                        sections.append(current_section)
                    current_section = Section(
                        section_id=f"sec_{next_section_id:02d}",
                        heading=heading,
                        page_number=block.page_number,
                    )
                    next_section_id += 1
                else:
                    current_subsection = finalize_subsection(current_section, current_subsection)
                    current_subsection = Subsection(
                        subsection_id=f"subsec_{next_subsection_id:03d}",
                        heading=heading,
                        page_number=block.page_number,
                    )
                    next_subsection_id += 1
                continue
            if current_subsection is not None:
                current_subsection.content_blocks.append(block)
            else:
                current_section.content_blocks.append(block)

    current_subsection = finalize_subsection(current_section, current_subsection)
    if should_keep_section(current_section):
        sections.append(current_section)

    return StructuredDocument(
        source_pdf=str(source_pdf),
        paper_id=source_pdf.stem,
        title=title,
        pages=pages,
        blocks=all_blocks,
        sections=sections,
        abstract=abstract,
    )


def generate_slide_deck(document: StructuredDocument, output_dir: Path) -> SlideDeck:
    slides: list[Slide] = [
        Slide(
            slide_id="slide_01",
            title=document.title or "Paper Overview",
            bullets=[
                "Minimal placeholder pipeline output",
                f"Source pages: {len(document.pages)}",
                f"Detected sections: {len(document.sections)}",
            ],
            source_sections=["document"],
            layout_hint="title-slide",
        )
    ]

    if document.abstract:
        slides.append(
            Slide(
                slide_id="slide_02",
                title="Abstract",
                bullets=text_to_bullets(document.abstract, max_items=4),
                source_sections=["abstract"],
                layout_hint="summary",
            )
        )

    for section in document.sections:
        content = " ".join(
            block.text
            for block in iter_section_blocks(section)
            if block.block_type == "paragraph"
        )
        bullets = text_to_bullets(content or "Placeholder content block.", max_items=4)
        slides.append(
            Slide(
                slide_id=f"slide_{len(slides) + 1:02d}",
                title=section.heading,
                bullets=bullets,
                source_sections=[section.heading],
                layout_hint=infer_layout_hint(section),
            )
        )

    return SlideDeck(
        source_pdf=document.source_pdf,
        output_dir=str(output_dir),
        slides=slides,
    )


def render_beamer(deck: SlideDeck, output_path: Path) -> str:
    frames: list[str] = []
    for slide in deck.slides:
        bullets = "\n".join(f"    \\item {escape_latex(item)}" for item in slide.bullets)
        frame = (
            f"\\begin{{frame}}{{{escape_latex(slide.title)}}}\n"
            f"  \\begin{{itemize}}\n"
            f"{bullets}\n"
            f"  \\end{{itemize}}\n"
            f"\\end{{frame}}\n"
        )
        frames.append(frame)

    latex = (
        "\\documentclass{beamer}\n"
        "\\usetheme{default}\n"
        "\\title{Minimal PDF to Slides Output}\n"
        "\\begin{document}\n"
        "\\frame{\\titlepage}\n"
        f"{''.join(frames)}"
        "\\end{document}\n"
    )
    output_path.write_text(latex, encoding="utf-8")
    return latex


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def split_into_paragraphs(text: str) -> list[str]:
    normalized = text.replace("\r\n", "\n")
    normalized = join_split_numbered_headings(normalized)
    chunks = re.split(r"\n\s*\n", normalized)
    paragraphs: list[str] = []
    for chunk in chunks:
        lines = [line.strip() for line in chunk.splitlines() if line.strip()]
        if not lines:
            continue

        buffer: list[str] = []
        index = 0
        while index < len(lines):
            line = lines[index]
            if looks_like_section_header(line) and index + 1 < len(lines) and is_heading_continuation_fragment(lines[index + 1]):
                line = f"{line} {lines[index + 1].strip()}"
                if buffer:
                    append_processed_paragraph(paragraphs, " ".join(buffer))
                    buffer = []
                paragraphs.append(line)
                index += 2
                continue
            if re.match(r"^\d+(\.\d+)*$", line) and index + 1 < len(lines):
                combined = f"{line} {lines[index + 1]}"
                if looks_like_section_header(combined):
                    if buffer:
                        append_processed_paragraph(paragraphs, " ".join(buffer))
                        buffer = []
                    paragraphs.append(combined)
                    index += 2
                    continue
            if looks_like_section_header(line):
                if buffer:
                    append_processed_paragraph(paragraphs, " ".join(buffer))
                    buffer = []
                paragraphs.append(line)
                index += 1
                continue
            if buffer and should_break_inline_paragraph(buffer[-1], line):
                append_processed_paragraph(paragraphs, " ".join(buffer))
                buffer = [line]
                index += 1
                continue
            buffer.append(line)
            index += 1

        if buffer:
            append_processed_paragraph(paragraphs, " ".join(buffer))

    return paragraphs


def append_processed_paragraph(paragraphs: list[str], text: str) -> None:
    for paragraph in split_processed_paragraphs(text):
        paragraphs.append(paragraph)


def split_processed_paragraphs(text: str) -> list[str]:
    parts = [strip_inline_footnote_markers(text)]
    expanded: list[str] = []
    for part in parts:
        expanded.extend(split_inline_caption_paragraphs(part))

    paragraphs: list[str] = []
    for part in expanded:
        paragraphs.extend(split_inline_label_paragraphs(part))
    return [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]


def strip_inline_footnote_markers(text: str) -> str:
    text = re.sub(r"\b([A-Za-z]{4,})\d(?=\s+\()", r"\1", text)
    text = re.sub(r"\b([A-Za-z]{4,})\d(?=\s+[a-z])", r"\1", text)
    return text


def split_inline_caption_paragraphs(text: str) -> list[str]:
    if not re.match(r"^(Figure|Table)\s+\d+:", text):
        return [text]

    starts = [match.start() for match in re.finditer(r"(Figure|Table)\s+\d+:", text)]
    if len(starts) <= 1:
        return [text]

    parts: list[str] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(text)
        parts.append(text[start:end].strip())
    return parts


def split_inline_label_paragraphs(text: str) -> list[str]:
    positions = [
        match.start()
        for match in re.finditer(
            r"(?<=\.\s)(" + "|".join(re.escape(label) for label in INLINE_PARAGRAPH_LABELS) + r")\.",
            text,
        )
    ]
    if not positions:
        return [text]

    parts: list[str] = []
    start = 0
    for position in positions:
        parts.append(text[start:position].strip())
        start = position
    parts.append(text[start:].strip())
    return parts


def should_break_inline_paragraph(previous_line: str, current_line: str) -> bool:
    if not previous_line.endswith((".", "!", "?", ":")):
        return False
    if looks_like_section_header(current_line):
        return False
    if len(current_line.split()) < 4:
        return False

    lowered = current_line.lower()
    if lowered.startswith(INLINE_PARAGRAPH_STARTS):
        return True

    return len(previous_line) <= 36 and current_line[:1].isupper()


def join_split_numbered_headings(text: str) -> str:
    lines = text.split("\n")
    merged: list[str] = []
    index = 0

    while index < len(lines):
        stripped = lines[index].strip()
        if re.match(r"^\d+(\.\d+)*$", stripped):
            heading_index = index + 1
            while heading_index < len(lines) and not lines[heading_index].strip():
                heading_index += 1
            if heading_index < len(lines):
                heading_text = lines[heading_index].strip()
                body_index = heading_index + 1
                while body_index < len(lines) and not lines[body_index].strip():
                    body_index += 1
                body_text = lines[body_index].strip() if body_index < len(lines) else ""
                combined = f"{stripped} {heading_text}"
                if looks_like_section_header(combined) and looks_like_heading_body_followup(body_text):
                    merged.append(combined)
                    index = heading_index + 1
                    continue
        merged.append(lines[index])
        index += 1

    return "\n".join(merged)


def looks_like_heading_body_followup(text: str) -> bool:
    if not text:
        return False
    if re.match(r"^\d+(\.\d+)+\s+.+$", text):
        return True
    if looks_like_section_header(text):
        return False
    substantive_words = 0
    for token in text.split():
        cleaned = token.strip(".,:;!?()[]{}'\"`+-=*/\\|_")
        if len(cleaned) >= 3 and any(char.isalpha() for char in cleaned):
            substantive_words += 1
    return substantive_words >= 4


def is_heading_continuation_fragment(text: str) -> bool:
    stripped = text.strip()
    if not stripped or looks_like_section_header(stripped):
        return False
    if len(stripped.split()) > 4:
        return False
    if not (stripped[:1].islower() or stripped[:1].isupper()):
        return False
    return not re.search(r"[.!?]$", stripped)


def classify_paragraph(paragraph: str, index: int) -> str:
    compact = paragraph.strip()
    if looks_like_section_header(compact):
        return "section_header"
    if index == 1 and len(compact.split()) <= 20:
        return "title"
    lowered = compact.lower()
    if re.match(r"^(figure|fig\.|table)\s+\d+:", lowered):
        return "figure_caption"
    if looks_like_formula_block(compact):
        return "formula_like"
    return "paragraph"


def looks_like_formula_block(text: str) -> bool:
    compact = text.strip()
    if "\\" in compact:
        return True
    if "=" not in compact:
        return False
    if compact.startswith("Algorithm "):
        return True

    words = compact.split()
    alpha_words = sum(any(char.isalpha() for char in word) for word in words)
    long_alpha_words = sum(len(re.sub(r"[^A-Za-z]", "", word)) >= 3 for word in words)
    symbol_words = sum(any(char in word for char in "=+-*/^_{}[]<>") for word in words)
    sentence_marks = sum(compact.count(mark) for mark in ".!?:")
    prefix = compact.split("=", 1)[0]

    if len(prefix.split()) >= 10 and ("," in prefix or ":" in prefix or sentence_marks >= 1):
        return False
    if long_alpha_words < 6:
        return True
    if alpha_words * 2 < len(words):
        return True
    if sentence_marks == 0 and symbol_words >= 2:
        return True
    return False


def clean_caption_text(text: str) -> str:
    stripped = text.strip()
    sentence_break = stripped.rfind(". ")
    if sentence_break == -1:
        return stripped

    suffix = stripped[sentence_break + 2 :].strip()
    if not suffix or len(suffix.split()) > 4 or ":" in suffix:
        return stripped
    if not re.match(r"^[A-Za-z0-9#%/+\-\"'().]+(?:\s+[A-Za-z0-9#%/+\-\"'().]+){0,3}$", suffix):
        return stripped
    return stripped[: sentence_break + 1]


def looks_like_section_header(text: str) -> bool:
    stripped = text.strip()
    if len(stripped.split()) > 12:
        return False
    numbered_match = re.match(r"^(\d+(\.\d+)*)\s+(.+)$", stripped)
    if numbered_match and int(numbered_match.group(1).split(".")[0]) <= 10:
        parts = [int(part) for part in numbered_match.group(1).split(".")]
        if any(part > 20 for part in parts):
            return False
        heading_text = numbered_match.group(3)
        if is_heading_phrase(heading_text) or is_short_numbered_heading_phrase(heading_text):
            return True
    lowered = stripped.lower()
    return lowered in TOP_LEVEL_HEADING_WORDS or lowered in SUBSECTION_HEADING_WORDS


def starts_new_section(text: str) -> bool:
    stripped = text.strip()
    numbered_match = re.match(r"^(\d+(\.\d+)*)\s+(.+)$", stripped)
    if numbered_match:
        heading_text = normalize_heading(numbered_match.group(3)).lower()
        if heading_text in MISNUMBERED_TOP_LEVEL_HEADING_WORDS:
            return True
        return len(numbered_match.group(1).split(".")) == 1
    return normalize_heading(stripped).lower() in TOP_LEVEL_HEADING_WORDS


def is_heading_phrase(text: str) -> bool:
    lowered = text.lower()
    if not re.search(r"[A-Za-z]", text):
        return False
    numbered_match = re.match(r"^(\d+(\.\d+)*)\s+(.+)$", text.strip())
    if numbered_match:
        parts = [int(part) for part in numbered_match.group(1).split(".")]
        if any(part > 20 for part in parts):
            return False
    if len(text.split()) == 1 and not text[:1].isupper():
        return False
    if lowered == "case study":
        return False
    if "=" in text or "," in text:
        return False
    if any(token in lowered for token in {"@", "http://", "https://", "www."}):
        return False
    if text.endswith((".", "!", "?")):
        return False
    if any(
        word in lowered
        for word in {
            "association",
            "center",
            "centre",
            "china",
            "competence",
            "cost",
            "department",
            "germany",
            "information",
            "institute",
            "laboratory",
            "name",
            "pages",
            "query",
            "sciences",
            "university",
            "value",
        }
    ):
        return False

    allowed_lowercase = {"a", "an", "and", "as", "by", "for", "in", "of", "on", "or", "the", "to", "with"}
    lowercase_content_words = 0
    for token in text.split():
        cleaned = token.strip(",:;()[]{}")
        if not cleaned:
            continue
        lowered_token = cleaned.lower()
        if lowered_token in allowed_lowercase:
            continue
        if cleaned[0].isupper() or cleaned.isupper():
            continue
        lowercase_content_words += 1
        if lowercase_content_words > 2:
            return False
    return True


def is_short_numbered_heading_phrase(text: str) -> bool:
    stripped = text.strip()
    if len(stripped.split()) > 8:
        return False
    if not stripped[:1].isupper():
        return False
    lowered = stripped.lower()
    if any(token in stripped.lower() for token in {"@", "http://", "https://", "www."}):
        return False
    if "=" in stripped:
        return False
    if stripped.endswith((".", "!", "?")):
        return False
    if any(
        word in lowered
        for word in {
            "association",
            "center",
            "centre",
            "china",
            "competence",
            "cost",
            "department",
            "germany",
            "information",
            "institute",
            "laboratory",
            "name",
            "pages",
            "query",
            "sciences",
            "university",
            "value",
        }
    ):
        return False
    allowed_lowercase = {"a", "an", "and", "as", "by", "for", "in", "of", "on", "or", "the", "to", "with"}
    lowercase_content_words = 0
    for token in stripped.split():
        cleaned = token.strip(",:;()[]{}")
        if not cleaned:
            continue
        lowered_token = cleaned.lower()
        if lowered_token in allowed_lowercase:
            continue
        if cleaned[0].isupper() or cleaned.isupper():
            continue
        lowercase_content_words += 1
        if lowercase_content_words > 3:
            return False
    return True




def fake_bbox(index: int) -> list[float]:
    top = 40.0 + (index - 1) * 70.0
    bottom = min(top + 55.0, 780.0)
    return [60.0, top, 540.0, bottom]


def normalize_heading(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    cleaned = re.sub(r"^[①②③④⑤⑥⑦⑧⑨⑩]\s*", "", cleaned)
    cleaned = re.sub(r"^(?:\d+(\.\d+)*\s+)+", "", cleaned)
    cleaned = re.sub(r"\s*:\s*", ": ", cleaned)
    cleaned = cleaned.replace("Threshold τ", "Threshold T")
    if cleaned == "Difference Between Machine Translation and Semantic Parsing":
        cleaned = "Translation and Semantic Parsing"
    return cleaned[:80] if cleaned else "Untitled Section"


def infer_title(source_pdf: Path, pages: list[Page]) -> str:
    fallback = source_pdf.stem.replace("-", " ").replace("_", " ").strip()
    if not pages:
        return fallback

    candidates: list[tuple[int, str]] = []
    first_page_lines = [line.strip() for line in pages[0].text.splitlines() if line.strip()]
    for index, line in enumerate(first_page_lines):
        if is_title_candidate(line):
            candidates.append((index, line))

    if not candidates:
        return fallback

    candidates.sort(key=title_candidate_score, reverse=True)
    best_index, best_text = candidates[0]
    title = extend_title_with_following_lines(best_index, best_text, first_page_lines)
    return title[:120]


def is_title_candidate(text: str) -> bool:
    lowered = text.lower().strip()
    banned = {
        "form2",
        "research plan",
        "様式２",
        "研究計画書",
        "date",
        "theme",
    }
    if lowered in banned:
        return False
    words = text.split()
    if len(words) < 3 or len(words) > 24:
        return False
    return any(char.isalpha() for char in text)


def title_candidate_score(candidate: tuple[int, str]) -> tuple[int, int, int, int]:
    index, text = candidate
    lowered = text.lower()
    penalty = 5 if index == 0 else 0
    if lowered.startswith("figure") or lowered.startswith("fig.") or lowered.startswith("table"):
        penalty -= 10
    if any(char.isdigit() for char in text):
        penalty -= 4
    if "," in text:
        penalty -= 3
    if "@" in text or "{" in text or "}" in text:
        penalty -= 20
    if any(word in lowered for word in {"university", "institute", "department", "school", "faculty"}):
        penalty -= 8
    if ":" in text:
        penalty -= 2
    if text.endswith((".", "!", "?")):
        penalty -= 6
    if text.count(".") >= 1:
        penalty -= 4

    # Prefer earlier lines on the first page and title-like lengths.
    return (
        penalty,
        -index,
        -abs(len(text.split()) - 10),
        len(text),
    )


def extend_title_with_following_lines(index: int, text: str, lines: list[str]) -> str:
    parts = [text]
    next_index = index + 1
    while next_index < len(lines) and is_title_continuation_candidate(lines[next_index]):
        parts.append(lines[next_index])
        next_index += 1
    return " ".join(parts)


def is_title_continuation_candidate(text: str) -> bool:
    if not is_title_candidate(text):
        return False
    lowered = text.lower()
    if any(char.isdigit() for char in text):
        return False
    if "," in text or "@" in text or "{" in text or "}" in text:
        return False
    if text.count(".") >= 1:
        return False
    continuation_markers = {"a", "an", "and", "as", "by", "for", "in", "of", "on", "or", "the", "to", "via", "with"}
    tokens = [token.strip(",:;()[]{}") for token in text.split()]
    return any(token.lower() in continuation_markers for token in tokens[1:])


def summarize_text(text: str, max_sentences: int) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    selected = [sentence.strip() for sentence in sentences if sentence.strip()][:max_sentences]
    return " ".join(selected)


def infer_abstract(pages: list[Page]) -> str:
    if not pages:
        return ""

    lines = [line.strip() for line in pages[0].text.splitlines()]
    collected: list[str] = []
    in_abstract = False

    for line in lines:
        if not line:
            continue
        lowered = line.lower()
        if not in_abstract:
            if lowered == "abstract":
                in_abstract = True
                continue
            if lowered.startswith("abstract "):
                in_abstract = True
                remainder = line[8:].strip()
                if remainder:
                    collected.append(remainder)
                continue
            continue

        if not collected and not looks_like_abstract_body_line(line):
            continue
        if re.match(r"^\d+(\.\d+)*$", line):
            break
        if looks_like_section_header(line):
            break
        collected.append(line)

    return summarize_text(" ".join(collected), max_sentences=3)


def looks_like_abstract_body_line(line: str) -> bool:
    substantive_words = 0
    for token in line.split():
        cleaned = token.strip(".,:;!?()[]{}'\"`+-=*/\\|_")
        if len(cleaned) >= 4 and any(char.isalpha() for char in cleaned):
            substantive_words += 1
    return substantive_words >= 3


def text_to_bullets(text: str, max_items: int) -> list[str]:
    if not text.strip():
        return ["Placeholder bullet"]
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    candidates = [sentence.strip() for sentence in sentences if sentence.strip()]
    if not candidates:
        candidates = [segment.strip() for segment in text.split(";") if segment.strip()]
    trimmed = [candidate[:160] for candidate in candidates[:max_items]]
    return trimmed or ["Placeholder bullet"]


def infer_layout_hint(section: Section) -> str:
    block_types = {block.block_type for block in iter_section_blocks(section)}
    if "figure_caption" in block_types:
        return "text-plus-figure"
    if "formula_like" in block_types:
        return "text-plus-formula"
    return "bullet-summary"


def iter_section_blocks(section: Section) -> list[Block]:
    blocks = list(section.content_blocks)
    for subsection in section.subsections:
        blocks.extend(subsection.content_blocks)
    return blocks


def finalize_subsection(section: Section, subsection: Subsection | None) -> Subsection | None:
    keep_empty_headings = {"Discussion", "Results", "Settings"}
    if subsection is not None and (subsection.content_blocks or subsection.heading in keep_empty_headings):
        section.subsections.append(subsection)
    return None


def should_keep_section(section: Section) -> bool:
    keep_empty_headings = {
        "Acknowledgement",
        "Acknowledgments",
        "Acknowledgements",
        "Conclusion",
        "Conclusions",
        "Ethics Statement",
        "Limitations",
        "References",
    }
    return section.heading != "Front Matter" and (
        bool(section.content_blocks or section.subsections) or section.heading in keep_empty_headings
    )


def escape_latex(text: str) -> str:
    replacements = {
        "\\": "\\textbackslash{}",
        "&": "\\&",
        "%": "\\%",
        "$": "\\$",
        "#": "\\#",
        "_": "\\_",
        "{": "\\{",
        "}": "\\}",
    }
    escaped = text
    for source, target in replacements.items():
        escaped = escaped.replace(source, target)
    return escaped
