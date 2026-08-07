"""Render Markdown into the existing Kovan Labs HTML templates."""

from __future__ import annotations

import html
import hashlib
import ipaddress
import json
import os
import re
import shutil
import socket
import subprocess
import tempfile
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import markdown
import yaml
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = {
    "conventional": ROOT / "templates" / "blog-template.html",
    "volume": ROOT / "templates" / "blog-volume-template.html",
    "radar": ROOT / "templates" / "blog-radar-template.html",
}
TEMPLATE_ALIASES = {
    "article": "conventional",
    "blog": "conventional",
    "standard": "conventional",
    "edition": "volume",
    "digest": "volume",
    "technology-radar": "radar",
}
REMOTE_IMAGE_LIMIT = 10 * 1024 * 1024
DEFAULT_MANIFEST = ROOT / "blog-generation-manifest.json"


class RenderError(RuntimeError):
    """Raised when a Markdown source cannot be rendered safely."""


@dataclass(frozen=True)
class Document:
    source: Path
    title: str
    summary: str
    author: str
    published_iso: str
    published_display: str
    category: str
    template: str
    body: str
    metadata: dict[str, Any]


REQUIRED_FIELDS = (
    "title",
    "summary",
    "author",
    "published_iso",
    "published_display",
    "category",
)


def validate_document(document: Document) -> None:
    """Confirm the required data-contract fields resolved before generation.

    A required field is considered present only when it is non-empty and does
    not still hold an unresolved ``{{PLACEHOLDER}}`` value. Missing values are
    reported together so a contributor can fix every gap in one pass instead of
    discovering them one generated file at a time.
    """
    missing = []
    for field in REQUIRED_FIELDS:
        value = str(getattr(document, field, "") or "").strip()
        if not value or "{{" in value:
            missing.append(field)
    if missing:
        raise RenderError(
            "Missing required fields before generation: " + ", ".join(missing)
        )


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "blog"


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", text, re.DOTALL)
    if not match:
        return {}, text

    try:
        parsed = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as error:
        raise RenderError(f"Invalid YAML frontmatter: {error}") from error
    if not isinstance(parsed, dict):
        raise RenderError("Markdown frontmatter must be a YAML mapping.")
    return {str(key).lower(): value for key, value in parsed.items()}, text[match.end() :]


def _plain_text(markdown_text: str) -> str:
    rendered = markdown.markdown(markdown_text, extensions=["extra"])
    return BeautifulSoup(rendered, "html.parser").get_text(" ", strip=True)


def _normalise_date(value: Any) -> tuple[str, str]:
    if isinstance(value, datetime):
        parsed = value.date()
    elif isinstance(value, date):
        parsed = value
    elif value:
        raw = str(value).strip()
        try:
            parsed = date.fromisoformat(raw)
        except ValueError:
            return raw, raw
    else:
        parsed = date.today()
    return parsed.isoformat(), parsed.strftime("%-d %B %Y")


def _git_added_date(source: Path) -> str | None:
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "--diff-filter=A",
                "--follow",
                "-1",
                "--format=%cs",
                "--",
                str(source.relative_to(ROOT)),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError, ValueError):
        return None
    return result.stdout.strip() or None


def _select_template(title: str, requested: Any) -> str:
    if requested:
        name = str(requested).strip().lower()
        name = TEMPLATE_ALIASES.get(name, name)
        if name not in TEMPLATES:
            choices = ", ".join(TEMPLATES)
            raise RenderError(f"Unknown template '{requested}'. Use one of: {choices}.")
        return name

    lowered = title.lower()
    if "radar" in lowered or any(term in lowered for term in ("maturity map", "adoption map", "ecosystem map")):
        return "radar"
    if any(term in lowered for term in ("volume", "edition", "digest", "monthly", "quarterly", "issue")):
        return "volume"
    return "conventional"


