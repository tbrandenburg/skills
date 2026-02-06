# Phase 2: Headers and Footers

## Goal
Remove repeated headers and footers from PDF pagination, copyright notices, page numbers, and document titles that appear throughout the converted markdown.

## Bad Examples

**Page numbers scattered throughout:**
```markdown
## 4.1 Requirements
Page 15 of 200
The requirements include...
Page 16 of 200
```

**Corporate footers everywhere:**
```markdown
## Introduction  
ISO 26262 Road Vehicles — Functional Safety
This document describes...
© ISO 2018 - All rights reserved
```

## Good Examples

**Clean sections without pagination:**
```markdown
## 4.1 Requirements
The requirements include...
```

**Content without corporate footers:**
```markdown
## Introduction
This document describes...
```

## Workflow

1. **Analyze**: Run `python scripts/extract_samples.py document.md`
   - Look for "REPEATED LINES" with page numbers, copyright, titles
   - Check samples for corporate footers at section ends
   - Identify document title repetition patterns
   - **IMPORTANT**: Note the exact header/footer text patterns in YOUR document!

2. **Plan**: Based on step 1 findings, create document-specific patterns
   ```bash
   # Example: If you found "Page 15 of 200" and "© ISO 2018 - All rights reserved"
   # Create patterns that match YOUR document's actual headers/footers:
   python scripts/apply_substitutions.py document.md -s 's/^Page [0-9]+ of [0-9]+$//' --dry-run
   ```
   **Don't copy-paste generic examples - adapt to what you actually found!**

3. **Test**: Preview changes with native `sed` (no modification)
   ```bash
   # These are EXAMPLES - adapt based on step 2 plan:
   sed 's/^Page [0-9].*//' document.md | head -20  # Preview changes
   sed 's/^© .*$//' document.md | grep -C2 "©"     # Check copyright removal
   ```

4. **Apply**: Use `sed -i.backup` to apply changes (creates automatic backup)
   ```bash
   # Use YOUR patterns from step 3, not these generic examples:
   sed -i.backup 's/^Page [0-9].*//' document.md
   sed -i.backup 's/^© .*$//' document.md
   ```

5. **Verify**: Run `python scripts/extract_samples.py document.md`
   - Confirm page numbers disappeared from samples
   - Check no copyright footers in sections
   - **Verify YOUR specific patterns worked correctly**

6. **Iterate**: Repeat steps 1-4 until all headers/footers removed

## Appendix

**Common patterns:**
- Page numbers: `s/^Page [0-9].*/`, `s/Page [0-9]+ of [0-9]+//g`
- Copyright: `s/^© .*[0-9]{4}.*/`, `s/All rights reserved.*//g`
- Document titles: `s/^ISO [0-9].*/`, `s/^[A-Z][A-Z ]+$/` (repeated company names)

**Document-specific examples:**
- ISO: `s/^ISO 26262.*/`
- Corporate: `s/Normen-Download-Beuth.*/`, `s/CONFIDENTIAL.*$/`
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