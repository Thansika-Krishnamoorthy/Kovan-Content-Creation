import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_env(path: Path = ROOT / ".env.poster-automation") -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key, value.strip().strip("\"'"))


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    service_role_key: str
    chrome_binary: str
    schedule_secret: str
    internal_secret: str
    generation_url: str
    teams_webhook_url: str | None

    @classmethod
    def from_env(cls) -> "Settings":
        load_env()
        return cls(
            supabase_url=supabase_url(),
            service_role_key=required("SUPABASE_SERVICE_ROLE_KEY"),
            chrome_binary=os.getenv("CHROME_BINARY", "google-chrome"),
            schedule_secret=required("POSTER_SCHEDULE_SECRET"),
            internal_secret=required("POSTER_INTERNAL_API_SECRET"),
            generation_url=os.getenv(
                "POSTER_GENERATION_URL",
                "http://127.0.0.1:8000/api/posters/generate",
            ),
            teams_webhook_url=os.getenv("TEAMS_WEBHOOK_URL") or None,
        )


def required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is required in .env.poster-automation")
    return value


def supabase_url() -> str:
    configured = os.getenv("SUPABASE_URL")
    if configured:
        return configured.rstrip("/")
    project_ref = required("SUPABASE_PROJECT_REF")
    return f"https://{project_ref}.supabase.co"
