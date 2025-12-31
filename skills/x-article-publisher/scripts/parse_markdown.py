#!/usr/bin/env python3
"""
Parse Markdown for X Articles publishing.

Extracts:
- Title (from first H1/H2 or first line)
- Cover image (first image)
- Content images with position info
- HTML content (images stripped)

Usage:
    python parse_markdown.py <markdown_file> [--output json|html]

Output (JSON):
{
    "title": "Article Title",
    "cover_image": "/path/to/cover.jpg",
    "content_images": [
        {"path": "/path/to/img1.jpg", "after_text": "text before image..."},
        ...
    ],
    "html": "<p>Content...</p><h2>Section</h2>..."
}
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def extract_images(markdown: str, base_path: Path) -> tuple[list[dict], str]:
    """Extract all images and return (image_list, markdown_without_images)."""
    images = []

    # Pattern for markdown images: ![alt](path)
    img_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')

    # Find all images with their positions
    for match in img_pattern.finditer(markdown):
        alt_text = match.group(1)
        img_path = match.group(2)

        # Resolve relative paths
        if not os.path.isabs(img_path):
            full_path = str(base_path / img_path)
        else:
            full_path = img_path

        # Get text before this image (last 50 chars for context)
        start_pos = match.start()
        text_before = markdown[:start_pos].strip()
        # Get last meaningful line
        lines_before = [l for l in text_before.split('\n') if l.strip()]
        after_text = lines_before[-1][:100] if lines_before else ""

        images.append({
            "path": full_path,
            "alt": alt_text,
            "after_text": after_text,
            "position": start_pos
        })

    # Remove images from markdown
    clean_markdown = img_pattern.sub('', markdown)
    # Clean up extra blank lines
    clean_markdown = re.sub(r'\n{3,}', '\n\n', clean_markdown)

    return images, clean_markdown


def extract_title(markdown: str) -> tuple[str, str]:
    """Extract title from first H1, H2, or first non-empty line.

    Returns:
        (title, markdown_without_title): Title string and markdown with H1 title removed.
        If title is from H1, it's removed from markdown to avoid duplication.
    """
    lines = markdown.strip().split('\n')
    title = "Untitled"
    title_line_idx = None

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        # H1 - use as title and mark for removal
        if stripped.startswith('# '):
            title = stripped[2:].strip()
            title_line_idx = idx
            break
        # H2 - use as title but don't remove (it's a section header)
        if stripped.startswith('## '):
            title = stripped[3:].strip()
            break
        # First non-empty, non-image line
        if not stripped.startswith('!['):
            title = stripped[:100]
            break

    # Remove H1 title line from markdown to avoid duplication
    if title_line_idx is not None:
        lines.pop(title_line_idx)
        markdown = '\n'.join(lines)

    return title, markdown


def markdown_to_html(markdown: str) -> str:
    """Convert markdown to HTML for X Articles rich text paste."""
    html = markdown

    # Headers (H2 only, H1 is title)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)

    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # Italic
    html = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html)

    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

    # Blockquotes
    html = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

    # Unordered lists
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

    # Ordered lists
    html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

    # Wrap consecutive <li> in <ul>
    html = re.sub(r'((?:<li>.*?</li>\n?)+)', r'<ul>\1</ul>', html)

    # Paragraphs - split by double newlines
    parts = html.split('\n\n')
    processed_parts = []

    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Skip if already a block element
        if part.startswith(('<h2>', '<h3>', '<blockquote>', '<ul>', '<ol>')):
            processed_parts.append(part)
        else:
            # Wrap in paragraph, convert single newlines to <br>
            part = part.replace('\n', '<br>')
            processed_parts.append(f'<p>{part}</p>')

    return ''.join(processed_parts)


def parse_markdown_file(filepath: str) -> dict:
    """Parse a markdown file and return structured data."""
    path = Path(filepath)
    base_path = path.parent

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract images first
    images, clean_markdown = extract_images(content, base_path)

    # Extract title (and remove H1 from markdown to avoid duplication)
    title, clean_markdown = extract_title(clean_markdown)

    # Convert to HTML
    html = markdown_to_html(clean_markdown)

    # Separate cover image from content images
    cover_image = images[0]["path"] if images else None
    content_images = images[1:] if len(images) > 1 else []

    return {
        "title": title,
        "cover_image": cover_image,
        "content_images": content_images,
        "html": html,
        "source_file": str(path.absolute())
    }


def main():
    parser = argparse.ArgumentParser(description='Parse Markdown for X Articles')
    parser.add_argument('file', help='Markdown file to parse')
    parser.add_argument('--output', choices=['json', 'html'], default='json',
                       help='Output format (default: json)')
    parser.add_argument('--html-only', action='store_true',
                       help='Output only HTML content')

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    result = parse_markdown_file(args.file)

    if args.html_only:
        print(result['html'])
    elif args.output == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result['html'])


if __name__ == '__main__':
    main()
