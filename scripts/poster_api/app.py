import hmac
import time
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Header, HTTPException

from .config import Settings
from .http import post_json, send_to_teams_media
from .models import GeneratePosterRequest, ScheduleRequest
from .renderer import (
    completed_years,
    render_gif,
)
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


def _as_event_list(events: dict | list[dict]) -> list[dict]:
    if isinstance(events, dict):
        return [events]
    return list(events)


def _join_english(parts: list[str]) -> str:
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    return f"{', '.join(parts[:-1])}, and {parts[-1]}"


def event_label(event: dict) -> str:
    name = event["person_name"]
    if event["event_type"] == "work_anniversary":
        return f"{name}'s work anniversary"
    return f"{name}'s birthday"


def email_subject(events: dict | list[dict]) -> str:
    """Professional Outlook subject for one or more celebrations today."""
    items = _as_event_list(events)
    if not items:
        return "Please join us in today's celebrations."
    joined = _join_english([event_label(event) for event in items])
    if len(items) == 1:
        name = items[0]["person_name"]
        return f"Today is {joined}. Please join us in wishing {name}."
    return f"Today is {joined}. Please join us in wishing them."


def email_plain_body(posters: list[dict]) -> str:
    """Greeting plus signed Storage URLs for today's GIFs."""
    if not posters:
        return ""
    intro = email_subject([poster["event"] for poster in posters])
    lines = [intro, ""]
    for poster in posters:
        name = poster["event"]["person_name"]
        lines.append(f"{name}: {poster['media_url']}")
    return "\n".join(lines)


def email_html_body(posters: list[dict]) -> str:
    """Show each GIF stored in Supabase inline in the Outlook body."""
    if not posters:
        return ""
    intro = email_subject([poster["event"] for poster in posters])
    images = "".join(
        f'<p><img src="{poster["media_url"]}" alt="Animated poster" /></p>'
        for poster in posters
    )
    return f"<p>{intro}</p>{images}"


def dependencies():
    settings = Settings.from_env()
    return settings, SupabaseClient(
        settings.supabase_url,
        settings.service_role_key,
    )


def wait_for_stored_generation(
    supabase: SupabaseClient,
    event_id: str,
    occurrence_date: date,
    attempts: int = 60,
    interval_seconds: int = 5,
) -> dict:
    """Wait for an earlier generation request that is still rendering.

    The HTTP client retries timed-out generation requests. A retry can observe
    the idempotent run while the original request is still processing and get
    a ``skipped`` response without a poster path. Polling the authoritative run
    record keeps delivery attached to the original render instead of silently
    abandoning it.
    """
    for attempt in range(attempts):
        run = supabase.get_run(event_id, occurrence_date)
        if run:
            if run.get("status") == "failed":
                raise RuntimeError(
                    run.get("error") or "Poster generation failed while awaiting storage"
                )
            if run.get("status") == "stored" and run.get("poster_path"):
                return {
                    "status": (
                        "skipped" if run.get("teams_delivered_at") else "stored"
                    ),
                    "poster_path": run["poster_path"],
                    "run_id": str(run["id"]),
                    "teams_delivered_at": run.get("teams_delivered_at"),
                }
        if attempt + 1 < attempts:
            time.sleep(interval_seconds)
    raise RuntimeError("Timed out waiting for poster generation to finish")


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
            and (
                not existing["poster_path"].lower().endswith(".gif")
                or not supabase.object_exists(
                    "generated-posters",
                    existing["poster_path"],
                )
            )
        ):
            supabase.update_run(
                str(existing["id"]),
                {
                    "status": "failed",
                    "error": "Regenerating poster as animated GIF",
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
        gif = render_gif(payload, photo, content_type, settings.chrome_binary)
        poster_path = (
            f"{payload.occurrence_date.year}/{payload.event_type}/"
            f"{payload.event_id}-{payload.occurrence_date.isoformat()}.gif"
        )
        supabase.upload_gif(poster_path, gif)
        # Remove a previous animated/static object for the same event/date so each
        # poster folder retains only the animated GIF.
        legacy_paths = [
            poster_path.removesuffix(".gif") + suffix
            for suffix in (".mp4", ".webp", ".png")
        ]
        for legacy_path in legacy_paths:
            if supabase.object_exists("generated-posters", legacy_path):
                supabase.delete_object("generated-posters", legacy_path)
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

    delivered_posters: list[dict] = []

    for event in events:
        try:
            generated = post_json(
                settings.generation_url,
                {
                    **event,
                    "occurrence_date": occurrence_date.isoformat(),
                },
                {"x-poster-internal-secret": settings.internal_secret},
                timeout=300,
            )
            if (
                generated["status"] == "skipped"
                and settings.teams_webhook_url
                and not generated.get("poster_path")
                and not generated.get("teams_delivered_at")
            ):
                generated = wait_for_stored_generation(
                    supabase,
                    str(event["event_id"]),
                    occurrence_date,
                )
            generated_path = generated.get("poster_path")
            if generated_path and not generated_path.lower().endswith(".gif"):
                raise RuntimeError(
                    "Animated-only delivery rejected non-GIF poster: "
                    f"{generated_path}"
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
            if settings.teams_webhook_url and generated_path:
                try:
                    media_url = supabase.signed_poster_url(
                        generated["poster_path"],
                        expires_in=60 * 60 * 24 * 365,
                    )
                    delivered_posters.append(
                        {
                            "event": event,
                            "run_id": generated["run_id"],
                            "poster_path": generated_path,
                            "media_url": media_url,
                            "file_name": generated["poster_path"].rsplit("/", 1)[-1],
                            "teams_message": teams_message(event, occurrence_date),
                        }
                    )
                except Exception as error:
                    if generated.get("run_id"):
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

    # One Outlook digest, then one Teams webhook per person (message + GIF URL).
    if settings.teams_webhook_url and delivered_posters:
        first = delivered_posters[0]
        try:
            send_to_teams_media(
                settings.teams_webhook_url,
                email_plain_body(delivered_posters),
                first["media_url"],
                first["file_name"],
                "image/gif",
                to=settings.poster_email_to,
                subject=email_subject(
                    [poster["event"] for poster in delivered_posters]
                ),
                kind="email",
                html_body=email_html_body(delivered_posters),
            )
            for poster in delivered_posters:
                send_to_teams_media(
                    settings.teams_webhook_url,
                    poster["teams_message"],
                    poster["media_url"],
                    poster["file_name"],
                    "image/gif",
                    person_name=poster["event"]["person_name"],
                    kind="teams",
                )
            delivered_at = datetime.now(timezone.utc).isoformat()
            for poster in delivered_posters:
                if poster.get("run_id"):
                    supabase.update_run(
                        poster["run_id"],
                        {
                            "teams_delivered_at": delivered_at,
                            "teams_error": None,
                        },
                    )
            result["delivered"] = len(delivered_posters)
        except Exception as error:
            for poster in delivered_posters:
                if poster.get("run_id"):
                    supabase.update_run(
                        poster["run_id"],
                        {"teams_error": str(error)},
                    )
            result["failures"].append({
                "event_id": "email-digest",
                "error": str(error),
            })
    return result


def authorize(actual: str | None, expected: str) -> None:
    if not actual or not hmac.compare_digest(actual, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")
