#!/usr/bin/env python3
"""
CodeSense Search Script

Searches indexed codebases and files for semantic matches.
Supports various search modes for different use cases.
"""

import argparse
import json
import sys
from pathlib import Path

# Add the skill directory to the path so we can import codesense_core
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from codesense_core import CodeSenseEngine, find_git_root


def format_results(results, format_type="text", show_score=True):
    """Format search results for display."""
    if format_type == "json":
        # Convert results to JSON-serializable format
        json_results = []
        for score, item in results:
            result_item = item.copy()
            result_item["similarity_score"] = score
            json_results.append(result_item)
        return json.dumps(json_results, indent=2)

    elif format_type == "text":
        output = []
        for i, (score, item) in enumerate(results, 1):
            output.append(f"\n🔍 Result {i}")
            if show_score:
                output.append(f"   Similarity: {score:.3f}")

            file_path = item.get("file", "unknown")
            if "line" in item:
                output.append(f"   Location: {file_path}:{item['line']}")
            else:
                output.append(f"   File: {file_path}")

            if "name" in item and item["name"] != "unnamed":
                output.append(f"   Name: {item['name']}")

            if "type" in item:
                output.append(f"   Type: {item['type']}")

            # Show code preview
            text = item.get("text", "")
            if len(text) > 200:
                text = text[:200] + "..."
            output.append(f"   Preview:\n{text}")
            output.append("   " + "─" * 50)

        return "\n".join(output)

    return str(results)


def main():
    parser = argparse.ArgumentParser(
        description="Search indexed codebases for semantic matches"
    )
    parser.add_argument(
        "query",
        type=str,
        help="Search query (natural language describing what to find)",
    )
    parser.add_argument(
        "--path",
        type=str,
        help="Path to repository (auto-detects git root if not specified)",
    )
    parser.add_argument(
        "--cache",
        type=str,
        default=".codesense_cache",
        help="Cache file name (default: .codesense_cache)",
    )
    parser.add_argument(
        "--results",
        "-k",
        type=int,
        default=10,
        help="Number of results to return (default: 10)",
    )
    parser.add_argument(
        "--extension",
        "-e",
        type=str,
        help="Filter by file extension (e.g., 'py', 'js')",
    )
    parser.add_argument(
        "--threshold",
        "-t",
        type=float,
        default=0.0,
        help="Minimum similarity threshold (0.0-1.0, default: 0.0)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Sentence transformer model to use",
    )
    parser.add_argument(
        "--mode",
        choices=["search", "similar", "impact"],
        default="search",
        help="Search mode: search (semantic), similar (find similar functions), impact (impact analysis)",
    )
    parser.add_argument(
        "--reference",
        type=str,
        help="Reference code for similarity search (use with --mode similar)",
    )
    parser.add_argument(
        "--context",
        type=str,
        default="",
        help="Additional context for impact analysis (use with --mode impact)",
    )

    args = parser.parse_args()

    try:
        # Initialize the engine
        engine = CodeSenseEngine(model_name=args.model)

        # Determine cache path
        if args.path:
            cache_path = Path(args.path) / args.cache
        else:
            repo_path = find_git_root()
            if repo_path:
                cache_path = Path(repo_path) / args.cache
            else:
                cache_path = Path(args.cache)

        # Load the index
        if not cache_path.exists():
            print(f"❌ No index found at {cache_path}")
            print("Run the indexing script first to create an index.")
            return 1

        print(f"Loading index from {cache_path}...")
        if not engine._load_cache_from_path(str(cache_path)):
            print("❌ Failed to load index")
            return 1

        # Perform search based on mode
        results = []

        if args.mode == "search":
            results = engine.search(
                query=args.query,
                k=args.results,
                file_extension=args.extension,
                similarity_threshold=args.threshold,
            )

        elif args.mode == "similar":
            if not args.reference:
                print("❌ --reference is required for similarity search")
                return 1

            results = engine.find_similar_functions(
                reference_function=args.reference,
                k=args.results,
                similarity_threshold=max(
                    args.threshold, 0.5
                ),  # Higher threshold for similarity
            )

        elif args.mode == "impact":
            results = engine.analyze_impact(
                symbol_name=args.query,
                context=args.context,
            )

        # Display results
        if not results:
            print("🔍 No matches found.")
            return 0

        print(f"\n🎯 Found {len(results)} matches:")
        print(format_results(results, args.format))

        return 0

    except Exception as e:
        print(f"❌ Error during search: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
