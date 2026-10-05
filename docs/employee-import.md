# Employee birthday and joining-date import

The importer reads a CSV or XLSX file and upserts one `people` row plus one
birthday and one work-anniversary `events` row per employee.

Use these columns. `employee_id` is optional; when it is absent, the importer
uses a stable normalized name key.

```csv
employee_id,name,date_of_joining,birthday
EMP001,Asha,15 March 2022,28 July
EMP002,Ravi,02 January 2020,29 February
```

The workbook format is also accepted:

```text
Name | DOJ / Work anniversary | Birthday
```

`NA` joining dates and blank birthdays are left without that event. The person
record is still imported.

Validate without writing to Supabase:

```bash
python3 scripts/import_employees.py employees.csv --dry-run
```

Import the validated file:

```bash
python3 scripts/import_employees.py employees.xlsx
```

The command reads `SUPABASE_PROJECT_REF` (or `SUPABASE_URL`) and
`SUPABASE_SERVICE_ROLE_KEY` from the environment or `.env.poster-automation`.
It creates a neutral placeholder in the private `employee-photos` bucket when
an employee has no photo. Uploading a real photo later and changing that
employee's `people.photo_path` is safe; a later employee import preserves the
existing path.

Birthday events store only `event_month` and `event_day`. Joining events store
the full `event_date`, which is used to calculate completed years.
