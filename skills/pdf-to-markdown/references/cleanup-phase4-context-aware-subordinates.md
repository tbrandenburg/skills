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
   - **CRITICAL**: Use BROADER detection to catch ALL non-numbered headings:
     ```bash
     # This is an example -> adapt it based on extracted samples!
     grep "^##\s\+[A-Za-z]" document.md | sort | uniq -c | sort -nr
     ```
   - Look for systematic patterns even if infrequent: ## PA X.X, ## Rating method RX
   - **IMPORTANT**: Note the actual patterns in YOUR document - don't assume standard formats!

2. **Plan**: Find ALL subordinate patterns (both frequent AND systematic)
   ```bash
   # These are EXAMPLES - adapt based on step 1 findings!
   # BROADER approach - catch ALL letter-starting headings (including those with numbers):
   # Frequent subordinates (3+ occurrences)
   FREQUENT=$(grep "^##\s\+[A-Za-z]" document.md | sort | uniq -c | awk '$1 >= 3 {print $2}' | cut -d' ' -f3- | paste -sd '|')
   
   # Systematic subordinates (even if infrequent)
   grep "^##\s\+\(Rating method\|PA [0-9]\|Process attribute\|Generic practice\)" document.md
   echo "Found frequent: $FREQUENT"
   ```
3. **Test**: Preview the subordinate conversion
   ```bash
   # These are EXAMPLES - adapt based on step 2 plan:
   # Test the pattern conversion (shows changes without modifying file)
   # 💡 DEPTH ADAPTATION: Use H4 (####) by default, H3 (###) if document has less nesting
   sed "s/^##\s\+\($SUBORDINATES\)\$/#### \1/g" document.md | grep -C2 "^#### " | head -20
   ```
4. **Apply**: Convert recurring subordinates (default: H4, adapt based on document depth)
   ```bash
   # Use YOUR patterns from step 3, not these generic examples:
   # Default to H4 (####) - adapt to H3 (###) if document typically uses less nesting
   # 💡 DEPTH HINT: Check existing subordinates in document - match their typical level
   sed -i.backup "s/^##\s\+\($SUBORDINATES\)\$/#### \1/g" document.md
   echo "Converted to subordinates: $SUBORDINATES"
   ```
5. **Verify**: Run `python scripts/extract_samples.py document.md`
   - Confirm recurring headings now appear as #### (or ###) instead of ##
   - Check that numbered sections (## 4.1, ## 4.2) remain as H2  
   - Ensure document hierarchy flows logically
   - **Verify YOUR specific subordinates were converted correctly**

6. **Iterate**: Repeat steps 1-5 until no more wrong subordinates found

## Guidelines

### ⚠️ **CRITICAL Generic Principles**
1. **Always analyze first** - never assume document structure
2. **Use BROAD detection** - `^##\s\+[A-Za-z]` not `^##\s\+[^0-9]` (misses "PA 4.2"!)
3. **Dual approach**: frequency analysis (3+) AND systematic patterns (1+)
4. **Preserve main structure** - protect numbered sections, annexes
5. **Validate changes** - test patterns before applying
6. **Context matters** - same heading might be main vs subordinate depending on position
7. **💡 ADAPT DEPTH** - Default H4 (####), use H3 (###) if document typically nests deeper

### Common Systematic Subordinate Patterns

Even if infrequent, these are usually subordinates and should be converted:

```bash
# Process/methodology documents
's/^## \(Process attribute name\)$/### \1/'
's/^## \(Rating method R[0-9]\)$/### \1/' 
's/^## \(PA [0-9]\+\.[0-9]\+\)$/### \1/'
's/^## \(Generic practice.*\)$/### \1/'

# Technical documents  
's/^## \(Table [0-9]\+\)$/### \1/'
's/^## \(Figure [0-9]\+\)$/### \1/'
's/^## \(Appendix [A-Z]\)$/### \1/'

# Academic/standards documents
's/^## \(Method\)$/### \1/'
's/^## \(Verification\)$/### \1/'
's/^## \(Requirements\)$/### \1/'
```

⚠️ **Key Lesson**: Don't rely only on frequency! Domain-specific subordinates may appear infrequently but still need conversion.