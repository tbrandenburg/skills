# Workflow Guide - Detailed Implementation

This guide provides step-by-step implementation details for the PDF to markdown conversion workflow.

## Phase 1: Initial Conversion

1. **Get PDF source**: File path or URL
2. **Setup environment**: Run `setup_venv.sh` if docling not installed  
3. **Convert to markdown**: Use `convert_full.py` with `--no-ocr` for best performance
4. **Verify output**: Check that markdown file was created

## Phase 2: Document Analysis & Planning

5. **Extract samples & analyze structure**: Run `extract_samples.py` to analyze document
   - Auto-detects structure type: HIERARCHICAL, STRUCTURED, STANDARD, or SIMPLE
   - Analyzes heading distribution and content density
   - Provides tailored recommendations based on document characteristics
   - Use output to plan cleanup phases

## Phase 3: Iterative Review and Cleanup

**Work in small, verifiable iterations:**

6. **Follow recommended phases**: Use the specific recommendations from extract_samples.py
7. **Review samples**: Agent examines samples for **ONE type of issue** at a time:
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

12. **Follow the 4-phase cleanup approach** in order:
    - Phase 1: Document Denoising
    - Phase 2: Headers/Footers  
    - Phase 3: Heading Structure
    - Phase 4: Spacing/Formatting
    
    Each phase: **dry-run → apply → verify** - small, safe iterations

## Phase 3: Optional Splitting (with Review)

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

## Phase 4: Final Verification

20. **Check samples one last time**: Ensure quality is good
21. **Review file structure**: Organized and understandable?
22. **Deliver results**: Provide clean markdown to user

## Error Handling and Recovery

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

## Best Practices

- **Always backup**: Substitution script auto-creates `.backup` file before changes
- **Review samples first**: Don't assume - check what's actually in the document
- **Test with dry-run**: Preview changes before applying
- **One issue at a time**: Fix page numbers, then headers, then headings - verify each
- **Document-specific patterns**: Each PDF is different - create custom regexps for each
- **Verify after each change**: Extract samples again to confirm success
### Document Splitting (Optional)

**Smart splitting based on document structure and content:**

```bash
# Use recommended parameters from extract_samples.py analysis
python scripts/split_markdown.py document.md --heading-level <suggested> --min-content <suggested>

# Common patterns:
# Hierarchical documents: level 3, min-content 4
# Structured documents: level 2, min-content 6  
# Standard documents: level 2, min-content 4
# Simple documents: level 2, min-content 5
```

**Splitting features:**
- **Content filtering**: Sections with < min-content lines are merged into previous sections
- **Smart merging**: Prevents trivial header-only files (like "## Part 6:")
- **Adaptive strategy**: Different heading levels work better for different document types

**When to split:**
- Large documents (>1000 lines) benefit from organization
- Multi-chapter/section documents work well split by major divisions
- Skip splitting for small/simple documents

## Quality Control

### Review Split Results

- **Restore on failure**: Use backup files to recover, don't continue with broken state
- **Review split results**: Check filenames and content before accepting split
- **Iterate until right**: If split doesn't meet criteria, delete and try different approach
- **Learn and adjust**: If a pattern doesn't work, understand why and adjust

## Advanced Integration

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

## Implementation Philosophy

The skill uses a flexible, agent-driven approach where agents review actual document content and create custom cleanup rules for each PDF through iterative check-correct-verify cycles. This handles the unique formatting issues in different documents better than hardcoded patterns.

**Why Iterative?**
- Small changes are safer than large ones
- Easy to verify each step worked correctly  
- Simple to recover if something goes wrong
- Agent can learn and adjust approach as they go
- **Document structure analysis**: Scripts detect patterns but require agent review to determine what's actually wrong (e.g., "## 3.1.1" looks like valid markdown, but semantically it should be "### 3.1.1" based on the numbering hierarchy)
- **Context-dependent fixes**: Each PDF has unique issues that require human judgment to identify and prioritize