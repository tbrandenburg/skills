# PDF to Markdown Scripts

This directory contains scripts for converting PDFs to markdown with flexible, agent-driven cleanup and splitting.

## Recommended Workflow

### 1. Convert PDF to Markdown
```bash
python convert_full.py document.pdf --no-ocr
```
Creates a single markdown file from the PDF (supports URLs too).

### 2. Review Document Samples
```bash
python extract_samples.py document.md
```
Shows:
- Beginning, middle, end sections
- All heading patterns
- Repeated lines (potential noise)

**Agent reviews samples** to identify document-specific issues.

### 3. Apply Custom Cleanup
```bash
python apply_substitutions.py document.md \
  -s 's/^## (\d+\.\d+\.\d+)/### \1/g' \
  -s 's/^Page \d+$//g' \
  -s 's/^© .*$//g' \
  --dry-run  # Preview first!
```

Agent creates regexp substitutions based on actual patterns seen in samples.
Each PDF is different - no hardcoded rules!

### 4. Split Document (Optional)
```bash
python analyze_split_points.py document.md  # See options
python split_markdown.py document.md --heading-level 1
```

## Complete Example

```bash
# 1. Convert PDF from URL
python convert_full.py https://example.com/paper.pdf --no-ocr

# 2. Extract samples to review
python extract_samples.py paper.md > samples.txt
# Agent reviews samples.txt

# 3. Create and test custom regexps
python apply_substitutions.py paper.md \
  -s 's/^## (\d+\.\d+\.\d+)/### \1/g' \
  -s 's/^### (\d+\.\d+) /## \1 /g' \
  -s 's/^Page \d+$//g' \
  -s 's/^© 20\d{2}.*$//g' \
  --dry-run

# 4. Apply cleanup (auto-creates backup)
python apply_substitutions.py paper.md \
  -s 's/^## (\d+\.\d+\.\d+)/### \1/g' \
  -s 's/^### (\d+\.\d+) /## \1 /g' \
  -s 's/^Page \d+$//g' \
  -s 's/^© 20\d{2}.*$//g'

# 5. Verify by checking samples again
python extract_samples.py paper.md

# 6. Split into chapters
python split_markdown.py paper.md --heading-level 1
```

## Core Scripts

| Script | Purpose |
|--------|---------|
| `convert_full.py` | Convert PDF to markdown (supports files and URLs) |
| `extract_samples.py` | Show document structure for agent review |
| `apply_substitutions.py` | Apply custom sed-style regexp substitutions |
| `analyze_split_points.py` | Propose document split strategies |
| `split_markdown.py` | Split markdown into multiple files |
| `setup_venv.sh` | Setup virtual environment with docling |

## Why Agent-Driven?

Every PDF is different:
- Different heading numbering schemes
- Different header/footer formats
- Different page number styles
- Unique boilerplate text

**Hardcoded patterns can't handle this variety!**

The new approach:
1. Agent sees actual document content
2. Agent creates regexps for specific issues
3. Agent tests with --dry-run
4. Agent applies with automatic backup

This is more flexible and handles any document.

## Substitution Pattern Reference

```bash
# Fix heading depth
-s 's/^## (\d+\.\d+\.\d+)/### \1/g'

# Remove page numbers (various formats)
-s 's/^Page \d+$//g'
-s 's/^\d+$//g'
-s 's/^- \d+ -$//g'

# Remove copyright
-s 's/^© 20\d{2}.*$//g'
-s 's/^Copyright.*$//gi'

# Remove repeated footer
-s 's/^Company Name Inc\.$//g'

# Fix spacing
-s 's/\n\n\n+/\n\n/g'  # Remove excessive blank lines
```

Flags:
- `g` = global (all occurrences)
- `i` = case insensitive
- `m` = multiline (automatically enabled)

## Virtual Environment

```bash
bash setup_venv.sh
source .venv/bin/activate
```

Or run scripts directly (uses system Python).

