---
name: wechat-article-capture
description: Use when the user shares a WeChat MP article URL (mp.weixin.qq.com) and wants to save it as an IMA note with images, or wants to capture/archive WeChat articles into their knowledge base. Triggers on: weixin.qq.com links, 微信公众号文章, 抓取微信文章, 保存到知识库/笔记.
---

# WeChat Article Capture

Capture WeChat MP articles — text + images — and save as IMA notes in the user's knowledge base.

## Why Two Tools Are Needed

WeChat articles have two anti-crawl mechanisms:
1. **WebFetch**: Gets text content but NOT images (lazy-loaded invisible placeholders)
2. **playwright browser**: Can scroll to trigger lazy-load, exposing real `data-src` URLs on `mmbiz.qpic.cn`

You MUST use both.

## Workflow

### Step 1: Fetch text via WebFetch

```
WebFetch(url, prompt="提取完整内容：标题、作者、正文、段落结构")
```

If WebFetch returns a captcha/environment-detection page, the article is behind WeChat's strict anti-crawl. Fall back: tell the user the article is protected and ask them to paste content directly.

### Step 2: Extract images via playwright

```bash
# Open the article
playwright-cli open "ARTICLE_URL"

# Scroll to trigger all lazy-loaded images (15 scrolls × 800px, 800ms wait each)
playwright-cli eval "async () => {
  for (let i = 0; i < 15; i++) {
    window.scrollBy(0, 800);
    await new Promise(r => setTimeout(r, 800));
  }
  const imgs = document.querySelectorAll('#js_content img, .rich_media_content img');
  return Array.from(imgs)
    .filter(img => img.naturalWidth > 0)
    .map(img => ({
      src: img.getAttribute('data-src') || img.src,
      width: img.naturalWidth,
      height: img.naturalHeight
    }));
}"

# Close browser when done
playwright-cli close
```

Key points:
- Use `data-src` attribute (the real URL), not `src` (which may be a placeholder)
- Filter out images with `naturalWidth === 0` (empty placeholders)
- Small divider GIFs (640×86) can be included or skipped — they're cosmetic

### Step 3: Write the note

Write cleaned/restructured markdown to `/tmp/ima_article.md`. Guidelines:
- Remove author attribution,公众号 branding, "扫码关注" CTAs
- Restructure with clear headings, remove fluff
- Embed images as `![desc](URL)` using the `data-src` URLs from step 2
- Place images at semantically appropriate positions in the article flow
- Keep all factual content intact

### Step 4: Query user's knowledge bases and ask which one to use

**Never hardcode a knowledge base ID.** Different users have different knowledge bases. You MUST query the user's available knowledge bases first.

First, list the user's knowledge bases via IMA API:

```bash
cd SKILL_DIR && node ima_api.cjs 'openapi/wiki/v1/get_knowledge_base_list' '{}' '{}'
```

Parse the response to extract the list of `{name, knowledge_base_id}` pairs.

Then present the options to the user:

- If the user has **only one** knowledge base → use it silently, just confirm: `已保存到知识库「XXX」`
- If the user has **multiple** knowledge bases → ask: `请选择要存入的知识库：` with the list of names
- If the user has **no knowledge base** → tell them: `你还没有创建知识库，请先在 IMA 中创建一个。`

### Step 5: Create note and add to chosen knowledge base

Use the IMA skill pipeline with the user-chosen `KB_ID`:

```python
import json, subprocess

with open('/tmp/ima_article.md', 'r') as f:
    content = f.read()

# Create note
body = json.dumps({'content_format': 1, 'content': content}, ensure_ascii=False)
result = subprocess.run(['node', 'SKILL_DIR/ima_api.cjs',
    'openapi/note/v1/import_doc', body], capture_output=True, text=True)
note_id = json.loads(result.stdout)['data']['note_id']

# Add to the user-chosen knowledge base
body2 = json.dumps({
    'media_type': 11,
    'note_info': {'content_id': note_id},
    'title': 'ARTICLE_TITLE',
    'knowledge_base_id': KB_ID  # From user selection
}, ensure_ascii=False)
subprocess.run(['node', 'SKILL_DIR/ima_api.cjs',
    'openapi/wiki/v1/add_knowledge', body2], capture_output=True, text=True)
```

SKILL_DIR is the directory containing `ima_api.cjs` (where the IMA skill is installed).

## Edge Cases

| Situation | Action |
|-----------|--------|
| WebFetch blocked (captcha page) | Tell user article is protected, ask for pasted content |
| playwright not installed | Install: `npm install -g @playwright/cli@latest` |
| No images found after scroll | Proceed with text-only note |
| Image URLs use `#imgIndex=X` suffix | Keep as-is, they work fine |
| Note title too long | Truncate to ~50 chars, keep key meaning |
| User has no knowledge base | Tell user to create one in IMA first |
| User has multiple knowledge bases | Ask user which one to save to — never assume |
| User has only one knowledge base | Use it silently, confirm with name |
