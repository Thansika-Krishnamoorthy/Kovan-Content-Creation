import base64
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

import server


class FakeResponse:
    status_code = 200
    is_error = False

    def json(self):
        return {
            "data": [{"b64_json": base64.b64encode(b"png-bytes").decode(), "media_type": "image/png"}],
            "usage": {"cost": 0.05},
        }


class FakeAsyncClient:
    last_json = None

    def __init__(self, *args, **kwargs):
        self.post = self._post

    async def _post(self, url, headers, json):
        FakeAsyncClient.last_json = json
        return FakeResponse()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None


class FakeUpload:
    filename = "speaker.png"
    content_type = "image/png"

    async def read(self, size=-1):
        return b"\x89PNG\r\n\x1a\nvalid-image"


class PosterApiTests(unittest.TestCase):
    def test_all_approved_logos_are_available_to_the_picker(self):
        approved_logos = {
            "logo_horizontal.png",
            "logo_horizontal_tagline.png",
            "logo_vertical.png",
            "logo_vertical_tagline.png",
            "logo_mono_ink.png",
            "logo_mono_white.png",
            "mark.png",
        }
        html = Path("Kovan_PromptGen.html").read_text(encoding="utf-8")
        for filename in approved_logos:
            self.assertTrue((server.BRAND_ASSETS_DIR / filename).is_file())
            self.assertIn(f'/brand-assets/{filename}', html)

    def test_model_prompt_uses_visual_direction_not_brand_spec_text(self):
        html = server.HTML_FILE.read_text(encoding="utf-8")
        self.assertIn("Do not add labels, captions, keys, palettes", html)
        self.assertIn("Do not render a logo, company name", html)
        self.assertIn("empty outlined rectangle", html)
        self.assertNotIn("Use Paper #FFFFFF", html)
        self.assertNotIn("Poppins 600/700", html)

    def test_health_endpoint_is_public(self):
        self.assertEqual(self.run_async(server.health()), {"status": "ok"})

    def test_generation_requires_server_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(HTTPException) as caught:
                self.run_async(server.generate_poster("make a poster", "4:5", None))
        self.assertEqual(caught.exception.status_code, 503)

    def run_async(self, coroutine):
        import asyncio

        return asyncio.run(coroutine)

    def test_generation_maps_prompt_ratio_and_speaker_reference(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "server-secret"}, clear=True):
            with patch("server.httpx.AsyncClient", FakeAsyncClient):
                result = self.run_async(server.generate_poster(
                    "make a Kovan poster",
                    "9:16",
                    FakeUpload(),
                ))
        self.assertTrue(result["image"].startswith("data:image/png;base64,"))
        self.assertEqual(FakeAsyncClient.last_json["aspect_ratio"], "9:16")
        self.assertEqual(len(FakeAsyncClient.last_json["input_references"]), 1)
        upstream_prompt = FakeAsyncClient.last_json["prompt"]
        self.assertIn("Never display palette labels", upstream_prompt)
        self.assertIn("Do not render any logo", upstream_prompt)
        self.assertIn("empty outlined rectangle", upstream_prompt)

    def test_generation_rejects_invalid_image_contents(self):
        class InvalidUpload(FakeUpload):
            async def read(self, size=-1):
                return b"not-an-image"

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "server-secret"}, clear=True):
            with self.assertRaises(HTTPException) as caught:
                self.run_async(server.generate_poster("make a poster", "4:5", InvalidUpload()))
        self.assertEqual(caught.exception.status_code, 422)

    def test_generation_rejects_unsupported_ratio_before_upstream_call(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "server-secret"}, clear=True):
            with self.assertRaises(HTTPException) as caught:
                self.run_async(server.generate_poster("make a poster", "16:9", None))
        self.assertEqual(caught.exception.status_code, 422)


if __name__ == "__main__":
    unittest.main()
