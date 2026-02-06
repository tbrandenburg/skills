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

2. **Test**: Apply patterns with `--dry-run`
   ```bash
   python scripts/apply_substitutions.py document.md -s 's/^## (Table [0-9])/#### \1/' --dry-run  
   python scripts/apply_substitutions.py document.md -s 's/^## (Figure [0-9])/#### \1/' --dry-run
   python scripts/apply_substitutions.py document.md -s 's/^## ([A-Z][a-z]*[^:]{0,20})$/\*\*\1:\*\*/' --dry-run
   ```

3. **Apply**: Remove `--dry-run` flag
   ```bash
   python scripts/apply_substitutions.py document.md -s 's/^## (Table [0-9])/#### \1/'
   python scripts/apply_substitutions.py document.md -s 's/^## (Figure [0-9])/#### \1/'  
   python scripts/apply_substitutions.py document.md -s 's/^## ([A-Z][a-z]*[^:]{0,20})$/\*\*\1:\*\*/'
   ```

4. **Verify**: Run `python scripts/extract_samples.py document.md`
   - Confirm tables/figures now at #### level
   - Check generic single words converted to bold text
   - Ensure document hierarchy flows logically

5. **Iterate**: Repeat steps 1-4 for other patterns like ## Note, ## Example

## Appendix

**Standard patterns:**
- Tables: `s/^## (Table [0-9])/#### \1/`
- Figures: `s/^## (Figure [0-9])/#### \1/`  
- Generic terms: `s/^## ([A-Z][a-z]*[^:]{0,20})$/\*\*\1:\*\*/'`

**Document-specific examples:**
- ISO: `s/^## (NOTE [0-9])/#### \1/`, `s/^## (EXAMPLE [0-9])/#### \1/`
- Technical: `s/^## (Input|Output|Result)$/\*\*\1:\*\*/'`
- Lists: `s/^## ([a-z]\))/\*\*\1\*\*/'`
