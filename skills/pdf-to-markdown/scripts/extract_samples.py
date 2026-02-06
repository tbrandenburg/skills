#!/usr/bin/env python3
"""
Extract representative samples from markdown document for agent review.
Shows document structure, headings, and potential noise patterns.
"""
import sys
import argparse
from pathlib import Path
from collections import Counter
import re


def extract_samples(markdown_content, lines_per_sample=50, min_repeats=3):
    """Extract samples from different parts of the document."""
    all_lines = markdown_content.split('\n')
    total_lines = len(all_lines)
    
    samples = {}
    
    # Beginning sample
    samples['beginning'] = '\n'.join(all_lines[:lines_per_sample])
    
    # Middle sample
    middle_start = (total_lines // 2) - (lines_per_sample // 2)
    middle_end = middle_start + lines_per_sample
    samples['middle'] = '\n'.join(all_lines[middle_start:middle_end])
    
    # End sample
    samples['end'] = '\n'.join(all_lines[-lines_per_sample:])
    
    # Extract all headings
    heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
    headings = []
    for line in all_lines:
        match = heading_pattern.match(line)
        if match:
            headings.append(line)
    
    samples['headings'] = headings[:50]  # First 50 headings
    
    # Find repeated lines (potential noise) - normalize Unicode variations
    line_counts = Counter()
    for line in all_lines:
        if line.strip():
            # Generic Unicode normalization for better pattern detection
            normalized = line.strip()
            
            # Normalize whitespace characters
            normalized = re.sub(r'[\u00A0\u2000-\u200B\u2028\u2029]', ' ', normalized)  # Various spaces to regular space
            
            # Normalize dash/hyphen variations
            normalized = re.sub(r'[\u2010-\u2015\u2212]', '-', normalized)  # Various dashes to regular hyphen
            
            # Normalize quotation marks
            normalized = re.sub(r'[\u2018\u2019]', "'", normalized)  # Smart single quotes to regular apostrophe  
            normalized = re.sub(r'[\u201C\u201D]', '"', normalized)  # Smart double quotes to regular quotes
            
            # Normalize multiple spaces to single space
            normalized = re.sub(r'\s+', ' ', normalized)
            
            line_counts[normalized] += 1
    
    repeated = [(line, count) for line, count in line_counts.items() 
                if count >= min_repeats and not heading_pattern.match(line)]
    repeated.sort(key=lambda x: x[1], reverse=True)
    
    samples['repeated'] = repeated[:20]  # Top 20 repeated patterns
    
    return samples, total_lines


def main():
    parser = argparse.ArgumentParser(
        description="Extract samples from markdown for review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script helps agents review document structure and identify cleanup needs.
The agent should examine samples for:
  - Wrong heading depths (e.g., ## 3.3.1 should be ###)
  - Headers/footers repeated on every page
  - Page numbers, copyright notices
  - Any document-specific formatting issues
        """
    )
    parser.add_argument("markdown_file", help="Input markdown file")
    parser.add_argument("--lines", type=int, default=50, 
                       help="Lines per sample section (default: 50)")
    parser.add_argument("--min-repeats", type=int, default=3,
                       help="Minimum repeats to show pattern (default: 3)")
    args = parser.parse_args()
    
    md_path = Path(args.markdown_file)
    if not md_path.exists():
        print(f"ERROR: File not found: {md_path}", file=sys.stderr)
        sys.exit(1)
    
    content = md_path.read_text(encoding='utf-8')
    samples, total_lines = extract_samples(content, args.lines, args.min_repeats)
    
    print("=" * 80)
    print(f"DOCUMENT SAMPLES: {md_path.name}")
    print(f"Total lines: {total_lines}")
    print("=" * 80)
    print()
    
    # Beginning
    print("--- BEGINNING (first {} lines) ---".format(args.lines))
    print(samples['beginning'])
    print()
    
    # Middle
    print("--- MIDDLE SECTION ({} lines) ---".format(args.lines))
    print(samples['middle'])
    print()
    
    # End
    print("--- END (last {} lines) ---".format(args.lines))
    print(samples['end'])
    print()
    
    # Headings
    print("=" * 80)
    print(f"HEADING PATTERNS (first {len(samples['headings'])} headings)")
    print("=" * 80)
    for heading in samples['headings']:
        print(heading)
    print()
    
    # Repeated patterns
    if samples['repeated']:
        print("=" * 80)
        print(f"REPEATED LINES (potential noise, appears {args.min_repeats}+ times)")
        print("=" * 80)
        for line, count in samples['repeated']:
            print(f"[{count}x] {line[:70]}")
        print()
    
    print("=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. Review samples above for issues:")
    print("   - Wrong heading depths based on numbering")
    print("   - Headers/footers (repeated lines)")
    print("   - Page numbers, copyright, boilerplate")
    print()
    print("2. Create regexp substitutions for each issue:")
    print("   Example: --substitute 's/^## (\\d+\\.\\d+\\.\\d+)/### \\1/'")
    print()
    print("3. Apply with: python scripts/apply_substitutions.py")


if __name__ == "__main__":
    main()
