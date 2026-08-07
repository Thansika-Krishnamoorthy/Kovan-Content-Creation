from __future__ import annotations

import base64
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.blog_renderer.core import (
    ROOT,
    RenderError,
    load_manifest,
    render_file,
    render_file_with_manifest,
    save_manifest,
)


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUB"
    "AScY42YAAAAASUVORK5CYII="
)


class BlogRendererTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "content")
        self.source_dir = Path(self.temp.name)
        self.image = self.source_dir / "diagram.png"
        self.image.write_bytes(PNG_1X1)
        self.source = self.source_dir / "article.md"
        self.original = """---
title: Rendering Markdown safely
author: Kovan Labs
date: 2026-07-23
category: Engineering
summary: A renderer test with an image and a table.
---

# Rendering Markdown safely

The supplied words remain in their original order.

## Image

![A one-pixel test diagram](diagram.png "Test diagram")

## Comparison

| Input | Output |
| --- | --- |
| Markdown | HTML |

> A highlighted Markdown quotation.

## Frequently asked questions

### Does the renderer use accessible FAQ controls?

Yes. FAQ questions become native disclosure controls.

### Does the Markdown source remain unchanged?

Yes. Rendering writes a separate HTML file.
"""
        self.source.write_text(self.original, encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_all_templates_render_without_placeholders(self) -> None:
        for template in ("conventional", "volume", "radar"):
            with self.subTest(template=template):
                output_dir = self.source_dir / f"output-{template}"
                output = render_file(
                    self.source,
                    output_dir,
                    forced_template=template,
                    overwrite=True,
                )
                page = output.read_text(encoding="utf-8")
                self.assertNotIn("{{", page)
                self.assertIn("The supplied words remain in their original order.", page)
                self.assertIn('class="table-wrap"', page)
                self.assertIn('class="faq"', page)
                self.assertEqual(page.count("<details>"), 2)
                self.assertEqual(page.count("<summary>"), 2)
                self.assertNotIn(
                    "<h3>Does the renderer use accessible FAQ controls?</h3>",
                    page,
                )
                self.assertIn("assets/rendering-markdown-safely/diagram.png", page)
                self.assertTrue(
                    (output.parent / "assets" / output.stem / "diagram.png").is_file()
                )
                self.assertEqual(self.source.read_text(encoding="utf-8"), self.original)

    def test_image_without_alt_text_is_rejected(self) -> None:
        self.source.write_text("# Missing alt\n\n![](diagram.png)\n", encoding="utf-8")
        with self.assertRaisesRegex(RenderError, "alt text"):
            render_file(self.source, self.source_dir / "invalid", overwrite=True)

    def test_manifest_skips_unchanged_and_updates_changed_source(self) -> None:
        manifest_path = self.source_dir / "manifest.json"
        output_dir = self.source_dir / "manifest-output"
        manifest = load_manifest(manifest_path)

        first_output, first_status = render_file_with_manifest(
            self.source,
            output_dir,
            manifest,
        )
        self.assertEqual(first_status, "created")
        self.assertIsNotNone(first_output)
        save_manifest(manifest_path, manifest)

        reloaded = load_manifest(manifest_path)
        second_output, second_status = render_file_with_manifest(
            self.source,
            output_dir,
            reloaded,
        )
        self.assertEqual(second_status, "skipped")
        self.assertEqual(second_output, first_output)

        self.source.write_text(
            self.original + "\n\n## New section\n\nThis paragraph was added later.\n",
            encoding="utf-8",
        )
        third_output, third_status = render_file_with_manifest(
            self.source,
            output_dir,
            reloaded,
        )
        self.assertEqual(third_status, "updated")
        self.assertEqual(third_output, first_output)
        self.assertIn(
            "This paragraph was added later.",
            third_output.read_text(encoding="utf-8"),
        )

    def test_full_article_renders_all_optional_sections(self) -> None:
        self.source.write_text(
            """---
title: Full article with every optional block
author: Ava Chen
date: 2026-08-01
category: Engineering culture
summary: Renders the image, table, quotation, highlighted note, and FAQ blocks together.
---

# Full article with every optional block

The intro paragraph leads the full article.

![A labelled architecture diagram](diagram.png "Figure 1: a labelled diagram")

## Side-by-side comparison

| Approach | Lead time | Risk |
| --- | --- | --- |
| Monolith | Fast | Higher |
| Services | Slower | Lower |

> A verbatim quotation from a linked source.

## Key takeaway

An important non-quotation note worth highlighting.

## Frequently asked questions

### Can a full article mix all optional sections?

Yes, every optional block renders in one article.

### Does the canonical template stay unchanged?

Yes, rendering writes a separate HTML file.
""",
            encoding="utf-8",
        )
        template_before = (ROOT / "templates" / "blog-template.html").read_text(
            encoding="utf-8"
        )
        output_dir = self.source_dir / "output-full"
        output = render_file(self.source, output_dir, overwrite=True)
        page = output.read_text(encoding="utf-8")

        self.assertNotIn("{{", page)
        self.assertIn('class="table-wrap"', page)
        self.assertIn('class="faq"', page)
        self.assertEqual(page.count("<details>"), 2)
        self.assertEqual(page.count("<summary>"), 2)
        self.assertIn("<figure>", page)
        self.assertIn("<blockquote>", page)
        self.assertIn("An important non-quotation note worth highlighting.", page)
        self.assertIn("By: <strong>Ava Chen</strong>", page)
        self.assertIn("assets/full-article-with-every-optional-block/diagram.png", page)
        self.assertTrue(
            (
                output.parent
                / "assets"
                / output.stem
                / "diagram.png"
            ).is_file()
        )
        self.assertEqual(
            (ROOT / "templates" / "blog-template.html").read_text(encoding="utf-8"),
            template_before,
            "The canonical template must not be modified by rendering.",
        )

    def test_minimal_article_omits_optional_sections(self) -> None:
        self.source.write_text(
            """---
title: Minimal article
author: Kovan Labs
date: 2026-08-01
category: Engineering
summary: A bare article with only required fields and prose.
---

# Minimal article

Only this single paragraph exists, so no optional section should appear.
""",
            encoding="utf-8",
        )
        template_before = (ROOT / "templates" / "blog-template.html").read_text(
            encoding="utf-8"
        )
        output_dir = self.source_dir / "output-minimal"
        output = render_file(self.source, output_dir, overwrite=True)
        page = output.read_text(encoding="utf-8")

        self.assertNotIn("{{", page)
        self.assertIn("Only this single paragraph exists", page)
        # No optional blocks may leave blank headings, wrappers, or placeholders.
        self.assertNotIn('class="table-wrap"', page)
        self.assertNotIn("<details>", page)
        self.assertNotIn("<summary>", page)
        self.assertNotIn("Frequently asked questions", page)
        self.assertNotIn("<figure>", page)
        self.assertNotIn("<blockquote>", page)
        self.assertEqual(
            (ROOT / "templates" / "blog-template.html").read_text(encoding="utf-8"),
            template_before,
            "The canonical template must not be modified by rendering.",
        )
        self.assertNotEqual(output.resolve(), (ROOT / "templates" / "blog-template.html").resolve())

    def test_missing_required_summary_is_rejected_before_generation(self) -> None:
        self.source.write_text(
            """---
title: Article without a summary
author: Kovan Labs
date: 2026-08-01
category: Engineering
---

# Article without a summary

## Section one

- A list item only, so no opening paragraph exists to infer a summary from.
""",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(RenderError, "Missing required fields"):
            render_file(self.source, self.source_dir / "invalid", overwrite=True)

    def test_missing_branch_is_rejected(self) -> None:
        with self.assertRaisesRegex(RenderError, "does not exist"):
            render_file(
                self.source_dir / "anywhere" / "article.md",
                self.source_dir / "branch-missing",
                overwrite=True,
                source_branch="definitely-no-such-branch-xyz",
            )

    def test_missing_source_file_is_rejected(self) -> None:
        with self.assertRaisesRegex(RenderError, "does not exist"):
            render_file(
                self.source_dir / "missing.md",
                self.source_dir / "missing-out",
                overwrite=True,
            )

    def test_non_markdown_source_is_rejected(self) -> None:
        note = self.source_dir / "notes.txt"
        note.write_text("# Just a text file", encoding="utf-8")
        with self.assertRaisesRegex(RenderError, "[Mm]arkdown"):
            render_file(note, self.source_dir / "txt-out", overwrite=True)

    def test_source_missing_on_branch_is_rejected(self) -> None:
        with self.assertRaisesRegex(RenderError, "does not exist on branch"):
            render_file(
                ROOT / "content" / "does-not-exist.md",
                self.source_dir / "branch-file-missing",
                overwrite=True,
                source_branch="blog-md-intake",
            )

    def test_branch_provenance_is_recorded(self) -> None:
        committed = ROOT / "content" / "spec-driven-development.md"
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        self.assertTrue(branch, "Test requires a checked-out branch.")
        sha = subprocess.run(
            ["git", "rev-parse", branch],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        with tempfile.TemporaryDirectory() as out_dir:
            output = render_file(
                committed,
                Path(out_dir),
                overwrite=True,
                source_branch=branch,
            )
            page = output.read_text(encoding="utf-8")
            self.assertIn("kovan-blog-provenance", page)
            self.assertIn(branch, page)
            self.assertIn("content/spec-driven-development.md", page)
            self.assertIn(sha, page)


if __name__ == "__main__":
    unittest.main()
