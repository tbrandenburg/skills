# AGENTS.md - Generic Skill Development Principles

## Core Principles

### 1. 🌐 **Stay Generic - Never Hardcode Specifics**

❌ **WRONG**: `if document_type == 'ISO': return iso_logic()`
✅ **CORRECT**: `if heading_ratio > threshold: return 'HIERARCHICAL'`

**Why**: Skills should work for ANY document, not just your examples.

### 2. 📚 **Use State-of-the-Art Libraries**

✅ **Current Best**: Docling v2.x, native Python regex, pathlib, argparse
❌ **Avoid**: Deprecated libraries, hardcoded paths, shell commands

### 3. 🔄 **Pattern-Based Instead of Example-Based**

❌ **WRONG**: `if 'VDA Quality' in content: return 'automotive'`
✅ **CORRECT**: `detect_repeated_patterns(lines, min_frequency=3)`

### 4. 🎛️ **Configurable with Smart Defaults**

```python
parser.add_argument("--min-content", type=int, default=3, 
                   help="Minimum content lines (auto-detected if not specified)")
```

### 5. 🧠 **Content-Aware Processing**

Analyze document structure to recommend optimal parameters:
```python
def analyze_structure(content):
    h2_count = len([l for l in lines if l.startswith('## ')])
    h3_count = len([l for l in lines if l.startswith('### ')])
    
    if h3_count > h2_count * 0.5:
        return {'level': 3, 'min_content': 4}
    return {'level': 2, 'min_content': 5}
```

## 🚫 **Anti-Patterns**

1. **Company/Standard Specificity**: No ISO, ASPICE, VDA, etc. in code
2. **Example Overfitting**: Don't optimize for your 2-3 test documents
3. **Hardcoded Thresholds**: Make parameters configurable
4. **Magic Numbers**: Use named constants

## 📋 **Success Checklist**

- [ ] Works with unseen documents?
- [ ] No hardcoded company/standard names?
- [ ] Configurable with smart defaults?
- [ ] Uses current libraries?
- [ ] Pattern-based detection?
- [ ] Graceful error handling?

## 🎯 **Goal**

Build tools that **adapt automatically** to new content, **provide reasonable results** without tuning, and **scale gracefully** across document types.

**Remember**: The goal is broad applicability, not optimization for current examples.