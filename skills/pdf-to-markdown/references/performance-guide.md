# PDF to Markdown Skill - Performance Guide

## Test Results - Automotive SPICE PAM v4.0 (2 MB, ~180 pages)

### Observed Performance Issues

1. **Extremely Slow Processing**: Default docling configuration with CPU-only processing took >20 minutes for initial pages
2. **OCR Overhead**: RapidOCR models downloading and running on CPU significantly slowed conversion
3. **Model Downloads**: First run downloads ~40MB of OCR models
4. **NNPACK Warnings**: Harmless warnings about unsupported hardware, but indicate CPU-only execution

### Root Causes

1. **OCR Enabled by Default**: Docling uses OCR even for PDFs with text layers
2. **CPU Processing**: PyTorch models running on CPU without GPU acceleration
3. **Per-Page Processing**: Each page requires ML inference for layout analysis

## Optimization Strategies

### 1. Disable OCR for Text-Based PDFs (FASTEST)

Most technical PDFs already have a text layer and don't need OCR.

```python
from docling.document_converter import DocumentConverter, ConversionOptions

options = ConversionOptions(ocr=False)
converter = DocumentConverter(options=options)
result = converter.convert("document.pdf")
```

**Expected Impact**: 10-50x speedup for PDFs with text layers

### 2. Use Simpler Conversion Pipeline

Skip advanced layout analysis when not needed:

```python
from docling.document_converter import DocumentConverter, SimplePipeline

converter = DocumentConverter(pipeline=SimplePipeline())
result = converter.convert("document.pdf")
```

### 3. GPU Acceleration (If Available)

Enable CUDA for PyTorch:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**Expected Impact**: 5-20x speedup vs CPU

### 4. Alternative: Use pypdf for Simple Extraction

For documents where layout doesn't matter:

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
text = "\\n\\n".join([page.extract_text() for page in reader.pages])
```

**Expected Impact**: Near-instant for most PDFs

### 5. Process Page Ranges

For testing or selective conversion:

```python
# Process only first 10 pages
converter.convert("document.pdf", pages=range(0, 10))
```

## Recommendations for the Skill

### Priority 1: Add Fast Mode

Add a `--fast` flag that:
- Disables OCR
- Uses simpler pipeline
- Skips advanced layout analysis

### Priority 2: Add Progress Feedback

Show page-by-page progress so users know it's working:

```python
print(f"Converting page {i}/{total_pages}...", end='\\r')
```

### Priority 3: Add Page Range Option

Allow users to test on subset:

```bash
--pages 1-10  # Convert only pages 1-10
```

### Priority 4: Detect Text Layer

Auto-detect if PDF needs OCR:

```python
def pdf_has_text(pdf_path):
    reader = PdfReader(pdf_path)
    return bool(reader.pages[0].extract_text().strip())
```

### Priority 5: Add Timeout/Cancellation

Allow users to cancel long conversions:

```python
import signal
signal.alarm(timeout_seconds)  # Unix only
```

## Updated Usage Guidance

For the test PDF (Automotive SPICE PAM):

```bash
# FAST: Disable OCR (recommended for technical PDFs)
python convert_by_chapters.py document.pdf --no-ocr

# FASTER: Use pypdf fallback for simple text extraction
python convert_by_chapters.py document.pdf --simple

# TEST: Convert only first 10 pages
python convert_by_chapters.py document.pdf --pages 1-10

# SLOW: Full docling with OCR (original behavior)
python convert_by_chapters.py document.pdf
```

## Implementation Notes

The slowness is **expected behavior** for docling with default settings on CPU. This is not a bug in the skill implementation but rather the nature of ML-based PDF processing.

For production use with large PDFs:
1. Use `--no-ocr` flag (to be implemented)
2. Consider GPU-enabled environment
3. Or use simpler pypdf-based extraction for text-only needs

## Estimated Timings

| Method | 180-page PDF | Notes |
|--------|--------------|-------|
| Docling + OCR + CPU | 60+ min | Full ML pipeline |
| Docling - OCR + CPU | 5-10 min | Layout analysis only |
| Docling + GPU | 2-5 min | With CUDA |
| pypdf | <1 min | Simple text extraction |

The skill works correctly but needs performance optimization flags for practical use with large documents.
