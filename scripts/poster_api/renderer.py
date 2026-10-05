import subprocess
import tempfile
from datetime import date
from pathlib import Path
from urllib.parse import urlencode

from .models import GeneratePosterRequest


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "figma-export" / "index.html"
ANIMATED_TEMPLATE = ROOT / "figma-export" / "index-animated.html"


def completed_years(event_date: date, occurrence_date: date) -> int:
    return occurrence_date.year - event_date.year


def template_url(
    template: Path,
    request: GeneratePosterRequest,
    photo_path: Path | None = None,
    skip_years: bool = False,
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
        if skip_years:
            parameters["years"] = ""  # Empty string to override placeholder
        else:
            years = completed_years(request.event_date, request.occurrence_date)
            parameters["years"] = (
                f"Cheers to {years} {'year' if years == 1 else 'years'}!"
            )
    if anniversary and photo_path:
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


def render_gif(
    request: GeneratePosterRequest,
    photo: bytes,
    photo_content_type: str,
    chrome_binary: str,
    frames: int = 48,
    fps: int = 6,
    width: int = 360,
    height: int = 450,
    skip_years: bool = False,
) -> bytes:
    """Render an animated poster from the animated HTML template."""
    if frames < 2:
        raise ValueError("frames must be >= 2")
    if request.event_type == "work_anniversary" and not photo:
        raise ValueError("An employee photo is required for work-anniversary GIFs")
    extension = ".png" if photo_content_type == "image/png" else ".jpg"
    with tempfile.TemporaryDirectory(prefix="kovan-poster-gif-") as directory:
        work = Path(directory)
        photo_path = work / f"employee{extension}"
        photo_path.write_bytes(photo)
        frame_paths: list[Path] = []
        for index in range(frames):
            frame_path = work / f"frame-{index:03d}.png"
            # Chrome can abort when repeatedly reusing a profile across rapid
            # headless launches (profile locks and stale renderer state). Give
            # every frozen frame an isolated profile and avoid /dev/shm limits.
            profile = work / f"profile-{index:03d}"
            source = template_url(ANIMATED_TEMPLATE, request, photo_path, skip_years=skip_years)
            separator = "&" if "?" in source else "?"
            source = f"{source}{separator}animation=gif"
            separator = "&" if "?" in source else "?"
            source = f"{source}{separator}frame={index / frames:.4f}"
            subprocess.run(
                [
                    chrome_binary, "--headless", "--disable-gpu", "--no-sandbox",
                    "--hide-scrollbars", "--allow-file-access-from-files",
                    "--disable-dev-shm-usage", "--no-first-run",
                    f"--user-data-dir={profile}",
                    "--run-all-compositor-stages-before-draw",
                    "--virtual-time-budget=4000", "--window-size=540,675",
                    f"--screenshot={frame_path}", source,
                ],
                check=True,
                timeout=40,
            )
            frame_paths.append(frame_path)

        gif_path = work / "poster.gif"
        subprocess.run(
            [
                "ffmpeg", "-y", "-framerate", str(fps),
                "-i", str(work / "frame-%03d.png"),
                "-filter_complex",
                (
                    f"scale={width}:{height}:flags=lanczos,fps={fps},"
                    "split[s0][s1];"
                    "[s0]palettegen=stats_mode=diff:max_colors=128[p];"
                    "[s1][p]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle"
                ),
                "-loop", "0", str(gif_path),
            ],
            check=True,
            timeout=90,
        )
        gif = gif_path.read_bytes()
        if not gif.startswith(b"GIF8"):
            raise RuntimeError("ffmpeg did not produce a valid GIF")
        return gif


def render_mp4(
    request: GeneratePosterRequest,
    photo: bytes,
    photo_content_type: str,
    chrome_binary: str,
    frames: int = 50,
    fps: int = 10,
    width: int = 540,
    height: int = 676,
) -> bytes:
    """Render the animated HTML poster as an H.264 MP4 video."""
    if frames < 2:
        raise ValueError("frames must be >= 2")
    if request.event_type == "work_anniversary" and not photo:
        raise ValueError("An employee photo is required for work-anniversary MP4s")
    # libx264 yuv420p requires even width and height.
    width += width % 2
    height += height % 2
    extension = ".png" if photo_content_type == "image/png" else ".jpg"
    with tempfile.TemporaryDirectory(prefix="kovan-poster-mp4-") as directory:
        work = Path(directory)
        photo_path = work / f"employee{extension}"
        photo_path.write_bytes(photo)
        for index in range(frames):
            frame_path = work / f"frame-{index:03d}.png"
            source = template_url(ANIMATED_TEMPLATE, request, photo_path)
            separator = "&" if "?" in source else "?"
            source = f"{source}{separator}animation=gif"
            source = f"{source}&frame={index / frames:.4f}"
            subprocess.run(
                [
                    chrome_binary, "--headless", "--disable-gpu", "--no-sandbox",
                    "--hide-scrollbars", "--allow-file-access-from-files",
                    f"--user-data-dir={work / f'profile-{index}'}",
                    "--run-all-compositor-stages-before-draw", "--virtual-time-budget=4000",
                    "--window-size=540,675", f"--screenshot={frame_path}", source,
                ],
                check=True,
                timeout=40,
            )
        output = work / "poster.mp4"
        subprocess.run(
            [
                "ffmpeg", "-y", "-framerate", str(fps),
                "-i", str(work / "frame-%03d.png"),
                "-vf", f"scale={width}:{height}:flags=lanczos,format=yuv420p",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(output),
            ],
            check=True,
            timeout=90,
        )
        mp4 = output.read_bytes()
        if not mp4.startswith(b"\x00\x00\x00") or b"ftyp" not in mp4[:32]:
            raise RuntimeError("ffmpeg did not produce a valid MP4")
        return mp4


def convert_png_to_webp(
    png_bytes: bytes,
    scale: float = 0.7,
    quality: int = 70,
    ffmpeg_binary: str = "ffmpeg",
) -> bytes:
    """Convert PNG bytes to WebP using ffmpeg to reduce file size.

    Mirrors the reference command:
        ffmpeg -i poster.png -vf "scale=iw*0.7:ih*0.7:flags=lanczos" \
               -c:v libwebp -quality 70 -lossless 0 poster.webp

    WebP at quality 70 is dramatically smaller than PNG (often 5-10x), which
    keeps the base64 payload sent to Teams well within Adaptive Card limits.
    """
    with tempfile.TemporaryDirectory(prefix="kovan-webp-") as directory:
        work = Path(directory)
        source = work / "poster.png"
        output = work / "poster.webp"
        source.write_bytes(png_bytes)
        subprocess.run(
            [
                ffmpeg_binary,
                "-i",
                str(source),
                "-vf",
                f"scale=iw*{scale}:ih*{scale}:flags=lanczos",
                "-c:v",
                "libwebp",
                "-quality",
                str(quality),
                "-lossless",
                "0",
                str(output),
            ],
            check=True,
            timeout=30,
        )
        webp = output.read_bytes()
        if not webp.startswith(b"RIFF") or b"WEBP" not in webp[:16]:
            raise RuntimeError("ffmpeg did not produce a valid WebP")
        return webp


def compress_webp_to_fit(
    webp_bytes: bytes,
    max_bytes: int = 28 * 1024,
    ffmpeg_binary: str = "ffmpeg",
) -> bytes:
    """Re-compress a WebP until its base64 payload fits under ``max_bytes``.

    Teams enforces a ~28 KB cap on the entire Adaptive Card payload. Base64
    inflates the image by ~33%, so the raw WebP must stay well under 28 KB.
    This progressively lowers quality and scale until the encoded payload
    fits, so an oversized poster is delivered instead of failing.
    """
    # Base64 inflates by ~4/3; leave headroom for the JSON wrapper/message.
    target = int(max_bytes * 0.70)
    for scale, quality in ((0.7, 70), (0.6, 60), (0.5, 50), (0.4, 40), (0.3, 30)):
        with tempfile.TemporaryDirectory(prefix="kovan-webp-fit-") as directory:
            work = Path(directory)
            source = work / "poster.webp"
            output = work / "poster_small.webp"
            source.write_bytes(webp_bytes)
            subprocess.run(
                [
                    ffmpeg_binary,
                    "-i",
                    str(source),
                    "-vf",
                    f"scale=iw*{scale}:ih*{scale}:flags=lanczos",
                    "-c:v",
                    "libwebp",
                    "-quality",
                    str(quality),
                    "-lossless",
                    "0",
                    str(output),
                ],
                check=True,
                timeout=30,
            )
            candidate = output.read_bytes()
            if len(candidate) <= target:
                return candidate
    # Last resort: return the smallest attempt even if still over the target.
    return candidate