def load_document(source: Path, forced_template: str | None = None) -> Document:
    source = source.resolve()
    if not source.is_file() or source.suffix.lower() != ".md":
        raise RenderError(f"Markdown source does not exist: {source}")

    metadata, body = _parse_frontmatter(source.read_text(encoding="utf-8"))
    h1 = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
    title = str(metadata.get("title") or (h1.group(1) if h1 else source.stem.replace("_", " ").replace("-", " ").title())).strip()
    if h1:
        body = body[: h1.start()] + body[h1.end() :]
        body = body.lstrip("\n")

    first_paragraph = next(
        (
            block.strip()
            for block in re.split(r"\n\s*\n", body)
            if block.strip()
            and not block.lstrip().startswith(("#", "-", "*", ">", "```", "|", "!["))
        ),
        "",
    )
    summary = str(metadata.get("summary") or metadata.get("description") or _plain_text(first_paragraph)).strip()
    if len(summary) > 180:
        summary = summary[:177].rsplit(" ", 1)[0] + "…"

    published_iso, published_display = _normalise_date(
        metadata.get("date") or _git_added_date(source)
    )
    selected = _select_template(title, forced_template or metadata.get("template"))
    return Document(
        source=source,
        title=title,
        summary=summary,
        author=str(metadata.get("author") or "Kovan Labs"),
        published_iso=published_iso,
        published_display=published_display,
        category=str(metadata.get("category") or "Technology"),
        template=selected,
        body=body.strip(),
        metadata=metadata,
    )


def _is_private_host(hostname: str) -> bool:
    try:
        addresses = socket.getaddrinfo(hostname, None)
    except socket.gaierror as error:
        raise RenderError(f"Could not resolve remote image host '{hostname}'.") from error
    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return True
    return False


def _safe_image_name(source: str, fallback: str) -> str:
    name = Path(urllib.parse.unquote(urllib.parse.urlparse(source).path)).name
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip(".-")
    return name or fallback


def _unique_destination(directory: Path, name: str) -> Path:
    candidate = directory / name
    index = 2
    while candidate.exists():
        candidate = directory / f"{Path(name).stem}-{index}{Path(name).suffix}"
        index += 1
    return candidate


