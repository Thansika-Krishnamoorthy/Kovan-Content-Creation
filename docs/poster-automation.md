# Python poster API and daily systemd scheduling

The project now uses two FastAPI endpoints:

```text
systemd user service
  → run the FastAPI app for /api/posters/cron and /api/posters/generate

systemd user timer at 08:00 Asia/Kolkata
  → POST /api/posters/cron
  → query Supabase for todays recurring events and employee details
  → POST /api/posters/generate for each matched event
  → render figma-export/index.html with headless Chrome
  → store the 1080×1350 PNG in generated-posters
  → send the stored poster to Microsoft Teams when configured
```

`/api/posters/cron` is the cron orchestration endpoint; `/api/posters/schedule`
is kept as an alias to the same handler for backward compatibility.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.poster-automation.example .env.poster-automation
```

Set every required value in `.env.poster-automation`. `TEAMS_WEBHOOK_URL` is
optional; without it, posters are generated and stored but not delivered.

Apply the Supabase migrations before starting the API:

```bash
npx supabase db push
```

The migrations provide the recurring-event RPCs, idempotent `poster_runs`
claims, private Storage buckets, and separate Teams delivery tracking.

## Start the API manually

```bash
.venv/bin/uvicorn scripts.poster_api.app:app --host 127.0.0.1 --port 8000
```

Interactive API documentation is available while the server is running:

```text
http://127.0.0.1:8000/docs
```

## Call endpoints manually

Cron endpoint for today:

```bash
.venv/bin/python scripts/run_poster_schedule.py
```

Cron endpoint for a test date:

```bash
.venv/bin/python scripts/run_poster_schedule.py --date 2026-07-28
```

The generation endpoint is internal. The cron endpoint supplies one
validated database row to it using `POSTER_INTERNAL_API_SECRET`.

## Install the 08:00 AM systemd timer

The installer creates two user-level systemd units:

- `kovan-poster-api.service` keeps the FastAPI endpoint server running.
- `kovan-poster-schedule.timer` triggers `kovan-poster-schedule.service` daily
  at 08:00 Asia/Kolkata. That service calls `/api/posters/cron`, which
  queries Supabase and calls `/api/posters/generate` for each matched event.

```bash
chmod +x scripts/install_poster_systemd_timer.sh scripts/run_poster_schedule.py
./scripts/install_poster_systemd_timer.sh
systemctl --user list-timers kovan-poster-schedule.timer
```

Check execution logs with `journalctl --user`. Generated images and run status
are available in Supabase under `generated-posters` and `poster_runs`.

Useful systemd commands:

```bash
systemctl --user status kovan-poster-api.service
systemctl --user status kovan-poster-schedule.timer
systemctl --user status kovan-poster-schedule.service
systemctl --user start kovan-poster-schedule.service
journalctl --user -u kovan-poster-api.service
journalctl --user -u kovan-poster-schedule.service
```

## Cron fallback

Cron is not used by the systemd installer. The original cron installer is kept
at `scripts/install_poster_cron.sh` so the job can be restored later if needed.
