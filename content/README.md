# Blog content intake

Add each new blog source as a Markdown file below `content/`. The rendering workflow reads the file, keeps it unchanged, and creates a separate HTML preview from one of the Kovan blog templates.

Optional frontmatter controls the page metadata and template:

```md
---
title: How AI agents are changing software development
author: Kovan Labs
date: 2026-07-23
category: Technology
summary: A short description used in the page banner and search metadata.
template: conventional
---
```

Supported template values are `conventional`, `volume`, and `radar`. When `template` is omitted, the renderer selects one from the title and defaults to `conventional`.

Use normal Markdown for headings, paragraphs, lists, links, blockquotes, code blocks, tables, and images. Give every image useful alt text:

```md
![Diagram explaining the workflow](images/workflow.png)
```

Local image paths are resolved relative to the Markdown file and copied beside the generated preview. The GitHub Actions preview also downloads valid public images referenced with `http` or `https`.

## Render locally

Let the renderer select the template:

```bash
python -m pip install --requirement requirements-blog-renderer.txt
python scripts/render_blog.py content/path/article.md
```

Use a specific template when needed:

```bash
python scripts/render_conventional_blog.py content/path/article.md
python scripts/render_volume_blog.py content/path/article.md
python scripts/render_radar_blog.py content/path/article.md
```

Generated files are written separately under `output/website/`. Add `--download-remote-images` to save public Markdown images locally, or `--overwrite` to intentionally replace an existing output.

## GitHub Actions preview

When a commit adds a Markdown file under `content/` on a non-main branch or pull request, the workflow renders it and uploads `rendered-blog-previews` as a downloadable Actions artifact. The workflow never modifies the Markdown and does not commit or push the generated HTML.
