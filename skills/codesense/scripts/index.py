#!/usr/bin/env python3
"""
CodeSense Indexing Script

Indexes codebases and arbitrary files for semantic search.
Supports various indexing modes and configuration options.
"""

import argparse
import sys
from pathlib import Path

# Add the skill directory to the path so we can import codesense_core
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from codesense_core import CodeSenseEngine, find_git_root


def main():
    parser = argparse.ArgumentParser(
        description="Index codebases and files for semantic search"
    )
    parser.add_argument(
        "--path",
        type=str,
        help="Path to repository or directory (auto-detects git root if not specified)",
    )
    parser.add_argument(
        "--files", nargs="+", help="Specific files to index (for log files, docs, etc.)"
    )
    parser.add_argument(
        "--cache",
        type=str,
        default=".codesense_cache",
        help="Cache file name (default: .codesense_cache)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for embedding generation (default: 32)",
    )
    parser.add_argument(
        "--force", action="store_true", help="Force re-indexing, ignore existing cache"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Chunk size for large files (default: 1000 characters)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Sentence transformer model to use",
    )
    parser.add_argument(
        "--stats", action="store_true", help="Show statistics after indexing"
    )

    args = parser.parse_args()

    try:
        # Initialize the engine
        engine = CodeSenseEngine(model_name=args.model)

        if args.files:
            # Index specific files
            print(f"Indexing {len(args.files)} files...")
            engine.index_files(
                files=args.files,
                cache_file=args.cache,
                batch_size=args.batch_size,
                force_reindex=args.force,
                chunk_size=args.chunk_size,
            )
        else:
            # Index codebase
            repo_path = args.path
            if not repo_path:
                repo_path = find_git_root()
                if not repo_path:
                    print("Error: No git repository found. Specify --path explicitly.")
                    return 1

            print(f"Indexing codebase at: {repo_path}")
            engine.index_codebase(
                repo_path=repo_path,
                cache_file=args.cache,
                batch_size=args.batch_size,
                force_reindex=args.force,
            )

        print("✅ Indexing completed successfully!")

        if args.stats:
            stats = engine.get_stats()
            print("\n📊 Index Statistics:")
            print(f"  Items indexed: {stats['indexed_items']}")
            print(f"  Model: {stats['model']}")
            print(f"  Index type: {stats['index_type']}")
            if stats.get("repo_path"):
                print(f"  Repository: {stats['repo_path']}")
            if stats.get("file_distribution"):
                print("  File distribution:")
                for ext, count in sorted(stats["file_distribution"].items()):
                    print(f"    {ext}: {count}")

        return 0

    except Exception as e:
        print(f"❌ Error during indexing: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
