from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .schema import PipelineRun
from .stages import (
    detect_layout_blocks,
    extract_text_from_pdf,
    generate_slide_deck,
    parse_structure,
    render_beamer,
    run_pdftotext,
    run_placeholder_ocr,
    split_into_pages,
    write_json,
)


def run_pipeline(
    input_pdf: Path,
    output_root: Path,
    cli_args: list[str] | None = None,
    pdftotext_mode: str = "default",
) -> PipelineRun:
    input_pdf = input_pdf.expanduser().resolve()
    run_dir = output_root.expanduser().resolve() / input_pdf.stem
    run_dir.mkdir(parents=True, exist_ok=True)

    raw_text_path = run_dir / "01_raw_text.txt"
    pages_path = run_dir / "02_pages.json"
    blocks_path = run_dir / "03_blocks.json"
    structured_doc_path = run_dir / "04_structured_document.json"
    slide_deck_path = run_dir / "05_slide_deck.json"
    latex_path = run_dir / "06_slides.tex"
    metadata_path = run_dir / "RUN_METADATA.json"
    summary_path = run_dir / "RUN_SUMMARY.md"

    if pdftotext_mode == "hybrid":
        raw_text = extract_text_from_pdf(input_pdf, raw_text_path, pdftotext_mode="default")
        column_pages = split_into_pages(run_pdftotext(input_pdf, pdftotext_mode="columns"))
    else:
        raw_text = extract_text_from_pdf(input_pdf, raw_text_path, pdftotext_mode=pdftotext_mode)
        column_pages = None
    pages = split_into_pages(raw_text)
    write_json(pages_path, [page.to_dict() for page in pages])

    pages = detect_layout_blocks(pages, column_pages=column_pages, hybrid_body_order=pdftotext_mode == "hybrid")
    pages = run_placeholder_ocr(pages)
    write_json(blocks_path, [page.to_dict() for page in pages])

    structured_document = parse_structure(input_pdf, pages)
    write_json(structured_doc_path, structured_document.to_dict())

    slide_deck = generate_slide_deck(structured_document, run_dir)
    write_json(slide_deck_path, slide_deck.to_dict())

    metadata = build_run_metadata(input_pdf, output_root, run_dir, raw_text, cli_args, pdftotext_mode)
    write_json(metadata_path, metadata)
    render_beamer(slide_deck, latex_path)
    summary_path.write_text(build_summary(structured_document, slide_deck, metadata), encoding="utf-8")

    return PipelineRun(
        input_pdf=input_pdf,
        run_dir=run_dir,
        raw_text_path=raw_text_path,
        pages_path=pages_path,
        blocks_path=blocks_path,
        structured_doc_path=structured_doc_path,
        slide_deck_path=slide_deck_path,
        latex_path=latex_path,
        metadata_path=metadata_path,
    )


def build_summary(structured_document, slide_deck, metadata: dict[str, object]) -> str:
    lines = [
        "# Run Summary",
        "",
        f"- Source PDF: `{structured_document.source_pdf}`",
        f"- Pages parsed: `{len(structured_document.pages)}`",
        f"- Sections inferred: `{len(structured_document.sections)}`",
        f"- Slides generated: `{len(slide_deck.slides)}`",
        f"- Run timestamp (UTC): `{metadata['run_timestamp_utc']}`",
        f"- Git commit: `{metadata['git_commit']}`",
        f"- Metadata file: `{metadata['metadata_file']}`",
        "",
        "## Notes",
        "- This is a placeholder end-to-end pipeline.",
        "- Layout detection, OCR, structure parsing, and slide generation are heuristic modules.",
        "- The current goal is to validate interfaces and intermediate outputs, not model accuracy.",
    ]
    return "\n".join(lines) + "\n"


def build_run_metadata(
    input_pdf: Path,
    output_root: Path,
    run_dir: Path,
    raw_text: str,
    cli_args: list[str] | None,
    pdftotext_mode: str,
) -> dict[str, object]:
    return {
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "input_pdf": str(input_pdf),
        "output_root": str(output_root.expanduser().resolve()),
        "run_dir": str(run_dir),
        "cwd": os.getcwd(),
        "cli_args": cli_args or [],
        "git_commit": get_git_commit(),
        "raw_text_char_count": len(raw_text),
        "pdftotext_mode": pdftotext_mode,
        "stages": [
            "extract_text_from_pdf",
            "split_into_pages",
            "detect_layout_blocks",
            "run_placeholder_ocr",
            "parse_structure",
            "generate_slide_deck",
            "render_beamer",
        ],
        "metadata_file": str(run_dir / "RUN_METADATA.json"),
    }


def get_git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip()
