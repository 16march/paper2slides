from __future__ import annotations

from pathlib import Path

from .schema import PipelineRun
from .stages import (
    detect_layout_blocks,
    extract_text_from_pdf,
    generate_slide_deck,
    parse_structure,
    render_beamer,
    run_placeholder_ocr,
    split_into_pages,
    write_json,
)


def run_pipeline(input_pdf: Path, output_root: Path) -> PipelineRun:
    input_pdf = input_pdf.expanduser().resolve()
    run_dir = output_root.expanduser().resolve() / input_pdf.stem
    run_dir.mkdir(parents=True, exist_ok=True)

    raw_text_path = run_dir / "01_raw_text.txt"
    pages_path = run_dir / "02_pages.json"
    blocks_path = run_dir / "03_blocks.json"
    structured_doc_path = run_dir / "04_structured_document.json"
    slide_deck_path = run_dir / "05_slide_deck.json"
    latex_path = run_dir / "06_slides.tex"
    summary_path = run_dir / "RUN_SUMMARY.md"

    raw_text = extract_text_from_pdf(input_pdf, raw_text_path)
    pages = split_into_pages(raw_text)
    write_json(pages_path, [page.to_dict() for page in pages])

    pages = detect_layout_blocks(pages)
    pages = run_placeholder_ocr(pages)
    write_json(blocks_path, [page.to_dict() for page in pages])

    structured_document = parse_structure(input_pdf, pages)
    write_json(structured_doc_path, structured_document.to_dict())

    slide_deck = generate_slide_deck(structured_document, run_dir)
    write_json(slide_deck_path, slide_deck.to_dict())

    render_beamer(slide_deck, latex_path)
    summary_path.write_text(build_summary(structured_document, slide_deck), encoding="utf-8")

    return PipelineRun(
        input_pdf=input_pdf,
        run_dir=run_dir,
        raw_text_path=raw_text_path,
        pages_path=pages_path,
        blocks_path=blocks_path,
        structured_doc_path=structured_doc_path,
        slide_deck_path=slide_deck_path,
        latex_path=latex_path,
    )


def build_summary(structured_document, slide_deck) -> str:
    lines = [
        "# Run Summary",
        "",
        f"- Source PDF: `{structured_document.source_pdf}`",
        f"- Pages parsed: `{len(structured_document.pages)}`",
        f"- Sections inferred: `{len(structured_document.sections)}`",
        f"- Slides generated: `{len(slide_deck.slides)}`",
        "",
        "## Notes",
        "- This is a placeholder end-to-end pipeline.",
        "- Layout detection, OCR, structure parsing, and slide generation are heuristic modules.",
        "- The current goal is to validate interfaces and intermediate outputs, not model accuracy.",
    ]
    return "\n".join(lines) + "\n"
