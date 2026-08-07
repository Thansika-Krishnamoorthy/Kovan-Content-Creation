---
title: How Kovan Labs Renders Blogs Automatically
author: Kovan Labs
date: 2026-08-07
category: Engineering
summary: Inside the automated pipeline that turns a plain Markdown draft into a branded Kovan Labs web preview.
---

# How Kovan Labs Renders Blogs Automatically

Every team member can write a blog in plain Markdown and let the build pipeline
turn it into a branded, on-brand web preview. The original draft is never edited;
a separate HTML page is generated from one of the approved Kovan templates.

![A small diagram of the render pipeline](images/pipeline.png "Figure 1: From Markdown draft to branded preview")

## Why keep the source untouched

Keep the Markdown as the single source of truth. Teammates focus on the ideas and
the words, not on pages or layout. Rendering happens automatically on every push,
so the preview is always in sync with the latest commit.

## What the renderer supports

The pipeline understands the ordinary Markdown you already know how to write:

- **Headings** for structure
- **Lists** for scannable points
- **Links** that open in a new tab
- **Blockquotes** for highlighted quotations
- **Code blocks** for technical snippets
- **Tables** for side-by-side comparison
- **Images** copied beside the preview

A short code example:

```python
def render(source, template):
    document = load_document(source)
    return template.fill(document)
```

> The renderer keeps every word in its original order and only adds the presentational
> layer around it.

## Comparing the template choices

| Template | Best for | Default notes |
| --- | --- | --- |
| Conventional | Single long-form article | Used when no template is requested |
| Volume | Multi-edition or digest posts | Adds volume and edition metadata |
| Radar | Technology-radar or ecosystem posts | Adds ring and quadrant placement |

## Frequently asked questions

### Does this change my Markdown file?

No. Rendering always writes a separate HTML preview beside the generated output.

### Can I choose which template to use?

Yes. Set `template: conventional`, `template: volume`, or `template: radar` in the
frontmatter. When omitted, the renderer picks a sensible default.
