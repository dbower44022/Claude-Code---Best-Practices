#!/usr/bin/env python3
"""Convert Markdown relative links to XWiki syntax.

Reads all .md files from docs/ directory and converts relative Markdown links
to XWiki link syntax, outputting converted files to an output/ directory.

Usage:
    python scripts/convert_links.py --space MySpace
    python scripts/convert_links.py --space MySpace --input docs/ --output output/
"""

import argparse
import re
import sys
from pathlib import Path


def filename_to_page_name(filename: str) -> str:
    """Convert a Markdown filename to an XWiki page name.

    Examples:
        01-project-setup.md -> 01-project-setup
        index.md -> index
    """
    return Path(filename).stem


def convert_markdown_link(match: re.Match, space_name: str) -> str:
    """Convert a single Markdown link to XWiki syntax.

    Handles these cases:
        [text](file.md)           -> [[text>>doc:Space.page]]
        [text](file.md#section)   -> [[text>>doc:Space.page||anchor="section"]]
        [text](#section)          -> [[text>>doc:||anchor="section"]]  (same-page anchor)
        [text](https://...)       -> unchanged (absolute URLs kept as-is)
    """
    link_text = match.group(1)
    link_target = match.group(2)

    # Leave absolute URLs unchanged
    if link_target.startswith(("http://", "https://", "mailto:")):
        return match.group(0)

    # Parse the target into file and anchor parts
    if "#" in link_target:
        file_part, anchor = link_target.split("#", 1)
    else:
        file_part = link_target
        anchor = None

    # Same-page anchor reference
    if not file_part:
        if anchor:
            return f'[[{link_text}>>doc:||anchor="{anchor}"]]'
        return match.group(0)

    # Convert filename to page name
    page_name = filename_to_page_name(file_part)

    if anchor:
        return f'[[{link_text}>>doc:{space_name}.{page_name}||anchor="{anchor}"]]'
    else:
        return f"[[{link_text}>>doc:{space_name}.{page_name}]]"


def convert_file_content(content: str, space_name: str) -> str:
    """Convert all Markdown links in file content to XWiki syntax."""
    # Match Markdown links: [text](target)
    # Negative lookbehind for ! to avoid matching image syntax ![alt](src)
    pattern = r"(?<!!)\[([^\]]+)\]\(([^)]+)\)"
    return re.sub(pattern, lambda m: convert_markdown_link(m, space_name), content)


def process_files(input_dir: Path, output_dir: Path, space_name: str) -> list[Path]:
    """Process all Markdown files in input_dir and write to output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)

    md_files = sorted(input_dir.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {input_dir}", file=sys.stderr)
        return []

    processed = []
    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        converted = convert_file_content(content, space_name)

        output_file = output_dir / md_file.name
        output_file.write_text(converted, encoding="utf-8")
        processed.append(output_file)
        print(f"Converted: {md_file.name} -> {output_file}")

    return processed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Markdown relative links to XWiki syntax"
    )
    parser.add_argument(
        "--space",
        required=True,
        help="XWiki space name (e.g., 'ClaudeCodeBestPractices')",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("docs"),
        help="Input directory containing .md files (default: docs/)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output"),
        help="Output directory for converted files (default: output/)",
    )
    args = parser.parse_args()

    if not args.input.is_dir():
        print(f"Error: Input directory '{args.input}' does not exist", file=sys.stderr)
        sys.exit(1)

    processed = process_files(args.input, args.output, args.space)
    print(f"\nConverted {len(processed)} file(s)")


if __name__ == "__main__":
    main()
