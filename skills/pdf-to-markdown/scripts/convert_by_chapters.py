#!/usr/bin/env python3
"""
Convert PDF to multiple markdown files, one per chapter.
Chapters are detected based on heading levels (H1/H2).
"""
import sys
import argparse
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Convert PDF to markdown files by chapter")
    parser.add_argument("pdf_path", help="Path to input PDF file")
    parser.add_argument("-o", "--output-dir", help="Output directory for markdown files (default: <pdf_name>_chapters/)")
    parser.add_argument("--heading-level", type=int, default=1, choices=[1, 2], 
                        help="Heading level to split on (1=H1, 2=H2, default: 1)")
    parser.add_argument("--no-ocr", action="store_true", help="Disable OCR (faster, for PDFs with text layer)")
    args = parser.parse_args()

    try:
        from docling.document_converter import DocumentConverter
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

    print(f"Converting {pdf_path} to chapters in {output_dir}...")
    if args.no_ocr:
        print("OCR disabled for faster processing")

    # Convert PDF to markdown
    try:
        from docling.document_converter import ConversionOptions
        if args.no_ocr:
            options = ConversionOptions(ocr=False)
            converter = DocumentConverter(options=options)
        else:
            converter = DocumentConverter()
    except ImportError:
        # Fallback for older docling versions
        converter = DocumentConverter()
        
    result = converter.convert(str(pdf_path))
    markdown_content = result.document.export_to_markdown()

    # Split by heading level
    heading_pattern = r'^#{' + str(args.heading_level) + r'}\s+(.+)$'
    chapters = []
    current_chapter = None
    current_content = []

    for line in markdown_content.split('\n'):
        match = re.match(heading_pattern, line)
        if match:
            # Save previous chapter
            if current_chapter is not None:
                chapters.append((current_chapter, '\n'.join(current_content)))
            
            # Start new chapter
            current_chapter = match.group(1).strip()
            current_content = [line]
        else:
            if current_chapter is not None:
                current_content.append(line)
            else:
                # Content before first chapter (e.g., title, introduction)
                if not current_content and line.strip():
                    current_chapter = "00_frontmatter"
                    current_content = [line]
                elif current_content:
                    current_content.append(line)

    # Save last chapter
    if current_chapter is not None and current_content:
        chapters.append((current_chapter, '\n'.join(current_content)))

    if not chapters:
        print("WARNING: No chapters detected. Creating single file.")
        output_file = output_dir / f"{pdf_path.stem}.md"
        output_file.write_text(markdown_content, encoding='utf-8')
        print(f"✓ Wrote {output_file}")
    else:
        # Write each chapter to a separate file
        for idx, (title, content) in enumerate(chapters, start=1):
            # Sanitize filename
            safe_title = re.sub(r'[^\w\s-]', '', title)
            safe_title = re.sub(r'[-\s]+', '_', safe_title).strip('_')
            safe_title = safe_title[:50]  # Limit length
            
            filename = f"{idx:02d}_{safe_title}.md"
            output_file = output_dir / filename
            output_file.write_text(content, encoding='utf-8')
            print(f"✓ Wrote {output_file}")

    print(f"\n✓ Successfully converted {len(chapters)} chapter(s) to {output_dir}")


if __name__ == "__main__":
    main()
