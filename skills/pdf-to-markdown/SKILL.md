---
name: pdf-to-markdown
description: Convert PDF documents to markdown format using docling, with flexible agent-driven cleanup. Workflow - (1) Load PDF from file or URL, (2) Convert to markdown, (3) Agent reviews document samples and creates custom regexp substitutions in small iterations for issues like wrong heading depths, headers/footers, page numbers, boilerplate (4) Optionally split with agent-proposed delimiters, reviewing filenames and structure. Each PDF is unique - agents adapt cleanup to actual document content through iterative check-correct-verify cycles, not hardcoded rules. IMPORTANT - Use --no-ocr flag for faster processing.
---

# PDF to Markdown Converter with Intelligent Cleanup

Convert PDF documents to markdown using the docling library, with built-in cleanup and smart splitting capabilities.

## Recommended Workflow

For best results with PDF conversion, especially for poorly formatted PDFs, follow this iterative workflow:

### 1. Convert PDF to Markdown

```bash
# Fast mode (recommended): Disable OCR for PDFs with text layer
python scripts/convert_full.py document.pdf --no-ocr
# Creates: document.md

# With OCR (slower, for scanned PDFs)
python scripts/convert_full.py document.pdf

# From URL
python scripts/convert_full.py https://example.com/document.pdf --no-ocr

# Custom output path
python scripts/convert_full.py document.pdf -o output.md --no-ocr

# Alternative: Use pdftotext for very fast text extraction (no OCR)
pdftotext -layout document.pdf document.md
# Note: pdftotext is faster but provides plain text, not structured markdown
```

### 2. Review and Clean Up Markdown - ITERATIVE APPROACH

**Work in small, verifiable iterations** - Fix ONE issue at a time:

```bash
# =================================================================
# ITERATION 1: Extract and review samples
# =================================================================
python scripts/extract_samples.py document.md
# Agent reviews output and identifies FIRST issue (e.g., "Page X" appears 150 times)

# =================================================================
# ITERATION 2: Fix ONE issue - Test first!
# =================================================================
python scripts/apply_substitutions.py document.md \
  -s 's/^Page \d+$//' \
  --dry-run  # ALWAYS test first - verify it matches correctly

# If dry-run looks good, apply it
python scripts/apply_substitutions.py document.md \
  -s 's/^Page \d+$//'
# ✓ Backup automatically created as document.md.backup

# =================================================================
# ITERATION 3: Verify the change worked
# =================================================================
python scripts/extract_samples.py document.md
# Agent checks: Did page numbers disappear? Any unintended changes?

# =================================================================
# ITERATION 4: Next issue - Copyright notices
# =================================================================
python scripts/apply_substitutions.py document.md \
  -s 's/^© 20\d{2}.*$//' \
  --dry-run  # Test again

# Apply if good
python scripts/apply_substitutions.py document.md \
  -s 's/^© 20\d{2}.*$//'

# =================================================================
# ITERATION 5: Verify again
# =================================================================
python scripts/extract_samples.py document.md
# Check that copyright lines are gone

# =================================================================
# Continue this cycle: Check → Correct → Verify
# =================================================================
# - Fix heading depths next
# - Then remove footers
# - Then cleanup spacing
# - Each time: dry-run → apply → verify
```

**CRITICAL Principles:**

1. **Small iterations**: Fix 1-2 issues per iteration, not everything at once
2. **Always verify**: Extract samples after EACH change to confirm it worked
3. **Test first**: ALWAYS use `--dry-run` before applying
4. **Backup recovery**: If something goes wrong:
   ```bash
   # Oops! That removed too much content
   cp document.md.backup document.md
   # Try again with more conservative/specific pattern
   python scripts/apply_substitutions.py document.md \
     -s 's/^Page \d+$//  # More specific pattern
     --dry-run
   ```
5. **Better safe than sorry**: 5 small successful fixes > 1 big failed attempt
6. **Never continue with broken state**: If a change fails, restore backup immediately

### 3. Split into Multiple Files (Optional) - ITERATIVE APPROACH

**Review and refine** - Don't accept bad splits:

