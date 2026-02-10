# CodeSense Use Cases and Patterns

This reference provides detailed examples of how to use CodeSense for different scenarios.

## Use Case 1: Guideline Search - Finding Patterns in Codebase

**Scenario:** Agent is searching for patterns in codebase to understand implementation conventions.

**Workflow:**
1. Index the codebase if not already done
2. Search for pattern-related queries
3. Analyze results to understand conventions

**Examples:**

```bash
# Index the repository
python scripts/index.py --path /path/to/repo

# Find error handling patterns
python scripts/search.py "error handling try catch exception" --results 15

# Find authentication patterns
python scripts/search.py "authentication middleware login token" --extension py

# Find database connection patterns
python scripts/search.py "database connection pool setup" --threshold 0.4
```

**LLM Integration Pattern:**
```
Use Case: Pattern Search
Query: {user_query_about_patterns}
Results: {codesense_search_results}

Analyze the search results to identify common patterns and conventions used in this codebase for {pattern_type}. Summarize:
1. Most common approaches used
2. Consistent patterns across different files
3. Best practices evident from the code
4. Recommendations for following established patterns
```

## Use Case 2: Simple Search - Finding Similar Symbols

**Scenario:** Agent is searching for similar symbols in codebase.

**Workflow:**
1. Search for symbols by name or functionality
2. Filter by file extension if needed
3. Get detailed information about each match

**Examples:**

```bash
# Find all functions related to parsing
python scripts/search.py "parse parser parsing" --results 20

# Find configuration-related code
python scripts/search.py "config configuration settings" --extension js

# Find test utilities
python scripts/search.py "test utility helper mock" --extension py --threshold 0.3
```

**LLM Integration Pattern:**
```
Use Case: Symbol Search
Query: {symbol_or_functionality}
Results: {codesense_search_results}

Based on the search results, provide information about:
1. Available symbols related to {symbol_or_functionality}
2. Their locations and purposes
3. Usage examples from the code
4. Relationships between different implementations
```

## Use Case 3: Impact Analysis - Understanding Dependencies

**Scenario:** Agent needs to understand the impact of changing a specific symbol.

**Workflow:**
1. Use impact analysis mode to find references
2. Search for related functionality
3. Analyze dependencies and usage patterns

**Examples:**

```bash
# Analyze impact of changing a function
python scripts/search.py "calculateTotal" --mode impact --context "payment processing"

# Find usages of a specific class
python scripts/search.py "UserManager" --mode impact --results 25

# Understand API endpoint dependencies
python scripts/search.py "/api/users" --mode impact --context "REST API endpoints"
```

**LLM Integration Pattern:**
```
Use Case: Impact Analysis
Symbol: {symbol_name}
Context: {additional_context}
Results: {codesense_impact_results}

Analyze the impact of modifying {symbol_name}:
1. Direct dependencies and references found
2. Potential side effects of changes
3. Areas of the codebase that would be affected
4. Recommended testing strategy
5. Refactoring considerations
```

## Use Case 4: DRY Analysis - Finding Similar Implementations

**Scenario:** Agent is looking for similar implementations in a large monorepo to identify code duplication.

**Workflow:**
1. Use similarity search with reference code
2. Set appropriate similarity thresholds
3. Identify refactoring opportunities

**Examples:**

```bash
# Find similar functions to a reference implementation
python scripts/search.py --mode similar --reference "$(cat reference_function.py)" --threshold 0.7

# Find duplicate validation logic
python scripts/search.py "validation validate input check" --threshold 0.6 --results 30

# Identify similar error handling
python scripts/search.py --mode similar --reference "def handle_error(error):" --threshold 0.5
```

**LLM Integration Pattern:**
```
Use Case: DRY Analysis  
Reference Code: {reference_implementation}
Similar Functions: {similarity_search_results}

Identify opportunities for code reuse and deduplication:
1. Functions with high similarity scores that could be consolidated
2. Common patterns that could be extracted into utilities
3. Differences between similar implementations
4. Suggested refactoring approach
5. Potential shared library or utility functions
```

## Use Case 5: Quick ANY Indexing - Temporary Files Analysis

**Scenario:** Agent prepares big temporary files (logs, git history) for analysis.

**Workflow:**
1. Index arbitrary files (logs, documentation, git history)
2. Search through indexed content
3. Extract insights and patterns

**Examples:**

```bash
# Index log files for analysis
python scripts/index.py --files /tmp/application.log /tmp/error.log --cache .log_cache

# Index git commit history
git log --oneline > /tmp/git_history.txt
python scripts/index.py --files /tmp/git_history.txt --cache .git_cache

# Index documentation files
python scripts/index.py --files docs/*.md README.md --cache .docs_cache --chunk-size 500

# Search through indexed logs
python scripts/search.py "error exception failed" --cache .log_cache --results 20

# Search through git history
python scripts/search.py "feature authentication" --cache .git_cache --results 10
```

**LLM Integration Pattern:**
```
Use Case: Temporary File Analysis
File Types: {file_types_indexed}
Query: {analysis_query}
Results: {search_results_from_temp_files}

Analyze the temporary file content:
1. Key patterns and trends identified
2. Relevant information related to {analysis_query}
3. Insights and correlations found
4. Actionable recommendations
5. Areas requiring further investigation
```

## Advanced Workflow Patterns

### Multi-Stage Analysis
```bash
# Stage 1: Initial broad search
python scripts/search.py "authentication" --results 50 > auth_functions.json

# Stage 2: Focused search on specific extension  
python scripts/search.py "JWT token validation" --extension py --threshold 0.5

# Stage 3: Impact analysis for specific functions
python scripts/search.py "validateToken" --mode impact --context "JWT authentication"
```

### Comparative Analysis
```bash
# Compare implementations across different languages
python scripts/search.py "user validation" --extension py --results 10
python scripts/search.py "user validation" --extension js --results 10  
python scripts/search.py "user validation" --extension java --results 10
```

### Progressive Refinement
```bash
# Start broad, then narrow down
python scripts/search.py "database" --results 100 --threshold 0.2
python scripts/search.py "database connection pool" --results 20 --threshold 0.5
python scripts/search.py "database transaction management" --results 10 --threshold 0.7
```

## Integration with LLM Workflows

### Pattern Recognition Workflow
1. **Index**: Ensure codebase is indexed
2. **Search**: Find relevant code patterns
3. **Analyze**: Use LLM to identify patterns and conventions
4. **Apply**: Use insights to guide development decisions

### Refactoring Workflow  
1. **Identify**: Use similarity search to find duplicate code
2. **Compare**: Analyze differences between similar implementations
3. **Plan**: Design refactoring strategy with LLM assistance
4. **Validate**: Use impact analysis to understand change implications

### Code Review Workflow
1. **Context**: Index the codebase being reviewed
2. **Search**: Find related implementations and patterns
3. **Compare**: Check consistency with existing code
4. **Recommend**: Use findings to provide informed review feedback

## Best Practices

### Indexing Best Practices
- Re-index after significant codebase changes
- Use appropriate cache names for different projects
- Consider batch sizes based on available memory
- Use file indexing for temporary analysis tasks

### Search Best Practices
- Start with broad searches, then narrow down
- Adjust similarity thresholds based on use case
- Use file extension filters for language-specific searches  
- Combine multiple search modes for comprehensive analysis

### Integration Best Practices
- Include context in LLM prompts about the search purpose
- Use search results to inform rather than replace analysis
- Combine CodeSense results with traditional code analysis tools
- Validate findings with actual code inspection when needed