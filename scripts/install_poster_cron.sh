#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_binary="$project_dir/.venv/bin/python"
if [[ ! -x "$python_binary" ]]; then
  echo "Missing .venv. Run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi
job="CRON_TZ=Asia/Kolkata\n0 10 * * * cd \"$project_dir\" && \"$python_binary\" scripts/run_poster_schedule.py >> \"$project_dir/poster-cron.log\" 2>&1"

current="$(crontab -l 2>/dev/null || true)"
filtered="$(printf '%s\n' "$current" | grep -v -E '^(CRON_TZ=Asia/Kolkata|.*scripts/(poster_worker/daily.mjs|run_poster_schedule.py).*)$' || true)"
printf '%s\n%s\n' "$filtered" "$job" | crontab -
echo "Installed daily poster endpoint call: 10:00 Asia/Kolkata"
