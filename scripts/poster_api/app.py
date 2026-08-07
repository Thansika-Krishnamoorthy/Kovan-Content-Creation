import hmac
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Header, HTTPException

from .config import Settings
from .http import post_json, send_to_teams
from .models import GeneratePosterRequest, ScheduleRequest
from .renderer import completed_years, render_png
from .supabase import SupabaseClient


app = FastAPI(title="Kovan Event Poster API", version="1.0.0")


def teams_message(event: dict, occurrence_date: date) -> str:
    """Build a friendly Teams message for an event.

    Examples:
        birthday        -> "Happy Birthday, Alice! 🎉"
        work_anniversary-> "Happy 5 Year Work Anniversary, Bob! 🎉"
    """
    name = event["person_name"]
    if event["event_type"] == "work_anniversary":
        event_date = event["event_date"]
        if isinstance(event_date, str):
            event_date = date.fromisoformat(event_date)
        years = completed_years(event_date, occurrence_date)
        label = "Year" if years == 1 else "Years"
        return f"Happy {years} {label} Work Anniversary, {name}! 🎉"
    return f"Happy Birthday, {name}! 🎉"


def dependencies():
    settings = Settings.from_env()
    return settings, SupabaseClient(
        settings.supabase_url,
        settings.service_role_key,
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/posters/generate")
def generate_poster(
    payload: GeneratePosterRequest,
    x_poster_internal_secret: str | None = Header(default=None),
):
    settings, supabase = dependencies()
    authorize(x_poster_internal_secret, settings.internal_secret)
    run = supabase.claim_run(str(payload.event_id), payload.occurrence_date)
    if not run:
        existing = supabase.get_run(
            str(payload.event_id),
            payload.occurrence_date,
        )
        if (
            existing
            and existing.get("poster_path")
            and not supabase.object_exists(
                "generated-posters",
                existing["poster_path"],
            )
        ):
            supabase.update_run(
                str(existing["id"]),
                {
                    "status": "failed",
                    "error": "Recorded poster is missing from Storage",
                },
            )
            run = supabase.claim_run(
                str(payload.event_id),
                payload.occurrence_date,
            )
        if run:
            existing = None
    if not run:
        return {
            "event_id": str(payload.event_id),
            "status": "skipped",
            "poster_path": existing["poster_path"] if existing else None,
            "run_id": str(existing["id"]) if existing else None,
            "teams_delivered_at": (
                existing.get("teams_delivered_at") if existing else None
            ),
        }

    try:
        if payload.event_type == "work_anniversary":
            photo, content_type = supabase.download(
                "employee-photos",
                payload.photo_path,
            )
        else:
            photo, content_type = b"", "image/jpeg"
        png = render_png(payload, photo, content_type, settings.chrome_binary)
        poster_path = (
            f"{payload.occurrence_date.year}/{payload.event_type}/"
            f"{payload.event_id}-{payload.occurrence_date.isoformat()}.png"
        )
        supabase.upload_png(poster_path, png)
        supabase.update_run(
            str(run["id"]),
            {"status": "stored", "poster_path": poster_path, "error": None},
        )
        return {
            "event_id": str(payload.event_id),
            "status": "stored",
            "poster_path": poster_path,
            "run_id": str(run["id"]),
            "teams_delivered_at": None,
        }
    except Exception as error:
        supabase.update_run(
            str(run["id"]),
            {"status": "failed", "error": str(error)},
        )
        raise HTTPException(status_code=500, detail="Poster generation failed") from error


@app.post("/api/posters/schedule")
@app.post("/api/posters/cron")
def run_schedule(
    payload: ScheduleRequest,
    x_poster_schedule_secret: str | None = Header(default=None),
):
    settings, supabase = dependencies()
    authorize(x_poster_schedule_secret, settings.schedule_secret)
    occurrence_date = payload.run_date or datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).date()
    events = supabase.events_due_on(occurrence_date)
    result = {
        "date": occurrence_date.isoformat(),
        "matched": len(events),
        "generated": 0,
        "delivered": 0,
        "skipped": 0,
        "failures": [],
    }

    for event in events:
        try:
            generated = post_json(
                settings.generation_url,
                {
                    **event,
                    "occurrence_date": occurrence_date.isoformat(),
                },
                {"x-poster-internal-secret": settings.internal_secret},
            )
            if generated["status"] == "skipped" and (
                not settings.teams_webhook_url
                or not generated.get("poster_path")
                or generated.get("teams_delivered_at")
            ):
                result["skipped"] += 1
                continue
            if generated["status"] == "stored":
                result["generated"] += 1
            if settings.teams_webhook_url:
                try:
                    poster_url = supabase.signed_poster_url(
                        generated["poster_path"]
                    )
                    send_to_teams(
                        settings.teams_webhook_url,
                        teams_message(event, occurrence_date),
                        poster_url,
                    )
                    supabase.update_run(
                        generated["run_id"],
                        {
                            "teams_delivered_at": datetime.now(
                                timezone.utc
                            ).isoformat(),
                            "teams_error": None,
                        },
                    )
                    result["delivered"] += 1
                except Exception as error:
                    supabase.update_run(
                        generated["run_id"],
                        {"teams_error": str(error)},
                    )
                    raise
        except Exception as error:
            result["failures"].append({
                "event_id": str(event["event_id"]),
                "error": str(error),
            })
    return result


def authorize(actual: str | None, expected: str) -> None:
    if not actual or not hmac.compare_digest(actual, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")
