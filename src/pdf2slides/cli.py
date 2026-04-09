from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Minimal PDF to structured slides pipeline.")
    parser.add_argument("input_pdf", type=Path, help="Path to the source PDF.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("outputs"),
        help="Root directory for pipeline outputs.",
    )
    parser.add_argument(
        "--pdftotext-mode",
        choices=["default", "layout", "columns", "hybrid"],
        default="default",
        help="pdftotext extraction mode.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run = run_pipeline(
        args.input_pdf,
        args.output_root,
        cli_args=sys.argv[1:],
        pdftotext_mode=args.pdftotext_mode,
    )
    print(f"Pipeline completed for {run.input_pdf}")
    print(f"Outputs written to {run.run_dir}")
    return 0
