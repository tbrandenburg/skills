# Phase 5: Cleanup Spacing and Formatting

This final cleanup phase addresses spacing inconsistencies, formatting artifacts, and document flow issues that remain after content cleanup.

## ⚠️ MANDATORY DETECTION STEP

**Before applying spacing fixes, ALWAYS identify spacing issues:**

```bash
# REQUIRED: Extract samples to see spacing problems
python scripts/extract_samples.py document.md --lines 100

# REQUIRED: Check for specific spacing issues
grep -n "^\s*$" document.md | wc -l    # Count blank lines
grep -n "  " document.md | head -10     # Find double spaces
grep -A5 -B5 "|" document.md | head -20 # Check table formatting

# If excessive blank lines (>200) or formatting issues found, Phase 5 is needed
```

## Common Spacing Issues

1. **Excessive blank lines** - Multiple consecutive empty lines
2. **Inconsistent paragraph spacing** - Mixed single/double spacing  
3. **Heading spacing** - Irregular spacing around section headings
4. **List formatting** - Poorly formatted bullet points and numbered lists
5. **Table spacing** - Malformed table structures from PDF conversion

## Basic Spacing Cleanup

### Remove Excessive Blank Lines
```bash
# Replace 3+ consecutive blank lines with just 2
python scripts/apply_substitutions.py document.md \
  -s 's/\n\n\n+/\n\n/g' \
  --dry-run
```

### Normalize Line Endings
```bash
# Ensure consistent line endings (Unix style)
python scripts/apply_substitutions.py document.md \
  -s 's/\r\n/\n/g' \
  --dry-run
```

### Clean Trailing Whitespace  
```bash
# Remove spaces at end of lines
python scripts/apply_substitutions.py document.md \
  -s 's/ +$//' \
  --dry-run
```

## Heading Formatting

### Consistent Heading Spacing
```bash
# Ensure headings have proper spacing before them
python scripts/apply_substitutions.py document.md \
  -s 's/\n(^## )/\n\n\1/g' \
  --dry-run
```

### Remove Extra Spaces in Headings
```bash
# Clean up double spaces in headings
python scripts/apply_substitutions.py document.md \
  -s 's/^(#{1,6}) +(.+)/\1 \2/g' \
  --dry-run
```

## List Formatting

### Fix Bullet Point Alignment
```bash
# Standardize bullet point format
python scripts/apply_substitutions.py document.md \
  -s 's/^[*+-] /- /g' \
  --dry-run
```

### Fix Numbered List Format
```bash
# Ensure proper numbered list spacing
python scripts/apply_substitutions.py document.md \
  -s 's/^(\d+)\./\1. /g' \
  --dry-run
```

### Fix Nested List Indentation
```bash
# Fix inconsistent indentation
python scripts/apply_substitutions.py document.md \
  -s 's/^   - /  - /g' \
  --dry-run
```

## Table Cleanup

### Fix Table Alignment
```bash
# Clean up pipe-separated tables
python scripts/apply_substitutions.py document.md \
  -s 's/ *\| */|/g' \
  --dry-run
```

### Remove Broken Table Fragments
```bash
# Remove incomplete table separators
python scripts/apply_substitutions.py document.md \
  -s 's/^[|+-]+$//g' \
  --dry-run
```

## Text Flow Issues

### Fix Hyphenated Words Split Across Lines
```bash
# Common word breaks from PDF conversion
python scripts/apply_substitutions.py document.md \
  -s 's/manage-\nment/management/g' \
  -s 's/develop-\nment/development/g' \
  --dry-run
```

### Fix Paragraph Breaks
```bash
# Join lines that were incorrectly split
# (Be very careful with this - test thoroughly)
python scripts/apply_substitutions.py document.md \
  -s 's/([a-z])\n([a-z])/\1 \2/g' \
  --dry-run
```

## Advanced Formatting

### Fix Quote Formatting
```bash
# Standardize quote marks
python scripts/apply_substitutions.py document.md \
  -s 's/"/"/g' \
  -s 's/"/"/g' \
  --dry-run
```

### Fix Em Dashes and Hyphens  
```bash
# Standardize dash usage
python scripts/apply_substitutions.py document.md \
  -s 's/—/--/g' \
  -s 's/–/-/g' \
  --dry-run
```

## Document-Specific Patterns

### Technical Documents
```bash
# Fix common technical formatting
python scripts/apply_substitutions.py document.md \
  -s 's/\bVer\. /Version /g' \
  -s 's/\bFig\. /Figure /g' \
  --dry-run
```

### Legal Documents
```bash
# Fix legal citation formats
python scripts/apply_substitutions.py document.md \
  -s 's/§ (\d+)/Section \1/g' \
  --dry-run
```

## Verification Methods

### 1. Visual Review
```bash
# Check a sample of the cleaned document
python scripts/extract_samples.py document.md --lines 100
```

### 2. Line Count Changes
```bash
# Compare line counts to see impact
wc -l document.md.backup document.md
```

### 3. Search for Common Issues
```bash
# Look for remaining formatting problems
grep -n "  " document.md | head -10    # Double spaces
grep -n "^\s*$" document.md | wc -l    # Count blank lines
```

### 4. Table Structure Check
```bash
# Verify tables are properly formatted
grep -A5 -B5 "|" document.md | head -20
```

## Iterative Approach

Apply spacing fixes in small batches:

1. **Basic cleanup first**: Excessive blank lines, trailing spaces
2. **Heading spacing**: Consistent spacing around sections  
3. **List formatting**: Fix bullets and numbering
4. **Table cleanup**: Address table formatting issues
5. **Advanced fixes**: Word breaks, paragraph flow

Each step: **dry-run → apply → verify**

## Success Criteria

1. **Consistent spacing**: No excessive blank lines (>2 consecutive)
2. **Clean headings**: Proper spacing and formatting around all headings  
3. **Readable lists**: Well-formatted bullet points and numbered lists
4. **Proper tables**: Tables render correctly in markdown viewers
5. **Flow integrity**: Text reads naturally without formatting artifacts
6. **Professional appearance**: Document looks polished and ready for use

## Recovery Strategy

If formatting fixes break content:

```bash
# Restore from backup
cp document.md.backup document.md

# Apply only the safest fixes
python scripts/apply_substitutions.py document.md \
  -s 's/\n\n\n+/\n\n/g'  # Just fix excessive blank lines
  --dry-run
```

## Final Quality Check

After all formatting cleanup:

```bash
# Extract final samples to verify quality
python scripts/extract_samples.py document.md

# Check document structure one last time  
python scripts/analyze_split_points.py document.md

# Verify no critical content was lost
diff -u document.md.backup document.md | head -50
```