#!/usr/bin/env python3
"""Generate Kovan blog preview HTML files from Markdown sources.

This script is intentionally dependency-free so it can run in GitHub Actions
without installing a Python package stack.
"""

from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "generated-blog-previews"


@dataclass
class MarkdownDoc:
    path: Path
    title: str
    summary: str
    author: str
    published: str
    category: str
    body: str


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "blog-preview"


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text

    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text

    raw = text[4:end]
    body = text[end + 5 :]
    meta: dict[str, str] = {}
    current_key = ""

    for line in raw.splitlines():
        if not line.strip():
            continue
        if re.match(r"^[A-Za-z0-9_-]+:", line):
            key, value = line.split(":", 1)
            current_key = key.strip().lower()
            meta[current_key] = value.strip().strip("\"'")
        elif current_key and line.strip().startswith("-"):
            item = line.strip()[1:].strip()
            meta[current_key] = ", ".join(filter(None, [meta[current_key], item]))

    return meta, body


def infer_doc(path: Path) -> MarkdownDoc:
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)

    h1_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    title = meta.get("title") or (h1_match.group(1).strip() if h1_match else path.stem.replace("_", " ").replace("-", " ").title())

    body_without_title = re.sub(r"^#\s+.+\n+", "", body, count=1, flags=re.MULTILINE)
    paragraphs = [line.strip() for line in body_without_title.splitlines() if line.strip() and not line.startswith("#")]
    summary = meta.get("summary") or (paragraphs[0] if paragraphs else f"A Kovan Labs article about {title}.")
    summary = re.sub(r"\s+", " ", summary).strip()
    if len(summary) > 180:
        summary = summary[:177].rsplit(" ", 1)[0] + "..."

    return MarkdownDoc(
        path=path,
        title=title,
        summary=summary,
        author=meta.get("author") or "Kovan Labs",
        published=meta.get("date") or date.today().isoformat(),
        category=meta.get("category") or "Technology",
        body=body_without_title.strip(),
    )


