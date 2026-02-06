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
   - **IMPORTANT**: Note the exact repeated text patterns in YOUR document!

2. **Analyze**: Based on step 1 findings, create document-specific patterns
   ```bash
   # Example: If you found "CONFIDENTIAL - Internal Use Only" 47x and "<!-- image -->" 23x
   # Create patterns that match YOUR document's actual boilerplate:
   python scripts/apply_substitutions.py document.md -s 's/^CONFIDENTIAL - Internal Use Only$//' --dry-run
   ```
   **Don't copy-paste generic examples - adapt to what you actually found!**

3. **Test**: Preview changes with native `sed` (no modification)
   ```bash
   # These are EXAMPLES - adapt based on step 1 findings:
   sed 's/<!-- image -->//g' document.md | head -20  # Preview first 20 lines
   sed 's/^CONFIDENTIAL.*$//' document.md | grep -C3 "CONFIDENTIAL" # See what changes
   ```

4. **Apply**: Use `sed -i.backup` to apply changes (creates automatic backup)
   ```bash
   # Use YOUR patterns from step 3, not these generic examples:
   sed -i.backup 's/<!-- image -->//g' document.md
   sed -i.backup 's/^CONFIDENTIAL.*$//' document.md
   ```

5. **Verify**: Run `python scripts/extract_samples.py document.md`
   - Confirm patterns disappeared from "REPEATED LINES" 
   - Check samples show clean content
   - **Verify YOUR specific patterns worked correctly**

6. **Iterate**: Repeat steps 1-5 until no more conversion artifacts or boilerplate found

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
# Preview changes
sed 's/^<!--.*image.*-->$//g' document.md | head -20

# Apply with backup
sed -i.backup 's/^<!--.*image.*-->$//g' document.md
```

### Remove Common Boilerplate
```bash
# Remove repeated organizational text (preview first)
sed 's/^CONFIDENTIAL.*$//' document.md | head -20
sed 's/^INTERNAL USE ONLY.*$//' document.md | head -20

# Apply with backup
sed -i.backup 's/^CONFIDENTIAL.*$//' document.md
sed -i.backup 's/^INTERNAL USE ONLY.*$//' document.md
```

### Remove Conversion Artifacts  
```bash
# Remove strange formatting remnants
sed -i.backup 's/^_+$//g' document.md
sed -i.backup 's/^-+$//g' document.md
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

# Try more conservative pattern (preview first)
sed 's/^<!-- image -->$//g' document.md | head -20  # More specific pattern

# Apply if looks good
sed -i.backup 's/^<!-- image -->$//g' document.md
```

## Success Criteria

- Target boilerplate patterns no longer appear in repeated lines analysis
- Document content remains intact and readable
- File size reduction indicates successful removal of noise