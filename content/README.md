# Blog Markdown source

This area holds Markdown source content used to generate a structured blog.

Each blog source should include:

- A Markdown file with the main content
- Any images referenced by the Markdown
- Optional frontmatter for details such as title, author, date, and tags

The Markdown does not need to follow the final blog template. The blog generator will read the source content and convert it into the approved blog structure.

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

## Blog generation

To generate a blog, provide the source branch and Markdown file path. The generator should validate that the file exists, read the Markdown, collect referenced images when available, and save the generated blog separately from the original source.
