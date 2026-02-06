---
name: pdf-to-markdown
description: Convert PDF documents to markdown format using docling, with flexible agent-driven cleanup. Workflow - (1) Load PDF from file or URL, (2) Convert to markdown, (3) Agent reviews document samples and creates custom regexp substitutions in small iterations for issues like wrong heading depths, headers/footers, page numbers, boilerplate (4) Optionally split with agent-proposed delimiters, reviewing filenames and structure. Each PDF is unique - agents adapt cleanup to actual document content through iterative check-correct-verify cycles, not hardcoded rules. IMPORTANT - Use --no-ocr flag for faster processing.
---

# PDF to Markdown Converter

Convert PDF documents to markdown using docling with intelligent cleanup and splitting.

## Quick Start

```bash
# 1. Setup (one-time)
bash scripts/setup_venv.sh

# 2. Convert PDF (fast mode recommended)
# Local file:
python scripts/convert_full.py document.pdf --no-ocr
# Or URL (docling downloads automatically):
python scripts/convert_full.py https://example.com/document.pdf --no-ocr

# 3. Iterative cleanup - fix ONE issue at a time:
python scripts/extract_samples.py document.md                    # Review
python scripts/apply_substitutions.py document.md -s 'pattern' --dry-run  # Test  
python scripts/apply_substitutions.py document.md -s 'pattern'             # Apply
python scripts/extract_samples.py document.md                    # Verify

# 3b. MANDATORY: Check for subordinate elements after Phase 3
grep "^## Table\|^## Figure\|^## [a-z])\|^## [A-Z][a-z]*[^:]\{0,20\}$" document.md           # Detect Phase 4 issues

# 4. Optional splitting
python scripts/analyze_split_points.py document.md               # Analyze
python scripts/split_markdown.py document.md --heading-level 2 --dry-run   # Test
python scripts/split_markdown.py document.md --heading-level 2             # Apply
```

## 5-Phase Cleanup Approach

**Work iteratively**: **dry-run → apply → verify** each phase:

1. **Document Denoising** → [cleanup-phase1-denoising.md](references/cleanup-phase1-denoising.md)  
   Remove image placeholders, boilerplate, conversion artifacts

2. **Headers/Footers** → [cleanup-phase2-headers-footers.md](references/cleanup-phase2-headers-footers.md)  
   Remove page numbers, copyright footers, repeated organizational content

3. **Basic Numbered Sections** → [cleanup-phase3-basic-numbered-sections.md](references/cleanup-phase3-basic-numbered-sections.md)  
   Analyze numbering patterns and fix heading depths to match logical document hierarchy

4. **⚠️ Context-Aware Subordinates** → [cleanup-phase4-context-aware-subordinates.md](references/cleanup-phase4-context-aware-subordinates.md)  
   **MANDATORY CHECK**: Fix tables, figures, list items incorrectly promoted to H2 headings
   ```bash
   # Always run these detection commands after Phase 3:
   grep "^## Table\|^## Figure\|^## [a-z])\|^## [A-Z][a-z]*[^:]\{0,20\}$" document.md
   ```

5. **Spacing/Formatting** → [cleanup-phase5-spacing-formatting.md](references/cleanup-phase5-spacing-formatting.md)  
   Clean up excessive blank lines, list formatting, table issues

## Critical Principles

- **Small iterations**: Fix 1-2 issues per iteration, not everything at once
- **Always verify**: Extract samples after EACH change to confirm it worked  
- **Test first**: ALWAYS use `--dry-run` before applying
- **Document-specific patterns**: Each PDF is unique - adapt to actual content
- **Safe recovery**: Use backup files if something goes wrong

## Performance Notes

⚠️ **Use `--no-ocr` flag** unless processing scanned documents:

- **Without OCR**: 5-10 minutes for 180-page PDF ✅
- **With OCR**: 60+ minutes for same PDF ❌  

See [performance-guide.md](references/performance-guide.md) for optimization details.

## Core Scripts

### convert_full.py
```bash
python scripts/convert_full.py <pdf_source> [--no-ocr] [-o output.md]
```
Supports both local files and URLs. Examples:
```bash
python scripts/convert_full.py document.pdf --no-ocr
python scripts/convert_full.py https://example.com/doc.pdf --no-ocr  
python scripts/convert_full.py https://example.com/doc.pdf -o custom.md --no-ocr
```

### extract_samples.py  
```bash
python scripts/extract_samples.py <markdown_file> [--min-repeats N]
```
Shows document structure and repeated patterns for cleanup planning.

### apply_substitutions.py
```bash
python scripts/apply_substitutions.py <markdown_file> -s 'pattern' [--dry-run]
```
Applies sed-style regex substitutions with automatic backup.

**Always use `--dry-run` first** to test patterns before applying.

Example usage:
```bash
# Test a pattern first
python scripts/apply_substitutions.py document.md -s 's/old/new/g' --dry-run

# Apply if satisfied with dry-run results
python scripts/apply_substitutions.py document.md -s 's/old/new/g'
```

**Pattern Development Strategy:**
1. Use `extract_samples.py` to identify issues
2. Develop patterns specific to your document
3. Test with `--dry-run` 
4. Apply and verify with `extract_samples.py`

See phase-specific documentation for detailed patterns and examples.

### analyze_split_points.py / split_markdown.py
```bash
python scripts/analyze_split_points.py <markdown_file>
python scripts/split_markdown.py <markdown_file> --heading-level 2 [--dry-run]
```

## Detailed Guides

- **Advanced Usage** → [docling-usage.md](references/docling-usage.md)
- **Performance Optimization** → [performance-guide.md](references/performance-guide.md)  
- **Workflow Details** → [workflow-guide.md](references/workflow-guide.md)
- **Script Reference** → [script-reference.md](references/script-reference.md)