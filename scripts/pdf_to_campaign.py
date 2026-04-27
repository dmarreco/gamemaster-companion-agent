#!/usr/bin/env python3
"""
Converts a PDF sourcebook into structured markdown files split by chapter/section.

Detects chapter headings by font size (the largest fonts on a page are usually headings).
Each chapter becomes its own markdown file under the output directory.

Usage:
    python3 scripts/pdf_to_campaign.py path/to/sourcebook.pdf campaigns/dark-sun/source/

Options:
    --min-heading-size FLOAT   Minimum font size to treat as a heading (default: auto-detect)
    --max-heading-size FLOAT   Only treat fonts smaller than this as headings (default: 999)
    --inspect                  Print font size statistics without converting (use to calibrate)
    --single-file              Output everything to a single markdown file instead of splitting
    --campaign NAME            Campaign folder name to create (uses new_campaign.py template)

Example workflow:
    # 1. Inspect font sizes to calibrate heading detection
    python3 scripts/pdf_to_campaign.py dark-sun.pdf /tmp/out --inspect

    # 2. Convert with detected settings
    python3 scripts/pdf_to_campaign.py dark-sun.pdf campaigns/dark-sun/source/

    # 3. The files are gitignored — run this script to regenerate from the PDF

Note:
    Output files contain third-party copyrighted content. Keep them gitignored.
    Only use for personal campaigns with materials you legally own.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not found. Install with: python3 -m pip install PyMuPDF", file=sys.stderr)
    sys.exit(1)


def collect_font_stats(doc: fitz.Document) -> dict:
    """Collect font size frequency across the document (sample first 50 pages)."""
    size_counts: Counter = Counter()
    sample_pages = min(50, len(doc))
    for page_num in range(sample_pages):
        page = doc[page_num]
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    size = round(span["size"], 1)
                    size_counts[size] += len(span["text"].strip())
    return size_counts


def auto_detect_heading_sizes(size_counts: dict) -> tuple[float, float]:
    """
    Auto-detect heading font sizes.
    Body text is the most common size. Headings are larger than body text.
    Returns (body_size, min_heading_size).
    """
    if not size_counts:
        return 10.0, 14.0
    body_size = max(size_counts, key=size_counts.get)
    heading_sizes = [s for s in size_counts if s > body_size * 1.2]
    if not heading_sizes:
        return body_size, body_size * 1.3
    return body_size, min(heading_sizes)


def extract_blocks(doc: fitz.Document, min_heading: float, max_heading: float) -> list[dict]:
    """
    Extract all text blocks from the document, tagging each as heading or body.
    Returns a list of dicts: {type: 'heading'|'body', level: int, text: str, page: int}
    """
    blocks = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_dict = page.get_text("dict")
        for block in page_dict["blocks"]:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                line_spans = line["spans"]
                if not line_spans:
                    continue
                # Use the max font size in the line to classify it
                max_size = max(span["size"] for span in line_spans)
                line_text = "".join(span["text"] for span in line_spans).strip()
                if not line_text:
                    continue
                if min_heading <= max_size <= max_heading:
                    # Approximate heading level by relative font size
                    if max_size >= min_heading * 1.4:
                        level = 1
                    elif max_size >= min_heading * 1.15:
                        level = 2
                    else:
                        level = 3
                    blocks.append({"type": "heading", "level": level, "text": line_text, "page": page_num + 1})
                else:
                    blocks.append({"type": "body", "text": line_text, "page": page_num + 1})
    return blocks


def slugify(text: str) -> str:
    """Convert heading text to a safe filename."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text[:60] or "untitled"


def blocks_to_markdown(blocks: list[dict]) -> str:
    """Convert a list of blocks to a markdown string."""
    lines = []
    prev_type = None
    for block in blocks:
        if block["type"] == "heading":
            prefix = "#" * block["level"]
            lines.append(f"\n{prefix} {block['text']}\n")
        else:
            text = block["text"]
            if prev_type == "body" and lines and not lines[-1].endswith("\n\n"):
                lines[-1] = lines[-1].rstrip("\n") + " " + text
            else:
                lines.append(text)
        prev_type = block["type"]
    return "\n".join(lines)


def split_into_chapters(blocks: list[dict]) -> list[tuple[str, list[dict]]]:
    """
    Split blocks at every level-1 heading.
    Returns list of (chapter_title, blocks) tuples.
    The first group captures everything before the first heading.
    """
    chapters: list[tuple[str, list[dict]]] = []
    current_title = "front-matter"
    current_blocks: list[dict] = []

    for block in blocks:
        if block["type"] == "heading" and block["level"] == 1:
            if current_blocks:
                chapters.append((current_title, current_blocks))
            current_title = block["text"]
            current_blocks = [block]
        else:
            current_blocks.append(block)

    if current_blocks:
        chapters.append((current_title, current_blocks))

    return chapters


