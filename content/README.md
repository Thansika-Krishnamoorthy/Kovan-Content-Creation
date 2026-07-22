# Blog content intake

Use this folder when a teammate gives blog content as a Markdown file.

## Folder convention

Create one folder per blog:

```text
content/
  blog-slug/
    content.md
    images/
      example-image.png
```

The source Markdown file should be named `content.md`. Images used by that Markdown should go in the same blog folder, preferably inside `images/`.

## How to reference images

Use normal Markdown image syntax:

```md
![Short image description](images/example-image.png)
```

External image URLs are also allowed when the image is publicly accessible:

```md
![Diagram title](https://example.com/diagram.png)
```

When the blog is generated, repo-local images can be copied into the blog output and the links can be updated automatically.

## Suggested Git workflow

1. Create a branch for the blog content, for example `blog-md-intake` or `blog-content-ai-agents`.
2. Add the teammate's Markdown at `content/<blog-slug>/content.md`.
3. Add any images at `content/<blog-slug>/images/`.
4. Generate the blog from that branch and Markdown path.
5. Keep the original Markdown unchanged, and save the generated blog separately.

