---
name: codesense
description: Semantic code search and codebase understanding through AI-powered indexing. Use for codebase exploration, pattern discovery, symbol lookup, impact analysis, DRY detection, and analysis of logs/git history. Triggered by needs for code understanding, searching similar implementations, finding patterns, or analyzing codebases semantically.
---

# CodeSense

## Overview

CodeSense provides semantic code search and understanding capabilities through AI-powered indexing. Transform any codebase or text files into a searchable semantic database to find patterns, analyze impact, detect duplicates, and understand code relationships through natural language queries.

## Core Capabilities

### 1. Codebase Indexing and Search
Index entire codebases to enable semantic search across functions, classes, and code patterns.

### 2. Pattern Discovery  
Find similar implementations, coding patterns, and architectural conventions across the codebase.

### 3. Impact Analysis
Understand dependencies and analyze the impact of potential changes to specific symbols or functions.

### 4. DRY Analysis
Identify duplicate or similar code implementations for refactoring opportunities in large monorepos.

### 5. Temporary File Analysis
Index and analyze arbitrary files like logs, git history, or documentation for insights and patterns.

## Quick Start Workflow

### Initial Setup
```bash
# CodeSense automatically manages its own virtual environment
# No need to install system-wide dependencies!

# Index your codebase (run once or when code changes significantly)
python scripts/run.py index.py --stats

# Start searching
python scripts/run.py search.py "authentication middleware" --results 10
```

**Note:** CodeSense automatically creates and manages its own isolated virtual environment with all required dependencies. This prevents conflicts with your system Python installation.

## Use Cases and Workflows

### Guideline Search - Finding Code Patterns

**When to use:** Agent needs to understand implementation patterns and conventions in a codebase.

**Workflow:**
1. **Index the codebase** (if not already done)
2. **Search for patterns** using natural language
3. **Analyze results** to understand coding conventions

**Examples:**
```bash
# Find error handling patterns
python scripts/run.py search.py "error handling try catch exception" --results 15

# Find authentication patterns  
python scripts/run.py search.py "authentication login token middleware" --extension py

# Find database patterns
python scripts/run.py search.py "database connection pool transaction" --threshold 0.4
```

**Integration with LLM:**
Use search results to inform LLM analysis of coding patterns and provide recommendations consistent with existing codebase conventions.

### Simple Search - Symbol Discovery

**When to use:** Agent needs to find specific functions, classes, or code elements.

**Workflow:**
1. **Search by functionality** or symbol name
2. **Filter by language** if needed  
3. **Review matches** for relevant implementations

**Examples:**
```bash  
# Find parsing functions
python scripts/run.py search.py "parse parser parsing" --results 20

# Find React components
python scripts/run.py search.py "React component" --extension jsx

# Find test utilities
python scripts/run.py search.py "test utility helper mock" --extension py --threshold 0.3
```

### Impact Analysis - Dependency Understanding

**When to use:** Agent needs to understand the impact of changing specific code symbols.

**Workflow:**
1. **Analyze symbol impact** with context
2. **Review dependencies** and usage patterns
3. **Plan changes** based on impact assessment

**Examples:**
```bash
# Analyze function impact
python scripts/run.py search.py "calculateTotal" --mode impact --context "payment processing"

# Understand class dependencies  
python scripts/run.py search.py "UserManager" --mode impact --results 25

# API endpoint analysis
python scripts/run.py search.py "/api/users" --mode impact --context "REST endpoints"
```

### DRY Analysis - Duplicate Detection

**When to use:** Agent wants to identify similar implementations for potential refactoring.

**Workflow:**
1. **Find similar functions** using reference code
2. **Set similarity thresholds** appropriately  
3. **Identify refactoring opportunities**

**Examples:**
```bash
# Find functions similar to a reference
python scripts/run.py search.py --mode similar --reference "$(cat reference.py)" --threshold 0.7

# Find duplicate validation logic
python scripts/run.py search.py "validation validate input check" --threshold 0.6 --results 30

# Identify similar error handling
python scripts/run.py search.py --mode similar --reference "def handle_error(error):" --threshold 0.5
```

