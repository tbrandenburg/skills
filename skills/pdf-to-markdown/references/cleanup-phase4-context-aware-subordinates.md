# Phase 4: Context-Aware Subordinate Elements

This phase fixes subordinate elements (tables, figures, list items) that were incorrectly promoted to major section headings. **Critical step that's often overlooked but essential for proper document hierarchy.**

## ⚠️ MANDATORY DETECTION STEP

**Before moving to Phase 5, ALWAYS check for these subordinate elements:**

```bash
# REQUIRED: Check for tables promoted to H2 (should be H4)
grep -n "^## Table" document.md

# REQUIRED: Check for figures promoted to H2 (should be H4)  
grep -n "^## Figure" document.md

# REQUIRED: Check for orphaned list items (should be content)
grep -n "^## [a-z])" document.md

# REQUIRED: Check for generic subordinate elements (should be H4)
grep -n "^## \(Method\|Procedure\|Protocol\|Standard\|Requirement\|Recommendation\|Example\|Note\)" document.md

# REQUIRED: Check for any single-word H2 that might be subordinate
grep -n "^## [A-Z][a-z]*[^:]\{0,20\}$" document.md

# If ANY of these return results, Phase 4 is REQUIRED
```

## Core Principle

**Tables, figures, and list items should be subordinate to their parent sections, not standalone major headings.**

The goal is to identify and fix elements that were incorrectly promoted during PDF conversion.

## Analysis Strategy

### Step 1: Understand Your Document's Structure
```bash
python scripts/analyze_split_points.py document.md
```

### Step 2: Examine Heading Patterns
```bash
# See all current headings with their patterns
grep -n "^##[#]* " document.md | head -50

# Focus on numbered/structured headings  
grep -n "^##[#]* [0-9A-Za-z]" document.md
```

### Step 3: Identify Logical Hierarchy
Look for these patterns in your document:
- **Numbering depth**: How many levels does the numbering go? (1.1.1 vs 1.1.1.1.1.1)
- **Numbering schemes**: Decimal (1.1.1), Roman (I.A.1), Mixed (1.a.i), Letters (A.1.a)
- **Content relationships**: Which sections are conceptually under others?
- **Consistency patterns**: Are similar content types at similar heading levels?

## Common Heading Structure Problems

### 1. Depth Mismatch
**Problem**: All numbered sections are H2 regardless of their actual depth
```
## 1. Introduction           ← Correct (level 2)
## 1.1 Overview              ← Wrong - should be H3  
## 1.1.1 Purpose            ← Wrong - should be H4
## 1.1.1.1 Scope            ← Wrong - should be H5
```

### 2. Inconsistent Hierarchy  
**Problem**: Similar content at different heading levels
```
## 2. Requirements          ← Level 2
### 2.1 Functional          ← Level 3  
## 2.1.1 User Interface      ← Wrong - should be H4
### 2.2 Non-Functional       ← Level 3
#### 2.2.1 Performance      ← Correct (level 4)
```

### 3. Missing Levels
**Problem**: Jumping from H2 directly to H4
```
## 3. Design               ← Level 2
#### 3.1 Architecture      ← Wrong - missing H3 level
```

### 4. Over-Deep Structures
**Problem**: Too many heading levels for the content complexity
```
########## 1.2.3.4.5.6.7.8.9 Detail   ← Probably too deep
```

## Pattern Development Strategy

### Step 1: Count Numbering Depth
Determine the maximum logical depth in your document:
```bash
# Look for deepest numbering patterns
grep -o "^## [0-9]" document.md | head -20        # 1-level: "## 1"  
grep -o "^## [0-9]\+\.[0-9]" document.md | head -20      # 2-level: "## 1.1"
grep -o "^## [0-9]\+\.[0-9]\+\.[0-9]" document.md | head -20   # 3-level: "## 1.1.1"
# Continue for deeper levels...
```

### Step 2: Create Depth-Based Patterns

**For decimal numbering (most common):**
```bash
# Template patterns - customize the numbering part for your document:

# 2-level (1.1) → should be H3
's/^## (\\d+\\.\\d+)\\.?/### \\1/g'

# 3-level (1.1.1) → should be H4  
's/^## (\\d+\\.\\d+\\.\\d+)\\.?/#### \\1/g'

# 4-level (1.1.1.1) → should be H5
's/^## (\\d+\\.\\d+\\.\\d+\\.\\d+)\\.?/##### \\1/g'

# 5-level (1.1.1.1.1) → should be H6
's/^## (\\d+\\.\\d+\\.\\d+\\.\\d+\\.\\d+)\\.?/###### \\1/g'
```

