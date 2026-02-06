# Phase 3: Basic Numbered Sections

## Goal
**SURGICALLY** fix heading hierarchy issues where numbered sections have incorrect markdown levels. This phase should ONLY modify headings that are actually broken - never apply blanket changes to all numbered headings.

## ⚠️ CRITICAL WARNING
**DO NOT apply patterns blindly to all numbered headings!** Many documents already have correct hierarchy. Always analyze first to identify what's actually broken.

## Bad Examples (THESE need fixing)

**Numbered sections as plain text (missing # markers):**
```markdown
6 ASIL determination

6.1 Overview of ASIL determination

6.2 Determination of ASIL
```

**Mixed hierarchy problems (inconsistent # levels):**
```markdown
## 6 ASIL determination
6.1 Overview of ASIL determination    ← Missing #
### 6.2 Determination of ASIL
```

**Flattened hierarchy (wrong # levels):**
```markdown
## 6 ASIL determination
## 6.1 Overview of ASIL determination    ← Should be ###
## 6.1.1 Determination of ASIL          ← Should be ####
```

## ✅ ALREADY CORRECT (DO NOT CHANGE)

**Proper hierarchy (leave this alone!):**
```markdown
## 5. Process capability levels
### 5.1. Process capability level 0
### 5.2. Process capability level 1
#### 5.2.1. PA 1.1 Process performance
```

## Good Examples (Target state)

**Proper markdown heading hierarchy:**
```markdown
## 6 ASIL determination

### 6.1 Overview of ASIL determination

### 6.2 Determination of ASIL

The ASIL determination process...
```

**Consistent heading levels:**
```markdown
## 6 ASIL determination
### 6.1 Overview
### 6.2 Process
#### 6.2.1 Step one
#### 6.2.2 Step two
```

## Surgical Workflow

1. **Analyze**: Run `python scripts/extract_samples.py document.md`
   - Examine HEADING PATTERNS section carefully
   - Look for inconsistencies: `## 6.1` mixed with `### 6.2` 
   - Identify plain text: lines like "6 Quality determination" (no # markers)
   - Find flattened hierarchy: `## 6.1.1` when it should be `####`
   - **CRITICAL**: Document what's BROKEN vs what's ALREADY CORRECT

2. **Plan**: Create specific detection patterns
   ```bash
   # Find plain text numbered sections (missing # entirely)
   grep "^[0-9]\+\.[0-9]\+ [A-Z]" document.md
   
   # Find potentially wrong hierarchy levels
   grep "^## [0-9]\+\.[0-9]\+\.[0-9]\+" document.md   # 3-level at ## (should be ###/####)
   grep "^### [0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+" document.md   # 4-level at ### (should be ####)
   ```

3. **SURGICAL PATTERNS**: Create TARGETED patterns for IDENTIFIED issues only
   ```bash
   # ONLY if step 2 found issues - adapt patterns to YOUR findings:
   # Plain text → headings: 's/^([0-9]+\.[0-9]+ [A-Z])/### \1/'
   # Wrong levels → correct levels: 's/^## ([0-9]+\.[0-9]+\.[0-9]+)/### \1/'
   ```
   **NEVER use blanket patterns like 's/^## ([0-9]+\.[0-9]+)/### \1/'** 

4. **SURGICAL TEST**: Preview ONLY the changes needed
   ```bash
   # Test ONLY patterns for issues you identified in step 2:
   sed 's/^([0-9]+\.[0-9]+ [A-Z])/### \1/' document.md | grep -E "^#{2,4} [0-9]" | head -20
   ```

5. **APPLY SURGICALLY**: Fix ONLY identified issues
   ```bash
   # Apply ONLY patterns for confirmed issues:
   sed -i.backup 's/^([0-9]+\.[0-9]+ [A-Z])/### \1/' document.md  # Example - adapt to YOUR needs
   ```

6. **VERIFY SURGICALLY**: Check only affected sections
   ```bash
   # Check hierarchy around modified sections:
   python scripts/extract_samples.py document.md | grep -A10 -B10 "HEADING PATTERNS"
   ```

7. **ITERATE**: Apply additional surgical fixes if needed

## 🚨 PREVENTION RULES

### Rule 1: Document Analysis First
**BEFORE any sed command**, understand your document's current state:
- What's the existing hierarchy pattern?
- Which sections are actually broken?
- Which sections are already correct?

### Rule 2: Targeted Fixes Only
**NEVER** apply these dangerous blanket patterns:
- ❌ `s/^## \([0-9]\+\.[0-9]\+\)/### \1/` (changes ALL 2-level headings)
- ❌ `s/^## \([0-9]\+\.[0-9]\+\.[0-9]\+\)/### \1/` (changes ALL 3-level headings)

**INSTEAD** use targeted patterns based on analysis:
- ✅ `s/^([0-9]+\.[0-9]+ [A-Z][^#])/### \1/` (only plain text sections)
- ✅ `s/^## (4\.[0-9]+\.[0-9]+ )/### \1/` (only specific broken sections)

### Rule 3: Test on Small Sections
Before applying to entire document:
```bash
# Test pattern on specific line range first:
sed -n '100,110p' document.md | sed 's/pattern/replacement/'
```

### Rule 4: Preserve Working Hierarchy
If you see properly structured sections like:
```markdown
## 5. Main section
### 5.1. Subsection
#### 5.1.1. Sub-subsection
```
**DO NOT MODIFY THEM!**

## Surgical Pattern Templates

### Safe Detection Patterns
```bash
# Find sections missing # markers entirely (safe to fix):
grep "^[0-9]\+\.[0-9]\+ [A-Z]" document.md

# Find inconsistent hierarchy (needs analysis):
grep -E "^#{2,4} [0-9]+\.[0-9]+(\.[0-9]+)*" document.md | sort | uniq -c
```

### Example Surgical Fixes (only after analysis!)
```bash
# ONLY if you found plain text sections:
sed 's/^([0-9]+\.[0-9]+ [A-Z])/### \1/' document.md

# ONLY if you found specific wrong levels:
sed 's/^## (6\.[0-9]+\.[0-9]+)/### \1/' document.md  # Fix only chapter 6 3-level headings
```

### Recovery Commands
```bash
# If you broke hierarchy, restore from backup:
cp document.md.backup document.md

# Check what your pattern would change before applying:
diff <(grep "^##" document.md) <(sed 's/pattern/replacement/' document.md | grep "^##")
```

## ❌ DANGEROUS Patterns (Never Use)

These patterns caused the Automotive SPICE hierarchy issue:

```bash
# ❌ DANGEROUS - affects ALL 2-level headings (including correct ones):
sed 's/^## \([0-9]\+\.[0-9]\+\)/### \1/'

# ❌ DANGEROUS - affects ALL 3-level headings:
sed 's/^## \([0-9]\+\.[0-9]\+\.[0-9]\+\)/### \1/'

# ❌ DANGEROUS - blanket changes without analysis:
sed 's/^## \([0-9]\+\.[0-9]\+\.\)/### \1/'
```

## ✅ SAFE Approach

1. **First** - understand what's broken:
   ```bash
   # Analyze current structure
   python scripts/extract_samples.py document.md | grep -A50 "HEADING PATTERNS"
   ```

2. **Then** - create targeted fixes:
   ```bash
   # Fix ONLY identified issues
   sed 's/specific-broken-pattern/correct-pattern/' document.md
   ```

⚠️ **REMEMBER**: The Automotive SPICE document had CORRECT hierarchy that was broken by blanket patterns. Always preserve working structure!
