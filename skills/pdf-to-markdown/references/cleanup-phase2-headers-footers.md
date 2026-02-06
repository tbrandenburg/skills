# Phase 2: Remove Headers and Footers

This phase targets repeated headers and footers that appear throughout the document from the original PDF pagination and corporate formatting.

## Common Header/Footer Patterns

1. **Page numbers** - "Page 1", "Page 15 of 200", etc.
2. **Copyright notices** - Repeated on every page
3. **Document titles** - Company names, document titles repeated as headers
4. **Organizational footers** - Department names, confidentiality notices
5. **Date stamps** - Revision dates repeated as footers

## Identification Strategy

Use `extract_samples.py` to identify repeated patterns:
```bash
python scripts/extract_samples.py document.md --min-repeats 10
```

Look for patterns that appear 10+ times - these are usually headers/footers.

## Common Removal Patterns

### Copyright Footers
```bash
# Generic copyright patterns - handles Unicode variations
python scripts/apply_substitutions.py document.md \
  -s 's/^.*\u00A9.*$//' \
  -s 's/^Copyright.*$//' \
  --dry-run

# Robust organizational footer removal (handles Unicode copyright symbols)
python scripts/apply_substitutions.py document.md \
  -s 's/^.*VDA Quality Management Center\s*$//g' \
  --dry-run
```

**Note**: PDF conversion may use Unicode copyright symbols (\\u00A9) instead of ASCII "©". The pattern `.*\\u00A9.*` catches various Unicode copyright formats.

### Page Numbers
```bash
# Simple page numbers
python scripts/apply_substitutions.py document.md \
  -s 's/^Page \d+$//' \
  --dry-run

# Page X of Y format  
python scripts/apply_substitutions.py document.md \
  -s 's/^Page \d+ of \d+$//' \
  --dry-run

# Page numbers with extra text
python scripts/apply_substitutions.py document.md \
  -s 's/^.*Page \d+.*$//' \
  --dry-run
```

### Document Headers
```bash
# Company/organization names repeated as headers
python scripts/apply_substitutions.py document.md \
  -s 's/^COMPANY NAME$//' \
  -s 's/^Department: .*$//' \
  --dry-run
```

### Date Stamps
```bash
# Various date formats in footers
python scripts/apply_substitutions.py document.md \
  -s 's/^Version: \d+\.\d+ - \d{4}-\d{2}-\d{2}$//' \
  -s 's/^Last updated: .*$//' \
  --dry-run
```

## Advanced Techniques

### Context-Aware Removal
Sometimes you need to preserve headers/footers that appear in legitimate content but remove them when they're just page artifacts:

```bash
# Remove only when isolated on their own lines
python scripts/apply_substitutions.py document.md \
  -s 's/^Confidential$//g'  # Only isolated occurrences
  --dry-run
```

### Pattern Combinations
```bash
# Multiple related patterns in one pass (test each first!)
python scripts/apply_substitutions.py document.md \
  -s 's/^©.*$//' \
  -s 's/^Page \d+$//' \
  -s 's/^CONFIDENTIAL$//' \
  --dry-run
```

## Verification Strategy

1. **Before and after counts**: Check how many instances were removed
   ```bash
   # Before
   grep -c "©" document.md.backup
   # After  
   grep -c "©" document.md
   ```

2. **Sample extraction**: Verify patterns are gone from repeated lines
   ```bash
   python scripts/extract_samples.py document.md
   ```

3. **Content integrity**: Ensure legitimate content wasn't removed
   - Check beginning and end of document
   - Spot-check a few middle sections

## Common Pitfalls

- **Over-broad patterns**: `s/.*Page.*//` might remove legitimate content mentioning "page"
- **Case sensitivity**: Remember to handle both "Page" and "PAGE"  
- **Partial matches**: A pattern might match part of legitimate content

## Success Criteria

- Target header/footer patterns no longer appear in repeated lines analysis
- Page structure looks clean when viewing samples
- No legitimate content was accidentally removed
- Document flows naturally without pagination artifacts