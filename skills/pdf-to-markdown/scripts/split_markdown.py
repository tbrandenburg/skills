#!/usr/bin/env python3
"""
Split markdown document into multiple files based on delimiters.
"""
import sys
import re
import argparse
from pathlib import Path


def sanitize_filename(title, max_length=50):
    """Convert title to safe filename."""
    # Remove markdown formatting
    title = re.sub(r'[#*_`]', '', title)
    # Remove special characters
    title = re.sub(r'[^\w\s-]', '', title)
    # Replace spaces with underscores
    title = re.sub(r'\s+', '_', title.strip())
    # Limit length
    if len(title) > max_length:
        title = title[:max_length].rsplit('_', 1)[0]
    return title


def filter_sections(sections, min_content_lines=3, merge_short=True):
    """Filter out trivial sections and optionally merge short ones."""
    filtered_sections = []
    
    for i, section in enumerate(sections):
        content_lines = [line for line in section['content'].split('\n') if line.strip()]
        
        # Skip sections that are just headers with no content
        if len(content_lines) < min_content_lines:
            if merge_short and filtered_sections:
                # Merge into previous section
                filtered_sections[-1]['content'] += '\n\n' + section['content']
                continue
            # Skip trivial sections
            continue
            
        filtered_sections.append(section)
    
    return filtered_sections


def split_by_heading_level(markdown_content, level):
    """Split markdown by heading level."""
    lines = markdown_content.split('\n')
    sections = []
    current_section = []
    current_title = None
    
    heading_pattern = re.compile(r'^(#{' + str(level) + r'})\s+(.+)$')
    
    for line in lines:
        match = heading_pattern.match(line)
        if match:
            # Save previous section
            if current_section:
                sections.append({
                    'title': current_title or 'frontmatter',
                    'content': '\n'.join(current_section)
                })
            # Start new section
            current_title = match.group(2).strip()
            current_section = [line]
        else:
            current_section.append(line)
    
    # Save last section
    if current_section:
        sections.append({
            'title': current_title or 'frontmatter',
            'content': '\n'.join(current_section)
        })
    
    return sections


def split_by_pattern(markdown_content, pattern, extract_title_pattern):
    """Split markdown by custom regex pattern."""
    lines = markdown_content.split('\n')
    sections = []
    current_section = []
    current_title = None
    
    delimiter_re = re.compile(pattern)
    extract_re = re.compile(extract_title_pattern) if extract_title_pattern else None
    
    for line in lines:
        if delimiter_re.match(line):
            # Save previous section
            if current_section:
                sections.append({
                    'title': current_title or 'frontmatter',
                    'content': '\n'.join(current_section)
                })
            # Extract title
            if extract_re:
                title_match = extract_re.search(line)
                current_title = title_match.group(1) if title_match else line
            else:
                current_title = line
            current_section = [line]
        else:
            current_section.append(line)
    
    # Save last section
    if current_section:
        sections.append({
            'title': current_title or 'frontmatter',
            'content': '\n'.join(current_section)
        })
    
    return sections


def main():
    parser = argparse.ArgumentParser(description="Split markdown into multiple files")
    parser.add_argument("markdown_file", help="Input markdown file")
    parser.add_argument("-o", "--output-dir", help="Output directory (default: <name>_split/)")
    parser.add_argument("--heading-level", type=int, help="Split on heading level (1-6)")
    parser.add_argument("--min-content", type=int, default=3, help="Minimum content lines per section (default: 3)")
    parser.add_argument("--no-merge", action="store_true", help="Don't merge short sections into previous ones")
    parser.add_argument("--pattern", help="Custom regex pattern for split points")
    parser.add_argument("--extract-title", help="Regex to extract title from delimiter line")
    parser.add_argument("--dry-run", action="store_true", help="Show split plan without creating files")
    args = parser.parse_args()
    
    md_path = Path(args.markdown_file)
    if not md_path.exists():
        print(f"ERROR: File not found: {md_path}", file=sys.stderr)
        sys.exit(1)
    
    # Validate arguments
    if not args.heading_level and not args.pattern:
        print("ERROR: Must specify either --heading-level or --pattern", file=sys.stderr)
        sys.exit(1)
    
    content = md_path.read_text(encoding='utf-8')
    
    # Split document
    if args.heading_level:
        sections = split_by_heading_level(content, args.heading_level)
    else:
        sections = split_by_pattern(content, args.pattern, args.extract_title)
    
    # Apply smart filtering
    if args.heading_level:  # Only filter for heading-based splits
        sections = filter_sections(sections, args.min_content, not args.no_merge)
    
    if not sections:
        print("No sections found")
        return
    
    print(f"Found {len(sections)} section(s):\n")
    
    # Prepare output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = md_path.parent / (md_path.stem + "_split")
    
    # Show plan
    for i, section in enumerate(sections):
        title = section['title']
        filename = f"{i:02d}_{sanitize_filename(title)}.md"
        lines = len(section['content'].split('\n'))
        print(f"{i:02d}. {filename}")
        print(f"    Title: {title[:60]}")
        print(f"    Lines: {lines}")
        print()
    
    if args.dry_run:
        print("(Dry run - no files created)")
        return
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write files
    for i, section in enumerate(sections):
        title = section['title']
        filename = f"{i:02d}_{sanitize_filename(title)}.md"
        output_path = output_dir / filename
        output_path.write_text(section['content'], encoding='utf-8')
    
    print(f"✓ Split complete: {len(sections)} files written to {output_dir}")


if __name__ == "__main__":
    main()
