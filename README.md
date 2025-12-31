# X Article Publisher Skill

A Claude Code skill for publishing Markdown articles to X (Twitter) Articles with rich text formatting.

## Features

- Convert Markdown to X Articles rich text format
- Auto-upload cover image and content images
- Preserve formatting: headers, bold, links, lists, blockquotes
- Clipboard-based workflow for efficiency
- Image compression support

## Requirements

- [Claude Code](https://claude.ai/code) CLI
- [Playwright MCP](https://github.com/anthropics/mcp-playwright) for browser automation
- X Premium Plus subscription (for Articles feature)
- Python 3.9+ with dependencies:
  ```bash
  pip install Pillow pyobjc-framework-Cocoa
  ```

## Installation

### Method 1: Clone to Skills Directory (Simple)

```bash
git clone https://github.com/wshuyi/x-article-publisher-skill.git ~/.claude/skills/x-article-publisher-skill
```

Or copy just the skill folder:

```bash
git clone https://github.com/wshuyi/x-article-publisher-skill.git /tmp/x-skill
cp -r /tmp/x-skill/skills/x-article-publisher ~/.claude/skills/
```

### Method 2: Plugin Marketplace

First, add the marketplace:

```
/plugin marketplace add wshuyi/x-article-publisher-skill
```

Then install:

```
/plugin install x-article-publisher@wshuyi/x-article-publisher-skill
```

## Usage

In Claude Code, simply say:

```
Publish /path/to/article.md to X
```

Or invoke directly:

```
/x-article-publisher /path/to/article.md
```

## Workflow

1. Parse Markdown file (extract title, images, convert to HTML)
2. Open X Articles editor
3. Upload cover image (first image in article)
4. Fill title
5. Paste formatted content via clipboard
6. Insert content images at correct positions
7. Save as draft (never auto-publishes)

## Supported Markdown

- `# H1` - Used as article title
- `## H2` - Section headers
- `**bold**` - Bold text
- `[text](url)` - Hyperlinks
- `> quote` - Blockquotes
- `- item` / `1. item` - Lists
- `![alt](image.jpg)` - Images

## File Structure

```
x-article-publisher-skill/
├── .claude-plugin/
│   └── plugin.json           # Plugin configuration
├── skills/
│   └── x-article-publisher/
│       ├── SKILL.md          # Skill instructions
│       └── scripts/
│           ├── parse_markdown.py
│           └── copy_to_clipboard.py
├── README.md
└── LICENSE
```

## License

MIT License - see [LICENSE](LICENSE)

## Author

wshuyi
