import base64
import json
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def post_json(
    url: str,
    payload: dict,
    headers: dict | None = None,
    attempts: int = 3,
    timeout: int = 60,
) -> dict:
    last_error = None
    for attempt in range(attempts):
        request = Request(
            url,
            method="POST",
            data=json.dumps(payload).encode(),
            headers={"content-type": "application/json", **(headers or {})},
        )
        try:
            with urlopen(request, timeout=timeout) as response:
                content = response.read()
                return json.loads(content) if content else {}
        except HTTPError as error:
            detail = error.read().decode(errors="replace")
            if error.code < 500:
                raise RuntimeError(f"HTTP {error.code}: {detail}") from error
            last_error = RuntimeError(f"HTTP {error.code}: {detail}")
        except OSError as error:
            last_error = error
        if attempt + 1 < attempts:
            time.sleep(2**attempt)
    raise RuntimeError(f"Request failed after {attempts} attempts: {last_error}")


def send_to_teams(webhook_url: str, employee_name: str, poster_url: str) -> None:
    """Post a generated poster to a Microsoft Teams channel.

    Uses the Power Automate webhook format (message + imageUrl) matching the
    flow triggered by ``test_teams.py``. The poster is referenced by its
    long-lived signed Supabase Storage URL (expires after 5 years) so Teams
    renders the image directly.
    """
    post_json(
        webhook_url,
        {
            "message": employee_name,
            "imageUrl": poster_url,
        },
    )


def send_to_teams_base64(
    webhook_url: str,
    employee_name: str,
    png_bytes: bytes,
) -> None:
    """Post a generated poster to a Microsoft Teams channel as a base64 image.

    The poster PNG is base64-encoded into a self-contained ``data:image/png;
    base64,...`` URI. Unlike a signed Storage URL, a data URI never expires,
    so the image stays visible in Teams indefinitely — at the cost of a larger
    HTTP payload (a 1080x1350 PNG is typically ~1-2 MB).
    """
    data_uri = "data:image/png;base64," + base64.b64encode(png_bytes).decode()
    post_json(
        webhook_url,
        {
            "message": employee_name,
            "imageUrl": data_uri,
        },
    )


def send_to_teams_webp_base64(
    webhook_url: str,
    employee_name: str,
    webp_bytes: bytes,
) -> None:
    """Post a generated poster to a Microsoft Teams channel as a base64 WebP.

    The poster WebP is base64-encoded into a ``data:image/webp;base64,...``
    URI and placed in an Adaptive Card ``Image`` element, which Teams renders
    inline. WebP is far smaller than PNG (often 5-10x), keeping the payload
    within the 28 KB Adaptive Card limit while remaining self-contained
    (never expires).

    Raises RuntimeError if the resulting JSON payload would exceed the 28 KB
    Adaptive Card limit, since Teams would reject the message.
    """
    data_uri = "data:image/webp;base64," + base64.b64encode(webp_bytes).decode()
    payload = {
        "message": employee_name,
        "imageUrl": data_uri,
    }
    _assert_within_adaptive_card_limit(payload)
    post_json(webhook_url, payload)


def send_to_teams_media(
    webhook_url: str,
    message: str,
    media_url: str,
    file_name: str,
    content_type: str,
    person_name: str | None = None,
    to: str | None = None,
    subject: str | None = None,
    kind: str | None = None,
    html_body: str | None = None,
    image_base64: str | None = None,
    extra: dict | None = None,
) -> None:
    """Send a hosted media URL to the Power Automate webhook.

    ``mediaUrl`` / ``imageUrl`` are signed links to the GIF in Supabase
    Storage. ``kind`` is ``email`` for the Outlook digest and ``teams`` for
    one Adaptive Card per person (``message`` + ``imageUrl``).
    """
    payload = {
        "message": message,
        "mediaUrl": media_url,
        "imageUrl": media_url,
        "fileName": file_name,
        "contentType": content_type,
    }
    if person_name:
        payload["personName"] = person_name
    if to:
        payload["to"] = to
    if subject:
        payload["subject"] = subject
    if kind:
        payload["kind"] = kind
    if html_body:
        payload["htmlBody"] = html_body
    if image_base64:
        payload["imageBase64"] = image_base64
    if extra:
        payload.update(extra)
    post_json(webhook_url, payload, timeout=180)


def _assert_within_adaptive_card_limit(payload: dict, limit: int = 28 * 1024) -> None:
    """Raise if the JSON-serialized payload exceeds the Adaptive Card limit.

    Teams enforces a ~28 KB cap on the entire Adaptive Card payload. Base64
    inflates the image by ~33%, so this guard fails fast before posting.
    """
    size = len(json.dumps(payload).encode())
    if size > limit:
        raise RuntimeError(
            f"Adaptive Card payload is {size} bytes, exceeding the {limit} byte "
            "limit. Compress the image further (smaller dimensions / lower "
            "WebP quality) before sending."
        )


def send_to_teams_webhook_base64(
    webhook_url: str,
    message: str,
    image_bytes: bytes,
    file_name: str,
    content_type: str = "image/webp",
) -> None:
    """Post a poster to a Power Automate webhook as a base64 file attachment.

    Sends ``{fileName, message, imageBase64}`` so the Power Automate flow can
    decode the base64 back to binary and attach it as a real file in Teams
    (rather than an inline Adaptive Card image, which cannot render data URIs).
    """
    post_json(
        webhook_url,
        {
            "fileName": file_name,
            "message": message,
            "imageBase64": base64.b64encode(image_bytes).decode(),
            "contentType": content_type,
        },
    )
