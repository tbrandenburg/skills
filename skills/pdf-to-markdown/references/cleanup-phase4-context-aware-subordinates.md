# Phase 4: Context-Aware Subordinates

## Goal
Fix complex hierarchical problems where content appears as peer-level headings when it should be subordinate. Examples: Table titles, Figure captions, and list items that became headings during PDF conversion.

## Bad Examples

**Tables as same-level headings:**
```markdown
## 6.2 ASIL determination

## Table 6-1: Severity classification

## 6.3 Safety goals
```

**Figures interrupting hierarchy:**
```markdown
### 6.1 Overview

## Figure 6-1: ASIL determination process

### 6.2 Process details
```

**Method names as headings:**
```markdown
## 7 Work products

## Method

## Verification

## 7.1 Documentation
```

## Good Examples

**Tables as subordinate content:**
```markdown
## 6.2 ASIL determination

#### Table 6-1: Severity classification

## 6.3 Safety goals
```

**Figures properly nested:**
```markdown
### 6.1 Overview

#### Figure 6-1: ASIL determination process

### 6.2 Process details
```

**Content items not as headings:**
```markdown
## 7 Work products

**Method:**
Requirements analysis...

**Verification:**
Review of documentation...

## 7.1 Documentation
```

## Workflow

1. **Detect**: Run `python scripts/extract_samples.py document.md`
   - Look for ## Table, ## Figure patterns that interrupt flow
   - Find generic single words as headings: pattern `^## [A-Z][a-z]*[^:]{0,20}$`
   - Check for list items that became headings: ## Input, ## Output
   - **IMPORTANT**: Note the actual patterns in YOUR document - don't assume standard formats!

2. **Analyze**: Based on step 1 findings, create document-specific patterns
   ```bash
   # Example: If you found "Table A.1 (continued)", "Table 5-2", "Figure E.1"
   # Create patterns that match YOUR document's actual format:
   python scripts/apply_substitutions.py document.md -s 's/^## (Table [A-Z0-9.-]*.*)/#### \1/' --dry-run
   ```
   **Don't copy-paste generic examples - adapt to what you actually found!**
3. **Test**: Apply YOUR document-specific patterns with `--dry-run`
   ```bash
   # These are EXAMPLES - adapt based on step 1 findings:
   python scripts/apply_substitutions.py document.md -s 's/^## (Table [A-Z0-9.].*)/#### \1/' --dry-run  
   python scripts/apply_substitutions.py document.md -s 's/^## (Figure [A-Z0-9.].*)/#### \1/' --dry-run
   python scripts/apply_substitutions.py document.md -s 's/^## ([A-Z][a-z]*[^:]{0,20})$/\*\*\1:\*\*/' --dry-run
   ```

4. **Apply**: Remove `--dry-run` flag (only if step 3 results look correct)
   ```bash
   # Use YOUR patterns from step 3, not these generic examples:
   python scripts/apply_substitutions.py document.md -s 's/^## (Table [A-Z0-9.].*)/#### \1/'
   python scripts/apply_substitutions.py document.md -s 's/^## (Figure [A-Z0-9.].*)/#### \1/'  
   python scripts/apply_substitutions.py document.md -s 's/^## ([A-Z][a-z]*[^:]{0,20})$/\*\*\1:\*\*/'
   ```

5. **Verify**: Run `python scripts/extract_samples.py document.md`
   - Confirm tables/figures now at #### level
   - Check generic single words converted to bold text
   - Ensure document hierarchy flows logically
   - **Verify YOUR specific patterns worked correctly**

6. **Iterate**: Repeat steps 1-5 for other patterns you discovered (## Note, ## Example, etc.)

## Appendix

**Pattern Templates (adapt to your document):**
- Tables: `s/^## (Table [A-Z0-9.].*)/#### \1/` (matches "Table 5", "Table A.1 (continued)", "Table E.2 - Example")
- Figures: `s/^## (Figure [A-Z0-9.].*)/#### \1/` (matches "Figure 6-1", "Figure A.1: Overview")
- Generic terms: `s/^## ([A-Z][a-z]*[^:]{0,20})$/\*\*\1:\*\*/'` (single words like "Method", "Input")

⚠️ **CRITICAL**: These are TEMPLATES. Always analyze your document first (step 1) and modify patterns to match what you actually find!

**Example adaptations (based on actual document analysis):**
- ISO documents: `s/^## (NOTE [0-9]*.*)/#### \1/`, `s/^## (EXAMPLE [0-9]*.*)/#### \1/`
- Technical manuals: `s/^## (Input|Output|Result)$/\*\*\1:\*\*/'`
- Academic papers: `s/^## ([a-z]\))/\*\*\1\*\*/'`
- Complex tables: `s/^## (Table [A-Z0-9.]*\s*\(continued\))/#### \1/` (for "(continued)" tables)

**Remember**: Run `extract_samples.py` first, see what YOUR document actually contains, then build patterns that match!
