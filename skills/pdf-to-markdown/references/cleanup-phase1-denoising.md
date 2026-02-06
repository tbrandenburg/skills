# Phase 1: Document Denoising

## Goal
Remove conversion artifacts and repeated boilerplate content that doesn't add value to the final document. Clean up image placeholders, organizational footers, and PDF conversion remnants.

## Bad Examples

**Image placeholders everywhere:**
```markdown
## Introduction
<!-- image -->
This section covers...
<!-- image -->
The process involves...
<!-- image -->
```

**Repeated boilerplate:**
```markdown
CONFIDENTIAL - Internal Use Only
CONFIDENTIAL - Internal Use Only  
CONFIDENTIAL - Internal Use Only
(appears 47 times throughout document)
```

## Good Examples

**Clean content without artifacts:**
```markdown
## Introduction
This section covers...
The process involves...
```

**No repeated organizational text** - boilerplate removed completely.

## Workflow

1. **Detect**: Run `python scripts/extract_samples.py document.md`
   - Look for "REPEATED LINES" section (10+ occurrences = boilerplate)
   - Check samples for `<!-- image -->` patterns
   - Identify conversion artifacts (strange formatting)

2. **Test**: Apply patterns with `--dry-run`
   ```bash
   python scripts/apply_substitutions.py document.md -s 's/<!-- image -->//g' --dry-run
   python scripts/apply_substitutions.py document.md -s 's/^CONFIDENTIAL.*$//' --dry-run
   ```

3. **Apply**: Remove `--dry-run` flag
   ```bash  
   python scripts/apply_substitutions.py document.md -s 's/<!-- image -->//g'
   python scripts/apply_substitutions.py document.md -s 's/^CONFIDENTIAL.*$//'
   ```

4. **Verify**: Run `python scripts/extract_samples.py document.md`
   - Confirm patterns disappeared from "REPEATED LINES" 
   - Check samples show clean content

5. **Iterate**: Repeat steps 1-4 until no more conversion artifacts or boilerplate found

## Appendix

**Common patterns:**
- Image placeholders: `s/<!--.*image.*-->//g`
- Boilerplate: `s/^CONFIDENTIAL.*$//`, `s/^INTERNAL USE ONLY.*$/`  
- Artifacts: `s/^_+$//g`, `s/^-+$//g`
- Empty blocks: `s/^\s*$\n^\s*$/\n/g`

**Document-specific examples:**
- Beuth headers: `s/Normen-Download-Beuth.*//g`
- ISO footers: `s/^© ISO 20[0-9][0-9].*$//`
- Corporate: `s/No disclosure to third parties.*//g`
python scripts/extract_samples.py document.md

# Look in the output for:
# - "REPEATED LINES" section (10+ occurrences indicate boilerplate)
# - Image placeholders in samples (<!-- image --> patterns)
# - Conversion artifacts (strange formatting, empty lines)
```

## Common Issues to Address

1. **Image placeholders** - PDF converters often leave `<!-- image -->` markers
2. **Conversion artifacts** - Strange formatting from PDF structure interpretation  
3. **Repeated boilerplate** - Headers, footers, disclaimers that appear on every page
4. **Empty content blocks** - Placeholder text or formatting remnants

## Recommended Patterns

### Remove Image Placeholders
```bash
python scripts/apply_substitutions.py document.md \
  -s 's/^<!--.*image.*-->$//g' \
  --dry-run
```

### Remove Common Boilerplate
```bash
# Remove repeated organizational text
python scripts/apply_substitutions.py document.md \
  -s 's/^CONFIDENTIAL.*$//' \
  -s 's/^INTERNAL USE ONLY.*$//' \
  --dry-run
```

### Remove Conversion Artifacts
```bash
# Remove strange formatting remnants
python scripts/apply_substitutions.py document.md \
  -s 's/^_+$//g' \
  -s 's/^-+$//g' \
  --dry-run
```

## Verification Steps

After each substitution:

1. **Extract samples** to confirm removal worked:
   ```bash
   python scripts/extract_samples.py document.md
   ```

2. **Check the repeated lines section** - target patterns should disappear or reduce significantly

3. **Spot-check content** - ensure no valuable content was accidentally removed

## Recovery

If something goes wrong:
```bash
# Restore from backup
cp document.md.backup document.md

# Try more conservative pattern
python scripts/apply_substitutions.py document.md \
  -s 's/^<!-- image -->$//g'  # More specific pattern
  --dry-run
```

## Success Criteria

- Target boilerplate patterns no longer appear in repeated lines analysis
- Document content remains intact and readable
- File size reduction indicates successful removal of noise