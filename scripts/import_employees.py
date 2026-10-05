"""Validate and upsert employee birthdays and joining dates into Supabase.

Input columns are: employee_id, name, date_of_joining, birthday.
Birthday values intentionally contain only day and month (for example,
``28 July``); joining dates contain a full year.
"""

from __future__ import annotations

import argparse
import csv
import io
import os
import re
from zipfile import ZipFile
from datetime import date, datetime
from pathlib import Path
from typing import Iterable
from typing import Optional
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw

try:  # Works both as ``python scripts/import_employees.py`` and as a module.
    from scripts.poster_api.supabase import SupabaseClient
except ModuleNotFoundError:  # pragma: no cover - direct CLI execution path
    from poster_api.supabase import SupabaseClient


REQUIRED_COLUMNS = {"name"}
COLUMN_ALIASES = {
    "doj_work_anniversary": "date_of_joining",
    "doj": "date_of_joining",
    "work_anniversary": "date_of_joining",
}
PLACEHOLDER_PATH = "defaults/employee-placeholder.png"


def _normalise_header(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")


def _canonical_header(value: object) -> str:
    header = _normalise_header(value)
    return COLUMN_ALIASES.get(header, header)


def _read_rows(path: Path) -> list[dict[str, str]]:
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ValueError("input file has no header row")
            headers = [_canonical_header(header) for header in reader.fieldnames]
            rows = [
                {
                    _canonical_header(key): (value or "").strip()
                    for key, value in row.items()
                    if key is not None
                }
                for row in reader
            ]
    elif path.suffix.lower() in {".xlsx", ".xlsm"}:
        try:
            from openpyxl import load_workbook
        except ImportError:
            headers, values = _read_xlsx_with_stdlib(path)
        else:
            workbook = load_workbook(path, read_only=True, data_only=True)
            sheet = workbook.active
            values = list(sheet.values)
            if not values:
                raise ValueError("input workbook is empty")
            headers = [_canonical_header(value) for value in values[0]]
            values = [
                [_cell_text(headers[index], value) for index, value in enumerate(row)]
                for row in values[1:]
            ]
        rows = [
            {
                headers[index]: _cell_text(headers[index], value)
                for index, value in enumerate(row)
                if index < len(headers) and headers[index]
            }
            for row in values
        ]
    else:
        raise ValueError("input must be a .csv, .xlsx, or .xlsm file")

    missing = REQUIRED_COLUMNS - set(headers)
    if missing:
        raise ValueError(f"missing required columns: {', '.join(sorted(missing))}")
    return [row for row in rows if any(row.values())]


def _read_xlsx_with_stdlib(path: Path) -> tuple[list[str], list[list[str]]]:
    """Read the first worksheet without requiring an XLSX package."""
    spreadsheet_ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    with ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = [
                "".join(node.text or "" for node in item.iter(f"{{{spreadsheet_ns}}}t"))
                for item in root.findall(f"{{{spreadsheet_ns}}}si")
            ]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relationship_map = {
            node.attrib["Id"]: node.attrib["Target"]
            for node in relationships
        }
        sheet = workbook.find(f"{{{spreadsheet_ns}}}sheets")[0]
        target = relationship_map[sheet.attrib[f"{{{rel_ns}}}id"]]
        worksheet_path = target if target.startswith("xl/") else f"xl/{target}"
        worksheet = ET.fromstring(archive.read(worksheet_path))

        values: list[list[str]] = []
        for row in worksheet.findall(f".//{{{spreadsheet_ns}}}sheetData/{{{spreadsheet_ns}}}row"):
            current: dict[int, str] = {}
            for cell in row.findall(f"{{{spreadsheet_ns}}}c"):
                reference = cell.attrib.get("r", "A1")
                column = 0
                for character in re.match(r"[A-Z]+", reference).group(0):
                    column = column * 26 + ord(character) - ord("A") + 1
                value = cell.find(f"{{{spreadsheet_ns}}}v")
                text = "" if value is None else value.text or ""
                if cell.attrib.get("t") == "s" and text:
                    text = shared[int(text)]
                current[column - 1] = text
            if current:
                values.append([current.get(index, "") for index in range(max(current) + 1)])
        if not values:
            raise ValueError("input workbook is empty")
        headers = [_canonical_header(value) for value in values[0]]
        return headers, values[1:]


def _cell_text(header: str, value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        if header == "birthday":
            return value.strftime("%d %B")
        return value.isoformat()
    return str(value).strip()


def _parse_joining_date(value: str, row_number: int) -> Optional[date]:
    if not value.strip() or value.strip().upper() in {"NA", "N/A", "-"}:
        return None
    formats = (
        "%d %B %Y", "%d %b %Y", "%d, %B, %Y", "%d, %b, %Y",
        "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d",
        "%d-%b-%y", "%d-%m-%y", "%d/%m/%y",
    )
    for format_string in formats:
        try:
            parsed = datetime.strptime(value.strip(), format_string).date()
            if parsed > date.today():
                raise ValueError("joining date is in the future")
            return parsed
        except ValueError as error:
            if str(error) == "joining date is in the future":
                raise ValueError(f"row {row_number}: {error}") from error
    raise ValueError(
        f"row {row_number}: invalid date_of_joining {value!r}; use DD Month YYYY"
    )


def _parse_birthday(value: str, row_number: int) -> Optional[tuple[int, int]]:
    if not value.strip() or value.strip().upper() in {"NA", "N/A", "-"}:
        return None
    cleaned = value.strip().replace(",", " ")
    cleaned = re.sub(r"\b(\d{1,2})(st|nd|rd|th)\b", r"\1", cleaned, flags=re.I)
    formats = (
        "%Y %d %B", "%Y %d %b", "%Y %d/%m", "%Y %d-%m",
        "%Y %d-%b", "%Y %d-%B",
        "%Y %d-%b-%y", "%Y %d-%B-%y",
    )
    for format_string in formats:
        try:
            parsed = datetime.strptime(f"2000 {cleaned}", format_string)
            # 2000 is used only for validation because it includes Feb 29;
            # no year is stored in Supabase.
            date(2000, parsed.month, parsed.day)
            return parsed.month, parsed.day
        except ValueError:
            continue
    raise ValueError(
        f"row {row_number}: invalid birthday {value!r}; use DD Month"
    )


def _slug(value: str) -> str:
    return "-".join(filter(None, re.sub(r"[^a-z0-9]+", "-", value.lower()).split("-")))


def _validated_rows(rows: Iterable[dict[str, str]]) -> list[dict]:
    result: list[dict] = []
    seen: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        employee_id = row.get("employee_id", "").strip() or f"name:{_slug(row.get('name', ''))}"
        name = row.get("name", "").strip()
        if not name:
            raise ValueError(f"row {row_number}: name is required")
        if employee_id in seen:
            raise ValueError(f"row {row_number}: duplicate employee_id {employee_id!r}")
        seen.add(employee_id)
        joining = _parse_joining_date(row.get("date_of_joining", ""), row_number)
        birthday = _parse_birthday(row.get("birthday", ""), row_number)
        result.append({
            "employee_id": employee_id,
            "name": name,
            "joining_date": joining,
            "birthday_month": birthday[0] if birthday else None,
            "birthday_day": birthday[1] if birthday else None,
        })
    if not result:
        raise ValueError("input contains no employee rows")
    return result


def _placeholder_png() -> bytes:
    image = Image.new("RGB", (512, 512), (238, 242, 247))
    draw = ImageDraw.Draw(image)
    draw.ellipse((176, 78, 336, 238), fill=(117, 132, 150))
    draw.ellipse((90, 220, 422, 520), fill=(117, 132, 150))
    output = io.BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"\''))


def _client() -> SupabaseClient:
    _load_env_file(Path(".env.poster-automation"))
    project_ref = os.getenv("SUPABASE_PROJECT_REF")
    url = os.getenv("SUPABASE_URL") or (
        f"https://{project_ref}.supabase.co" if project_ref else None
    )
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_PROJECT_REF (or SUPABASE_URL) and "
            "SUPABASE_SERVICE_ROLE_KEY are required"
        )
    return SupabaseClient(url, key)


def import_employees(path: Path, dry_run: bool = False) -> dict[str, int]:
    rows = _validated_rows(_read_rows(path))
    if dry_run:
        return {"rows": len(rows), "created": 0, "updated": 0}

    client = _client()
    placeholder_exists = client.object_exists("employee-photos", PLACEHOLDER_PATH)
    if not placeholder_exists:
        client.upload_png(PLACEHOLDER_PATH, _placeholder_png())

    created = updated = 0
    for row in rows:
        existing = client.person_by_employee_id(row["employee_id"])
        photo_path = (existing or {}).get("photo_path") or PLACEHOLDER_PATH
        person = client.upsert_person({
            "employee_id": row["employee_id"],
            "name": row["name"],
            "photo_path": photo_path,
            "timezone": (existing or {}).get("timezone") or "Asia/Kolkata",
            "active": (existing or {}).get("active", True),
        })
        if row["birthday_month"] is not None:
            client.upsert_event({
                "person_id": person["id"],
                "event_type": "birthday",
                "event_date": None,
                "event_month": row["birthday_month"],
                "event_day": row["birthday_day"],
                "template_key": "birthday-default",
                "active": True,
            })
        if row["joining_date"] is not None:
            client.upsert_event({
                "person_id": person["id"],
                "event_type": "work_anniversary",
                "event_date": row["joining_date"].isoformat(),
                "event_month": None,
                "event_day": None,
                "template_key": "anniversary-default",
                "active": True,
            })
        if existing:
            updated += 1
        else:
            created += 1
    return {"rows": len(rows), "created": created, "updated": updated}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        result = import_employees(args.file, dry_run=args.dry_run)
    except (OSError, RuntimeError, ValueError) as error:
        parser.error(str(error))
    mode = "validated" if args.dry_run else "imported"
    print(f"{mode} {result['rows']} employee rows")
    if not args.dry_run:
        print(f"created={result['created']} updated={result['updated']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
