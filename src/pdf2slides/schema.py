from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Block:
    block_id: str
    page_number: int
    block_type: str
    text: str
    bbox: list[float]
    source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Page:
    page_number: int
    text: str
    blocks: list[Block] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_number": self.page_number,
            "text": self.text,
            "blocks": [block.to_dict() for block in self.blocks],
        }


@dataclass
class Section:
    heading: str
    page_number: int
    content_blocks: list[Block] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "heading": self.heading,
            "page_number": self.page_number,
            "content_blocks": [block.to_dict() for block in self.content_blocks],
        }


@dataclass
class StructuredDocument:
    source_pdf: str
    title: str
    pages: list[Page]
    sections: list[Section]
    abstract: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_pdf": self.source_pdf,
            "title": self.title,
            "pages": [page.to_dict() for page in self.pages],
            "sections": [section.to_dict() for section in self.sections],
            "abstract": self.abstract,
        }


@dataclass
class Slide:
    slide_id: str
    title: str
    bullets: list[str]
    source_sections: list[str]
    layout_hint: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SlideDeck:
    source_pdf: str
    output_dir: str
    slides: list[Slide]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_pdf": self.source_pdf,
            "output_dir": self.output_dir,
            "slides": [slide.to_dict() for slide in self.slides],
        }


@dataclass
class PipelineRun:
    input_pdf: Path
    run_dir: Path
    raw_text_path: Path
    pages_path: Path
    blocks_path: Path
    structured_doc_path: Path
    slide_deck_path: Path
    latex_path: Path