### Step 3: Handle Alternative Numbering Schemes

**Roman numerals:**
```bash
# I.A.1 style
's/^## ([IVX]+\\.[A-Z]\\.[0-9]+)/#### \\1/g'

# I.1.a style  
's/^## ([IVX]+\\.[0-9]+\\.[a-z]+)/#### \\1/g'
```

**Letter-based:**
```bash  
# A.1.a style
's/^## ([A-Z]\\.[0-9]+\\.[a-z]+)/#### \\1/g'

# Appendix patterns
's/^## (Appendix [A-Z])/## \\1/g'      # Keep appendices as H2
's/^## (Annex [A-Z])/## \\1/g'         # Keep annexes as H2
```

**Mixed schemes:**
```bash
# Analyze your specific patterns first:
grep -o "^## [^#]\\+" document.md | sort | uniq -c | sort -nr

# Then create patterns based on what you find
```

## Implementation Approach

### 1. Start with Analysis
```bash
# Don't jump straight to regex - understand first
python scripts/extract_samples.py document.md
python scripts/analyze_split_points.py document.md

# Count occurrences of different patterns
grep "^## [0-9]" document.md | wc -l           # How many numbered H2s?
grep "^### [0-9]" document.md | wc -l          # How many numbered H3s?
```

### 2. Develop Custom Patterns
Based on your analysis, create patterns specific to your document:

```bash
# Example workflow (adapt to your findings):

# If you find: Many "## 1.1.1" that should be "### 1.1.1"
python scripts/apply_substitutions.py document.md \
  -s 's/^## ([0-9]+\\.[0-9]+\\.[0-9]+)/### \\1/g' \
  --dry-run

# If you find: Deep numbering like "## 1.1.1.1.1" 
python scripts/apply_substitutions.py document.md \
  -s 's/^## ([0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+)/###### \\1/g' \
  --dry-run
```

### 3. Work Incrementally
```bash
# Fix one depth level at a time:
# 1st: Fix deepest levels (5-level → H6)
# 2nd: Fix 4-level → H5  
# 3rd: Fix 3-level → H4
# 4th: Fix 2-level → H3
# This prevents conflicts between overlapping patterns
```

## Verification Methods

### 1. Structure Analysis
```bash
# Compare before/after heading distribution
python scripts/analyze_split_points.py document.md
```

Expected result: More balanced distribution across heading levels.

### 2. Logical Flow Check
```bash
# Extract outline to verify it makes sense
grep "^#" document.md | head -100
```

Ask: Does this outline reflect the document's actual organization?

### 3. Numbering Consistency
```bash
# Check that similar numbering depths have similar heading levels
grep -n "^### [0-9]\\+\\.[0-9]\\+\\.[0-9]\\+" document.md | head -10
grep -n "^#### [0-9]\\+\\.[0-9]\\+\\.[0-9]\\+\\.[0-9]\\+" document.md | head -10
```

## Document-Specific Considerations

### Technical Standards
- Often have very deep numbering (6+ levels)
- May use mixed numbering schemes (1.1.a.i)
- Appendices typically remain at H2 level

### Academic Papers
- Usually 3-4 heading levels maximum
- Introduction, Methods, Results → H2
- Subsections → H3, sub-subsections → H4

### Legal Documents  
- Complex numbering: §1.1(a)(i)
- May need special handling for legal citations
- Definitions sections often have unique structure

### Corporate Documents
- Executive Summary → H2
- Business units → H2, departments → H3, processes → H4
- May have inconsistent numbering schemes

## Success Criteria

1. **Logical hierarchy**: Content organization matches heading structure
2. **Consistent depth**: Similar content types at similar heading levels  
3. **Balanced distribution**: Not all H2 or all H6
4. **Navigable structure**: Easy to understand and split if needed
5. **Numbering alignment**: Heading level reflects numbering complexity

## Common Mistakes to Avoid

- **One-size-fits-all**: Don't use generic patterns without analysis
- **Over-correction**: Some flat hierarchies are intentional
- **Ignoring content**: Visual patterns might not match logical structure  
- **Pattern conflicts**: Overlapping regex can cause unexpected results
- **Missing edge cases**: Check appendices, annexes, references separately

