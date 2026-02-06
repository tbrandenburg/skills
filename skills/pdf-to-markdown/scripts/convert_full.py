#!/usr/bin/env python3
"""
Convert PDF to a single markdown file using docling.
Supports both local files and URLs with enhanced table extraction.
"""
import sys
import argparse
import importlib
from pathlib import Path
from urllib.parse import urlparse


def is_url(string):
    """Check if the string is a valid URL."""
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def get_output_filename(source, custom_output=None):
    """Determine output filename from source (URL or local path)."""
    if custom_output:
        return Path(custom_output)
    
    if is_url(source):
        # Extract filename from URL, fallback to generic name
        parsed = urlparse(source)
        filename = Path(parsed.path).name
        if filename and filename.endswith('.pdf'):
            return Path(filename).with_suffix('.md')
        else:
            # Fallback for URLs without clear filenames
            return Path("document.md")
    else:
        # Local file path
        return Path(source).with_suffix('.md')


def main():
    parser = argparse.ArgumentParser(description="Convert PDF to markdown")
    parser.add_argument("pdf_source", help="Path to input PDF file or URL")
    parser.add_argument("-o", "--output", help="Output markdown file path (default: <pdf_name>.md)")
    parser.add_argument("--no-ocr", action="store_true", help="Disable OCR (faster, for PDFs with text layer)")
    args = parser.parse_args()

    try:
        docling_mod = importlib.import_module("docling.document_converter")
        DocumentConverter = getattr(docling_mod, "DocumentConverter")
    except ImportError:
        print("ERROR: docling not installed. Install with: pip install docling", file=sys.stderr)
        sys.exit(1)

    source = args.pdf_source
    
    # Validate source (file existence check only for local files)
    if not is_url(source):
        pdf_path = Path(source)
        if not pdf_path.exists():
            print(f"ERROR: PDF file not found: {pdf_path}", file=sys.stderr)
            sys.exit(1)

    # Determine output path
    output_path = get_output_filename(source, args.output)

    if output_path.exists():
        print(
            f"ERROR: Output file already exists: {output_path}\n"
            "Choose a different path with -o/--output or remove the existing file first.",
            file=sys.stderr,
        )
        sys.exit(2)

    # Print status
    source_type = "URL" if is_url(source) else "file"
    print(f"Converting {source_type}: {source}")
    print(f"Output: {output_path}")
    print("Features: Enhanced tables + code understanding")
    if args.no_ocr:
        print("OCR disabled for faster processing")

    # Convert PDF to markdown with enhanced document processing
    try:
        # Import required classes for advanced options
        PdfFormatOption = getattr(docling_mod, "PdfFormatOption")
        PdfPipelineOptions = getattr(docling_mod, "PdfPipelineOptions", None)
        TableStructureOptions = getattr(docling_mod, "TableStructureOptions", None)
        TableFormerMode = getattr(docling_mod, "TableFormerMode", None)
        InputFormat = getattr(docling_mod, "InputFormat", None)
        
        # Try to get these from pipeline_options module if not in main module
        if not PdfPipelineOptions:
            pipeline_mod = importlib.import_module("docling.datamodel.pipeline_options")
            PdfPipelineOptions = getattr(pipeline_mod, "PdfPipelineOptions")
            TableStructureOptions = getattr(pipeline_mod, "TableStructureOptions")
            TableFormerMode = getattr(pipeline_mod, "TableFormerMode")
        
        if not InputFormat:
            base_models_mod = importlib.import_module("docling.datamodel.base_models")
            InputFormat = getattr(base_models_mod, "InputFormat")
        
        # Configure enhanced pipeline options for robust document processing
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_table_structure = True  # Enable table structure extraction
        pipeline_options.do_ocr = not args.no_ocr  # OCR based on command line flag
        pipeline_options.do_code_enrichment = True  # Enable code syntax understanding
        
        if TableStructureOptions and TableFormerMode:
            pipeline_options.table_structure_options = TableStructureOptions(
                do_cell_matching=True,  # Standard cell matching for most documents
                mode=TableFormerMode.ACCURATE  # Use accurate mode for best table quality
            )
        
        # Create converter with enhanced table options
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        
    except Exception as e:
        print(f"Warning: Could not configure advanced table options: {e}")
        print("Falling back to basic converter...")
        # Fallback for older docling versions or missing dependencies
        try:
            ConversionOptions = getattr(docling_mod, "ConversionOptions")
            if args.no_ocr:
                options = ConversionOptions(ocr=False)
                converter = DocumentConverter(options=options)
            else:
                converter = DocumentConverter()
        except Exception:
            converter = DocumentConverter()
    
    # Docling handles both local files and URLs with the same convert() method
    result = converter.convert(source)
    
    # Export as markdown
    markdown_content = result.document.export_to_markdown()
    
    # Write to file
    output_path.write_text(markdown_content, encoding='utf-8')
    
    print(f"✓ Successfully converted to {output_path}")


if __name__ == "__main__":
    main()