### Quick File Indexing - Temporary Analysis  

**When to use:** Agent needs to analyze logs, git history, or other temporary files.

**Workflow:**
1. **Index target files** with appropriate chunking
2. **Search indexed content** for patterns
3. **Extract insights** and recommendations

**Examples:**
```bash
# Index and search log files
python scripts/run.py index.py --files /tmp/app.log /tmp/error.log --cache .log_cache
python scripts/run.py search.py "error exception failed" --cache .log_cache --results 20

# Index git history for analysis
git log --oneline > /tmp/commits.txt  
python scripts/run.py index.py --files /tmp/commits.txt --cache .git_cache
python scripts/run.py search.py "feature authentication" --cache .git_cache --results 10

# Index documentation
python scripts/run.py index.py --files docs/*.md --cache .docs_cache --chunk-size 500
python scripts/run.py search.py "API endpoint documentation" --cache .docs_cache
```

## Script Reference

### Index Script (scripts/index.py)
Creates searchable indexes from codebases or arbitrary files.

**Key Options:**
- `--path` - Repository path (auto-detects git root)
- `--files` - Specific files to index  
- `--cache` - Cache file name
- `--batch-size` - Memory vs speed tuning
- `--force` - Rebuild index ignoring cache
- `--chunk-size` - For large file processing

### Search Script (scripts/search.py)  
Searches indexed content using natural language queries.

**Key Options:**
- `query` - Natural language search query
- `--results` - Number of results to return
- `--extension` - Filter by file extension
- `--threshold` - Minimum similarity score
- `--mode` - Search mode (search/similar/impact)
- `--format` - Output format (text/json)

## Configuration and Tuning

### Performance Tuning
- **Small repos**: Use default settings
- **Large repos**: Increase `--batch-size` to 64-128  
- **Memory constrained**: Reduce `--batch-size` to 8-16
- **High precision**: Increase `--threshold` to 0.6+
- **Broad search**: Lower `--threshold` to 0.2-0.4

### Model Selection
- **Default**: `sentence-transformers/all-MiniLM-L6-v2` (fast, balanced)
- **Higher accuracy**: `sentence-transformers/all-mpnet-base-v2` (slower)
- **Faster processing**: `sentence-transformers/all-MiniLM-L12-v2`

For detailed configuration options, see [configuration.md](references/configuration.md).

## Integration Patterns

### LLM Workflow Integration
1. **Context Building**: Use search results to provide relevant code context
2. **Pattern Analysis**: Search for examples to inform implementation decisions  
3. **Change Planning**: Use impact analysis for refactoring guidance
4. **Code Review**: Find similar implementations for consistency checking

### Multi-Stage Analysis
1. **Broad Search**: Initial exploration with low thresholds
2. **Focused Search**: Narrow down with higher thresholds and filters
3. **Impact Assessment**: Analyze dependencies for identified elements
4. **Recommendation**: Combine findings for informed decisions

## Best Practices

### Indexing Best Practices
- Re-index after significant codebase changes
- Use descriptive cache names for different projects
- Consider memory constraints when setting batch sizes
- Use file-specific indexing for temporary analysis

### Search Best Practices  
- Start broad, then narrow with thresholds and filters
- Use file extension filters for language-specific searches
- Combine different search modes for comprehensive analysis
- Validate important findings with direct code inspection

### Integration Best Practices
- Provide context about search purpose in LLM prompts
- Use search results to inform rather than replace analysis
- Combine with traditional code analysis tools
- Include similarity scores in analysis when relevant

## Troubleshooting

### Common Issues
- **Memory errors**: Reduce batch size
- **Poor results**: Lower similarity threshold, rephrase query
- **Missing results**: Check file extensions, verify indexing
- **Slow performance**: Use file extension filters, smaller result sets

For detailed troubleshooting, see [configuration.md](references/configuration.md).

## References

### Detailed Use Cases
See [use_cases.md](references/use_cases.md) for comprehensive examples of each use case with LLM integration patterns.

### Configuration Guide  
See [configuration.md](references/configuration.md) for detailed performance tuning, model selection, and troubleshooting guidance.