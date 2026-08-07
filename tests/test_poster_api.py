import unittest
import subprocess
import sys
import os
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from scripts.poster_api.models import GeneratePosterRequest
from scripts.poster_api.renderer import completed_years, template_url
from scripts.poster_api.app import app, authorize, generate_poster, run_schedule
from scripts.poster_api.config import supabase_url
from scripts.poster_api.models import ScheduleRequest
from fastapi import HTTPException


class PosterApiTests(unittest.TestCase):
    def test_supabase_url_can_be_derived_from_project_ref(self):
        environment = {
            key: value
            for key, value in os.environ.items()
            if key not in {"SUPABASE_URL", "SUPABASE_PROJECT_REF"}
        }
        environment["SUPABASE_PROJECT_REF"] = "example-project"
        with patch.dict(os.environ, environment, clear=True):
            self.assertEqual(
                supabase_url(),
                "https://example-project.supabase.co",
            )

    def test_schedule_client_can_be_executed_as_a_script(self):
        result = subprocess.run(
            [sys.executable, "scripts/run_poster_schedule.py", "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Call the poster cron endpoint", result.stdout)

    def test_birthday_template_url_uses_figma_export(self):
        request = GeneratePosterRequest(
            event_id="745a9af7-2616-480f-ad06-59b29ce82237",
            event_type="birthday",
            event_date=date(1995, 7, 28),
            occurrence_date=date(2026, 7, 28),
            person_id="257838bc-b80f-408f-b124-7ab575effd91",
            person_name="Ada & Grace",
            photo_path="ada/profile.jpg",
            template_key="birthday-default",
        )

        url = template_url(Path("/project/figma-export/index.html"), request)
        query = parse_qs(urlparse(url).query)

        self.assertEqual(urlparse(url).path, "/project/figma-export/index.html")
        self.assertEqual(query["poster"], ["birthday"])
        self.assertEqual(query["name"], ["Ada & Grace"])

    def test_anniversary_template_calculates_completed_years(self):
        self.assertEqual(
            completed_years(date(2020, 7, 28), date(2026, 7, 28)),
            6,
        )

    def test_work_anniversary_database_template_alias_is_supported(self):
        request = GeneratePosterRequest(
            event_id="745a9af7-2616-480f-ad06-59b29ce82237",
            event_type="work_anniversary",
            event_date=date(2020, 7, 28),
            occurrence_date=date(2026, 7, 28),
            person_id="257838bc-b80f-408f-b124-7ab575effd91",
            person_name="Ada",
            photo_path="ada/profile.jpg",
            template_key="work-anniversary",
        )
        self.assertEqual(request.template_key, "work-anniversary")

    def test_template_key_must_match_event_type(self):
        with self.assertRaises(ValueError):
            GeneratePosterRequest(
                event_id="745a9af7-2616-480f-ad06-59b29ce82237",
                event_type="birthday",
                event_date=date(1995, 7, 28),
                occurrence_date=date(2026, 7, 28),
                person_id="257838bc-b80f-408f-b124-7ab575effd91",
                person_name="Ada",
                photo_path="ada/profile.jpg",
                template_key="anniversary-default",
            )

    def test_api_defines_both_poster_endpoints(self):
        paths = app.openapi()["paths"]
        self.assertIn("/api/posters/schedule", paths)
        self.assertIn("/api/posters/cron", paths)
        self.assertIn("/api/posters/generate", paths)
        self.assertIn("post", paths["/api/posters/schedule"])
        self.assertIn("post", paths["/api/posters/cron"])
        self.assertIn("post", paths["/api/posters/generate"])
        # cron and schedule must share the same orchestration handler.
        handlers = {
            route.path: route.endpoint
            for route in app.routes
            if route.path in {"/api/posters/schedule", "/api/posters/cron"}
        }
        self.assertEqual(
            handlers["/api/posters/cron"],
            handlers["/api/posters/schedule"],
        )

    def test_invalid_secret_is_unauthorized(self):
        with self.assertRaises(HTTPException) as context:
            authorize("wrong", "expected")
        self.assertEqual(context.exception.status_code, 401)

    def test_stored_generation_is_reused_for_pending_teams_delivery(self):
        request = GeneratePosterRequest(
            event_id="745a9af7-2616-480f-ad06-59b29ce82237",
            event_type="birthday",
            event_date=date(1995, 7, 28),
            occurrence_date=date(2026, 7, 28),
            person_id="257838bc-b80f-408f-b124-7ab575effd91",
            person_name="Ada",
            photo_path="ada/profile.jpg",
            template_key="birthday-default",
        )
        supabase = SimpleNamespace(
            claim_run=lambda *_: None,
            get_run=lambda *_: {
                "id": "run-id",
                "poster_path": "2026/birthday/poster.png",
                "teams_delivered_at": None,
            },
            object_exists=lambda *_: True,
        )
        settings = SimpleNamespace(internal_secret="internal")

        with patch(
            "scripts.poster_api.app.dependencies",
            return_value=(settings, supabase),
        ):
            response = generate_poster(request, "internal")

        self.assertEqual(response["status"], "skipped")
        self.assertEqual(response["poster_path"], "2026/birthday/poster.png")
        self.assertIsNone(response["teams_delivered_at"])

    def test_missing_stored_object_is_reclaimed_for_regeneration(self):
        request = GeneratePosterRequest(
            event_id="745a9af7-2616-480f-ad06-59b29ce82237",
            event_type="birthday",
            event_date=date(1995, 7, 28),
            occurrence_date=date(2026, 7, 28),
            person_id="257838bc-b80f-408f-b124-7ab575effd91",
            person_name="Ada",
            photo_path="ada/profile.jpg",
            template_key="birthday-default",
        )
        claims = iter([None, {"id": "run-id"}])
        updates = []
        supabase = SimpleNamespace(
            claim_run=lambda *_: next(claims),
            get_run=lambda *_: {
                "id": "run-id",
                "poster_path": "2026/birthday/missing.png",
                "teams_delivered_at": None,
            },
            object_exists=lambda *_: False,
            update_run=lambda run_id, values: updates.append((run_id, values)),
            upload_png=lambda *_: None,
        )
        settings = SimpleNamespace(
            internal_secret="internal",
            chrome_binary="google-chrome",
        )

        with (
            patch(
                "scripts.poster_api.app.dependencies",
                return_value=(settings, supabase),
            ),
            patch(
                "scripts.poster_api.app.render_png",
                return_value=b"\x89PNG\r\n\x1a\n",
            ),
        ):
            response = generate_poster(request, "internal")

        self.assertEqual(response["status"], "stored")
        self.assertEqual(updates[0][1]["status"], "failed")

    def test_schedule_forwards_database_parameters_to_generation_endpoint(self):
        event = {
            "event_id": "745a9af7-2616-480f-ad06-59b29ce82237",
            "event_type": "birthday",
            "event_date": "1995-07-28",
            "template_key": "birthday-default",
            "person_id": "257838bc-b80f-408f-b124-7ab575effd91",
            "person_name": "Ada",
            "photo_path": "ada/profile.jpg",
        }
        supabase = SimpleNamespace(events_due_on=lambda *_: [event])
        settings = SimpleNamespace(
            schedule_secret="schedule",
            internal_secret="internal",
            generation_url="http://internal/generate",
            teams_webhook_url=None,
        )

        with (
            patch(
                "scripts.poster_api.app.dependencies",
                return_value=(settings, supabase),
            ),
            patch(
                "scripts.poster_api.app.post_json",
                return_value={
                    "status": "stored",
                    "poster_path": "2026/birthday/poster.png",
                    "run_id": "run-id",
                    "teams_delivered_at": None,
                },
            ) as post,
        ):
            response = run_schedule(
                ScheduleRequest(run_date=date(2026, 7, 28)), "schedule"
            )

        forwarded = post.call_args.args[1]
        self.assertEqual(forwarded["person_name"], "Ada")
        self.assertEqual(forwarded["occurrence_date"], "2026-07-28")
        self.assertEqual(response["generated"], 1)

    def test_stored_poster_is_counted_as_skipped_when_teams_is_disabled(self):
        event = {
            "event_id": "745a9af7-2616-480f-ad06-59b29ce82237",
            "person_name": "Ada",
        }
        supabase = SimpleNamespace(events_due_on=lambda *_: [event])
        settings = SimpleNamespace(
            schedule_secret="schedule",
            internal_secret="internal",
            generation_url="http://internal/generate",
            teams_webhook_url=None,
        )
        with (
            patch(
                "scripts.poster_api.app.dependencies",
                return_value=(settings, supabase),
            ),
            patch(
                "scripts.poster_api.app.post_json",
                return_value={
                    "status": "skipped",
                    "poster_path": "2026/birthday/poster.png",
                    "teams_delivered_at": None,
                },
            ),
        ):
            response = run_schedule(
                ScheduleRequest(run_date=date(2026, 7, 29)), "schedule"
            )

        self.assertEqual(response["skipped"], 1)
        self.assertEqual(response["generated"], 0)


if __name__ == "__main__":
    unittest.main()
