from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from .schema import Block, Page, Section, Slide, SlideDeck, StructuredDocument


def extract_text_from_pdf(pdf_path: Path, output_txt: Path) -> str:
    command = ["pdftotext", str(pdf_path), "-"]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError("pdftotext is required for the minimal pipeline.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"pdftotext failed for {pdf_path}.") from exc

    text = result.stdout
    output_txt.write_text(text, encoding="utf-8")
    return text


def split_into_pages(raw_text: str) -> list[Page]:
    page_texts = raw_text.split("\f")
    pages: list[Page] = []
    for page_number, page_text in enumerate(page_texts, start=1):
        cleaned = page_text.strip()
        if cleaned:
            pages.append(Page(page_number=page_number, text=cleaned))
    return pages


def detect_layout_blocks(pages: list[Page]) -> list[Page]:
    for page in pages:
        paragraphs = split_into_paragraphs(page.text)
        blocks: list[Block] = []
        for index, paragraph in enumerate(paragraphs, start=1):
            block_type = classify_paragraph(paragraph, index)
            bbox = fake_bbox(index)
            blocks.append(
                Block(
                    block_id=f"p{page.page_number}_b{index}",
                    page_number=page.page_number,
                    block_type=block_type,
                    text=paragraph,
                    bbox=bbox,
                    source="placeholder_layout_detector",
                )
            )
        page.blocks = blocks
    return pages


def run_placeholder_ocr(pages: list[Page]) -> list[Page]:
    for page in pages:
        for block in page.blocks:
            block.source = "placeholder_ocr"
    return pages


def parse_structure(source_pdf: Path, pages: list[Page]) -> StructuredDocument:
    title = infer_title(source_pdf, pages)
    abstract_parts: list[str] = []
    sections: list[Section] = []
    current_section = Section(heading="Introduction", page_number=1)

    for page in pages:
        for block in page.blocks:
            if block.block_type == "section_header":
                if current_section.content_blocks or current_section.heading != "Introduction":
                    sections.append(current_section)
                current_section = Section(heading=normalize_heading(block.text), page_number=block.page_number)
                continue
            if block.block_type == "paragraph" and len(" ".join(abstract_parts)) < 700:
                abstract_parts.append(block.text)
            current_section.content_blocks.append(block)

    if current_section.content_blocks or not sections:
        sections.append(current_section)

    abstract = summarize_text(" ".join(abstract_parts), max_sentences=3)
    return StructuredDocument(
        source_pdf=str(source_pdf),
        title=title,
        pages=pages,
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
        content = " ".join(block.text for block in section.content_blocks if block.block_type == "paragraph")
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
    chunks = re.split(r"\n\s*\n", normalized)
    paragraphs = [" ".join(line.strip() for line in chunk.splitlines() if line.strip()) for chunk in chunks]
    return [paragraph for paragraph in paragraphs if paragraph]


def classify_paragraph(paragraph: str, index: int) -> str:
    compact = paragraph.strip()
    if index == 1 and len(compact.split()) <= 20:
        return "title"
    if looks_like_section_header(compact):
        return "section_header"
    lowered = compact.lower()
    if lowered.startswith("figure") or lowered.startswith("fig.") or lowered.startswith("table"):
        return "figure_caption"
    if "\\" in compact or "=" in compact:
        return "formula_like"
    return "paragraph"


def looks_like_section_header(text: str) -> bool:
    stripped = text.strip()
    if len(stripped.split()) > 12:
        return False
    if re.match(r"^\(\d+\)\s+[A-Z]", stripped):
        return True
    if re.match(r"^(\d+(\.\d+)*)\s+[A-Z]", stripped):
        return True
    heading_words = {"abstract", "introduction", "method", "methods", "results", "discussion", "conclusion"}
    return stripped.lower() in heading_words


def fake_bbox(index: int) -> list[float]:
    top = 40.0 + (index - 1) * 70.0
    bottom = min(top + 55.0, 780.0)
    return [60.0, top, 540.0, bottom]


def normalize_heading(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned[:80] if cleaned else "Untitled Section"


def infer_title(source_pdf: Path, pages: list[Page]) -> str:
    fallback = source_pdf.stem.replace("-", " ").replace("_", " ").strip()
    if not pages:
        return fallback

    candidates: list[str] = []
    first_page_lines = [line.strip() for line in pages[0].text.splitlines() if line.strip()]
    for line in first_page_lines:
        if is_title_candidate(line):
            candidates.append(line)

    if not candidates:
        return fallback

    candidates.sort(key=lambda line: (":" in line, len(line.split()), len(line)), reverse=True)
    return candidates[0][:120]


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
    if len(words) < 4 or len(words) > 24:
        return False
    return any(char.isalpha() for char in text)


def summarize_text(text: str, max_sentences: int) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    selected = [sentence.strip() for sentence in sentences if sentence.strip()][:max_sentences]
    return " ".join(selected)


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
    block_types = {block.block_type for block in section.content_blocks}
    if "figure_caption" in block_types:
        return "text-plus-figure"
    if "formula_like" in block_types:
        return "text-plus-formula"
    return "bullet-summary"


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
