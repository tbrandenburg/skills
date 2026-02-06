# Phase 1: Document Denoising and Deboilerplating

The first cleanup phase removes conversion artifacts and repeated boilerplate content that doesn't add value to the final document.

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