def inline_markdown(value: str) -> str:
    escaped = html.escape(value)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>', escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    return escaped


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    blocks: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    in_fence = False
    fence_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            items = "".join(f"<li>{inline_markdown(item)}</li>" for item in list_items)
            blocks.append(f"<ul>{items}</ul>")
            list_items = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_fence:
                blocks.append(f"<pre><code>{html.escape(chr(10).join(fence_lines))}</code></pre>")
                fence_lines = []
                in_fence = False
            else:
                flush_paragraph()
                flush_list()
                in_fence = True
            continue

        if in_fence:
            fence_lines.append(line)
            continue

        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        image_match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", stripped)
        if image_match:
            flush_paragraph()
            flush_list()
            alt, src = image_match.groups()
            blocks.append(
                '<figure>'
                f'<img src="{html.escape(src, quote=True)}" alt="{html.escape(alt, quote=True)}">'
                f"<figcaption>{html.escape(alt) if alt else 'Article image'}</figcaption>"
                "</figure>"
            )
            continue

        heading = re.match(r"^(#{2,4})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            flush_list()
            level = min(len(heading.group(1)), 3)
            heading_text = inline_markdown(heading.group(2).strip())
            heading_id = slugify(re.sub(r"<[^>]+>", "", heading.group(2)))
            blocks.append(f'<h{level} id="{heading_id}">{heading_text}</h{level}>')
            continue

        if stripped.startswith(("- ", "* ")):
            flush_paragraph()
            list_items.append(stripped[2:].strip())
            continue

        paragraph.append(stripped)

    flush_paragraph()
    flush_list()
    return "\n".join(blocks)


def render_html(doc: MarkdownDoc) -> str:
    article = markdown_to_html(doc.body)
    year = doc.published[:4] if re.match(r"^\d{4}", doc.published) else str(date.today().year)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{html.escape(doc.summary, quote=True)}">
  <title>{html.escape(doc.title)} | Kovan Labs</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --spark:#f14924; --amber:#ffbe00; --jade:#00a86b; --cobalt:#0066a4;
      --ink:#090c08; --body:#1a1c19; --grey:#5a5f58; --grey-light:#9aa09a;
      --paper:#fff; --mist:#f4f5f4; --line:#d9dcd7;
      --font-display:"Poppins","Segoe UI",system-ui,-apple-system,Arial,sans-serif;
      --font-body:"Inter","Segoe UI",system-ui,-apple-system,Arial,sans-serif;
      --radius-md:8px; --radius-lg:16px; --shadow-card:0 2px 8px rgba(9,12,8,.08);
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; overflow-x:clip; color:var(--body); background:var(--paper); font:400 1rem/1.6 var(--font-body); }}
    img {{ display:block; max-width:100%; height:auto; }}
    a {{ color:var(--cobalt); text-underline-offset:.2em; }}
    a:hover {{ color:var(--ink); }}
    .skip-link {{ position:absolute; left:16px; top:-80px; z-index:10; padding:12px 16px; color:var(--paper); background:var(--ink); border-radius:var(--radius-md); }}
    .skip-link:focus {{ top:16px; }}
    .brand-bar {{ padding:20px clamp(24px,5vw,64px); background:var(--paper); border-bottom:1px solid var(--line); }}
    .brand-bar__inner,.hero__inner {{ width:min(100%,1200px); margin-inline:auto; }}
    .site-logo {{ display:block; width:clamp(180px,22vw,260px); min-width:120px; max-width:72%; height:auto; }}
    .hero {{ position:relative; isolation:isolate; overflow:hidden; padding:clamp(32px,5vw,64px) clamp(24px,5vw,64px); color:var(--paper); background:var(--ink); }}
    .hero__motif {{ position:absolute; z-index:-1; inset-block:0; right:0; width:clamp(300px,52vw,760px); max-width:none; height:100%; object-fit:cover; object-position:left center; opacity:.42; pointer-events:none; -webkit-mask-image:linear-gradient(90deg,transparent 0%,rgba(0,0,0,.28) 22%,#000 58%); mask-image:linear-gradient(90deg,transparent 0%,rgba(0,0,0,.28) 22%,#000 58%); }}
    .category {{ display:inline-block; margin-bottom:16px; color:var(--spark); font-size:.8125rem; font-weight:600; letter-spacing:.09em; text-transform:uppercase; }}
    h1,h2,h3 {{ color:var(--ink); font-family:var(--font-display); font-weight:600; line-height:1.15; letter-spacing:-.01em; }}
    h1 {{ max-width:19ch; margin:0; color:var(--paper); font-size:clamp(2.25rem,5vw,3.8125rem); font-weight:700; }}
    .summary {{ max-width:62ch; margin:16px 0 0; color:var(--grey-light); font-size:clamp(1.0625rem,2vw,1.25rem); line-height:1.55; }}
    .article {{ width:min(calc(100% - 48px),760px); margin-inline:auto; padding:32px 0 96px; }}
    .byline {{ display:flex; flex-wrap:wrap; gap:8px 24px; padding-bottom:24px; color:var(--grey); border-bottom:1px solid var(--line); font-size:.875rem; }}
    .byline strong {{ color:var(--body); }}
    h2 {{ margin:48px 0 16px; font-size:clamp(1.9375rem,4vw,2.4375rem); }}
    h3 {{ margin:32px 0 12px; font-size:clamp(1.375rem,3vw,1.75rem); }}
    p {{ margin:0 0 16px; }}
    ul {{ margin:0 0 16px; padding-left:1.25rem; }}
    li + li {{ margin-top:8px; }}
    figure {{ margin:32px 0; }}
    figure img {{ width:100%; border-radius:var(--radius-lg); }}
    figcaption {{ margin-top:8px; color:var(--grey); font-size:.8125rem; }}
    pre {{ overflow-x:auto; padding:20px; background:var(--mist); border-radius:var(--radius-md); box-shadow:0 0 0 1px rgba(0,102,164,.14),0 0 0 4px rgba(0,168,107,.05),0 0 24px rgba(0,102,164,.16); }}
    footer {{ padding:32px 24px; color:var(--paper); background:var(--ink); text-align:center; }}
    .social {{ display:flex; justify-content:center; gap:12px; margin-bottom:16px; }}
    .social a {{ display:grid; width:40px; height:40px; place-items:center; color:var(--paper); border:1px solid var(--grey); border-radius:999px; }}
    .social a:hover {{ color:var(--paper); background:var(--spark); border-color:var(--spark); }}
    .social svg {{ width:20px; height:20px; fill:currentColor; }}
    footer p {{ margin:0; color:var(--grey-light); font-size:.8125rem; }}
    @media (max-width:520px) {{
      .brand-bar {{ padding:16px 24px; }}
      .hero {{ padding-block:32px; }}
      .hero__motif {{ right:-10%; width:72%; opacity:.2; }}
      .article {{ width:min(calc(100% - 32px),760px); }}
    }}
  </style>
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to article</a>
  <div class="brand-bar"><div class="brand-bar__inner"><img class="site-logo" src="../05%20Brand%20Assets/logo_horizontal.png" alt="Kovan Labs" width="1800" height="364"></div></div>
  <header class="hero">
    <div class="hero__inner">
      <span class="category">{html.escape(doc.category)}</span>
      <h1>{html.escape(doc.title)}</h1>
      <p class="summary">{html.escape(doc.summary)}</p>
    </div>
    <img class="hero__motif" src="../05%20Brand%20Assets/graphic_dotwave.png" alt="" width="900" height="360" aria-hidden="true">
  </header>
  <main class="article" id="main-content">
    <div class="byline">
      <span>By: <strong>{html.escape(doc.author)}</strong></span>
      <time datetime="{html.escape(doc.published)}">Published {html.escape(doc.published)}</time>
    </div>
    {article}
  </main>
  <footer>
    <nav class="social" aria-label="Kovan Labs social media">
      <a href="https://in.linkedin.com/company/kovan-labs" aria-label="LinkedIn"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 8.1H3.2V21h3.3V8.1ZM4.9 3A1.9 1.9 0 1 0 5 6.8 1.9 1.9 0 0 0 4.9 3ZM21 13.6c0-3.9-2.1-5.7-4.9-5.7a4.2 4.2 0 0 0-3.8 2.1V8.1H9V21h3.3v-6.4c0-1.7.3-3.3 2.4-3.3s2.1 1.9 2.1 3.4V21H21v-7.4Z"/></svg></a>
      <a href="https://www.instagram.com/lifeatkovan/" aria-label="Instagram"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2c2.7 0 3 0 4.1.1 2.7.1 4 1.4 4.2 4.2.1 1.1.1 1.4.1 4.1s0 3-.1 4.1c-.1 2.7-1.4 4-4.2 4.2-1.1.1-1.4.1-4.1.1s-3 0-4.1-.1c-2.7-.1-4-1.4-4.2-4.2C2 15 2 14.7 2 12s0-3 .1-4.1c.1-2.7 1.4-4 4.2-4.2C9 2 9.3 2 12 2Zm0 2c-2.6 0-2.9 0-3.9.1-1.8.1-2.7.9-2.8 2.8-.1 1-.1 1.3-.1 3.9s0 2.9.1 3.9c.1 1.8.9 2.7 2.8 2.8 1 .1 1.3.1 3.9.1s2.9 0 3.9-.1c1.8-.1 2.7-.9 2.8-2.8.1-1 .1-1.3.1-3.9s0-2.9-.1-3.9c-.1-1.8-.9-2.7-2.8-2.8-1-.1-1.3-.1-3.9-.1Zm0 3a5 5 0 1 1 0 10 5 5 0 0 1 0-10Zm0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6Zm5.2-3.2a1.2 1.2 0 1 1 0 2.4 1.2 1.2 0 0 1 0-2.4Z"/></svg></a>
    </nav>
    <p>© {year} Kovan Labs. All rights reserved.</p>
  </footer>
</body>
</html>
"""


def is_content_markdown(path: Path) -> bool:
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return False
    return relative.parts[:1] == ("content",) and path.suffix.lower() == ".md"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", help="Markdown files to generate")
    args = parser.parse_args()

    files = [ROOT / item for item in args.files]
    markdown_files = [path for path in files if path.exists() and is_content_markdown(path)]

    if not markdown_files:
        print("No content/**/*.md files found to generate.")
        return 0

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for path in markdown_files:
        doc = infer_doc(path)
        output_path = OUTPUT_DIR / f"{slugify(doc.title)}.html"
        output_path.write_text(render_html(doc), encoding="utf-8")
        print(f"Generated {output_path.relative_to(ROOT)} from {path.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
