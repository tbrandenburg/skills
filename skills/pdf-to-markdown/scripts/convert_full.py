#!/usr/bin/env python3
"""
Convert PDF to a single markdown file using docling.
"""
import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Convert PDF to markdown")
    parser.add_argument("pdf_path", help="Path to input PDF file")
    parser.add_argument("-o", "--output", help="Output markdown file path (default: <pdf_name>.md)")
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

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = pdf_path.with_suffix('.md')

    print(f"Converting {pdf_path} to {output_path}...")
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
    
    # Export as markdown
    markdown_content = result.document.export_to_markdown()
    
    # Write to file
    output_path.write_text(markdown_content, encoding='utf-8')
    
    print(f"✓ Successfully converted to {output_path}")


if __name__ == "__main__":
    main()
