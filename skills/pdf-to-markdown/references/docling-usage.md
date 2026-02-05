# Docling Usage Reference

## Overview

Docling is a Python library for converting documents (PDF, DOCX, etc.) to markdown and other formats. It provides high-quality extraction with support for tables, images, and document structure.

GitHub: https://github.com/docling-project/docling

## Installation

```bash
pip install docling
```

## Basic Usage

### Simple PDF to Markdown

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("document.pdf")
markdown = result.document.export_to_markdown()
```

### Access Document Structure

The converted document provides structured access to:

- **Headings**: Detected heading hierarchy (H1, H2, etc.)
- **Paragraphs**: Body text content
- **Tables**: Extracted table data
- **Images**: Embedded images with metadata
- **Metadata**: Document properties

### Export Formats

```python
# Markdown
markdown = result.document.export_to_markdown()

# JSON
json_data = result.document.export_to_json()

# HTML
html = result.document.export_to_html()

# Plain text
text = result.document.export_to_text()
```

## Advanced Features

### Custom Conversion Options

```python
from docling.document_converter import DocumentConverter, ConversionOptions

options = ConversionOptions(
    ocr=True,  # Enable OCR for scanned PDFs
    extract_images=True,  # Extract embedded images
    extract_tables=True,  # Extract tables
)

converter = DocumentConverter(options=options)
result = converter.convert("document.pdf")
```

### Batch Conversion

```python
from pathlib import Path

converter = DocumentConverter()
pdf_dir = Path("./pdfs")

for pdf_file in pdf_dir.glob("*.pdf"):
    result = converter.convert(str(pdf_file))
    output = pdf_file.with_suffix('.md')
    output.write_text(result.document.export_to_markdown())
```

## Document Structure

Access document elements programmatically:

```python
result = converter.convert("document.pdf")
doc = result.document

# Iterate through document elements
for element in doc.elements:
    if element.type == "heading":
        level = element.level  # 1, 2, 3, etc.
        text = element.text
    elif element.type == "paragraph":
        text = element.text
    elif element.type == "table":
        table_data = element.data
```

## Common Patterns

### Split by Headings

To split a document by chapters/sections:

1. Convert PDF to markdown
2. Parse markdown to identify heading markers (`#`, `##`, etc.)
3. Split content at heading boundaries
4. Write each section to separate files

### Handle Large Documents

For very large PDFs:

- Convert in chunks if API supports it
- Use streaming/iterator patterns if available
- Monitor memory usage during conversion

## Troubleshooting

### Missing Dependencies

If docling fails to import, ensure all dependencies are installed:

```bash
pip install --upgrade docling
```

### OCR for Scanned PDFs

For scanned documents without text layer:

```python
options = ConversionOptions(ocr=True)
converter = DocumentConverter(options=options)
```

This requires tesseract-ocr installed on the system.

### Virtual Environment

Always use a virtual environment to avoid conflicts:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install docling
```