def _download_image(url: str, destination_dir: Path, index: int) -> Path:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise RenderError(f"Unsupported remote image URL: {url}")
    if _is_private_host(parsed.hostname):
        raise RenderError(f"Remote image host is not public: {parsed.hostname}")

    request = urllib.request.Request(url, headers={"User-Agent": "KovanBlogRenderer/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            content_type = response.headers.get_content_type()
            if not content_type.startswith("image/"):
                raise RenderError(f"Remote URL is not an image ({content_type}): {url}")
            length = response.headers.get("Content-Length")
            if length and int(length) > REMOTE_IMAGE_LIMIT:
                raise RenderError(f"Remote image exceeds 10 MB: {url}")
            data = response.read(REMOTE_IMAGE_LIMIT + 1)
    except (OSError, ValueError) as error:
        raise RenderError(f"Could not download remote image '{url}': {error}") from error
    if len(data) > REMOTE_IMAGE_LIMIT:
        raise RenderError(f"Remote image exceeds 10 MB: {url}")

    extension = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "image/svg+xml": ".svg",
    }.get(content_type, "")
    name = _safe_image_name(url, f"image-{index}{extension}")
    if not Path(name).suffix and extension:
        name += extension
    destination = _unique_destination(destination_dir, name)
    destination.write_bytes(data)
    return destination


def _copy_local_image(
    source_value: str,
    document: Document,
    destination_dir: Path,
    repo_root: Path,
) -> Path:
    parsed_path = urllib.parse.unquote(urllib.parse.urlparse(source_value).path)
    candidate = (document.source.parent / parsed_path).resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError as error:
        raise RenderError(
            f"Image path escapes the repository content directory: {source_value}"
        ) from error
    if not candidate.is_file():
        raise RenderError(f"Referenced image does not exist: {source_value}")
    destination = _unique_destination(destination_dir, _safe_image_name(source_value, "image"))
    shutil.copy2(candidate, destination)
    return destination


def _process_article(
    document: Document,
    output_path: Path,
    download_remote_images: bool,
    repo_root: Path,
) -> str:
    rendered = markdown.markdown(
        document.body,
        extensions=["extra", "sane_lists", "toc"],
        extension_configs={"toc": {"permalink": False}},
        output_format="html5",
    )
    soup = BeautifulSoup(rendered, "html.parser")

    for link in soup.find_all("a", href=True):
        parsed = urllib.parse.urlparse(link["href"])
        if parsed.scheme in {"http", "https"}:
            link["target"] = "_blank"
            link["rel"] = "noopener noreferrer"

    asset_dir = output_path.parent / "assets" / output_path.stem
    image_index = 0
    for image in soup.find_all("img"):
        image_index += 1
        source_value = str(image.get("src", "")).strip()
        alt = str(image.get("alt", "")).strip()
        if not source_value:
            raise RenderError("An image is missing its source path.")
        if not alt:
            raise RenderError(f"Image '{source_value}' needs meaningful alt text.")

        parsed = urllib.parse.urlparse(source_value)
        if parsed.scheme in {"http", "https"}:
            if download_remote_images:
                asset_dir.mkdir(parents=True, exist_ok=True)
                copied = _download_image(source_value, asset_dir, image_index)
                image["src"] = copied.relative_to(output_path.parent).as_posix()
        elif parsed.scheme or source_value.startswith("//"):
            raise RenderError(f"Unsupported image source: {source_value}")
        else:
            asset_dir.mkdir(parents=True, exist_ok=True)
            copied = _copy_local_image(source_value, document, asset_dir, repo_root)
            image["src"] = copied.relative_to(output_path.parent).as_posix()

        image["loading"] = "lazy"
        image["decoding"] = "async"
        parent = image.parent
        if parent and parent.name == "p" and not parent.get_text(strip=True) and len(parent.find_all("img", recursive=False)) == 1:
            figure = soup.new_tag("figure")
            parent.replace_with(figure)
            image.extract()
            figure.append(image)
            title = str(image.get("title", "")).strip()
            if title:
                caption = soup.new_tag("figcaption")
                caption.string = title
                figure.append(caption)

    for table in soup.find_all("table"):
        wrapper = soup.new_tag("div", attrs={"class": "table-wrap"})
        table.wrap(wrapper)
        for header in table.find_all("th"):
            header["scope"] = "col"

    _convert_faq_section(soup)
    return str(soup)


def _convert_faq_section(soup: BeautifulSoup) -> None:
    """Turn an FAQ H2 followed by H3 questions into native disclosures."""

    accepted_titles = {"frequently asked questions", "faq", "faqs"}
    for heading in soup.find_all("h2"):
        title = re.sub(r"\s+", " ", heading.get_text(" ", strip=True)).casefold()
        if title not in accepted_titles:
            continue

        siblings = []
        node = heading.next_sibling
        while node is not None:
            next_node = node.next_sibling
            if getattr(node, "name", None) == "h2":
                break
            siblings.append(node)
            node = next_node

        if not any(getattr(item, "name", None) == "h3" for item in siblings):
            continue

        section = soup.new_tag("section", attrs={"class": "faq"})
        heading_id = str(heading.get("id") or "faq-title")
        heading["id"] = heading_id
        section["aria-labelledby"] = heading_id
        heading.insert_before(section)
        heading.extract()
        section.append(heading)

        current_details = None
        for item in siblings:
            item.extract()
            if getattr(item, "name", None) == "h3":
                current_details = soup.new_tag("details")
                summary = soup.new_tag("summary")
                summary.string = item.get_text(" ", strip=True)
                current_details.append(summary)
                section.append(current_details)
            elif current_details is not None:
                current_details.append(item)
            else:
                section.append(item)
        break


ARTICLE_CSS = """
  <style id="markdown-renderer-styles">
    .rendered-article{position:relative;width:min(calc(100% - 48px),760px);margin-inline:auto;padding:32px 0 96px}
    .rendered-article .byline{display:flex;flex-wrap:wrap;gap:8px 24px;padding-bottom:24px;margin-bottom:32px;color:var(--grey);border-bottom:1px solid var(--line);font-size:.875rem}
    .rendered-article h2{margin:48px 0 16px}.rendered-article h3{margin:32px 0 12px}.rendered-article h4{margin:24px 0 8px;color:var(--ink);font-family:var(--font-display,var(--display));font-size:1.25rem}
    .rendered-article p{margin:0 0 16px}.rendered-article ul,.rendered-article ol{margin:0 0 20px;padding-left:1.5rem}.rendered-article li+li{margin-top:8px}
    .rendered-article figure{margin:32px 0}.rendered-article figure img{width:100%;height:auto;max-height:min(70vh,720px);object-fit:contain;border-radius:16px}.rendered-article figcaption{margin-top:8px;color:var(--grey);font-size:.8125rem}
    .rendered-article blockquote{margin:32px 0;padding:20px 24px;color:var(--body);background:var(--mist);border:0;border-radius:8px;box-shadow:0 0 0 1px rgba(0,102,164,.14),0 0 0 4px rgba(0,168,107,.05),0 0 24px rgba(0,102,164,.16)}
    .rendered-article blockquote p:last-child{margin-bottom:0}.rendered-article pre{overflow-x:auto;padding:20px;background:var(--mist);border-radius:8px}.rendered-article code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
    .rendered-article :not(pre)>code{padding:.1em .35em;background:var(--field,#edeeec);border-radius:4px}.rendered-article .table-wrap{overflow-x:auto;margin:24px 0;border:1px solid var(--line);border-radius:8px}
    .rendered-article table{width:100%;min-width:560px;border-collapse:collapse}.rendered-article th,.rendered-article td{padding:16px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}
    .rendered-article th{color:var(--paper);background:var(--ink);font-weight:600}.rendered-article tbody tr:nth-child(even){background:var(--mist)}.rendered-article tr:last-child td{border-bottom:0}
    .rendered-article hr{margin:48px 0;border:0;border-top:1px solid var(--line)}
    .rendered-article .faq{margin-top:48px;padding:0;background:transparent}.rendered-article .faq details{margin:12px 0;padding:16px 20px;background:var(--mist);border:1px solid transparent;border-radius:8px}
    .rendered-article .faq details[open]{background:var(--paper);border-color:var(--line);box-shadow:0 2px 8px rgba(9,12,8,.08)}.rendered-article .faq summary{cursor:pointer;color:var(--ink);font-family:var(--font-display,var(--display));font-weight:600}
    .rendered-article .faq details p:last-child{margin-bottom:0}
    @media(max-width:520px){.rendered-article{width:min(calc(100% - 32px),760px);padding-top:24px}.rendered-article th,.rendered-article td{padding:12px}}
  </style>
"""


def _replace_main(template: str, article_html: str, document: Document) -> str:
    byline = (
        '<div class="byline">'
        f"<span>By: <strong>{html.escape(document.author)}</strong></span>"
        f'<time datetime="{html.escape(document.published_iso)}">'
        f"Published {html.escape(document.published_display)}</time></div>"
    )
    main = f'<main class="rendered-article" id="main-content">{byline}{article_html}</main>'
    replaced, count = re.subn(r"<main\b[^>]*>.*?</main>", main, template, count=1, flags=re.DOTALL)
    if count != 1:
        raise RenderError(f"Template '{document.template}' does not contain exactly one main element.")
    return replaced


def _asset_prefix(output_path: Path) -> str:
    brand = ROOT / "05 Brand Assets"
    relative = Path(urllib.parse.quote(os.path.relpath(brand, output_path.parent), safe="/"))
    return relative.as_posix()


def _replace_brand_assets(template: str, output_path: Path, document: Document) -> str:
    prefix = _asset_prefix(output_path)
    names = ("logo_horizontal.png", "logo_mono_white.png", "graphic_dotwave.png", "graphic_rings.png", "graphic_spark.png")
    for name in names:
        template = re.sub(
            rf'https://res\.cloudinary\.com/[^"\']+/{re.escape(Path(name).stem)}[^"\']*\.png',
            f"{prefix}/{name}",
            template,
        )
    logo = "logo_mono_white.png" if document.template == "volume" else "logo_horizontal.png"
    if logo not in template:
        raise RenderError(f"Required brand logo '{logo}' was not found in the selected template.")
    return template


def _metadata_replacements(document: Document) -> dict[str, str]:
    volume_number = str(document.metadata.get("volume") or document.metadata.get("volume_number") or "1")
    series = str(document.metadata.get("series") or document.metadata.get("series_name") or "Kovan Labs insights")
    edition = str(document.metadata.get("edition") or document.metadata.get("edition_label") or "Edition")
    entry_count = str(
        document.metadata.get("entry_count")
        or max(1, len(re.findall(r"^##\s+", document.body, re.MULTILINE)))
    )
    return {
        "BLOG_TITLE": document.title,
        "VOLUME_TITLE": document.title,
        "VOLUME_NUMBER": volume_number,
        "ONE_LINE_SUMMARY": document.summary,
        "VOLUME_SUMMARY": document.summary,
        "AUTHOR_NAME": document.author,
        "EDITOR_NAME": document.author,
        "PUBLISH_DATE_ISO": document.published_iso,
        "PUBLISH_DATE_DISPLAY": document.published_display,
        "CATEGORY": document.category,
        "SERIES_NAME": series,
        "EDITION_LABEL": edition,
        "ENTRY_COUNT": entry_count,
        "YEAR": document.published_iso[:4] if re.match(r"^\d{4}", document.published_iso) else str(date.today().year),
    }


def _git(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=check,
    )


def _git_sha(ref: str) -> str:
    result = _git(["rev-parse", "--verify", "--quiet", ref], check=False)
    if result.returncode == 0:
        return result.stdout.strip()
    return ""


def _branch_exists_remote(branch: str) -> bool:
    result = _git(["ls-remote", "--heads", "origin", branch], check=False)
    return bool(result.stdout.strip())


def _branch_commit_sha(branch: str) -> str:
    """Return the head commit SHA for a branch, validating it exists."""
    sha = _git_sha(branch)
    if sha:
        return sha
    origin_sha = _git_sha(f"origin/{branch}")
    if origin_sha:
        return origin_sha
    if _branch_exists_remote(branch):
        raise RenderError(
            f"Source branch '{branch}' exists on 'origin' but is not fetched locally. "
            f"Run 'git fetch origin {branch}' first."
        )
    raise RenderError(
        f"Source branch '{branch}' does not exist locally or on 'origin'."
    )


def _materialise_branch_content(branch: str) -> Path:
    """Extract the committed content/ tree of a branch into a temp directory.

    Returns the temp directory whose layout mirrors ROOT (so the Markdown
    source path stays relative to the repository root).
    """
    ref = branch if _git_sha(branch) else f"origin/{branch}"
    proc = subprocess.run(
        ["git", "archive", "--format=tar", ref, "content/"],
        cwd=ROOT,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RenderError(
            f"Could not read content/ from branch '{branch}': "
            f"{proc.stderr.decode(errors='replace').strip()}"
        )
    temp_dir = Path(tempfile.mkdtemp(prefix="kovan-blog-branch-"))
    archive = temp_dir / "content.tar"
    archive.write_bytes(proc.stdout)
    extract = subprocess.run(
        ["tar", "-xf", str(archive), "-C", str(temp_dir)],
        capture_output=True,
        text=True,
    )
    if extract.returncode != 0:
        raise RenderError(f"Could not extract content/ from branch '{branch}'.")
    return temp_dir


def _embed_provenance(template: str, provenance: dict[str, Any]) -> str:
    metas = "".join(
        f'<meta name="{key}" content="{html.escape(str(value), quote=True)}">'
        for key, value in provenance.items()
    )
    comment = (
        "<!-- kovan-blog-provenance: "
        + json.dumps(provenance, sort_keys=True)
        + " -->"
    )
    head = re.search(r"<head[^>]*>", template)
    if head:
        return template[: head.end()] + metas + comment + template[head.end() :]
    return template + comment


def render_file(
    source: Path,
    output_dir: Path,
    *,
    forced_template: str | None = None,
    download_remote_images: bool = False,
    overwrite: bool = False,
    output_path: Path | None = None,
    source_branch: str | None = None,
) -> Path:
    source = source.resolve()
    try:
        source_rel = source.relative_to(ROOT)
    except ValueError:
        raise RenderError(
            f"Source must be inside the repository content directory: {source}"
        )

    repo_root = ROOT
    provenance: dict[str, Any] | None = None
    if source_branch:
        commit_sha = _branch_commit_sha(source_branch)
        branch_root = _materialise_branch_content(source_branch)
        branch_source = (branch_root / source_rel).resolve()
        if not branch_source.is_file():
            raise RenderError(
                f"Markdown source '{source_rel.as_posix()}' does not exist on "
                f"branch '{source_branch}'."
            )
        source = branch_source
        repo_root = branch_root
        provenance = {
            "source_branch": source_branch,
            "source_file": source_rel.as_posix(),
            "source_commit": commit_sha,
        }

    document = load_document(source, forced_template)
    output_dir = output_dir.resolve()
    if document.template == "volume" and output_dir.name != "volume":
        output_dir = output_dir / "volume"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_path.resolve() if output_path else output_dir / f"{slugify(document.title)}.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and not overwrite:
        raise RenderError(f"Output already exists: {output_path}. Use --overwrite to replace it.")

    for required in TEMPLATES.values():
        if not required.is_file():
            raise RenderError(f"Required template is missing: {required}")
    article_html = _process_article(document, output_path, download_remote_images, repo_root)
    template = TEMPLATES[document.template].read_text(encoding="utf-8")
    template = _replace_main(template, article_html, document)
    template = re.sub(
        r'<nav class="section-nav".*?</nav>',
        "",
        template,
        count=1,
        flags=re.DOTALL,
    )
    template = _replace_brand_assets(template, output_path, document)
    validate_document(document)
    for key, value in _metadata_replacements(document).items():
        template = template.replace(f"{{{{{key}}}}}", html.escape(value, quote=True))
    template = template.replace("</head>", f"{ARTICLE_CSS}</head>", 1)

    if provenance is not None:
        template = _embed_provenance(template, provenance)

    leftovers = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", template)))
    if leftovers:
        raise RenderError(f"Unresolved template placeholders: {', '.join(leftovers)}")

    output_path.write_text(template, encoding="utf-8")
    return output_path


def source_hash(source: Path) -> str:
    return hashlib.sha256(source.read_bytes()).hexdigest()


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "sources": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise RenderError(f"Invalid blog generation manifest: {error}") from error
    if not isinstance(data, dict):
        raise RenderError("Blog generation manifest must be a JSON object.")
    sources = data.setdefault("sources", {})
    if not isinstance(sources, dict):
        raise RenderError("Blog generation manifest 'sources' must be a JSON object.")
    data.setdefault("version", 1)
    return data


def save_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_file_with_manifest(
    source: Path,
    output_dir: Path,
    manifest: dict[str, Any],
    *,
    forced_template: str | None = None,
    download_remote_images: bool = False,
    source_branch: str | None = None,
) -> tuple[Path | None, str]:
    source = source.resolve()
    source_key = source.relative_to(ROOT).as_posix()
    current_hash = source_hash(source)
    sources = manifest.setdefault("sources", {})
    previous = sources.get(source_key)
    if (
        source_branch is None
        and isinstance(previous, dict)
        and previous.get("source_hash") == current_hash
    ):
        output_value = previous.get("output_file")
        output_path = ROOT / str(output_value) if output_value else None
        return output_path, "skipped"

    document = load_document(source, forced_template)
    stored_output = previous.get("output_file") if isinstance(previous, dict) else None
    output_path = ROOT / str(stored_output) if stored_output else None
    if output_path is not None:
        output_path = output_path.resolve()
    rendered = render_file(
        source,
        output_dir,
        forced_template=forced_template,
        download_remote_images=download_remote_images,
        overwrite=True,
        output_path=output_path,
        source_branch=source_branch,
    )
    try:
        output_value = rendered.relative_to(ROOT).as_posix()
    except ValueError:
        output_value = rendered.as_posix()
    sources[source_key] = {
        "source_hash": current_hash,
        "output_file": output_value,
        "title": document.title,
        "template": document.template,
        "last_generated": date.today().isoformat(),
    }
    return rendered, "updated" if previous else "created"
