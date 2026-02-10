#!/usr/bin/env python3
"""
CodeSense Quick Demo

A lightweight demo version that shows CodeSense functionality without heavy ML dependencies.
Uses a simple text-based similarity approach for demonstration.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter


def find_git_root(path=None):
    """Find git repository root directory."""
    if not path:
        path = os.getcwd()

    try:
        result = subprocess.run(
            ["git", "-C", path, "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def extract_functions_simple(file_path: str) -> List[Dict]:
    """Simple function extraction using regex patterns."""
    functions = []

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Python function pattern
        if file_path.endswith(".py"):
            pattern = r"^(def\s+\w+.*?):.*?(?=\n(?:def|class|\Z))"
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)

            for match in matches:
                func_text = match.group(0)
                lines = func_text.split("\n")

                functions.append(
                    {
                        "file": file_path,
                        "line": content[: match.start()].count("\n") + 1,
                        "text": func_text[:500]
                        + ("..." if len(func_text) > 500 else ""),
                        "type": "function_definition",
                        "name": re.search(r"def\s+(\w+)", func_text).group(1)
                        if re.search(r"def\s+(\w+)", func_text)
                        else "unnamed",
                    }
                )

        # JavaScript function patterns
        elif file_path.endswith((".js", ".ts")):
            patterns = [
                r"function\s+(\w+)\s*\([^)]*\)\s*\{[^}]*\}",
                r"const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*\{[^}]*\}",
                r"(\w+)\s*:\s*function\s*\([^)]*\)\s*\{[^}]*\}",
            ]

            for pattern in patterns:
                matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
                for match in matches:
                    func_text = match.group(0)
                    name = match.group(1) if match.groups() else "unnamed"

                    functions.append(
                        {
                            "file": file_path,
                            "line": content[: match.start()].count("\n") + 1,
                            "text": func_text[:500]
                            + ("..." if len(func_text) > 500 else ""),
                            "type": "function_definition",
                            "name": name,
                        }
                    )

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

    return functions


def simple_similarity(query: str, text: str) -> float:
    """Simple text similarity based on word overlap."""
    query_words = set(query.lower().split())
    text_words = set(text.lower().split())

    if not query_words:
        return 0.0

    intersection = query_words & text_words
    union = query_words | text_words

    # Jaccard similarity with query bias
    jaccard = len(intersection) / len(union) if union else 0.0
    query_coverage = len(intersection) / len(query_words)

    return (jaccard * 0.3) + (query_coverage * 0.7)


def demo_index_repository(repo_path: str = None) -> List[Dict]:
    """Demo indexing function."""
    if repo_path is None:
        repo_path = find_git_root()
        if not repo_path:
            raise ValueError("No git repository found.")

    print(f"🔍 Demo indexing: {repo_path}")

    # Get Python and JavaScript files
    try:
        git_files = (
            subprocess.run(
                ["git", "-C", repo_path, "ls-files"],
                capture_output=True,
                text=True,
                check=True,
            )
            .stdout.strip()
            .split("\n")
        )
    except subprocess.CalledProcessError:
        raise ValueError(f"{repo_path} is not a git repository")

    all_functions = []

    for relative_path in git_files:
        if not relative_path:
            continue

        file_path = os.path.join(repo_path, relative_path)
        if not os.path.isfile(file_path):
            continue

        if file_path.endswith((".py", ".js", ".ts")):
            functions = extract_functions_simple(file_path)
            all_functions.extend(functions)

    print(f"✅ Found {len(all_functions)} functions")
    return all_functions


def demo_search(
    functions: List[Dict], query: str, k: int = 10
) -> List[Tuple[float, Dict]]:
    """Demo search function."""
    results = []

    for func in functions:
        # Combine function name, text, and file for search
        searchable_text = f"{func['name']} {func['text']} {func['file']}"
        similarity = simple_similarity(query, searchable_text)

        if similarity > 0.1:  # Basic threshold
            results.append((similarity, func))

    # Sort by similarity and return top k
    results.sort(key=lambda x: x[0], reverse=True)
    return results[:k]


def main():
    print("🎯 CodeSense Quick Demo")
    print("=" * 40)

    try:
        # Index repository
        functions = demo_index_repository()

        # Test search for "pdf"
        print(f"\n🔍 Searching for 'pdf'...")
        results = demo_search(functions, "pdf", k=10)

        if not results:
            print("❌ No matches found for 'pdf'")
            return

        print(f"✅ Found {len(results)} matches:")
        print("=" * 40)

        for i, (score, func) in enumerate(results, 1):
            print(f"\n🔍 Result {i}")
            print(f"   Similarity: {score:.3f}")
            print(f"   Location: {func['file']}:{func['line']}")
            print(f"   Name: {func['name']}")
            print(f"   Type: {func['type']}")
            print(f"   Preview:\n{func['text'][:200]}...")
            print("   " + "─" * 50)

        return results

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    main()