## Recovery Strategy

If patterns cause problems:
```bash
# Always restore from backup first
cp document.md.backup document.md

# Try more conservative patterns:
# 1. More specific regex (add word boundaries)  
# 2. Target fewer levels at once
# 3. Add context requirements (spaces, punctuation)
# 4. Test on document samples first

# Example: More conservative pattern
's/^## ([0-9]+\\.[0-9]+\\.[0-9]+)\\. /### \\1. /g'  # Requires ". " after number
```

## Advanced Techniques

### Pattern Testing
```bash
# Test regex patterns without applying:
echo "## 1.2.3 Test Heading" | sed 's/^## ([0-9]+\\.[0-9]+\\.[0-9]+)/### \\1/'

# Count potential matches before applying:
grep -c "^## [0-9]\\+\\.[0-9]\\+\\.[0-9]\\+" document.md
```

### Incremental Development
```bash
# Build patterns incrementally:
# Start simple: grep "^## [0-9]" document.md
# Add complexity: grep "^## [0-9]\\+\\.[0-9]" document.md  
# Refine further: grep "^## [0-9]\\+\\.[0-9]\\+\\.[0-9]" document.md
```

The key is to **analyze first, pattern second** - let your document's actual structure guide the patterns, not predefined assumptions.

## Phase 4: Context-Aware Subordinate Element Corrections

**Problem Solved**: Tables, figures, and other elements that logically belong under their parent sections but were promoted to inappropriate heading levels.

### Common Issue Example
```markdown
### 8.4.2 The software unit design and implementation shall:
- a) be suitable to satisfy requirements...
- d) verifiability.

## Table 5 - Notations for software unit design  ← Wrong! Should be H4
```

After correction:
```markdown  
### 8.4.2 The software unit design and implementation shall:
- a) be suitable to satisfy requirements...
- d) verifiability.

#### Table 5 - Notations for software unit design  ← Correct! Now H4
```

### Generic Patterns for Subordinate Elements

#### Generic Subordinate Elements
Fix single-word headings that were incorrectly promoted to H2 (Method, Procedure, Protocol, etc.):
```bash
python scripts/apply_substitutions.py document.md -s 's/^## ([A-Z][a-z]*[^:]\{0,20\}$)/#### \1/g' --dry-run
python scripts/apply_substitutions.py document.md -s 's/^## ([A-Z][a-z]*[^:]\{0,20\}$)/#### \1/g'
```

This pattern catches common subordinate elements like:
- `## Method` → `#### Method`
- `## Procedure` → `#### Procedure`  
- `## Protocol` → `#### Protocol`
- `## Standard` → `#### Standard`
- `## Requirement` → `#### Requirement`
- `## Example` → `#### Example`
- And any other single capitalized word that shouldn't be a major section

#### Tables
Fix tables that were incorrectly promoted to H2:
```bash
python scripts/apply_substitutions.py document.md -s 's/^## (Table [0-9A-Za-z\\. ]+.*)/#### \\1/g' --dry-run
python scripts/apply_substitutions.py document.md -s 's/^## (Table [0-9A-Za-z\\. ]+.*)/#### \\1/g'
```

#### Figures  
Fix figures that were incorrectly promoted to H2:
```bash
python scripts/apply_substitutions.py document.md -s 's/^## (Figure [0-9A-Za-z\\. ]+.*)/#### \\1/g' --dry-run
python scripts/apply_substitutions.py document.md -s 's/^## (Figure [0-9A-Za-z\\. ]+.*)/#### \\1/g'
```

#### List Continuation Items
Fix orphaned list items (a), b), c), h) verifiability, etc.) that became H2:
```bash
python scripts/apply_substitutions.py document.md -s 's/^## ([a-z]\\) .*)/#### \\1/g' --dry-run
python scripts/apply_substitutions.py document.md -s 's/^## ([a-z]\\) .*)/#### \\1/g'
```

#### Named Elements  
Fix named elements that should be subordinate (methods, procedures, ratings, etc.):
```bash
# Generic pattern covers: "Rating method R2", "Test procedure TP-1", "Assessment tool AT-3", etc.
python scripts/apply_substitutions.py document.md -s 's/^## ([A-Z][a-z]+ [a-z]+ [A-Z0-9-]+.*)/#### \\1/g' --dry-run
python scripts/apply_substitutions.py document.md -s 's/^## ([A-Z][a-z]+ [a-z]+ [A-Z0-9-]+.*)/#### \\1/g'
```