```bash
# =================================================================
# STEP 1: Analyze document structure
# =================================================================
python scripts/analyze_split_points.py document.md
# Shows: heading levels, sample sections, suggested strategies

# =================================================================
# STEP 2: Test split with --dry-run
# =================================================================
python scripts/split_markdown.py document.md --heading-level 1 --dry-run

# Agent REVIEWS the proposed split:
# ✓ Are filenames understandable? (can I tell content from filename alone?)
# ✓ Is the split logical? (related content together?)
# ✓ Right number of files? (not too many tiny files, not too few huge ones?)
# ✓ Are sections complete? (no truncated content?)

# =================================================================
# STEP 3a: If split looks GOOD → Execute
# =================================================================
python scripts/split_markdown.py document.md --heading-level 1
# ✓ Creates document_split/ directory with numbered files

# =================================================================
# STEP 3b: If split is NOT GOOD → Try different strategy
# =================================================================
# Too many files? Use HIGHER heading level:
python scripts/split_markdown.py document.md --heading-level 2 --dry-run

# Filenames unclear? Try custom pattern:
python scripts/split_markdown.py document.md \
  --pattern "^## \d+\.\d+ " \
  --extract-title "(\d+\.\d+ .+)$" \
  --dry-run

# =================================================================
# STEP 4: Verify split results
# =================================================================
ls -lh document_split/          # Check filenames
head -20 document_split/01_*.md  # Spot-check first file
head -20 document_split/05_*.md  # Check middle file

# Agent verifies:
# - Can I understand each file's content from its filename?
# - Is content properly separated and complete?
# - Are file sizes reasonable?

# =================================================================
# STEP 5: If STILL not right → Delete and retry
# =================================================================
rm -rf document_split/  # Remove bad split
# Analyze structure again, try different approach
python scripts/analyze_split_points.py document.md  # Review options
python scripts/split_markdown.py document.md --heading-level 3 --dry-run
```

**Split Success Criteria** (ALL must be met):

1. **Understandable filenames**: You know the content from filename alone
2. **Logical grouping**: Related content stays together
3. **Reasonable size**: Not 100 tiny files, not 2 huge files
4. **Complete sections**: No truncated or missing content

**If ANY criterion fails**: Delete split directory, analyze again, try different strategy!

## Performance Notes

⚠️ **IMPORTANT**: Default mode with OCR is extremely slow for large PDFs on CPU (~60+ minutes for 180-page PDF).

**Recommended**: Always use `--no-ocr` flag unless processing scanned documents.

- **With OCR (default)**: 60+ minutes for 180-page PDF on CPU
- **Without OCR (`--no-ocr`)**: 5-10 minutes for same PDF
- **With GPU**: 2-5 minutes
- **With pdftotext**: Seconds (but less structured)

See [references/performance-guide.md](references/performance-guide.md) for detailed optimization strategies.

## Virtual Environment Setup

The scripts require docling, which should be installed in a virtual environment:

```bash
# Setup (one-time)
bash scripts/setup_venv.sh

# Activate when needed
source scripts/.venv/bin/activate

# Or scripts work without activation (will use system Python)
```

The virtual environment is created at `scripts/.venv/` and includes docling.

## How It Works

### Step 1: PDF Conversion

1. PDF is loaded from file path or URL
2. docling's `DocumentConverter` parses the PDF structure
3. Entire document is exported as a single markdown file
4. Initial conversion preserves all content but may have formatting issues

### Step 2: Iterative Agent-Driven Cleanup

The agent works in small, verifiable iterations:

**Iteration Cycle (Repeat for each issue type):**
1. Extract samples from document
2. Review samples and identify ONE type of issue
3. Create custom regexp for THIS issue only
4. Test with --dry-run to preview changes
5. Apply if good (automatic backup created)
6. Verify by extracting samples again
7. If failed: restore from backup, try different pattern
8. Move to next issue type

**Why Iterative?**
- Small changes are safer than large ones
- Easy to verify each step worked correctly
- Simple to recover if something goes wrong
- Agent can learn and adjust approach as they go

**Custom Regexp Creation**:
- Agent generates sed-style substitution patterns based on actual content
- Patterns fix heading depths, remove noise, correct formatting
- No hardcoded rules - agent adapts to each document's unique issues
- Each pattern is tested before application

**Safe Application**:
- Automatic backup created before any changes
- Dry-run mode to preview all changes
- Can restore from backup if anything goes wrong
- Multiple small substitutions better than one large change

