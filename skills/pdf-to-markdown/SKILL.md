---
name: pdf-to-markdown
description: Convert PDF documents to markdown format using docling, with flexible agent-driven cleanup. Workflow - (1) Load PDF from file or URL, (2) Convert to markdown, (3) Agent reviews document samples and creates custom regexp substitutions in small iterations for issues like wrong heading depths, headers/footers, page numbers, boilerplate (4) Optionally split with agent-proposed delimiters, reviewing filenames and structure. Each PDF is unique - agents adapt cleanup to actual document content through iterative check-correct-verify cycles, not hardcoded rules. IMPORTANT - Use --no-ocr flag for faster processing.
---

# PDF to Markdown Converter

Convert PDF documents to markdown using docling with intelligent cleanup and splitting.

## Mandatory Workflow

You **must follow** the steps below **in order**.
Use your TODO tool to complete each step including it's sub-tasks thouroughly and consecutively before proceeding with the next step.

### Step 1: Environment Setup (One-time)
```bash
bash scripts/setup_venv.sh
```

### Step 2: PDF Conversion
Convert your PDF to initial markdown (use `--no-ocr` for faster processing):

```bash
# Local file:
python scripts/convert_full.py document.pdf --no-ocr

# Or from URL (docling downloads automatically):
python scripts/convert_full.py https://example.com/document.pdf --no-ocr
```

### Step 3: Follow the 5-Phase Cleanup Process

**🚨 CRITICAL**: Work through **all 5 phases sequentially**. Each phase builds on the previous one:

1. **Phase 1: Document Denoising** → [cleanup-phase1-denoising.md](references/cleanup-phase1-denoising.md)
2. **Phase 2: Headers/Footers** → [cleanup-phase2-headers-footers.md](references/cleanup-phase2-headers-footers.md)  
3. **Phase 3: Basic Numbered Sections** → [cleanup-phase3-basic-numbered-sections.md](references/cleanup-phase3-basic-numbered-sections.md)
4. **Phase 4: Context-Aware Subordinates** → [cleanup-phase4-context-aware-subordinates.md](references/cleanup-phase4-context-aware-subordinates.md)
5. **Phase 5: Spacing/Formatting** → [cleanup-phase5-spacing-formatting.md](references/cleanup-phase5-spacing-formatting.md)

**For each phase**: Follow the iterative process described in the phase-specific documentation.

### Step 4: Consider Document Splitting
After completing all 5 phases, evaluate if splitting would improve usability:

```bash
# Analyze potential split points
python scripts/analyze_split_points.py document.md

# Test splitting (if desired)
python scripts/split_markdown.py document.md --heading-level 2 --dry-run

# Apply splitting (if satisfied with test results)
python scripts/split_markdown.py document.md --heading-level 2
```

## Key Cleanup Principles

**Work iteratively within each phase**: **dry-run → apply → verify**

- **Small iterations**: Fix 1-2 issues per iteration, not everything at once
- **Always verify**: Extract samples after EACH change to confirm it worked  
- **Test first**: ALWAYS use `--dry-run` before applying substitutions
- **Document-specific patterns**: Each PDF is unique - adapt to actual content
- **Safe recovery**: Automatic backup files created for each change

### Essential Commands for Each Phase

```bash
# Review document structure and patterns
python scripts/extract_samples.py document.md

# Test a substitution pattern  
sed 's/pattern/replacement/' document.md | head -20  # Preview changes

# Apply the pattern (creates automatic backup)
sed -i.backup 's/pattern/replacement/' document.md

# Verify the change worked as expected
python scripts/extract_samples.py document.md
```

**⚠️ Phase 4 Mandatory Check**: After completing Phase 3, always run this detection:
```bash
grep "^## Table\|^## Figure\|^## [a-z])\|^## [A-Z][a-z]*[^:]\{0,20\}$" document.md
```

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

### extract_samples.py  
```bash
python scripts/extract_samples.py <markdown_file> [--min-repeats N]
```
Shows document structure and repeated patterns for cleanup planning.

## Cleanup with Native Sed

Use native `sed` for regex substitutions (faster and more reliable than Python wrappers):

**Preview changes:**
```bash
sed 's/old/new/g' document.md | head -20  # See first 20 lines of output
```

**Apply changes (with automatic backup):**  
```bash
sed -i.backup 's/old/new/g' document.md
```

**Pattern Development Strategy:**
1. Use `extract_samples.py` to identify issues
2. Develop patterns specific to your document  
3. Test with preview (`sed 's/pattern/replacement/' file`)
4. Apply with backup (`sed -i.backup 's/pattern/replacement/' file`)
5. Verify with `extract_samples.py`

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