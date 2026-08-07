#!/usr/bin/env python3
"""Get the image URL of a poster in the generated-posters bucket and send it to Teams.

When the systemd timer runs, the poster is generated and stored in the
generated-posters bucket. This script fetches the signed image URL for a
poster and posts it to the Teams channel as a {message, imageUrl} payload.

Usage:
    # Send the most recently stored poster
    .venv/bin/python scripts/send_poster_to_teams.py

    # Send a specific poster by its storage path
    .venv/bin/python scripts/send_poster_to_teams.py --path 2026/birthday/<id>-2026-08-06.png

    # Send the latest poster for a specific date
    .venv/bin/python scripts/send_poster_to_teams.py --date 2026-08-06
"""

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.poster_api.config import load_env
from scripts.poster_api.http import send_to_teams
from scripts.poster_api.supabase import SupabaseClient

BUCKET = "generated-posters"


def build_client() -> SupabaseClient:
    load_env()
    url = os.getenv("SUPABASE_URL") or f"https://{os.getenv('SUPABASE_PROJECT_REF')}.supabase.co"
    return SupabaseClient(url, os.getenv("SUPABASE_SERVICE_ROLE_KEY"))


def _walk_posters(client: SupabaseClient, prefix: str = "") -> list[dict]:
    """Recursively collect PNG poster objects under a prefix.

    Each returned dict has the object metadata plus a ``path`` key holding the
    full storage path (including folder prefixes).
    """
    posters: list[dict] = []
    objects = client.list_objects(BUCKET, prefix=prefix, limit=1000)
    for obj in objects:
        name = obj.get("name", "")
        if not name or name.endswith(".emptyFolderPlaceholder"):
            continue
        if name.lower().endswith(".png"):
            full = f"{prefix}/{name}".strip("/")
            posters.append({**obj, "path": full})
        else:
            # It's a subfolder; recurse into it.
            posters.extend(_walk_posters(client, prefix=f"{prefix}/{name}".strip("/")))
    return posters


def latest_poster(client: SupabaseClient, date_prefix: str | None = None) -> str:
    """Return the storage path of the most recently added poster.

    If ``date_prefix`` (YYYY-MM-DD) is given, only posters whose filename
    contains that date are considered.
    """
    posters = _walk_posters(client)
    if date_prefix:
        posters = [obj for obj in posters if date_prefix in obj.get("name", "")]
    if not posters:
        raise RuntimeError(f"No posters found in {BUCKET}" + (f" for date {date_prefix!r}" if date_prefix else ""))
    # newest first by updated_at
    posters.sort(key=lambda obj: obj.get("updated_at", ""), reverse=True)
    return posters[0]["path"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", help="Storage path of the poster to send")
    parser.add_argument("--date", help="YYYY-MM-DD to pick the latest poster for that date")
    parser.add_argument("--message", help="Message text (defaults to the poster filename)")
    parser.add_argument("--expires-in", type=int, default=3600, help="Signed URL lifetime (seconds)")
    args = parser.parse_args()

    client = build_client()

    if args.path:
        poster_path = args.path
    elif args.date:
        poster_path = latest_poster(client, date_prefix=args.date)
    else:
        poster_path = latest_poster(client)

    image_url = client.signed_poster_url(poster_path, expires_in=args.expires_in)
    message = args.message or Path(poster_path).stem

    webhook = os.getenv("TEAMS_WEBHOOK_URL")
    if not webhook:
        raise RuntimeError("TEAMS_WEBHOOK_URL is not set in .env.poster-automation")

    print(f"Poster: {poster_path}")
    print(f"Image URL: {image_url}")
    send_to_teams(webhook, message, image_url)
    print("Sent to Teams.")


if __name__ == "__main__":
    main()
