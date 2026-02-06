#!/usr/bin/env python3
"""
Analyze markdown structure and propose split strategies.
"""
import sys
import re
import argparse
from pathlib import Path
from collections import defaultdict


def analyze_structure(markdown_content):
    """Analyze document structure for split strategies."""
    lines = markdown_content.split('\n')
    
    # Count headings by level
    heading_counts = defaultdict(int)
    heading_samples = defaultdict(list)
    
    heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
    
    for line in lines:
        match = heading_pattern.match(line)
        if match:
            hashes, title = match.groups()
            level = len(hashes)
            heading_counts[level] += 1
            if len(heading_samples[level]) < 5:
                heading_samples[level].append(title.strip())
    
    return heading_counts, heading_samples


def main():
    parser = argparse.ArgumentParser(description="Analyze markdown structure for splitting")
    parser.add_argument("markdown_file", help="Input markdown file")
    args = parser.parse_args()
    
    md_path = Path(args.markdown_file)
    if not md_path.exists():
        print(f"ERROR: File not found: {md_path}", file=sys.stderr)
        sys.exit(1)
    
    content = md_path.read_text(encoding='utf-8')
    heading_counts, heading_samples = analyze_structure(content)
    
    if not heading_counts:
        print("No headings found in document")
        return
    
    print("Document Structure Analysis\n")
    print("Heading Levels:")
    for level in sorted(heading_counts.keys()):
        print(f"  H{level}: {heading_counts[level]} heading(s)")
    
    print("\n" + "="*60 + "\n")
    print("Sample Headings:\n")
    
    for level in sorted(heading_counts.keys()):
        print(f"H{level} Examples:")
        for sample in heading_samples[level]:
            print(f"  {'#' * level} {sample}")
        print()
    
    print("="*60 + "\n")
    print("Suggested Split Strategies:\n")
    
    # Suggest strategies
    strategies = []
    
    if heading_counts.get(1, 0) > 0:
        strategies.append({
            'name': 'Split on H1 (Main Chapters)',
            'command': f'split_markdown.py {args.markdown_file} --heading-level 1',
            'result': f'~{heading_counts[1]} files'
        })
    
    if heading_counts.get(2, 0) > 0:
        strategies.append({
            'name': 'Split on H2 (Sections)',
            'command': f'split_markdown.py {args.markdown_file} --heading-level 2',
            'result': f'~{heading_counts[2]} files'
        })
    
    if heading_counts.get(3, 0) > 0:
        strategies.append({
            'name': 'Split on H3 (Subsections)',
            'command': f'split_markdown.py {args.markdown_file} --heading-level 3',
            'result': f'~{heading_counts[3]} files'
        })
    
    # Check for numbered sections
    has_numbered = any(re.match(r'^\d+\.', sample) for samples in heading_samples.values() for sample in samples)
    if has_numbered:
        strategies.append({
            'name': 'Split on Numbered Sections (e.g., "1. ", "2. ")',
            'command': f'split_markdown.py {args.markdown_file} --pattern "^#+ \\d+\\. " --extract-title "(\\d+\\. .+)$"',
            'result': 'Files numbered by section'
        })
    
    for i, strategy in enumerate(strategies, 1):
        print(f"{i}. {strategy['name']}")
        print(f"   Command: {strategy['command']}")
        print(f"   Result: {strategy['result']}")
        print()
    
    if not strategies:
        print("No clear split points detected. Document may not have structured headings.")


if __name__ == "__main__":
    main()
