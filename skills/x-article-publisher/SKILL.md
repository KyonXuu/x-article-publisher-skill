---
name: x-article-publisher
description: Publish Markdown articles to X (Twitter) Articles editor with proper formatting. Use when user wants to publish a Markdown file/URL to X Articles, or mentions "publish to X", "post article to Twitter", "X article", or wants help with X Premium article publishing. Handles cover image upload and converts Markdown to rich text automatically.
---

# X Article Publisher

Publish Markdown content to X (Twitter) Articles editor, preserving formatting with rich text conversion.

## Prerequisites

- Playwright MCP for browser automation
- User logged into X with Premium Plus subscription
- Python 3.9+ with dependencies: `pip install Pillow pyobjc-framework-Cocoa`

## Scripts

Located in `~/.claude/skills/x-article-publisher/scripts/`:

### parse_markdown.py
Parse Markdown and extract structured data:
```bash
python parse_markdown.py <markdown_file> [--output json|html] [--html-only]
```
Returns JSON with: title, cover_image, content_images (with positions), html

### copy_to_clipboard.py
Copy image or HTML to system clipboard:
```bash
# Copy image (with optional compression)
python copy_to_clipboard.py image /path/to/image.jpg [--quality 80]

# Copy HTML for rich text paste
python copy_to_clipboard.py html --file /path/to/content.html
```

## Workflow

**Strategy: "先文后图" (Text First, Images Later)**

For articles with multiple images, paste ALL text content first, then insert images at correct positions.

1. Parse Markdown with Python script → get title, images, HTML
2. Navigate to X Articles editor
3. Upload cover image (first image)
4. Fill title
5. Copy HTML to clipboard (Python) → Paste with Cmd+V
6. Insert content images at correct positions
7. Save as draft (NEVER auto-publish)

## Step 1: Parse Markdown (Python)

Use `parse_markdown.py` to extract all structured data:

```bash
python ~/.claude/skills/x-article-publisher/scripts/parse_markdown.py /path/to/article.md
```

Output JSON:
```json
{
  "title": "Article Title",
  "cover_image": "/path/to/first-image.jpg",
  "content_images": [
    {"path": "/path/to/img2.jpg", "after_text": "text before image..."},
    {"path": "/path/to/img3.jpg", "after_text": "another paragraph..."}
  ],
  "html": "<p>Content...</p><h2>Section</h2>..."
}
```

Save HTML to temp file for clipboard:
```bash
python parse_markdown.py article.md --html-only > /tmp/article_html.html
```

## Step 2: Open X Articles Editor

```
browser_navigate: https://x.com/compose/articles
browser_snapshot to verify editor loaded
```

If login needed, prompt user to log in manually.

## Step 3: Upload Cover Image

1. Click "添加照片或视频" button
2. Use browser_file_upload with the cover image path (from JSON output)
3. Verify image uploaded

## Step 4: Fill Title

- Find textbox with "添加标题" placeholder
- Use browser_type to input title (from JSON output)

## Step 5: Paste Text Content (Python Clipboard)

Copy HTML to system clipboard using Python, then paste:

```bash
# Copy HTML to clipboard
python ~/.claude/skills/x-article-publisher/scripts/copy_to_clipboard.py html --file /tmp/article_html.html
```

Then in browser:
```
browser_click on editor textbox
browser_press_key: Meta+v
```

This preserves all rich text formatting (H2, bold, links, lists).

## Step 6: Insert Content Images (Python Clipboard)

**关键优化**: 使用 Python 剪贴板直接粘贴图片，而非点击多次按钮上传。

For each content image (from `content_images` array):

```bash
# 1. Copy image to clipboard (with compression)
python ~/.claude/skills/x-article-publisher/scripts/copy_to_clipboard.py image /path/to/img.jpg --quality 85
```

```
# 2. Click target paragraph (use after_text to locate)
browser_click on paragraph element

# 3. Paste image
browser_press_key: Meta+v

# 4. Wait for upload (use 3-second cycles, not 10 seconds)
browser_wait_for textGone="正在上传媒体" time=3
# If timeout, repeat wait until upload completes
```

**对比**:
- ❌ 旧方法: 点击段落 → 添加媒体内容 → 媒体 → 添加照片或视频 → file_upload → 等待 (5步)
- ✅ 新方法: Python复制 → 点击段落 → 粘贴 → 等待 (2步浏览器操作)

**Tip**: Use unique text from `after_text` field to identify correct insertion points.

## Step 7: Save Draft

1. Verify content pasted (check word count indicator)
2. Draft auto-saves, or click Save button if needed
3. Click "预览" to verify formatting
4. Report: "Draft saved. Review and publish manually."

## Critical Rules

1. **NEVER publish** - Only save draft
2. **First image = cover** - Upload first image as cover image
3. **Rich text conversion** - Always convert Markdown to HTML before pasting
4. **Use clipboard API** - Paste via clipboard for proper formatting
5. **Verify steps** - browser_snapshot after each action

## Supported Formatting

- H2 headers (## )
- Blockquotes (> )
- Bold text (**)
- Hyperlinks ([text](url))
- Ordered lists (1. 2. 3.)
- Unordered lists (- )
- Paragraphs

## Example Flow

User: "Publish /path/to/article.md to X"

```bash
# Step 1: Parse Markdown
python ~/.claude/skills/x-article-publisher/scripts/parse_markdown.py /path/to/article.md > /tmp/article.json
python ~/.claude/skills/x-article-publisher/scripts/parse_markdown.py /path/to/article.md --html-only > /tmp/article_html.html
```

2. Navigate to https://x.com/compose/articles
3. Upload cover image (browser_file_upload for cover only)
4. Fill title (from JSON: `title`)
5. Copy & paste HTML:
   ```bash
   python ~/.claude/skills/x-article-publisher/scripts/copy_to_clipboard.py html --file /tmp/article_html.html
   ```
   Then: browser_press_key Meta+v
6. For each content image (from JSON: `content_images`):
   ```bash
   python copy_to_clipboard.py image /path/to/img.jpg --quality 85
   ```
   - Click paragraph matching `after_text`
   - browser_press_key Meta+v
   - Wait 3s cycles until upload complete
7. Verify in preview
8. "Draft saved. Please review and publish manually."

## Best Practices

### 为什么用 Python 而非浏览器内 JavaScript？

1. **本地处理更可靠**: Python 直接操作系统剪贴板，不受浏览器沙盒限制
2. **图片压缩**: 上传前压缩图片 (--quality 85)，减少上传时间
3. **代码复用**: 脚本固定不变，无需每次重新编写转换逻辑
4. **调试方便**: 脚本可单独测试，问题易定位

### 等待策略

- ❌ 保守等待: `time=10` 一次性等10秒，浪费时间
- ✅ 循环等待: `time=3` 每3秒检查一次，大多数情况3-6秒完成

### 图片插入效率

每张图片的浏览器操作从5步减少到2步：
- 旧: 点击 → 添加媒体 → 媒体 → 添加照片 → file_upload
- 新: 点击段落 → Meta+v

### 封面图 vs 内容图

- **封面图**: 使用 browser_file_upload（因为有专门的上传按钮）
- **内容图**: 使用 Python 剪贴板 + 粘贴（更高效）
