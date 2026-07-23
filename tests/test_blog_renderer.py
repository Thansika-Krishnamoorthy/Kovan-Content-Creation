from __future__ import annotations

import base64
import tempfile
import unittest
from pathlib import Path

from scripts.blog_renderer.core import ROOT, RenderError, render_file


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
                self.assertIn("assets/rendering-markdown-safely/diagram.png", page)
                self.assertTrue(
                    (output.parent / "assets" / output.stem / "diagram.png").is_file()
                )
                self.assertEqual(self.source.read_text(encoding="utf-8"), self.original)

    def test_image_without_alt_text_is_rejected(self) -> None:
        self.source.write_text("# Missing alt\n\n![](diagram.png)\n", encoding="utf-8")
        with self.assertRaisesRegex(RenderError, "alt text"):
            render_file(self.source, self.source_dir / "invalid", overwrite=True)


if __name__ == "__main__":
    unittest.main()
