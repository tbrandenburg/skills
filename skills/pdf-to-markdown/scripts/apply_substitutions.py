#!/usr/bin/env python3
"""
Apply sed-style regexp substitutions to markdown file.
Automatically creates backup before making changes.
"""
import sys
import re
import argparse
from pathlib import Path
import shutil


def parse_substitution(pattern):
    """Parse sed-style substitution pattern: s/search/replace/flags"""
    if not pattern.startswith('s/'):
        raise ValueError(f"Substitution must start with 's/': {pattern}")
    
    # Split by unescaped /
    parts = []
    current = ''
    escaped = False
    
    for char in pattern[2:]:  # Skip 's/'
        if escaped:
            current += char
            escaped = False
        elif char == '\\':
            current += char
            escaped = True
        elif char == '/':
            parts.append(current)
            current = ''
        else:
            current += char
    
    if current:  # Last part (flags)
        parts.append(current)
    
    if len(parts) < 2:
        raise ValueError(f"Invalid substitution pattern: {pattern}")
    
    search = parts[0]
    replace = parts[1]
    flags_str = parts[2] if len(parts) > 2 else ''
    
    # Parse flags
    flags = 0
    if 'i' in flags_str:
        flags |= re.IGNORECASE
    if 'm' in flags_str:
        flags |= re.MULTILINE
    
    global_replace = 'g' in flags_str
    
    return search, replace, flags, global_replace


def apply_substitution(content, search, replace, flags, global_replace):
    """Apply a single substitution to content."""
    # Always use MULTILINE for line-based patterns (^ and $ match line boundaries)
    flags |= re.MULTILINE
    
    if global_replace:
        return re.sub(search, replace, content, flags=flags)
    else:
        return re.sub(search, replace, content, count=1, flags=flags)


def main():
    parser = argparse.ArgumentParser(
        description="Apply regexp substitutions to markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fix heading depth: ## 1.2.3 → ### 1.2.3
  -s 's/^## (\\d+\\.\\d+\\.\\d+)/### \\1/'
  
  # Remove page numbers (case insensitive, global)
  -s 's/^Page \\d+$//gi'
  
  # Remove copyright lines
  -s 's/^© 20\\d{2}.*$//'
  
  # Multiple substitutions
  -s 's/pattern1/replace1/' -s 's/pattern2/replace2/'

Flags:
  g = global (replace all occurrences, not just first)
  i = case insensitive
  m = multiline mode

Note: Automatic backup is created before any changes.
        """
    )
    parser.add_argument("markdown_file", help="Input markdown file")
    parser.add_argument("-s", "--substitute", action="append", required=True,
                       help="Sed-style substitution: 's/search/replace/flags'")
    parser.add_argument("--backup", help="Backup filename (default: <file>.backup)")
    parser.add_argument("-o", "--output", help="Output file (default: overwrites input)")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show changes without applying")
    args = parser.parse_args()
    
    md_path = Path(args.markdown_file)
    if not md_path.exists():
        print(f"ERROR: File not found: {md_path}", file=sys.stderr)
        sys.exit(1)
    
    # Parse all substitutions
    substitutions = []
    for pattern in args.substitute:
        try:
            search, replace, flags, global_replace = parse_substitution(pattern)
            substitutions.append((pattern, search, replace, flags, global_replace))
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Read content
    content = md_path.read_text(encoding='utf-8')
    original_content = content
    
    # Apply substitutions
    print(f"Applying {len(substitutions)} substitution(s)...\n")
    
    for i, (pattern, search, replace, flags, global_replace) in enumerate(substitutions, 1):
        before_lines = len(content.split('\n'))
        content = apply_substitution(content, search, replace, flags, global_replace)
        after_lines = len(content.split('\n'))
        
        # Count actual replacements made
        before_sub = content if i > 1 else original_content  # Content before this substitution
        matches_before = len(re.findall(search, before_sub, flags=flags))
        matches_after = len(re.findall(search, content, flags=flags))
        changes = matches_before - matches_after  # Actual substitutions made
        
        print(f"{i}. {pattern}")
        print(f"   Matched: {changes} occurrence(s)")
        if before_lines != after_lines:
            print(f"   Lines: {before_lines} → {after_lines}")
        print()
    
    # Show diff summary
    original_lines = original_content.split('\n')
    new_lines = content.split('\n')
    
    if original_content == content:
        print("No changes made (patterns didn't match anything)")
        return
    
    # Count changed lines
    changed = sum(1 for o, n in zip(original_lines, new_lines) if o != n)
    print(f"Summary: {changed} line(s) modified")
    
    if args.dry_run:
        print("\n(Dry run - no files modified)")
        return
    
    # Create backup
    backup_path = Path(args.backup) if args.backup else md_path.with_suffix(md_path.suffix + '.backup')
    shutil.copy2(md_path, backup_path)
    print(f"\n✓ Backup created: {backup_path}")
    
    # Write output
    output_path = Path(args.output) if args.output else md_path
    output_path.write_text(content, encoding='utf-8')
    print(f"✓ Changes written to: {output_path}")


if __name__ == "__main__":
    main()
