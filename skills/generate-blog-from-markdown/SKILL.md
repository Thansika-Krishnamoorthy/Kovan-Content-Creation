---
name: generate-blog-from-markdown
description: Generate a Kovan Labs blog from a Markdown source file stored in this repository. Use when the user provides or references a Git branch and .md path, asks to convert Markdown content into a blog, or wants blog images collected from Markdown references without requiring separate image handoff. This skill validates the source file, preserves the original Markdown, resolves repo-local and allowed public images, then uses the Kovan blog template workflow to save a finished HTML blog.
---

# Generate Blog From Markdown

Use this skill when a blog must be created from a `.md` file in the current repository.

This is a skill-only workflow. Do not require a separate generator script unless the user explicitly asks for one.

## Required Inputs

Gather or infer:

- Source branch, such as `blog-md-intake`
- Markdown file path, such as `content/sample-blog/content.md`
- Optional output filename or slug
- Optional preferred blog type: conventional, volume, or radar

If the branch is omitted, use the current branch. If the Markdown path is omitted and exactly one likely `.md` source exists under `content/`, use it and state that assumption. If multiple likely files exist, ask the user which one to use.

## Source Validation

Before generating the blog:

1. Confirm the repository is available.
2. Confirm the source branch exists locally or on `origin`.
3. Confirm the source file exists and ends in `.md`.
4. Read the Markdown content without modifying it.
5. If the source branch differs from the current branch, inspect the file from that branch with Git read commands instead of switching branches when the worktree has unrelated changes.
6. Preserve the original Markdown file. Never rewrite, format, or move it unless the user explicitly asks.

Prefer safe read-only Git commands for source inspection:

```bash
git show <branch>:<path/to/content.md>
```

Use local file reads only when the target branch is already checked out or when the file exists in the current worktree.

## Markdown Intake

Extract useful metadata from frontmatter when present:

- `title`
- `author`
- `date`
- `category`
- `tags`
- `summary`

If frontmatter is missing, infer reasonable values from the H1, first paragraph, file path, and current date. Leave a clear placeholder only when a value cannot be inferred safely.

Treat the Markdown as source material, not as the final article structure. Keep the author's intent and factual claims, but improve flow, headings, clarity, and completeness when converting it into the Kovan blog format.

## Image Handling

Find Markdown images written as:

```md
![Alt text](path-or-url)
```

For repo-local image paths:

1. Resolve relative paths from the Markdown file's directory.
2. Confirm the image exists in the selected branch or current worktree.
3. Copy the image into an output asset location near the generated blog when needed.
4. Update the final HTML image path so it resolves from the saved blog file.

For public image URLs:

1. Use the image only when the URL is publicly accessible and appropriate to reuse.
2. Download the image only when the user has allowed direct image download or when the project workflow already permits it.
3. Save downloaded images near the output blog and update the final HTML path.
4. If the URL is inaccessible or reuse is unclear, report the image as unresolved instead of inventing a replacement.

Every genuine content image needs useful alt text. Decorative Kovan brand assets must use empty alt text and must not be treated as article evidence.

## Blog Generation

Use the existing `write-kovan-blog` skill for the branded HTML rules, template selection, editorial standards, SEO checks, brand assets, and validation.

Follow this handoff:

1. Read the Markdown source and identify the article purpose, title, summary, body sections, links, images, and FAQs.
2. Select the correct Kovan template using `write-kovan-blog` rules:
   - Conventional article: `templates/blog-template.html`
   - Volume or edition: `templates/blog-volume-template.html`
   - Technology radar: `templates/blog-radar-template.html`
3. Convert the Markdown into a complete Kovan Labs blog, not a plain Markdown export.
4. Save the finished HTML separately from the source Markdown.
5. Do not edit reusable templates directly. Copy the selected template into the output path before filling it.

Default output locations:

- Conventional and radar blogs: `output/website/<slug>.html`
- Volume blogs: `output/website/volume/<slug>.html`
- Optional processed Markdown draft: `output/blogs/<slug>.md`

Use lowercase hyphenated filenames based on the title. If a target file already exists, do not overwrite it unless the user asks; add a version suffix instead.

## Completion Checklist

Before reporting completion:

- Source branch and Markdown path are recorded.
- Source Markdown remains unchanged.
- Final HTML exists.
- No required `{{PLACEHOLDER}}` remains.
- Images resolve or unresolved images are reported clearly.
- Links are valid where they can be checked.
- Output path is reported to the user.
- Any assumptions are stated briefly.

