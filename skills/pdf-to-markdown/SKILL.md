---
name: pdf-to-markdown
description: Convert PDF documents to markdown format using docling. Supports two modes - (1) single markdown file for entire PDF, and (2) multiple markdown files split by chapters/sections. Use when users need to convert PDFs to markdown, extract text from PDFs into markdown format, or split PDF content into chapter-based markdown files. IMPORTANT - For large PDFs or faster processing, use --no-ocr flag to disable OCR (recommended for technical PDFs with text layers).
---

# PDF to Markdown Converter

Convert PDF documents to markdown using the docling library, with support for single-file or chapter-based splitting.

## Quick Start

### Convert PDF to Single Markdown File

```bash
# Fast mode (recommended): Disable OCR for PDFs with text layer
python scripts/convert_full.py document.pdf --no-ocr
# Creates: document.md

# With OCR (slower, for scanned PDFs)
python scripts/convert_full.py document.pdf

# Custom output path
python scripts/convert_full.py document.pdf -o output.md --no-ocr
```

### Convert PDF to Multiple Chapter Files

```bash
# Fast mode (recommended)
python scripts/convert_by_chapters.py document.pdf --no-ocr
# Creates: document_chapters/01_Introduction.md, 02_Methods.md, etc.

# Custom output directory
python scripts/convert_by_chapters.py document.pdf -o chapters/ --no-ocr

# Split on H2 instead of H1
python scripts/convert_by_chapters.py document.pdf --heading-level 2 --no-ocr
```

## Performance Notes

⚠️ **IMPORTANT**: Default mode with OCR is extremely slow for large PDFs on CPU (~60+ minutes for 180-page PDF).

**Recommended**: Always use `--no-ocr` flag unless processing scanned documents.

- **With OCR (default)**: 60+ minutes for 180-page PDF on CPU
- **Without OCR (`--no-ocr`)**: 5-10 minutes for same PDF
- **With GPU**: 2-5 minutes

See [references/performance-guide.md](references/performance-guide.md) for detailed optimization strategies.

## Virtual Environment Setup

The scripts require docling, which should be installed in a virtual environment:

```bash
# Setup (automatic)
bash scripts/setup_venv.sh

# Or use wrapper script (handles setup automatically)
python scripts/run_conversion.py full document.pdf
python scripts/run_conversion.py chapters document.pdf
```

The virtual environment is created at `scripts/.venv/` and includes docling.

## How It Works

### Single File Mode

1. Uses docling's `DocumentConverter` to parse PDF
2. Exports entire document as markdown
3. Writes to single output file

Best for: Small to medium documents, when you need all content in one place.

### Chapter Mode

1. Converts PDF to markdown using docling
2. Splits markdown by heading level (H1 by default, H2 optional)
3. Creates separate files for each chapter with numbered filenames
4. Sanitizes chapter titles for safe filenames

Best for: Large documents, books, reports with clear chapter structure.

**Heading Detection**: Uses regex to identify markdown headings (`#` for H1, `##` for H2). Adjusts split level with `--heading-level` parameter.

**Filename Generation**: Chapter titles become filenames with:
- Sequential numbering (01, 02, 03, etc.)
- Sanitized text (removes special characters, replaces spaces with underscores)
- Length limit (50 characters max)

**Frontmatter Handling**: Content before the first chapter is saved as `00_frontmatter.md`.

## Implementation Notes

### Running Scripts

Two approaches:

1. **Direct execution**: Run `convert_full.py` or `convert_by_chapters.py` directly. Requires docling installed in current environment.

2. **Via wrapper**: Use `run_conversion.py` to handle virtual environment automatically.

### Virtual Environment

Virtual environments isolate dependencies:

```bash
# Create venv
python3 -m venv scripts/.venv

# Activate
source scripts/.venv/bin/activate

# Install docling
pip install docling

# Run scripts
python scripts/convert_full.py document.pdf
```

Scripts work with or without venv - use venv to avoid system-wide installation.

### Error Handling

Scripts handle common errors:
- Missing PDF file: Exits with error message
- Missing docling: Shows installation instructions
- No chapters detected: Falls back to single file output

## Advanced Usage

For detailed docling features and options, see [references/docling-usage.md](references/docling-usage.md).

### Custom Heading Level

By default, chapter mode splits on H1 headings. For documents with H1 as title and H2 as chapters:

```bash
python scripts/convert_by_chapters.py document.pdf --heading-level 2
```

### Batch Processing

Process multiple PDFs:

```bash
for pdf in *.pdf; do
    python scripts/convert_full.py "$pdf"
done
```

### Integration with Other Tools

The markdown output can be:
- Committed to version control for tracking changes
- Processed with markdown tools (pandoc, etc.)
- Indexed for search
- Used as input for AI processing

## Workflow Guidance

When a user requests PDF conversion:

1. **Clarify requirements**: Single file or chapter split?
2. **Check PDF location**: Ensure file path is accessible
3. **Choose appropriate script**: `convert_full.py` or `convert_by_chapters.py`
4. **Setup if needed**: Run `setup_venv.sh` if docling not installed
5. **Execute conversion**: Run script with appropriate parameters
6. **Verify output**: Check created markdown files
7. **Handle errors**: If conversion fails, check error messages and PDF quality

## Script Reference

### convert_full.py

```
Usage: convert_full.py <pdf_path> [-o OUTPUT] [--no-ocr]

Arguments:
  pdf_path              Path to input PDF file
  -o, --output OUTPUT   Output markdown file (default: <pdf_name>.md)
  --no-ocr              Disable OCR for faster processing (recommended)
```

### convert_by_chapters.py

```
Usage: convert_by_chapters.py <pdf_path> [-o OUTPUT_DIR] [--heading-level LEVEL] [--no-ocr]

Arguments:
  pdf_path                    Path to input PDF file
  -o, --output-dir DIR        Output directory (default: <pdf_name>_chapters/)
  --heading-level LEVEL       Heading level to split on: 1 or 2 (default: 1)
  --no-ocr                    Disable OCR for faster processing (recommended)
```

### run_conversion.py

```
Usage: run_conversion.py [full|chapters] <pdf_path> [options]

Modes:
  full        Single markdown file (uses convert_full.py)
  chapters    Multiple chapter files (uses convert_by_chapters.py)
```

### setup_venv.sh

```
Usage: bash setup_venv.sh

Creates virtual environment at scripts/.venv and installs docling.
```
