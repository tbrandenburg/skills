#!/usr/bin/env python3
"""
Convert PDF to multiple markdown files, one per chapter.
Chapters are detected based on heading levels (H1/H2).
"""
import sys
import argparse
import re
import importlib
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Convert PDF to markdown files by chapter")
    parser.add_argument("pdf_path", help="Path to input PDF file")
    parser.add_argument("-o", "--output-dir", help="Output directory for markdown files (default: <pdf_name>_chapters/)")
    parser.add_argument("--heading-level", type=int, default=1, choices=[1, 2], 
                        help="Heading level to split on (1=H1, 2=H2, default: 1)")
    parser.add_argument("--no-ocr", action="store_true", help="Disable OCR (faster, for PDFs with text layer)")
    parser.add_argument(
        "--no-auto-heading-fallback",
        action="store_false",
        dest="auto_heading_fallback",
        help="Disable auto fallback to the other heading level when split yields <= 1 chapter",
    )
    parser.set_defaults(auto_heading_fallback=True)
    parser.add_argument(
        "--min-chapter-lines",
        type=int,
        default=0,
        help="Merge chapters with fewer than N non-empty lines into the previous chapter (default: 0=disabled)",
    )
    args = parser.parse_args()

    try:
        docling_mod = importlib.import_module("docling.document_converter")
        DocumentConverter = getattr(docling_mod, "DocumentConverter")
    except ImportError:
        print("ERROR: docling not installed. Install with: pip install docling", file=sys.stderr)
        sys.exit(1)

    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"ERROR: PDF file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = pdf_path.parent / f"{pdf_path.stem}_chapters"
    
    output_dir.mkdir(parents=True, exist_ok=True)

    # If the directory already contains markdown files, fail early to avoid mixing outputs.
    existing_md = list(output_dir.glob("*.md"))
    if existing_md:
        print(
            f"ERROR: Output directory already contains {len(existing_md)} .md file(s): {output_dir}\n"
            "Choose a different directory with -o/--output-dir or remove existing files first.",
            file=sys.stderr,
        )
        sys.exit(2)

    print(f"Converting {pdf_path} to chapters in {output_dir}...")
    if args.no_ocr:
        print("OCR disabled for faster processing")

    # Convert PDF to markdown
    try:
        ConversionOptions = getattr(docling_mod, "ConversionOptions")
        if args.no_ocr:
            options = ConversionOptions(ocr=False)
            converter = DocumentConverter(options=options)
        else:
            converter = DocumentConverter()
    except Exception:
        # Fallback for older docling versions or API differences
        converter = DocumentConverter()
        
    result = converter.convert(str(pdf_path))
    markdown_content = result.document.export_to_markdown()

    def split_markdown(md: str, heading_level: int):
        heading_pattern = r"^#{" + str(heading_level) + r"}\s+(.+)$"
        frontmatter_lines = []
        chapters_local = []
        current_title = None
        current_lines = []

        for line in md.split("\n"):
            match = re.match(heading_pattern, line)
            if match:
                if current_title is not None:
                    chapters_local.append((current_title, "\n".join(current_lines)))
                current_title = match.group(1).strip()
                current_lines = [line]
            else:
                if current_title is None:
                    frontmatter_lines.append(line)
                else:
                    current_lines.append(line)

        if current_title is not None and current_lines:
            chapters_local.append((current_title, "\n".join(current_lines)))

        return frontmatter_lines, chapters_local

    def count_nonempty_lines(text: str) -> int:
        return sum(1 for ln in text.splitlines() if ln.strip())

    frontmatter, chapters = split_markdown(markdown_content, args.heading_level)

    if args.auto_heading_fallback and len(chapters) <= 1:
        fallback_level = 2 if args.heading_level == 1 else 1
        fm2, ch2 = split_markdown(markdown_content, fallback_level)
        if len(ch2) > len(chapters):
            print(
                f"NOTE: Found {len(chapters)} chapter(s) at heading level {args.heading_level}; "
                f"retrying with level {fallback_level} -> {len(ch2)} chapter(s)"
            )
            frontmatter, chapters = fm2, ch2

    if args.min_chapter_lines and args.min_chapter_lines > 0 and chapters:
        merged = []
        for title, content in chapters:
            if merged and count_nonempty_lines(content) < args.min_chapter_lines:
                prev_title, prev_content = merged[-1]
                merged[-1] = (prev_title, prev_content.rstrip() + "\n\n" + content.lstrip())
            else:
                merged.append((title, content))
        chapters = merged

    wrote_frontmatter = False
    wrote_single = False

    # Write frontmatter (content before first chapter)
    if any(line.strip() for line in frontmatter):
        fm_file = output_dir / "00_00_frontmatter.md"
        fm_text = "\n".join(frontmatter).strip() + "\n"
        fm_file.write_text(fm_text, encoding="utf-8")
        print(f"✓ Wrote {fm_file}")
        wrote_frontmatter = True

    if not chapters:
        print("WARNING: No chapters detected. Creating single file.")
        output_file = output_dir / f"{pdf_path.stem}.md"
        output_file.write_text(markdown_content, encoding='utf-8')
        print(f"✓ Wrote {output_file}")
        wrote_single = True
    else:
        # Write each chapter to a separate file
        for idx, (title, content) in enumerate(chapters, start=1):
            # Sanitize filename
            safe_title = re.sub(r'[^\w\s-]', '', title)
            safe_title = re.sub(r'[-\s]+', '_', safe_title).strip('_')
            safe_title = safe_title[:50]  # Limit length

            if not safe_title:
                safe_title = f"chapter_{idx:02d}"
            
            filename = f"{idx:02d}_{safe_title}.md"
            output_file = output_dir / filename
            output_file.write_text(content, encoding='utf-8')
            print(f"✓ Wrote {output_file}")

    if wrote_single:
        total_written = (1 if wrote_frontmatter else 0) + 1
    else:
        total_written = (1 if wrote_frontmatter else 0) + len(chapters)

    print(f"\n✓ Successfully converted {total_written} file(s) to {output_dir}")


if __name__ == "__main__":
    main()
