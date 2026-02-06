# Table Cleanup Patterns

Common issues with PDF-to-markdown table conversion and solutions.

## Contents Tables (Table of Contents)

**Issue**: Complex dot-leader tables become malformed with broken alignment
**Pattern**: Multiple columns with excessive dots and misaligned content

### Solution 1: Remove malformed Contents tables entirely
```bash
python scripts/apply_substitutions.py file.md \
  --substitute 's/^## Contents$/## Contents\n\n*(Table of Contents structure preserved but reformatted for readability)*/; /^\| .*\.{10,}/,/^$/d'
```

### Solution 2: Simplify Contents table structure  
```bash
python scripts/apply_substitutions.py file.md \
  --substitute 's/\| [^|]*\.{5,}[^|]* \|/|/g'
```

## Methodology Tables

**Issue**: Tables with structured methodology columns (e.g., A/B/C/D rating systems) can have alignment issues
**Detection**: Look for patterns like `| A | B | C | D |` or similar structured columns

### Preserve methodology tables - they usually convert well

## Method Tables with Long Text

**Issue**: Table cells with very long content wrap poorly
**Pattern**: `| Very long text that exceeds normal cell width... |`

### Solution: Convert to bullet lists if content is too long
```bash
python scripts/apply_substitutions.py file.md \
  --substitute 's/^\| ([^|]{100,}) \|$/- \1/g'
```

## Broken Table Borders

**Issue**: Incomplete table border lines from PDF conversion
**Pattern**: Lines with partial `|----` sequences

### Solution: Clean up incomplete table borders
```bash
python scripts/apply_substitutions.py file.md \
  --substitute '/^\|[-\s]*\|?[-\s]*$/d'
```

## Usage Recommendations

1. **Always preserve methodology tables** - they convert well with enhanced docling
2. **Consider removing Contents tables** - they're usually malformed and not needed in markdown
3. **Convert overly wide tables to lists** when content readability is poor
4. **Clean up artifacts** but preserve meaningful table structure

## Document-Specific Patterns

### Standards Documents
- Contents tables: Usually malformed, consider removal
- Methodology tables: Generally convert well, preserve
- Method tables: May need width adjustments

### Process Documents  
- Process tables: Usually convert well
- Assessment tables: Preserve structure
- Simple contents: Can often be kept