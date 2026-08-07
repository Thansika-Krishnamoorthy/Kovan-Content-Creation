import json
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def post_json(
    url: str,
    payload: dict,
    headers: dict | None = None,
    attempts: int = 3,
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
            with urlopen(request, timeout=60) as response:
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
    signed Supabase Storage URL so Teams renders the image directly.
    """
    post_json(
        webhook_url,
        {
            "message": employee_name,
            "imageUrl": poster_url,
        },
    )