### Step 3: Smart Splitting (Optional)

If the user wants to split the document:

**Analysis Phase**:
- Extracts document samples to show structure
- Identifies heading levels and patterns (H1, H2, numbered sections)
- Proposes split strategies with examples
- Lets user choose or customize the delimiter

**Split Execution with Review**:
- Uses chosen delimiter (heading level or custom regex)
- Extracts section titles for filenames
- Creates numbered, sanitized filenames
- Agent reviews results against success criteria
- If not successful: delete, analyze, try different approach

## Advanced Usage

For detailed docling features and options, see [references/docling-usage.md](references/docling-usage.md).

### Batch Processing

Process multiple PDFs:

```bash
for pdf in *.pdf; do
    python scripts/convert_full.py "$pdf" --no-ocr
done
```

### Integration with Other Tools

The markdown output can be:
- Committed to version control for tracking changes
- Processed with markdown tools (pandoc, etc.)
- Indexed for search
- Used as input for AI processing

## Workflow Guidance

When a user requests PDF conversion, follow this iterative sequence:

### Phase 1: Initial Conversion

1. **Get PDF source**: File path or URL
2. **Setup environment**: Run `setup_venv.sh` if docling not installed
3. **Convert to markdown**: Use `convert_full.py` with `--no-ocr` for best performance
4. **Verify output**: Check that markdown file was created

### Phase 2: Iterative Review and Cleanup

**Work in small, verifiable iterations:**

5. **Extract samples**: Run `extract_samples.py` to see document structure
6. **Review samples**: Agent examines samples for **ONE type of issue** at a time:
   - Start with most obvious/frequent issue (e.g., page footers appearing 100+ times)
   - Don't try to fix everything at once!

7. **Create regexp for ONE issue**: Generate sed-style pattern for this specific issue
   - Example: `'s/^Page \d+$//'` for page numbers
   
8. **Test with dry-run**: Preview changes before applying
   ```bash
   python scripts/apply_substitutions.py document.md -s 'pattern' --dry-run
   ```

9. **Apply if good**: Execute the substitution (auto-backup created)
   ```bash
   python scripts/apply_substitutions.py document.md -s 'pattern'
   ```

10. **Verify with samples**: Check that it worked correctly
    ```bash
    python scripts/extract_samples.py document.md
    ```

11. **If something went wrong**:
    - Restore from backup: `cp document.md.backup document.md`
    - Try more conservative pattern
    - Or try different approach
    - **Never continue with broken state!**

12. **Repeat steps 6-11** for next issue type:
    - Fix page numbers → verify → fix headers → verify → fix headings → verify
    - Each iteration should be small and safe
    - Better 5 small successful fixes than 1 big failed attempt

### Phase 3: Optional Splitting (with Review)

13. **Analyze structure**: Run `analyze_split_points.py` to show options
14. **Propose strategies**: Present heading levels and sample delimiters to user
15. **Test split with dry-run**: 
    ```bash
    python scripts/split_markdown.py document.md --heading-level 2 --dry-run
    ```

16. **Review split plan**:
    - Are filenames understandable?
    - Is the grouping logical?
    - Right number of files (not too many/few)?

17. **Execute split if good**:
    ```bash
    python scripts/split_markdown.py document.md --heading-level 2
    ```

18. **Verify split results**:
    - Check filenames: `ls -lh document_split/`
    - Spot-check content: `head -20 document_split/01_*.md`
    - Verify completeness: All sections present?

19. **If split not successful**:
    - Delete split directory: `rm -rf document_split/`
    - Analyze why it failed (filenames unclear? wrong granularity?)
    - Try different heading level or custom pattern
    - Test with `--dry-run` again
    - Repeat until split meets success criteria

### Phase 4: Final Verification

20. **Check samples one last time**: Ensure quality is good
21. **Review file structure**: Organized and understandable?
22. **Deliver results**: Provide clean markdown to user

### Error Handling and Recovery

- **Conversion fails**: Check PDF quality, try with OCR enabled
- **Cleanup removes content**: Review samples first, test with --dry-run, adjust regexps
  - **Recovery**: `cp document.md.backup document.md` and try again
