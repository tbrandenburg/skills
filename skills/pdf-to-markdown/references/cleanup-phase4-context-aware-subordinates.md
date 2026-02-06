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

1. **Analyze**: Run `python scripts/extract_samples.py document.md`
   - Look for ## Table, ## Figure patterns that interrupt flow
   - Check for list items that became headings: ## Input, ## Output
   - Use content-aware detection to find subordinate patterns
   - **IMPORTANT**: Note the actual patterns in YOUR document - don't assume standard formats!

2. **Plan**: Find recurring non-numbered H2 headings (likely subordinates)
   ```bash
   # These are EXAMPLES - adapt based on step 1 analysis:
   # Find H2 headings that appear 3+ times (excluding numbered sections)
   SUBORDINATES=$(grep "^##\s\+[^0-9]" document.md | sort | uniq -c | awk '$1 >= 3 {print $2}' | cut -d' ' -f2- | paste -sd '|')
   echo "Found recurring subordinates: $SUBORDINATES"
   ```
3. **Test**: Preview the subordinate conversion
   ```bash
   # These are EXAMPLES - adapt based on step 2 plan:
   # Test the pattern conversion (shows changes without modifying file)
   sed "s/^##\s\+\($SUBORDINATES\)\$/### \1/g" document.md | grep -C2 "^### " | head -20
   ```
4. **Apply**: Convert recurring subordinates to H3
   ```bash
   # Use YOUR patterns from step 3, not these generic examples:
   # Apply the conversion (creates backup automatically)
   sed -i.backup "s/^##\s\+\($SUBORDINATES\)\$/### \1/g" document.md
   echo "Converted to subordinates: $SUBORDINATES"
   ```
5. **Verify**: Run `python scripts/extract_samples.py document.md`
   - Confirm recurring headings now appear as ### instead of ##
   - Check that numbered sections (## 4.1, ## 4.2) remain as H2  
   - Ensure document hierarchy flows logically
   - **Verify YOUR specific subordinates were converted correctly**

6. **Iterate**: Repeat steps 1-5 until no more wrong subordinates found

## ⚠️ **CRITICAL Generic Principles**
1. **Always analyze first** - never assume document structure
2. **Use frequency analysis** - subordinates repeat across documents  
3. **Preserve main structure** - protect numbered sections, annexes
4. **Validate changes** - test patterns before applying
5. **Context matters** - same heading might be main vs subordinate depending on position

**Result**: The improved Phase 4 now automatically adapts to ANY document type by discovering its unique subordinate heading patterns, following AGENTS.md principles of being generic and content-aware rather than example-specific.
