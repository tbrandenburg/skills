# Phase 5: Spacing and Formatting

## Goal
Clean up inconsistent spacing, remove excessive blank lines, and standardize formatting to create readable, well-structured markdown that follows best practices.

## Bad Examples

**Excessive blank lines:**
```markdown
## 6.1 Overview


The overview section...



### 6.1.1 Purpose


This subsection...
```

**Inconsistent heading spacing:**
```markdown
##6.2 ASIL determination
The ASIL determination...
###6.2.1 Process
Without proper spacing...
```

**Mixed formatting patterns:**
```markdown
**Input**: Data from analysis
Input: More data here
*Output*: Results
**Output**: Different formatting
```

## Good Examples

**Consistent blank line spacing:**
```markdown
## 6.1 Overview

The overview section...

### 6.1.1 Purpose

This subsection...
```

**Proper heading spacing:**
```markdown
## 6.2 ASIL determination

The ASIL determination...

### 6.2.1 Process

With proper spacing...
```

**Standardized formatting:**
```markdown
**Input:** Data from analysis
**Input:** More data here  
**Output:** Results
**Output:** Consistent formatting
```

## Workflow

1. **Detect**: Run `python scripts/extract_samples.py document.md`
   - Look for multiple consecutive blank lines (3+ empty lines)
   - Check for headings without spaces after # markers
   - Find inconsistent bold/italic patterns
   - **IMPORTANT**: Note the exact spacing/formatting issues in YOUR document!

2. **Analyze**: Based on step 1 findings, create document-specific patterns
   ```bash
   # Example: If you found headings like "##6.1" and "###6.1.1"
   # Create patterns that match YOUR document's actual spacing issues:
   python scripts/apply_substitutions.py document.md -s 's/^##([0-9])/## \1/' --dry-run
   ```
   **Don't copy-paste generic examples - adapt to what you actually found!**

3. **Test**: Apply YOUR document-specific patterns with `--dry-run`
   ```bash
   # These are EXAMPLES - adapt based on step 1 findings:
   python scripts/apply_substitutions.py document.md -s 's/\n\n\n+/\n\n/g' --dry-run
   python scripts/apply_substitutions.py document.md -s 's/^##([^ ])/## \1/' --dry-run
   python scripts/apply_substitutions.py document.md -s 's/^###([^ ])/### \1/' --dry-run
   ```

4. **Apply**: Remove `--dry-run` flag (only if step 3 results look correct)
   ```bash
   # Use YOUR patterns from step 3, not these generic examples:
   python scripts/apply_substitutions.py document.md -s 's/\n\n\n+/\n\n/g'
   python scripts/apply_substitutions.py document.md -s 's/^##([^ ])/## \1/'
   python scripts/apply_substitutions.py document.md -s 's/^###([^ ])/### \1/'
   ```

5. **Verify**: Run `python scripts/extract_samples.py document.md`
   - Confirm no excessive blank lines in samples
   - Check headings have proper spacing
   - Verify consistent formatting patterns
   - **Verify YOUR specific patterns worked correctly**

6. **Iterate**: Repeat steps 1-5 for edge cases like trailing spaces, mixed emphasis

## Appendix

**Pattern Templates (adapt to your document):**
- Excessive blanks: `s/\n\n\n+/\n\n/g`
- Heading spacing: `s/^##([^ ])/## \1/`, `s/^###([^ ])/### \1/`
- Trailing spaces: `s/[ \t]+$//g`

**Example adaptations (based on actual document analysis):**
- Bold patterns: `s/\*([^*]+)\*/\*\*\1\*\*/g`
- List spacing: `s/^([*-]) /\1 /` 
- Code blocks: `s/^```([a-z]*)/```\1/`

⚠️ **CRITICAL**: These are TEMPLATES. Always analyze your document first (step 1) and modify patterns to match what you actually find!
