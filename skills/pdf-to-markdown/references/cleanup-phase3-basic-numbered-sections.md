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

2. **Test**: Apply patterns with `--dry-run`
   ```bash
   python scripts/apply_substitutions.py document.md -s 's/^([0-9]+\s)/## \1/' --dry-run
   python scripts/apply_substitutions.py document.md -s 's/^([0-9]+\.[0-9]+\s)/### \1/' --dry-run
   ```

3. **Apply**: Remove `--dry-run` flag
   ```bash  
   python scripts/apply_substitutions.py document.md -s 's/^([0-9]+\s)/## \1/'
   python scripts/apply_substitutions.py document.md -s 's/^([0-9]+\.[0-9]+\s)/### \1/'
   ```

4. **Verify**: Run `python scripts/extract_samples.py document.md`
   - Confirm all numbered sections now have # markers
   - Check proper hierarchy: ## for main, ### for subsections

5. **Iterate**: Repeat steps 1-4 for deeper levels (6.1.1 → ####)

## Appendix

**Standard patterns:**
- Main sections: `s/^([0-9]+\s)/## \1/`
- Subsections: `s/^([0-9]+\.[0-9]+\s)/### \1/`  
- Sub-subsections: `s/^([0-9]+\.[0-9]+\.[0-9]+\s)/#### \1/`

**Common variations:**
- With dots: `s/^([0-9]+\.\s)/## \1/`
- Appendices: `s/^(Annex [A-Z]\s)/## \1/`
- Multiple spaces: `s/^([0-9]+)\s+/## \1 /`