- **Regexps don't match**: Check actual patterns in samples, refine expressions
  - Use `--dry-run` to test before applying
- **Split produces unclear filenames**: Try different heading level or custom pattern
  - Delete bad split: `rm -rf document_split/`
  - Re-analyze and try different strategy
- **Split creates wrong granularity**: 
  - Too many files? Use higher heading level (H2 instead of H3)
  - Too few files? Use lower heading level (H3 instead of H2)
  - Delete and retry with adjusted settings

### Best Practices

- **Always backup**: Substitution script auto-creates `.backup` file before changes
- **Review samples first**: Don't assume - check what's actually in the document
- **Test with dry-run**: Preview changes before applying
- **One issue at a time**: Fix page numbers, then headers, then headings - verify each
  - **Small iterations beat big failures**
- **Document-specific patterns**: Each PDF is different - create custom regexps for each
- **Verify after each change**: Extract samples again to confirm success
- **Restore on failure**: Use backup files to recover, don't continue with broken state
- **Review split results**: Check filenames and content before accepting split
- **Iterate until right**: If split doesn't meet criteria, delete and try different approach
- **Learn and adjust**: If a pattern doesn't work, understand why and adjust

## Script Reference

### Conversion Scripts

#### convert_full.py
```
Usage: convert_full.py <pdf_path> [-o OUTPUT] [--no-ocr]

Arguments:
  pdf_path              Path to input PDF file or URL
  -o, --output OUTPUT   Output markdown file (default: <pdf_name>.md)
  --no-ocr              Disable OCR for faster processing (recommended)
```

#### setup_venv.sh
```
Usage: bash setup_venv.sh

Creates virtual environment at scripts/.venv and installs docling.
```

### Cleanup Scripts

#### extract_samples.py
```
Usage: extract_samples.py <markdown_file> [--lines LINES] [--min-repeats N]

Extracts representative samples from the document for agent review.
Output:
  - First N lines (start of document)
  - Middle section sample
  - Last N lines (end of document)
  - All unique heading patterns
  - Lines that appear N+ times (potential noise)
  
Arguments:
  markdown_file         Input markdown file
  --lines LINES         Lines per sample section (default: 50)
  --min-repeats N       Minimum repeats to show pattern (default: 3)
```

#### apply_substitutions.py
```
Usage: apply_substitutions.py <markdown_file> -s PATTERN [-s PATTERN ...] [--dry-run]

Applies sed-style regexp substitutions to markdown file.
Creates automatic backup before any changes.

Arguments:
  markdown_file                Input markdown file
  -s, --substitute PATTERN     Sed-style pattern: 's/search/replace/flags'
                               Can be specified multiple times
  --backup FILE                Backup filename (default: <file>.backup)
  --dry-run                    Show changes without applying
  -o, --output FILE            Output file (default: overwrites input)

Examples:
  # Fix heading depth: ## 1.2.3 → ### 1.2.3
  -s 's/^## (\d+\.\d+\.\d+)/### \1/g'
  
  # Remove page numbers
  -s 's/^Page \d+$//g'
  
  # Remove copyright lines
  -s 's/^© 20\d{2}.*$//g'
  
  # Multiple substitutions (apply one at a time for safety!)
  -s 's/pattern1/replace1/g'
```

### Splitting Scripts

#### analyze_split_points.py
```
Usage: analyze_split_points.py <markdown_file>

Analyzes document structure and proposes split strategies.
Output: 
  - Available heading levels
  - Sample sections from document
  - Suggested split strategies with examples
```

#### split_markdown.py
```
Usage: split_markdown.py <markdown_file> [-o OUTPUT_DIR] [OPTIONS]

Arguments:
  markdown_file                 Input markdown file
  -o, --output-dir DIR          Output directory (default: <name>_split/)
  --heading-level LEVEL         Split on heading level: 1, 2, 3, etc.
  --pattern REGEX               Custom regex pattern for split points
  --extract-title REGEX         Regex to extract title from delimiter line
  --dry-run                     Show split plan without creating files
```

## Implementation Notes

The skill uses a flexible, agent-driven approach where agents review actual document content and create custom cleanup rules for each PDF through iterative check-correct-verify cycles. This handles the unique formatting issues in different documents better than hardcoded patterns.

All scripts support `--help` for detailed usage information.