#### Appendix Subsections
Fix appendix items that should be subsections:
```bash
python scripts/apply_substitutions.py document.md -s 's/^## ([A-Z]\\.[0-9]+.*)/### \\1/g' --dry-run
python scripts/apply_substitutions.py document.md -s 's/^## ([A-Z]\\.[0-9]+.*)/### \\1/g'
```

#### Notes and Examples
Fix NOTE, EXAMPLE, or similar that became headings:
```bash
python scripts/apply_substitutions.py document.md -s 's/^## (NOTE[0-9]* .*)/#### \\1/g' --dry-run
python scripts/apply_substitutions.py document.md -s 's/^## (NOTE[0-9]* .*)/#### \\1/g'

python scripts/apply_substitutions.py document.md -s 's/^## (EXAMPLE[0-9]* .*)/#### \\1/g' --dry-run  
python scripts/apply_substitutions.py document.md -s 's/^## (EXAMPLE[0-9]* .*)/#### \\1/g'
```

### Detection Strategy

First, identify problematic headings:
```bash
# Find tables that might be at wrong level
grep -n "^## Table" document.md

# Find figures that might be at wrong level  
grep -n "^## Figure" document.md

# Find suspicious single-word H2 headings that might be subordinate
grep -n "^## [A-Z][a-z]*[^:]\{0,20\}$" document.md

# Find named elements that might be at wrong level (generic pattern)
grep -n "^## [A-Z][a-z]\+ [a-z]\+ [A-Z0-9-]\+" document.md

# Find list items that became headings
grep -n "^## [a-z]) " document.md

# Find potential appendix issues
grep -n "^## [A-Z]\." document.md
```

### Verification After Phase 4

Check that the hierarchy makes sense:
```bash
python scripts/extract_samples.py document.md
```

Look for:
- ✅ Tables/figures at H4 level under their relevant sections
- ✅ No orphaned list items at H2 level  
- ✅ Proper flow: H2 → H3 → H4 → content
- ✅ Appendix sections at appropriate depth

### Document-Type Specific Adaptations

**Technical Standards (ISO, ASPICE, etc.):**
- Main clauses: `## 1 Scope` → H2 ✓
- Subsections: `### 1.1 Purpose` → H3 ✓  
- Tables: `#### Table 1 - Methods` → H4 ✓
- List continuations: `#### h) verifiability` → H4 ✓

**Academic Papers:**
- Sections: `## 2 Methodology` → H2 ✓
- Subsections: `### 2.1 Data Collection` → H3 ✓
- Figures: `#### Figure 1 - Overview` → H4 ✓
- References: `#### [1] Author et al.` → H4 ✓

**User Manuals:**
- Chapters: `## Chapter 3: Configuration` → H2 ✓
- Procedures: `### 3.1 Initial Setup` → H3 ✓  
- Steps: `#### Step 1: Download` → H4 ✓
- Screenshots: `#### Figure 3-1: Main Menu` → H4 ✓

### Complete Phase 4 Workflow

```bash
# Detection first - check for subordinate elements
grep -n "^## Table\|^## Figure\|^## [a-z])\|^## [A-Z][a-z]*[^:]\{0,20\}$" document.md

# If found, apply appropriate fixes:
# Tables and figures
python scripts/apply_substitutions.py document.md -s 's/^## (Table [0-9A-Za-z\. ]+.*)/#### \1/g'
python scripts/apply_substitutions.py document.md -s 's/^## (Figure [0-9A-Za-z\. ]+.*)/#### \1/g'

# Generic single-word subordinate elements
python scripts/apply_substitutions.py document.md -s 's/^## ([A-Z][a-z]*[^:]\{0,20\}$)/#### \1/g'

# Named elements and list items
python scripts/apply_substitutions.py document.md -s 's/^## ([A-Z][a-z]+ [a-z]+ [A-Z0-9-]+.*)/#### \1/g'
python scripts/apply_substitutions.py document.md -s 's/^## ([a-z]\) .*)/- \1/g'
python scripts/apply_substitutions.py document.md -s 's/^## ([A-Z]\\.[0-9]+.*)/### \\1/g'

# Verification
python scripts/extract_samples.py document.md
```

This two-phase approach ensures both structural consistency (3a) and contextual appropriateness (4) while remaining generic and adaptable to any document type.