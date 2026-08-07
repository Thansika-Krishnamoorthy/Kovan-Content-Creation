#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path

# Direct execution sets sys.path to scripts/, but imports use the repository's
# scripts package. Add the project root so both direct and module execution work.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.poster_api.config import load_env, required
from scripts.poster_api.http import post_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Call the poster cron endpoint")
    parser.add_argument("--date", help="Optional YYYY-MM-DD run date")
    args = parser.parse_args()
    load_env()
    payload = {"run_date": args.date} if args.date else {}
    result = post_json(
        os.getenv(
            "POSTER_SCHEDULE_URL",
            "http://127.0.0.1:8000/api/posters/cron",
        ),
        payload,
        {"x-poster-schedule-secret": required("POSTER_SCHEDULE_SECRET")},
    )
    print(json.dumps(result))


if __name__ == "__main__":
    main()
