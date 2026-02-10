"""
Codesense Core - Production-ready semantic code search engine
Adapted from the semantic search PoC with enhancements for production use.
"""

import gzip
import json
import os
import pickle
import subprocess
import sys
from pathlib import Path
from textwrap import dedent
from typing import List, Dict, Tuple, Optional

import torch
import numpy as np
from sentence_transformers import SentenceTransformer, util


def find_git_root(path: Optional[str] = None) -> Optional[str]:
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


class CodeSenseEngine:
    """
    Production-ready semantic code search engine for codebase understanding.

    Features:
    - Semantic indexing of code functions and classes
    - Pattern search for finding similar implementations
    - Impact analysis through dependency mapping
    - Support for arbitrary file indexing (logs, docs, etc.)
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.functions = []
        self.embeddings = None
        self.index_metadata = {}

        # Supported languages with tree-sitter parsers
        self.file_extensions = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".c": "c",
            ".h": "c",
            ".cpp": "cpp",
            ".hpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".cs": "c_sharp",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
        }

        # Code node types to extract
        self.node_types = [
            "function_definition",
            "method_definition",
            "function_declaration",
            "method_declaration",
            "class_definition",
            "class_declaration",
            "interface_declaration",
            "enum_declaration",
            "struct_declaration",
        ]

    def index_codebase(
        self,
        repo_path: Optional[str] = None,
        cache_file: str = ".codesense_cache",
        batch_size: int = 32,
        force_reindex: bool = False,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> "CodeSenseEngine":
        """
        Index all code functions and classes in a repository.

        Args:
            repo_path: Repository path (auto-detects git root if None)
            cache_file: Cache filename (default: .codesense_cache)
            batch_size: Batch size for embedding generation
            force_reindex: Skip cache and re-index from scratch
            include_patterns: Glob patterns to include (e.g., ['src/**/*.py'])
            exclude_patterns: Glob patterns to exclude (e.g., ['**/test_*.py'])
        """
        # Auto-detect git repository
        if repo_path is None:
            repo_path = find_git_root()
            if not repo_path:
                raise ValueError(
                    "No git repository found. Specify repo_path explicitly."
                )

        print(f"Indexing codebase in {repo_path}")

        # Try to load cache first unless force_reindex is True
        if not force_reindex and self._load_cache(repo_path, cache_file):
            return self

        # Extract all functions and classes
        self.functions = []
        self.index_metadata = {
            "repo_path": repo_path,
            "model_name": self.model_name,
            "index_type": "codebase",
            "patterns": {
                "include": include_patterns,
                "exclude": exclude_patterns,
            },
        }

        files_to_process = self._get_code_files(
            repo_path, include_patterns, exclude_patterns
        )

        for file_path in files_to_process:
            self._process_code_file(file_path, repo_path)

        if not self.functions:
            raise ValueError(f"No code functions found in {repo_path}")

        print(f"Found {len(self.functions)} code elements")
        return self._generate_embeddings_and_cache(repo_path, cache_file, batch_size)

    def index_files(
        self,
        files: List[str],
        cache_file: str = ".codesense_files_cache",
        batch_size: int = 32,
        force_reindex: bool = False,
        chunk_size: int = 1000,
    ) -> "CodeSenseEngine":
        """
        Index arbitrary files (logs, docs, git history, etc.).

        Args:
            files: List of file paths to index
            cache_file: Cache filename
            batch_size: Batch size for embedding generation
            force_reindex: Skip cache and re-index from scratch
            chunk_size: Characters per chunk for large files
        """
        print(f"Indexing {len(files)} files")

        # Try to load cache first
        cache_path = cache_file
        if not force_reindex and self._load_file_cache(cache_path):
            return self

        self.functions = []
        self.index_metadata = {
            "files": files,
            "model_name": self.model_name,
            "index_type": "files",
            "chunk_size": chunk_size,
        }

        for file_path in files:
            self._process_text_file(file_path, chunk_size)

        if not self.functions:
            raise ValueError("No content found in provided files")

        print(f"Created {len(self.functions)} text chunks")
        return self._generate_embeddings_and_cache_files(cache_path, batch_size)

    def search(
        self,
        query: str,
        k: int = 10,
        file_extension: Optional[str] = None,
        similarity_threshold: float = 0.0,
    ) -> List[Tuple[float, Dict]]:
        """
        Search for semantically similar code or content.

        Args:
            query: Natural language query describing what to find
            k: Number of results to return
            file_extension: Filter by file extension (e.g., "py", "js")
            similarity_threshold: Minimum similarity score (0.0 to 1.0)

        Returns:
            List of (similarity_score, content_info) tuples
        """
        if self.embeddings is None:
            raise ValueError(
                "No index loaded. Call index_codebase() or index_files() first."
            )

        # Encode query
        query_embedding = self.model.encode(query, convert_to_tensor=True)

        # Filter functions if needed
        filtered_functions, filtered_embeddings = self._filter_results(
            file_extension, similarity_threshold, query_embedding
        )

        if not filtered_functions:
            return []

        # Cosine similarity search
        cos_scores = util.cos_sim(query_embedding, filtered_embeddings)[0]
        top_results = torch.topk(cos_scores, k=min(k, len(cos_scores)), sorted=True)

        # Return results
        results = []
        for score, idx in zip(top_results[0], top_results[1]):
            if float(score) >= similarity_threshold:
                results.append((float(score), filtered_functions[idx]))

        return results

    def find_similar_functions(
        self,
        reference_function: str,
        k: int = 10,
        similarity_threshold: float = 0.7,
    ) -> List[Tuple[float, Dict]]:
        """
        Find functions similar to a reference function (for DRY analysis).

        Args:
            reference_function: Code text of the reference function
            k: Number of similar functions to find
            similarity_threshold: Minimum similarity for matches
        """
        if self.embeddings is None:
            raise ValueError("No index loaded. Call index_codebase() first.")

        # Encode the reference function
        ref_embedding = self.model.encode(reference_function, convert_to_tensor=True)

        # Calculate similarities
        cos_scores = util.cos_sim(ref_embedding, self.embeddings)[0]
        top_results = torch.topk(cos_scores, k=min(k, len(cos_scores)), sorted=True)

        # Return results above threshold
        results = []
        for score, idx in zip(top_results[0], top_results[1]):
            if float(score) >= similarity_threshold:
                results.append((float(score), self.functions[idx]))

        return results

    def analyze_impact(
        self,
        symbol_name: str,
        context: str = "",
    ) -> List[Tuple[float, Dict]]:
        """
        Analyze impact of a symbol by finding references and related code.

        Args:
            symbol_name: Name of function/class/variable to analyze
            context: Additional context about the symbol
        """
        query = f"function {symbol_name} call usage reference {context}"
        return self.search(query, k=20, similarity_threshold=0.3)

    def get_stats(self) -> Dict:
        """Get statistics about the current index."""
        if not self.functions:
            return {"indexed_items": 0, "status": "empty"}

        file_counts = {}
        for func in self.functions:
            file_path = func.get("file", "unknown")
            ext = Path(file_path).suffix or "no_ext"
            file_counts[ext] = file_counts.get(ext, 0) + 1

        return {
            "indexed_items": len(self.functions),
            "model": self.model_name,
            "index_type": self.index_metadata.get("index_type", "unknown"),
            "file_distribution": file_counts,
            "repo_path": self.index_metadata.get("repo_path"),
        }

    def _get_code_files(
        self,
        repo_path: str,
        include_patterns: Optional[List[str]],
        exclude_patterns: Optional[List[str]],
    ) -> List[str]:
        """Get list of code files to process."""
        try:
            # Get all git-tracked files
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

        files_to_process = []
        for relative_path in git_files:
            if not relative_path:
                continue

            file_path = os.path.join(repo_path, relative_path)
            if not os.path.isfile(file_path):
                continue

            # Check file extension
            ext = Path(file_path).suffix
            if ext not in self.file_extensions:
                continue

            # TODO: Add pattern filtering logic here if needed
            files_to_process.append(file_path)

        return files_to_process

    def _process_code_file(self, file_path: str, repo_path: str):
        """Process a single code file and extract functions."""
        try:
            # Import tree_sitter_languages here to avoid issues if not installed
            from tree_sitter_languages import get_parser
        except ImportError:
            print(
                "Warning: tree_sitter_languages not available. Install with: pip install tree-sitter-languages"
            )
            return

        ext = Path(file_path).suffix
        language = self.file_extensions.get(ext)

        if not language:
            return

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            parser = get_parser(language)
            tree = parser.parse(bytes(content, "utf8"))

            # Extract functions and classes
            elements = self._extract_code_elements(tree.root_node, file_path, content)
            self.functions.extend(elements)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def _process_text_file(self, file_path: str, chunk_size: int):
        """Process a text file by chunking it."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Split into chunks
            chunks = []
            for i in range(0, len(content), chunk_size):
                chunk = content[i : i + chunk_size]
                if chunk.strip():  # Skip empty chunks
                    chunks.append(
                        {
                            "file": file_path,
                            "chunk": i // chunk_size,
                            "text": chunk.strip(),
                            "type": "text_chunk",
                        }
                    )

            self.functions.extend(chunks)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def _extract_code_elements(self, node, file_path: str, content: str) -> List[Dict]:
        """Extract code elements (functions, classes) from AST."""
        elements = []
        nodes_to_visit = [node]

        while nodes_to_visit:
            current = nodes_to_visit.pop(0)

            if current.type in self.node_types:
                start_line = current.start_point[0]
                end_line = current.end_point[0]

                # Extract element text
                lines = content.split("\n")[start_line : end_line + 1]
                element_text = dedent("\n".join(lines))

                # Try to extract element name
                element_name = self._extract_element_name(current, content)

                elements.append(
                    {
                        "file": file_path,
                        "line": start_line + 1,
                        "text": element_text,
                        "type": current.type,
                        "name": element_name,
                    }
                )

            # Add children to visit
            for child in current.children:
                nodes_to_visit.append(child)

        return elements

    def _extract_element_name(self, node, content: str) -> str:
        """Extract name of code element (function/class name)."""
        # Simple name extraction - could be improved per language
        lines = content.split("\n")
        start_line = node.start_point[0]

        if start_line < len(lines):
            line = lines[start_line]
            # Basic pattern matching for common cases
            for keyword in ["def ", "function ", "class ", "interface "]:
                if keyword in line:
                    parts = line.split(keyword)
                    if len(parts) > 1:
                        name_part = parts[1].split("(")[0].split("{")[0].split(" ")[0]
                        return name_part.strip()

        return "unnamed"

    def _generate_embeddings_and_cache(
        self, repo_path: str, cache_file: str, batch_size: int
    ):
        """Generate embeddings and save to cache."""
        print("Generating embeddings...")
        function_texts = [f["text"] for f in self.functions]
        self.embeddings = self.model.encode(
            function_texts,
            convert_to_tensor=True,
            show_progress_bar=True,
            batch_size=batch_size,
        )

        # Save cache
        cache_path = os.path.join(repo_path, cache_file)
        self._save_cache(cache_path)
        return self

    def _generate_embeddings_and_cache_files(self, cache_path: str, batch_size: int):
        """Generate embeddings for file indexing and save to cache."""
        print("Generating embeddings...")
        function_texts = [f["text"] for f in self.functions]
        self.embeddings = self.model.encode(
            function_texts,
            convert_to_tensor=True,
            show_progress_bar=True,
            batch_size=batch_size,
        )

        self._save_cache(cache_path)
        return self

    def _save_cache(self, cache_path: str):
        """Save embeddings and metadata to cache file."""
        dataset = {
            "functions": self.functions,
            "embeddings": self.embeddings,
            "model_name": self.model_name,
            "metadata": self.index_metadata,
        }

        with gzip.open(cache_path, "wb") as f:
            f.write(pickle.dumps(dataset))

        print(f"Cached embeddings to {cache_path}")

    def _load_cache(self, repo_path: str, cache_file: str) -> bool:
        """Load cached embeddings if available and compatible."""
        cache_path = os.path.join(repo_path, cache_file)
        return self._load_cache_from_path(cache_path)

    def _load_file_cache(self, cache_path: str) -> bool:
        """Load cached embeddings from absolute path."""
        return self._load_cache_from_path(cache_path)

    def _load_cache_from_path(self, cache_path: str) -> bool:
        """Load cache from specific path."""
        if not os.path.exists(cache_path):
            return False

        try:
            with gzip.open(cache_path, "rb") as f:
                dataset = pickle.loads(f.read())

            # Check model compatibility
            if dataset.get("model_name") != self.model_name:
                print("Model mismatch - cache invalid")
                return False

            self.functions = dataset["functions"]
            self.embeddings = dataset["embeddings"]
            self.index_metadata = dataset.get("metadata", {})

            print(f"Loaded {len(self.functions)} cached items")
            return True

        except Exception as e:
            print(f"Error loading cache: {e}")
            return False

    def _filter_results(
        self,
        file_extension: Optional[str],
        similarity_threshold: float,
        query_embedding: torch.Tensor,
    ) -> Tuple[List[Dict], torch.Tensor]:
        """Filter results by file extension and similarity threshold."""
        if file_extension:
            # Normalize extension
            if not file_extension.startswith("."):
                file_extension = "." + file_extension

            # Find matching function indices
            valid_indices = []
            for i, func in enumerate(self.functions):
                file_path = func.get("file", "")
                if file_path.endswith(file_extension):
                    valid_indices.append(i)

            if not valid_indices:
                print(f"No items found with extension '{file_extension}'")
                return [], torch.tensor([])

            # Filter embeddings and functions
            filtered_embeddings = self.embeddings[valid_indices]
            filtered_functions = [self.functions[i] for i in valid_indices]
        else:
            filtered_embeddings = self.embeddings
            filtered_functions = self.functions

        return filtered_functions, filtered_embeddings
