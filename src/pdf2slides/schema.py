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
    reading_order_index: int
    source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Page:
    page_number: int
    text: str
    width: float = 612.0
    height: float = 792.0
    blocks: list[Block] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_number": self.page_number,
            "width": self.width,
            "height": self.height,
            "block_ids": [block.block_id for block in self.blocks],
            "text": self.text,
            "blocks": [block.to_dict() for block in self.blocks],
        }


@dataclass
class Section:
    section_id: str
    heading: str
    page_number: int
    content_blocks: list[Block] = field(default_factory=list)
    subsections: list["Subsection"] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        page_end = self.page_number
        if self.content_blocks:
            page_end = max(page_end, self.content_blocks[-1].page_number)
        if self.subsections:
            page_end = max(page_end, max(subsection.page_end for subsection in self.subsections))
        return {
            "section_id": self.section_id,
            "heading": self.heading,
            "page_number": self.page_number,
            "page_start": self.page_number,
            "page_end": page_end,
            "content_block_ids": [block.block_id for block in self.content_blocks],
            "content_blocks": [block.to_dict() for block in self.content_blocks],
            "subsections": [subsection.to_dict() for subsection in self.subsections],
        }


@dataclass
class StructuredDocument:
    source_pdf: str
    paper_id: str
    title: str
    pages: list[Page]
    blocks: list[Block]
    sections: list[Section]
    abstract: str
    assets: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_pdf": self.source_pdf,
            "paper_id": self.paper_id,
            "title": self.title,
            "abstract": self.abstract,
            "page_count": len(self.pages),
            "pages": [page.to_dict() for page in self.pages],
            "blocks": [block.to_dict() for block in self.blocks],
            "sections": [section.to_dict() for section in self.sections],
            "assets": self.assets,
            "metadata": {
                "ir_version": "structured-document-v0",
                **self.metadata,
            },
        }


@dataclass
class Subsection:
    subsection_id: str
    heading: str
    page_number: int
    content_blocks: list[Block] = field(default_factory=list)

    @property
    def page_end(self) -> int:
        if self.content_blocks:
            return self.content_blocks[-1].page_number
        return self.page_number

    def to_dict(self) -> dict[str, Any]:
        return {
            "subsection_id": self.subsection_id,
            "heading": self.heading,
            "page_number": self.page_number,
            "page_start": self.page_number,
            "page_end": self.page_end,
            "content_block_ids": [block.block_id for block in self.content_blocks],
            "content_blocks": [block.to_dict() for block in self.content_blocks],
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
    metadata_path: Path
