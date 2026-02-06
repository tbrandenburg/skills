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
   - Find generic single words as headings: pattern `^## [A-Z][a-z]*[^:]{0,20}$`
   - Check for list items that became headings: ## Input, ## Output
   - **IMPORTANT**: Note the actual patterns in YOUR document - don't assume standard formats!

2. **Plan**: Use multiple detection strategies for comprehensive coverage
   ```bash
   # Strategy A: Single words (original pattern) - catches short subordinate terms
   grep "^## [A-Z][a-z]*[^:]\{0,20\}$" document.md
   
   # Strategy B: Multi-word phrases - catches longer subordinate headings  
   grep "^## [A-Z][a-z ]* [a-z]" document.md
   
   # Strategy C: Context-based - headings appearing after known structural elements
   grep -A1 "^#### Process ID$\|^#### Process attribute ID$" document.md | grep "^##"
   
   # Strategy D: Length-based - very short headings are often subordinate
   grep "^## [A-Z][A-Za-z ]\{1,40\}$" document.md
   
   # Strategy E: Pattern exclusion - everything except known good patterns
   grep "^## [^0-9]" document.md | grep -v "^## [0-9]\+\.\|^## [A-Z][A-Z]\|^## Annex"
   ```
   **Use multiple strategies to ensure comprehensive detection!**
3. **Test**: Preview changes with multiple strategies
   ```bash
   # Test A: Single words  
   sed 's/^## ([A-Z][a-z]*[^:]{0,20})$/#### \1/' document.md | grep -C2 "####"
   
   # Test B: Multi-word subordinates
   sed 's/^## ([A-Z][a-z ]* [a-z][a-zA-Z ]*[a-z])$/#### \1/' document.md | grep -C2 "####"
   
   # Test C: Comprehensive subordinate pattern (broader catch)
   sed 's/^## ([A-Z][A-Za-z ]{1,50}[^0-9:])$/#### \1/' document.md | grep -C2 "####" | head -20
   
   # Test D: Safe exclusion approach - convert everything except known good patterns
   sed '/^## [0-9]\+\.\|^## [A-Z][A-Z]\|^## Annex/!s/^## ([^0-9].*)/#### \1/' document.md | head -30
   ```
   **Try multiple approaches - use the one that catches your specific subordinates best!**

4. **Apply**: Use the most effective strategy from testing
   ```bash
   # Approach 1: Multi-strategy sequential application
   sed -i.backup 's/^## ([A-Z][a-z]*[^:]{0,20})$/#### \1/' document.md          # Single words
   sed -i.backup 's/^## ([A-Z][a-z ]* [a-z][a-zA-Z ]*[a-z])$/#### \1/' document.md # Multi-words
   
   # Approach 2: Comprehensive single pattern (recommended for most cases)
   sed -i.backup 's/^## ([A-Z][A-Za-z ]{1,50}[^0-9:])$/#### \1/' document.md
   
   # Approach 3: Safe exclusion (most aggressive - use carefully)
   sed -i.backup '/^## [0-9]\+\.\|^## [A-Z][A-Z]\|^## Annex/!s/^## ([^0-9].*)/#### \1/' document.md
   ```
   **Choose the approach that worked best in your testing phase!**

5. **Verify**: Run `python scripts/extract_samples.py document.md`
   - Confirm tables/figures now at #### level
   - Check generic single words converted to bold text
   - Ensure document hierarchy flows logically
   - **Verify YOUR specific patterns worked correctly**

6. **Iterate**: Repeat steps 1-5 for other patterns you discovered (## Note, ## Example, etc.)

## Appendix

**Pattern Templates (adapt to your document):**
- Single words: `s/^## ([A-Z][a-z]*[^:]{0,20})$/#### \1/` 
- Multi-word phrases: `s/^## ([A-Z][a-z ]* [a-z][a-zA-Z ]*[a-z])$/#### \1/`
- Comprehensive: `s/^## ([A-Z][A-Za-z ]{1,50}[^0-9:])$/#### \1/` (catches both)
- Safe exclusion: `/^## [0-9]\+\.\|^## [A-Z][A-Z]\|^## Annex/!s/^## ([^0-9].*)/#### \1/`
- Tables: `s/^## (Table [A-Z0-9.].*)/#### \1/` 
- Figures: `s/^## (Figure [A-Z0-9.].*)/#### \1/` 

**New Generic Strategies:**
- **Length-based**: `s/^## ([A-Z][A-Za-z ]{1,40}[a-z])$/#### \1/` (short headings likely subordinate)
- **Context-aware**: Apply different patterns based on what precedes the heading
- **Negative matching**: Fix everything except known good patterns

⚠️ **CRITICAL**: These are TEMPLATES. Always analyze your document first (step 1) and modify patterns to match what you actually find!

**Multi-word subordinate examples that the original pattern missed:**
- "Process innovation process attribute" - needs multi-word pattern
- "Configuration Management System" - needs phrase detection  
- "Work product management process attribute" - needs longer phrase support
- "Generic practices implementation" - needs context-aware detection

**Recommended Generic Approach:**
1. **Start conservative**: Use single-word pattern first 
2. **Expand gradually**: Add multi-word pattern for remaining issues
3. **Use exclusion lists**: Protect known good headings (numbered sections, annexes, etc.)
4. **Manual verification**: Always check results - some headings may legitimately be main-level

**Example adaptations (based on actual document analysis):**
- ISO documents: `s/^## (NOTE [0-9]*.*)/#### \1/`, `s/^## (EXAMPLE [0-9]*.*)/#### \1/`
- Technical manuals: `s/^## (Input|Output|Result)$/**\1:**/'`
- Academic papers: `s/^## ([a-z]\))/\*\*\1\*\*/'`
- Complex tables: `s/^## (Table [A-Z0-9.]*\s*\(continued\))/#### \1/` (for "(continued)" tables)

**Remember**: Run `extract_samples.py` first, see what YOUR document actually contains, then build patterns that match!
