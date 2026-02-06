# Script Reference - Complete Documentation

Detailed documentation for all scripts in the PDF to markdown conversion toolkit.

## Conversion Scripts

### convert_full.py
```
Usage: convert_full.py <pdf_source> [-o OUTPUT] [--no-ocr]

Arguments:
  pdf_source            Path to input PDF file or URL
  -o, --output OUTPUT   Output markdown file (default: <pdf_name>.md)
  --no-ocr              Disable OCR for faster processing (recommended)
  
Examples:
  # Local file
  python scripts/convert_full.py document.pdf --no-ocr
  
  # URL (docling downloads automatically)
  python scripts/convert_full.py https://example.com/doc.pdf --no-ocr
  
  # URL with custom output
  python scripts/convert_full.py https://example.com/doc.pdf -o custom.md --no-ocr
  
  # Without OCR disabled (slower, for scanned documents)
  python scripts/convert_full.py https://example.com/scanned.pdf
```

### setup_venv.sh
```
Usage: bash setup_venv.sh

Creates virtual environment at scripts/.venv and installs docling.
Only needs to be run once per system.

Details:
  - Creates Python virtual environment in scripts/.venv/
  - Installs docling and all dependencies
  - Compatible with Python 3.8+
```

## Analysis Scripts

### extract_samples.py
```
Usage: extract_samples.py <markdown_file> [--lines LINES] [--min-repeats N]

Extracts representative samples from the document for agent review.

Arguments:
  markdown_file         Input markdown file
  --lines LINES         Lines per sample section (default: 50)
  --min-repeats N       Minimum repeats to show pattern (default: 3)

Output:
  - First N lines (start of document)
  - Middle section sample
  - Last N lines (end of document)
  - All unique heading patterns
  - Lines that appear N+ times (potential noise)

Examples:
  python scripts/extract_samples.py document.md
  python scripts/extract_samples.py document.md --lines 100 --min-repeats 5
```

### analyze_split_points.py
```
Usage: analyze_split_points.py <markdown_file>

Analyzes document structure and proposes split strategies.

Output: 
  - Available heading levels (H1, H2, H3, etc.)
  - Sample sections from document
  - Suggested split strategies with examples
  - Estimated file counts for each strategy

Examples:
  python scripts/analyze_split_points.py document.md
```

## Cleanup Scripts

### apply_substitutions.py
```
Usage: apply_substitutions.py <markdown_file> -s PATTERN [-s PATTERN ...] [OPTIONS]

Applies sed-style regexp substitutions to markdown file.
Creates automatic backup before any changes.

Arguments:
  markdown_file                Input markdown file
  -s, --substitute PATTERN     Sed-style pattern: 's/search/replace/flags'
                               Can be specified multiple times
  --backup FILE                Backup filename (default: <file>.backup)
  --dry-run                    Show changes without applying
  -o, --output FILE            Output file (default: overwrites input)

Pattern Format:
  's/search/replace/flags'     Standard sed substitution
  
  Flags:
    g    - Global (replace all occurrences)
    i    - Case insensitive
    m    - Multiline mode

Examples:
  # Fix heading depth: ## 1.2.3 → ### 1.2.3
  python scripts/apply_substitutions.py document.md \
    -s 's/^## (\d+\.\d+\.\d+)/### \1/g'
  
  # Fix deeper heading levels: ## 1.2.3.4 → #### 1.2.3.4  
  python scripts/apply_substitutions.py document.md \
    -s 's/^## (\d+\.\d+\.\d+\.\d+)/#### \1/g'
  
  # Remove page numbers
  python scripts/apply_substitutions.py document.md \
    -s 's/^Page \d+$//g'
  
  # Remove copyright lines
  python scripts/apply_substitutions.py document.md \
    -s 's/^© 20\d{2}.*$//g'
  
  # Remove image placeholders
  python scripts/apply_substitutions.py document.md \
    -s 's/^<!--.*image.*-->$//g'
  
  # Multiple substitutions (test each individually first!)
  python scripts/apply_substitutions.py document.md \
    -s 's/^Page \d+$//g' \
    -s 's/^© .*$//g' \
    --dry-run

  # Always test with --dry-run first
  python scripts/apply_substitutions.py document.md \
    -s 's/pattern/replacement/g' \
    --dry-run
```

