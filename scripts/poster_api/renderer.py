import subprocess
import tempfile
from datetime import date
from pathlib import Path
from urllib.parse import urlencode

from .models import GeneratePosterRequest


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "figma-export" / "index.html"


def completed_years(event_date: date, occurrence_date: date) -> int:
    return occurrence_date.year - event_date.year


def template_url(
    template: Path,
    request: GeneratePosterRequest,
    photo_path: Path | None = None,
) -> str:
    anniversary = request.event_type == "work_anniversary"
    parameters = {
        "export": "png",
        "poster": "anniversary" if anniversary else "birthday",
        "width": 540,
        "height": 675,
        "kicker": "Happy",
        "title": "Work Anniversary" if anniversary else "Birthday",
        "name": request.person_name,
        "message": (
            "Wishing you continued success and happiness ahead."
            if anniversary
            else "May this year bring you even more success and happiness."
        ),
    }
    if anniversary:
        years = completed_years(request.event_date, request.occurrence_date)
        parameters["years"] = (
            f"Cheers to {years} {'year' if years == 1 else 'years'}!"
        )
        if photo_path:
            parameters["photo"] = photo_path.resolve().as_uri()
    return f"{template.resolve().as_uri()}?{urlencode(parameters)}"


def render_png(
    request: GeneratePosterRequest,
    photo: bytes,
    photo_content_type: str,
    chrome_binary: str,
) -> bytes:
    extension = ".png" if photo_content_type == "image/png" else ".jpg"
    with tempfile.TemporaryDirectory(prefix="kovan-poster-") as directory:
        work = Path(directory)
        photo_path = work / f"employee{extension}"
        output_path = work / "poster.png"
        photo_path.write_bytes(photo)
        source = template_url(TEMPLATE, request, photo_path)
        subprocess.run(
            [
                chrome_binary,
                "--headless",
                "--disable-gpu",
                "--hide-scrollbars",
                "--allow-file-access-from-files",
                "--force-device-scale-factor=2",
                f"--user-data-dir={work / 'profile'}",
                "--run-all-compositor-stages-before-draw",
                "--virtual-time-budget=3000",
                "--window-size=540,675",
                f"--screenshot={output_path}",
                source,
            ],
            check=True,
            timeout=30,
        )
        png = output_path.read_bytes()
        if not png.startswith(b"\x89PNG\r\n\x1a\n"):
            raise RuntimeError("Chrome did not produce a valid PNG")
        return png
