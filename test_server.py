import base64
import os
import unittest
from unittest.mock import AsyncMock, patch

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
    def __init__(self, *args, **kwargs):
        self.post = AsyncMock(return_value=FakeResponse())

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None


class FakeUpload:
    filename = "speaker.png"
    content_type = "image/png"

    async def read(self, size=-1):
        return b"fake-image"


class PosterApiTests(unittest.TestCase):
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

    def test_generation_rejects_unsupported_ratio_before_upstream_call(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "server-secret"}, clear=True):
            with self.assertRaises(HTTPException) as caught:
                self.run_async(server.generate_poster("make a poster", "16:9", None))
        self.assertEqual(caught.exception.status_code, 422)


if __name__ == "__main__":
    unittest.main()