def convert(pdf_path: Path, out_dir: Path, min_heading: float, max_heading: float, single_file: bool) -> None:
    print(f"\nOpening {pdf_path.name} ({pdf_path.stat().st_size // (1024*1024)}MB)...")
    doc = fitz.open(str(pdf_path))
    print(f"  {len(doc)} pages")

    print(f"  Extracting text (heading threshold: ≥{min_heading:.1f}pt)...")
    blocks = extract_blocks(doc, min_heading, max_heading)

    headings = [b for b in blocks if b["type"] == "heading"]
    print(f"  Found {len(headings)} headings, {len(blocks) - len(headings)} body blocks")

    out_dir.mkdir(parents=True, exist_ok=True)

    if single_file:
        md = blocks_to_markdown(blocks)
        out_file = out_dir / f"{pdf_path.stem}.md"
        out_file.write_text(md, encoding="utf-8")
        print(f"\n✅ Written: {out_file} ({out_file.stat().st_size // 1024}KB)")
    else:
        chapters = split_into_chapters(blocks)
        print(f"\n  {len(chapters)} chapters detected:")
        written = []
        for i, (title, chapter_blocks) in enumerate(chapters, 1):
            md = blocks_to_markdown(chapter_blocks)
            slug = f"{i:02d}-{slugify(title)}"
            out_file = out_dir / f"{slug}.md"
            out_file.write_text(md, encoding="utf-8")
            size_kb = out_file.stat().st_size // 1024
            print(f"    {slug}.md ({size_kb}KB)")
            written.append(out_file)

        print(f"\n✅ {len(written)} files written to {out_dir}/")

    # Write an index file
    index_lines = [f"# {pdf_path.stem} — Source Index\n"]
    index_lines.append(f"Extracted from `{pdf_path.name}` ({len(doc)} pages)\n")
    if not single_file:
        for i, (title, _) in enumerate(chapters, 1):
            slug = f"{i:02d}-{slugify(title)}"
            index_lines.append(f"- [{title}](./{slug}.md)")
    (out_dir / "index.md").write_text("\n".join(index_lines))
    print(f"  Index written: {out_dir}/index.md")


def inspect(pdf_path: Path) -> None:
    """Print font size statistics to help calibrate heading detection."""
    print(f"\nInspecting {pdf_path.name} (sampling first 50 pages)...")
    doc = fitz.open(str(pdf_path))
    size_counts = collect_font_stats(doc)
    body_size, min_heading = auto_detect_heading_sizes(size_counts)

    print(f"\nFont size distribution (by character count):")
    for size, count in sorted(size_counts.items(), reverse=True)[:20]:
        bar = "█" * min(40, count // max(1, max(size_counts.values()) // 40))
        marker = " ← likely body text" if size == body_size else ""
        marker = " ← suggested heading threshold" if size == min_heading else marker
        print(f"  {size:6.1f}pt  {count:6d} chars  {bar}{marker}")

    print(f"\nAuto-detected:")
    print(f"  Body text size:       {body_size:.1f}pt")
    print(f"  Min heading size:     {min_heading:.1f}pt  (--min-heading-size {min_heading:.1f})")
    print(f"\nRun conversion with:")
    print(f"  python3 scripts/pdf_to_campaign.py {pdf_path} <output_dir> --min-heading-size {min_heading:.1f}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert a PDF sourcebook to split markdown files for campaign use."
    )
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("output", help="Output directory for markdown files")
    parser.add_argument("--min-heading-size", type=float, default=None,
                        help="Minimum font size (pt) to treat as a heading. Auto-detected if omitted.")
    parser.add_argument("--max-heading-size", type=float, default=999.0,
                        help="Maximum font size (pt) to treat as a heading (default: 999)")
    parser.add_argument("--inspect", action="store_true",
                        help="Print font statistics without converting")
    parser.add_argument("--single-file", action="store_true",
                        help="Write everything to a single markdown file")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"Error: PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    if args.inspect:
        inspect(pdf_path)
        return

    out_dir = Path(args.output)

    # Auto-detect heading size if not provided
    if args.min_heading_size is None:
        print("Auto-detecting heading sizes (sampling first 50 pages)...")
        doc = fitz.open(str(pdf_path))
        size_counts = collect_font_stats(doc)
        _, min_heading = auto_detect_heading_sizes(size_counts)
        print(f"  Detected min heading size: {min_heading:.1f}pt  (override with --min-heading-size)")
    else:
        min_heading = args.min_heading_size

    convert(pdf_path, out_dir, min_heading, args.max_heading_size, args.single_file)


if __name__ == "__main__":
    main()
