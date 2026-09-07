"""FastAPI server for the Kovan Labs Seedream poster studio."""

from __future__ import annotations

import base64
import mimetypes
import os
from pathlib import Path
from typing import Annotated

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


ROOT = Path(__file__).resolve().parent
HTML_FILE = ROOT / "Kovan_PromptGen.html"
BRAND_ASSETS_DIR = ROOT / " Brand Assets"
load_dotenv(ROOT / ".env")
OPENROUTER_URL = "https://openrouter.ai/api/v1/images"
MODEL = "bytedance-seed/seedream-4.5"
MAX_PROMPT_CHARS = 20_000
MAX_REFERENCE_BYTES = 10 * 1024 * 1024
ALLOWED_ASPECT_RATIOS = {"4:5", "1:1", "9:16", "3:4"}
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
IMAGE_SIGNATURES = {
    "image/jpeg": (b"\xff\xd8\xff",),
    "image/png": (b"\x89PNG\r\n\x1a\n",),
    "image/gif": (b"GIF87a", b"GIF89a"),
    "image/webp": (b"RIFF",),
}

app = FastAPI(title="Kovan Labs Seedream Poster API", version="1.0.0")
app.mount("/brand-kit", StaticFiles(directory=ROOT / "brand-kit"), name="brand-kit")
# The repository keeps this legacy directory with a leading space in its name.
app.mount("/brand-assets", StaticFiles(directory=BRAND_ASSETS_DIR), name="brand-assets")


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(HTML_FILE)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


async def reference_data_url(upload: UploadFile | None) -> str | None:
    if upload is None or not upload.filename:
        return None
    content_type = (upload.content_type or "").lower()
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="Speaker image must be a JPEG, PNG, WebP, or GIF.")
    contents = await upload.read(MAX_REFERENCE_BYTES + 1)
    if len(contents) > MAX_REFERENCE_BYTES:
        raise HTTPException(status_code=413, detail="Speaker image must be 10 MB or smaller.")
    if not contents or not any(contents.startswith(signature) for signature in IMAGE_SIGNATURES[content_type]):
        raise HTTPException(status_code=422, detail="Speaker image contents do not match the declared image type.")
    if content_type == "image/webp" and contents[8:12] != b"WEBP":
        raise HTTPException(status_code=422, detail="Speaker image contents do not match the declared image type.")
    media_type = content_type or mimetypes.guess_type(upload.filename)[0] or "image/png"
    encoded = base64.b64encode(contents).decode("ascii")
    return f"data:{media_type};base64,{encoded}"


def upstream_error(response: httpx.Response) -> HTTPException:
    status = response.status_code
    if status in {401, 403}:
        return HTTPException(status_code=502, detail="OpenRouter authentication failed. Check OPENROUTER_API_KEY.")
    if status == 402:
        return HTTPException(status_code=502, detail="OpenRouter rejected the request because the account has insufficient credit.")
    if status == 429:
        return HTTPException(status_code=429, detail="OpenRouter rate limit reached. Try again shortly.")
    if 400 <= status < 500:
        return HTTPException(status_code=400, detail="OpenRouter rejected the generation request. Check the prompt and image settings.")
    return HTTPException(status_code=502, detail="OpenRouter could not generate the poster right now.")


@app.post("/api/generate")
async def generate_poster(
    prompt: Annotated[str, Form(...)],
    aspect_ratio: Annotated[str, Form(...)],
    speaker: Annotated[UploadFile | None, File()] = None,
) -> dict:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=503, detail="The server is missing OPENROUTER_API_KEY.")
    prompt = prompt.strip()
    if not prompt:
        raise HTTPException(status_code=422, detail="Prompt cannot be empty.")
    if len(prompt) > MAX_PROMPT_CHARS:
        raise HTTPException(status_code=422, detail="Prompt is too long. Keep it under 20,000 characters.")
    if aspect_ratio not in ALLOWED_ASPECT_RATIOS:
        raise HTTPException(status_code=422, detail="Unsupported poster aspect ratio.")

    speaker_url = await reference_data_url(speaker)
    payload: dict = {
        "model": MODEL,
        "prompt": (
            f"{prompt}\n\nCreate one simple, empty outlined rectangle in the top-left as the logo frame. "
            "Make it approximately 28% of the canvas wide and 18% high, with a clear interior and surrounding area. "
            "Nothing may overlap the logo frame: no text, icons, pills, shapes, motifs, or illustrations. "
            "Do not render any logo, company name, wordmark, initials, or brand mark anywhere; the original official logo is composited over the frame after generation. "
            "Never display palette labels, colour names, hex codes, font names, style names, proportions, specifications, instructions, or design notes in the poster."
        ),
        "resolution": "2K",
        "aspect_ratio": aspect_ratio,
        "n": 1,
        "output_format": "png",
    }
    if speaker_url:
        payload["input_references"] = [{"type": "image_url", "image_url": {"url": speaker_url}}]

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=15.0)) as client:
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Poster generation timed out. Try again.") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Could not reach OpenRouter. Try again.") from exc

    if response.is_error:
        raise upstream_error(response)
    try:
        result = response.json()
        image = result["data"][0]
        encoded = image["b64_json"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise HTTPException(status_code=502, detail="OpenRouter returned an invalid image response.") from exc

    media_type = image.get("media_type", "image/png")
    if not media_type.startswith("image/"):
        raise HTTPException(status_code=502, detail="OpenRouter returned an unsupported image format.")
    usage = result.get("usage") if isinstance(result.get("usage"), dict) else {}
    return {"image": f"data:{media_type};base64,{encoded}", "media_type": media_type, "usage": usage}
