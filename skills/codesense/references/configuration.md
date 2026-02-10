# CodeSense Configuration and Tuning Guide

This reference provides detailed configuration options and tuning guidance for optimal CodeSense performance.

## Core Configuration Options

### Model Selection

**Default Model:** `sentence-transformers/all-MiniLM-L6-v2`
- Fast and efficient for most use cases
- Good balance of speed and accuracy
- Small download size (80MB)

**Alternative Models:**
```bash
# More accurate but slower
--model sentence-transformers/all-mpnet-base-v2

# Faster but less accurate  
--model sentence-transformers/all-MiniLM-L12-v2

# Code-specific model (if available)
--model microsoft/codebert-base
```

### Batch Size Tuning

**Memory vs Speed Trade-offs:**

```bash
# Low memory systems (4GB RAM)
--batch-size 8

# Standard systems (8-16GB RAM)  
--batch-size 32

# High memory systems (32GB+ RAM)
--batch-size 128
```

**Guidelines:**
- Larger batch sizes = faster processing but more memory
- Reduce batch size if you encounter out-of-memory errors
- Optimal batch size depends on model and system specifications

### Similarity Thresholds

**Use Case-Based Thresholds:**

```bash
# Broad exploration (find many potential matches)
--threshold 0.1

# General search (balanced precision/recall)
--threshold 0.3

# Precise matching (high confidence results only)
--threshold 0.7

# Near-duplicate detection
--threshold 0.8
```

**Threshold Selection Guide:**
- **0.0-0.2**: Very broad, may include loosely related matches
- **0.2-0.4**: Good for exploratory searches
- **0.4-0.6**: Balanced for most use cases
- **0.6-0.8**: High precision, fewer false positives
- **0.8-1.0**: Near-duplicates and very similar code

### Cache Management

**Cache Naming Strategies:**
```bash
# Project-specific caches
--cache .codesense_myproject

# Feature-specific caches
--cache .codesense_auth_module  

# Temporary analysis caches
--cache /tmp/logs_analysis_cache

# Version-specific caches
--cache .codesense_v2.1.0
```

**Cache Best Practices:**
- Use descriptive cache names for multiple projects
- Store caches in project root for team sharing
- Clean up temporary caches after analysis
- Re-index when codebase changes significantly

## Performance Optimization

### Indexing Performance

**Large Repository Strategies:**
```bash
# Progressive indexing with smaller batches
python scripts/index.py --batch-size 16 --stats

# Force clean rebuild
python scripts/index.py --force --batch-size 64

# Memory monitoring during indexing
python scripts/index.py --batch-size 32 --stats
```

**Filtering Strategies:**
- Focus on relevant directories only
- Exclude test files and generated code when appropriate
- Use include/exclude patterns (future feature)

### Search Performance  

**Query Optimization:**
```bash
# Limit results for faster responses
python scripts/search.py "query" --results 5

# Use file extension filters
python scripts/search.py "query" --extension py

# Combine with thresholds
python scripts/search.py "query" --threshold 0.4 --results 20
```

**Response Time Expectations:**
- Index loading: 1-5 seconds for typical repositories
- Query processing: 0.1-2 seconds depending on index size
- Result formatting: Negligible impact

## Language-Specific Configuration

### Supported Languages and Extensions

**Tier 1 (Full Support):**
- Python (.py) - `python`
- JavaScript (.js, .jsx) - `javascript`  
- TypeScript (.ts, .tsx) - `typescript`
- Java (.java) - `java`

**Tier 2 (Good Support):**
- Go (.go) - `go`
- Rust (.rs) - `rust`
- C/C++ (.c, .h, .cpp, .hpp, .cc, .cxx) - `c`/`cpp`
- C# (.cs) - `c_sharp`

**Tier 3 (Basic Support):**
- Ruby (.rb) - `ruby`
- PHP (.php) - `php`
- Swift (.swift) - `swift`
- Kotlin (.kt) - `kotlin`
- Scala (.scala) - `scala`

### Language-Specific Search Tips

**Python:**
```bash
# Find class definitions
python scripts/search.py "class definition" --extension py

# Find async/await patterns
python scripts/search.py "async await asynchronous" --extension py
```

**JavaScript/TypeScript:**
```bash
# Find React components  
python scripts/search.py "React component" --extension jsx --extension tsx

# Find async functions
python scripts/search.py "async function promise" --extension js
```

**Java:**
```bash
# Find interface implementations
python scripts/search.py "implements interface" --extension java

# Find exception handling
python scripts/search.py "try catch exception" --extension java
```

## System Requirements and Scaling

### Minimum Requirements
- **RAM**: 4GB (with batch-size 8)
- **Storage**: 1GB free space for models and caches
- **Python**: 3.8+
- **Dependencies**: torch, sentence-transformers, tree-sitter-languages

### Recommended Configuration
- **RAM**: 8GB+ (batch-size 32)
- **CPU**: Multi-core for faster embedding generation
- **Storage**: SSD for faster cache loading
- **GPU**: Optional, provides 2-5x speedup for large repositories

### Scaling Guidelines

**Repository Size Scaling:**
- **Small** (< 1,000 functions): Default settings work well
- **Medium** (1,000-10,000 functions): Consider batch-size 64
- **Large** (10,000+ functions): Use batch-size 128+, monitor memory

**Team Usage Scaling:**
- Share cache files in project repositories
- Use consistent model versions across team
- Consider dedicated indexing server for very large codebases

## Troubleshooting Common Issues

### Memory Issues
```bash
# Error: CUDA out of memory / RAM exceeded
# Solution: Reduce batch size
python scripts/index.py --batch-size 8

# Error: Process killed during indexing
# Solution: Index in smaller chunks or increase system memory
```

### Performance Issues
```bash
# Slow indexing
# Check: Model download, use faster model, reduce batch size
python scripts/index.py --model sentence-transformers/all-MiniLM-L12-v2

# Slow search
# Check: Large index, use file extension filters, increase threshold
python scripts/search.py "query" --extension py --threshold 0.4
```

### Accuracy Issues
```bash
# Poor search results
# Solution: Lower threshold, try different query phrasing
python scripts/search.py "alternative query phrasing" --threshold 0.2

# Missing expected results
# Solution: Check if files were indexed, verify file extensions
python scripts/index.py --stats
```

### Cache Issues
```bash
# Corrupted cache
# Solution: Force re-indexing
python scripts/index.py --force

# Model mismatch
# Solution: Use consistent model or rebuild cache
python scripts/index.py --model sentence-transformers/all-MiniLM-L6-v2 --force
```

## Advanced Configuration

### Custom Model Integration
```python
# For advanced users: Custom model configuration
from codesense_core import CodeSenseEngine

# Use custom model
engine = CodeSenseEngine(model_name="path/to/custom/model")

# Custom similarity functions (future enhancement)
# engine.set_similarity_function(custom_similarity_fn)
```

### Integration with CI/CD
```bash
# Automated indexing in CI pipeline
#!/bin/bash
python scripts/index.py --force --batch-size 32 --stats
if [ $? -eq 0 ]; then
    echo "Indexing successful"
    # Cache can be used by team members
else
    echo "Indexing failed"
    exit 1
fi
```

### Monitoring and Metrics
```bash
# Get index statistics
python scripts/index.py --stats

# Monitor search performance
time python scripts/search.py "performance test query" --results 10

# Cache size monitoring
du -sh .codesense_cache
```

This configuration guide provides comprehensive tuning options for different use cases, system constraints, and performance requirements.