## Splitting Scripts

### split_markdown.py
```
Usage: split_markdown.py <markdown_file> [-o OUTPUT_DIR] [OPTIONS]

Splits a markdown file into multiple files based on heading structure.

Arguments:
  markdown_file                 Input markdown file
  -o, --output-dir DIR          Output directory (default: <name>_split/)
  --heading-level LEVEL         Split on heading level: 1, 2, 3, etc.
  --pattern REGEX               Custom regex pattern for split points
  --extract-title REGEX         Regex to extract title from delimiter line
  --dry-run                     Show split plan without creating files

Examples:
  # Split on H2 headings
  python scripts/split_markdown.py document.md --heading-level 2
  
  # Test split first
  python scripts/split_markdown.py document.md --heading-level 2 --dry-run
  
  # Custom output directory
  python scripts/split_markdown.py document.md -o custom_split/ --heading-level 2
  
  # Custom pattern for numbered sections
  python scripts/split_markdown.py document.md \
    --pattern "^## \d+\.\d+ " \
    --extract-title "(\d+\.\d+ .+)$"
  
  # Split on H3 headings (more granular)  
  python scripts/split_markdown.py document.md --heading-level 3
```

## Common Workflow Combinations

### Basic Cleanup Workflow
```bash
# 1. Extract samples to review issues
python scripts/extract_samples.py document.md

# 2. Remove most common noise (test first)
python scripts/apply_substitutions.py document.md \
  -s 's/^<!--.*image.*-->$//g' \
  --dry-run

# 3. Apply if good
python scripts/apply_substitutions.py document.md \
  -s 's/^<!--.*image.*-->$//g'

# 4. Verify changes
python scripts/extract_samples.py document.md
```

### Heading Structure Fix
```bash
# Fix numbered heading depths
python scripts/apply_substitutions.py document.md \
  -s 's/^## (\d+\.\d+\.\d+)\./### \1./g' \
  -s 's/^## (\d+\.\d+\.\d+\.\d+)\./#### \1./g' \
  --dry-run

# Apply if patterns look correct
python scripts/apply_substitutions.py document.md \
  -s 's/^## (\d+\.\d+\.\d+)\./### \1./g' \
  -s 's/^## (\d+\.\d+\.\d+\.\d+)\./#### \1./g'
```

### Document Splitting
```bash
# Analyze structure
python scripts/analyze_split_points.py document.md

# Test split
python scripts/split_markdown.py document.md --heading-level 2 --dry-run

# Apply if structure looks good
python scripts/split_markdown.py document.md --heading-level 2

# Verify results
ls -lh document_split/
head -20 document_split/01_*.md
```

## Error Handling

### Recovery from Bad Substitutions
```bash
# Restore from automatic backup
cp document.md.backup document.md

# Or restore from specific backup
cp document.md.backup.timestamp document.md
```

### Debugging Patterns
```bash
# Test pattern matching
grep -n "pattern" document.md

# Count matches
grep -c "pattern" document.md

# See context around matches
grep -B2 -A2 "pattern" document.md
```

## Performance Tips

- Use `--no-ocr` flag for text-based PDFs (much faster)
- Process large documents in phases rather than all at once
- Test substitution patterns on small samples first
- Use `--dry-run` extensively before applying changes
- Back up important documents before processing

## Troubleshooting

### Common Issues
1. **"docling not installed"**: Run `bash scripts/setup_venv.sh`
2. **"Pattern not found"**: Check exact text format with `grep`
3. **"Too many matches"**: Make patterns more specific
4. **"Content removed accidentally"**: Restore from backup, refine pattern

### Getting Help
All scripts support `--help` for detailed usage information:
```bash
python scripts/convert_full.py --help
python scripts/extract_samples.py --help
python scripts/apply_substitutions.py --help
python scripts/analyze_split_points.py --help
python scripts/split_markdown.py --help
```