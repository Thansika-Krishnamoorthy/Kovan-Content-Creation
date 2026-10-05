import json
import time
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class SupabaseClient:
    def __init__(self, url: str, service_role_key: str):
        self.url = url.rstrip("/")
        self.headers = {
            "apikey": service_role_key,
            "authorization": f"Bearer {service_role_key}",
        }

    def events_due_on(self, occurrence_date: date) -> list[dict]:
        return self._json(
            "/rest/v1/rpc/poster_events_due_on",
            method="POST",
            body={"requested_date": occurrence_date.isoformat()},
        )

    def person_by_employee_id(self, employee_id: str) -> dict | None:
        rows = self._json(
            "/rest/v1/people"
            f"?employee_id=eq.{quote(employee_id, safe='')}"
            "&select=*&limit=1"
        )
        return rows[0] if rows else None

    def upsert_person(self, values: dict) -> dict:
        rows = self._json(
            "/rest/v1/people?on_conflict=employee_id",
            method="POST",
            body=values,
            extra_headers={
                "prefer": "resolution=merge-duplicates,return=representation",
            },
        )
        if not rows:
            raise RuntimeError("Supabase did not return the upserted person")
        return rows[0]

    def upsert_event(self, values: dict) -> dict:
        rows = self._json(
            "/rest/v1/events?on_conflict=person_id,event_type",
            method="POST",
            body=values,
            extra_headers={
                "prefer": "resolution=merge-duplicates,return=representation",
            },
        )
        if not rows:
            raise RuntimeError("Supabase did not return the upserted event")
        return rows[0]

    def claim_run(self, event_id: str, occurrence_date: date) -> dict | None:
        rows = self._json(
            "/rest/v1/rpc/claim_poster_run",
            method="POST",
            body={
                "requested_event_id": event_id,
                "requested_date": occurrence_date.isoformat(),
            },
        )
        return rows[0] if rows else None

    def update_run(self, run_id: str, values: dict) -> None:
        self._json(
            f"/rest/v1/poster_runs?id=eq.{quote(run_id, safe='')}",
            method="PATCH",
            body=values,
            extra_headers={"prefer": "return=minimal"},
        )

    def get_run(self, event_id: str, occurrence_date: date) -> dict | None:
        rows = self._json(
            "/rest/v1/poster_runs"
            f"?event_id=eq.{quote(event_id, safe='')}"
            f"&occurrence_date=eq.{occurrence_date.isoformat()}"
            "&select=*"
            "&limit=1"
        )
        return rows[0] if rows else None

    def download(self, bucket: str, path: str) -> tuple[bytes, str]:
        response = self._request(
            f"/storage/v1/object/{quote(bucket, safe='')}/{quote(path, safe='/')}"
        )
        content_type = response.headers.get_content_type()
        if content_type not in {"image/jpeg", "image/png", "image/webp", "image/gif", "video/mp4"}:
            raise RuntimeError(f"{bucket}/{path} must be JPEG, PNG, WebP, GIF, or MP4")
        return response.read(), content_type

    def upload_png(self, path: str, png: bytes) -> None:
        self._request(
            f"/storage/v1/object/generated-posters/{quote(path, safe='/')}",
            method="POST",
            data=png,
            extra_headers={"content-type": "image/png", "x-upsert": "true"},
        ).read()

    def upload_webp(self, path: str, webp: bytes) -> None:
        self._request(
            f"/storage/v1/object/generated-posters/{quote(path, safe='/')}",
            method="POST",
            data=webp,
            extra_headers={"content-type": "image/webp", "x-upsert": "true"},
        ).read()

    def upload_gif(self, path: str, gif: bytes) -> None:
        self._request(
            f"/storage/v1/object/generated-posters/{quote(path, safe='/')}",
            method="POST",
            data=gif,
            extra_headers={"content-type": "image/gif", "x-upsert": "true"},
        ).read()

    def upload_mp4(self, path: str, mp4: bytes) -> None:
        self._request(
            f"/storage/v1/object/generated-posters/{quote(path, safe='/')}",
            method="POST",
            data=mp4,
            extra_headers={"content-type": "video/mp4", "x-upsert": "true"},
        ).read()

    def delete_object(self, bucket: str, path: str) -> None:
        self._request(
            f"/storage/v1/object/{quote(bucket, safe='')}/{quote(path, safe='/')}",
            method="DELETE",
        ).read()

    def object_exists(self, bucket: str, path: str) -> bool:
        try:
            self._request(
                f"/storage/v1/object/{quote(bucket, safe='')}/"
                f"{quote(path, safe='/')}",
                method="GET",
                extra_headers={"range": "bytes=0-0"},
            ).read()
            return True
        except RuntimeError as error:
            if "not_found" in str(error) or "Object not found" in str(error):
                return False
            raise

    def signed_poster_url(self, path: str, expires_in: int = 3600) -> str:
        payload = self._json(
            f"/storage/v1/object/sign/generated-posters/{quote(path, safe='/')}",
            method="POST",
            body={"expiresIn": expires_in},
        )
        signed = payload["signedURL"]
        return signed if signed.startswith("http") else f"{self.url}/storage/v1{signed}"

    def list_objects(
        self,
        bucket: str,
        prefix: str = "",
        limit: int = 100,
    ) -> list[dict]:
        """List objects in a Storage bucket under an optional prefix.

        Returns a list of object metadata dicts (name, id, updated_at, ...).
        """
        return self._json(
            f"/storage/v1/object/list/{quote(bucket, safe='')}",
            method="POST",
            body={"prefix": prefix, "limit": limit},
        )

    def _json(
        self,
        path: str,
        method: str = "GET",
        body: dict | None = None,
        extra_headers: dict | None = None,
    ):
        data = json.dumps(body).encode() if body is not None else None
        response = self._request(
            path,
            method=method,
            data=data,
            extra_headers={"content-type": "application/json", **(extra_headers or {})},
        )
        content = response.read()
        return json.loads(content) if content else None

    def _request(
        self,
        path: str,
        method: str = "GET",
        data: bytes | None = None,
        extra_headers: dict | None = None,
        attempts: int = 4,
    ):
        request = Request(
            f"{self.url}{path}",
            method=method,
            data=data,
            headers={**self.headers, **(extra_headers or {})},
        )
        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                return urlopen(request, timeout=30)
            except HTTPError as error:
                detail = error.read().decode(errors="replace")
                # 5xx and 429 are transient; retry them. 4xx are permanent.
                if error.code < 500 and error.code != 429:
                    raise RuntimeError(
                        f"Supabase {error.code}: {detail}"
                    ) from error
                last_error = RuntimeError(f"Supabase {error.code}: {detail}")
            except (URLError, TimeoutError, OSError) as error:
                # DNS failures, connection resets, and timeouts are transient.
                last_error = error
            if attempt + 1 < attempts:
                time.sleep(2**attempt)
        raise RuntimeError(
            f"Supabase request failed after {attempts} attempts: {last_error}"
        ) from last_error
