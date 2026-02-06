# Phase 3: Basic Numbered Sections

## Goal
Fix simple heading hierarchy issues where numbered sections appear as plain text instead of proper markdown headings. Convert "1. Introduction", "1.1 Overview" into ## 1. Introduction, ### 1.1 Overview.

## Bad Examples

**Numbered sections as plain text:**
```markdown
6 ASIL determination

6.1 Overview of ASIL determination

6.2 Determination of ASIL

The ASIL determination process...
```

**Mixed hierarchy problems:**
```markdown
## 6 ASIL determination
6.1 Overview of ASIL determination
### 6.2 Determination of ASIL
```

**Flattened hierarchy :**
```markdown
## 6 ASIL determination
## 6.1 Overview of ASIL determination
## 6.1.1 Determination of ASIL
## 6.1.2 Determination of ASIL
```

## Good Examples

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

## Workflow

1. **Detect**: Run `python scripts/extract_samples.py document.md`
   - Look for lines starting with just numbers: "6 ASIL determination"
   - Find mixed patterns: some headings with #, some without
   - Check numbered subsections: "6.1", "6.2.1" patterns
   - **IMPORTANT**: Note the exact numbering patterns in YOUR document!

2. **Analyze**: Based on step 1 findings, create document-specific patterns
   ```bash
   # Example: If you found "6 ASIL determination" and "6.1 Overview"
   # Create patterns that match YOUR document's actual numbering:
   python scripts/apply_substitutions.py document.md -s 's/^([0-9]+\s+[A-Z])/## \1/' --dry-run
   ```
   **Don't copy-paste generic examples - adapt to what you actually found!**

3. **Test**: Preview changes with native `sed` (no modification)
   ```bash
   # These are EXAMPLES - adapt based on step 1 findings:
   sed 's/^([0-9]+\s)/## \1/' document.md | head -20        # Preview heading changes
   sed 's/^([0-9]+\.[0-9]+\s)/### \1/' document.md | head -20  # Check subsections
   ```

4. **Apply**: Use `sed -i.backup` to apply changes (creates automatic backup)
   ```bash
   # Use YOUR patterns from step 3, not these generic examples:
   sed -i.backup 's/^([0-9]+\s)/## \1/' document.md
   sed -i.backup 's/^([0-9]+\.[0-9]+\s)/### \1/' document.md
   ```

5. **Verify**: Run `python scripts/extract_samples.py document.md`
   - Confirm all numbered sections now have # markers
   - Check proper hierarchy: ## for main, ### for subsections
   - **Verify YOUR specific patterns worked correctly**

6. **Iterate**: Repeat steps 1-5 for deeper levels (6.1.1 → ####)

## Appendix

**Pattern Templates (adapt to your document):**
- Main sections: `s/^([0-9]+\s)/## \1/`
- Subsections: `s/^([0-9]+\.[0-9]+\s)/### \1/`  
- Sub-subsections: `s/^([0-9]+\.[0-9]+\.[0-9]+\s)/#### \1/`

**Example adaptations (based on actual document analysis):**
- With dots: `s/^([0-9]+\.\s)/## \1/`
- Appendices: `s/^(Annex [A-Z]\s)/## \1/`
- Multiple spaces: `s/^([0-9]+)\s+/## \1 /`

⚠️ **CRITICAL**: These are TEMPLATES. Always analyze your document first (step 1) and modify patterns to match what you actually find!
