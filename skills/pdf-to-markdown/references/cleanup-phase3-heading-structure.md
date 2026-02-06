# Phase 3: Fix Heading Structure and Depths

This phase corrects the markdown heading hierarchy to match the document's logical structure. PDF converters often assign incorrect heading levels based on visual formatting rather than semantic meaning.

## Core Principle

**Heading depth should reflect content hierarchy, not visual appearance.**

The goal is to analyze your document's actual structure and create patterns that match its specific organization.

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